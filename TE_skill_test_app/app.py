from flask import Flask, render_template, request
import pandas as pd
import tradingeconomics as te

app = Flask(__name__)
te.login()


@app.route("/", methods=["GET", "POST"])
def home():

    table = ""
    if request.method == "POST":
        country = request.form.get("country")
        indicator = request.form.get("indicator")
        data = fetch_data(country, indicator)
    else:
        data = fetch_data("mexico", "gdp")

    # Process data
    data = data.dropna(subset=["LastUpdate"])
    del data["HistoricalDataSymbol"]

    table = data.to_html(classes="data", header="true", index=False)
    title = data.iloc[1, 0] + " - " + data.iloc[1, 1] + " data"
    labels = data["DateTime"].tolist()[::-1]
    values = data["Value"].tolist()[::-1]

    return render_template(
        "index.html", table=table, title=title, labels=labels, values=values
    )


@app.route("/compare", methods=["GET", "POST"])
def compare():

    table = ""
    if request.method == "POST":
        country1 = request.form.get("country1")
        country2 = request.form.get("country2")
        indicator = request.form.get("indicator")
    else:
        country1 = "Mexico"
        country2 = "Sweden"
        indicator = "GDP"

    data1 = fetch_data(country1, indicator)
    data2 = fetch_data(country2, indicator)

    # Process data for both countries
    data1 = data1.dropna(subset=["LastUpdate"])
    data2 = data2.dropna(subset=["LastUpdate"])

    del data1["HistoricalDataSymbol"]
    del data1["Category"]
    del data1["Country"]
    del data2["HistoricalDataSymbol"]
    del data2["Category"]
    del data2["Country"]

    # Create a combined DataFrame for comparison
    combined_data = pd.merge(
        data1, data2, on="DateTime", suffixes=(f"_{country1}", f"_{country2}")
    )
    table = combined_data.to_html(classes="data", header="true", index=False)

    title = f"{country1} vs {country2} - {indicator} data"
    labels = combined_data["DateTime"].tolist()[::-1]
    values1 = combined_data[f"Value_{country1}"].tolist()[::-1]
    values2 = combined_data[f"Value_{country2}"].tolist()[::-1]

    return render_template(
        "compare.html",
        table=table,
        title=title,
        labels=labels,
        values1=values1,
        values2=values2,
    )


def fetch_data(country, indicator):
    data = te.getHistoricalData(country=country, indicator=indicator, output_type="df")
    return data


if __name__ == "__main__":
    app.run(debug=True)
