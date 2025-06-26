import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 🚀 Load environment variables
load_dotenv()

# 🔗 Project imports
from utils.flight_api import get_flight_info
from utils.weather_api import get_weather_risk
from backendd.analysis import calculate_risk_score, get_risk_level
from utils.pdf_generator import generate_report

# 🌐 Page settings
st.set_page_config(page_title="Flight Safety Insight", layout="centered")
st.title("🛫 Flight Safety Insight")
st.subheader("Check flight safety using AI + real-time data.")

# ✏️ User inputs
flight_number = st.text_input("Enter Flight Number (e.g. EK202)")
date = st.date_input("Select Date")

# 🧠 Process button
if st.button("Analyze Flight"):
    st.info("🔍 Fetching flight information...")

    # Step 1: Get flight info from API
    flight_info = get_flight_info(flight_number)
    if flight_info:
        code = flight_info["airline_code"]
        st.success(f"✅ Flight Found: {flight_info['airline_name']} | Status: {flight_info['status']}")
        st.write(f"- From: `{flight_info['departure_airport']}`")
        st.write(f"- To: `{flight_info['arrival_airport']}`")
        st.write(f"- Airline Code: `{code}`")
    else:
        st.error("❌ Could not fetch flight information. Please check the flight number.")
        st.stop()

    # Step 2: Load airline safety data from local CSV
    df = pd.read_csv("data/airline_safety.csv")
    match = df[df["airline_code"] == code]

    if not match.empty:
        airline = match.iloc[0]

        # Step 3: Calculate base risk score
        score = calculate_risk_score(airline['incidents'], airline['last_5_years_rating'])
        risk = get_risk_level(score)

        # Step 4: Weather check at arrival city
        arrival_city = flight_info["arrival_airport"].split(",")[0]
        show_weather = st.checkbox("🌦️ Show weather info even if no risk", value=True)
        weather_alert = get_weather_risk(arrival_city)

        if weather_alert:
            st.warning(f"⚠️ Weather Risk at Destination: {weather_alert}")
            score = max(0, score)
            risk = get_risk_level(score)
            score -= 15
        elif show_weather:
            st.info(f"✅ Weather at destination looks clear. No alerts.")


        # Store session for PDF report
        st.session_state.flight_data = {
            "flight_number": flight_number,
            "airline_name": airline["airline_name"],
            "score": score,
            "risk": risk,
            "weather_alert": weather_alert
        }

        # Step 5: Display Results
        st.subheader("✈️ Flight Safety Score")
        st.write(f"- Incidents: `{airline['incidents']}`")
        st.write(f"- Safety Rating (Last 5 Years): ⭐ {airline['last_5_years_rating']}/5")
        st.write(f"**Adjusted Score:** {score}/100")
        st.write(
            f"**Risk Level:** :red[{risk}]" if risk == "High Risk"
            else f"**Risk Level:** :orange[{risk}]" if risk == "Moderate Risk"
            else f"**Risk Level:** :green[{risk}]"
        )

        # Step 6: Show Trend Chart
        trend_df = pd.read_csv("data/incident_trend.csv")
        trend_airline = trend_df[trend_df["airline_code"] == code]

        if not trend_airline.empty:
            st.subheader("📊 Incident History (Last 4 Years)")
            fig, ax = plt.subplots()
            ax.bar(trend_airline["year"], trend_airline["incidents"], color='skyblue')
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Incidents")
            ax.set_title(f"{airline['airline_name']} - Incident Trend")
            st.pyplot(fig)

    else:
        st.error("❌ Airline not found in local safety database.")

# 📝 Generate PDF Report
if "flight_data" in st.session_state:
    data = st.session_state.flight_data
    if st.button("📄 Generate PDF Report"):
        pdf_buffer = generate_report(
            data["flight_number"],
            data["airline_name"],
            data["score"],
            data["risk"],
            data["weather_alert"]
        )
        st.download_button(
            label="⬇️ Download Report",
            data=pdf_buffer,
            file_name="Flight_Safety_Report.pdf",
            mime="application/pdf"
        )
