import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --------------------------
# Helper Functions
# --------------------------

def fetch_worldbank_data(country_code, indicator):
    """
    Fetch yearly data from the World Bank API.
    """
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=60"
    response = requests.get(url)

    try:
        data = response.json()[1]
    except:
        return None

    records = []
    for entry in data:
        if entry["value"] is not None:
            records.append({"year": int(entry["date"]), "value": float(entry["value"])})

    df = pd.DataFrame(records)
    return df.sort_values("year")


def interpret_economy(gdp_df, inf_df):
    """
    Generate simple interpretation of GDP and Inflation trends.
    """
    interpretation = ""

    # GDP Trend
    if gdp_df is not None and len(gdp_df) > 1:
        if gdp_df["value"].iloc[-1] > gdp_df["value"].iloc[0]:
            interpretation += "- **GDP is growing overall**, indicating economic expansion.\n"
        else:
            interpretation += "- **GDP is declining**, suggesting slower economic activity.\n"

    # Inflation Trend
    if inf_df is not None and len(inf_df) > 1:
        latest_inf = inf_df["value"].iloc[-1]
        if latest_inf > 6:
            interpretation += f"- Inflation is **high ({latest_inf:.2f}%)**, risk of prices rising quickly.\n"
        elif latest_inf < 2:
            interpretation += f"- Inflation is **very low ({latest_inf:.2f}%)**, may indicate weak demand.\n"
        else:
            interpretation += f"- Inflation is **stable ({latest_inf:.2f}%)**, which is healthy.\n"

    return interpretation


# --------------------------
# Streamlit UI
# --------------------------

st.title("🌍 Country GDP & Inflation Explorer")
st.write("Select a country to view its economic indicators year-by-year.")

# List of countries + World Bank country codes
countries = {
    "India": "IN",
    "United States": "US",
    "United Kingdom": "GB",
    "China": "CN",
    "Japan": "JP",
    "Germany": "DE",
    "France": "FR",
    "Canada": "CA",
    "Australia": "AU",
    "Brazil": "BR",
    "Russia": "RU",
}

country = st.selectbox("Choose a Country", list(countries.keys()))
code = countries[country]

st.subheader(f"📊 Economic Data for {country}")

# GDP (Indicator: NY.GDP.MKTP.CD)
gdp_df = fetch_worldbank_data(code, "NY.GDP.MKTP.CD")

# Inflation (Indicator: FP.CPI.TOTL.ZG)
inf_df = fetch_worldbank_data(code, "FP.CPI.TOTL.ZG")

if gdp_df is not None and inf_df is not None:
    # GDP Chart
    st.write("### 💵 GDP (Current US$)")
    fig_gdp = px.line(gdp_df, x="year", y="value", markers=True,
                      title=f"GDP Trend - {country}")
    st.plotly_chart(fig_gdp)

    # Inflation Chart
    st.write("### 📈 Inflation Rate (%)")
    fig_inf = px.line(inf_df, x="year", y="value", markers=True,
                      title=f"Inflation Trend - {country}")
    st.plotly_chart(fig_inf)

    # Show Data Tables
    st.write("### 📄 GDP Data Table")
    st.dataframe(gdp_df)

    st.write("### 📄 Inflation Data Table")
    st.dataframe(inf_df)

    # Interpretation
    st.write("### 🧠 Interpretation")
    st.info(interpret_economy(gdp_df, inf_df))

else:
    st.error("Unable to fetch data. Please try another country or check your internet connection.")

