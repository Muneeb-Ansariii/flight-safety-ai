import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from dotenv import load_dotenv

# 🚀 Load environment variables
load_dotenv()

# 🔗 Project imports
from utils.flight_api import get_flight_info
from utils.weather_api import get_weather_risk
from backendd.analysis import calculate_risk_score, get_risk_level
from utils.pdf_generator import generate_report

# 🌐 Page settings and custom CSS
st.set_page_config(page_title="Flight Safety Insight", layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Roboto', sans-serif;
            background-image: url('https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?auto=format&fit=crop&w=1470&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }

        [data-testid="stAppViewContainer"] > .main {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }

        .title { font-size: 36px; font-weight: bold; margin-bottom: 0; color: black; }
        .subtitle { font-size: 20px; margin-top: 0; color: black; }
        .stButton>button { border-radius: 12px; font-size: 16px; padding: 0.5rem 1rem; background-color: #28a745 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='title'>🛫 Flight Safety Insight</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Analyze flight safety using real-time data and AI risk models</p>", unsafe_allow_html=True)

# --- Inputs ---
col1, col2 = st.columns([2, 1])
with col1:
    flight_number = st.text_input("Enter Flight Number", placeholder="e.g. EK202")
with col2:
    date = st.date_input("Select Flight Date", min_value=datetime.date.today())

# --- Analyze Button ---
if st.button("🔍 Analyze Flight"):
    with st.spinner("Fetching flight details and analyzing safety..."):
        date_str = date.strftime("%Y-%m-%d")
        flight_info = get_flight_info(flight_number, date_str)

        if not flight_info:
            st.error("❌ Could not fetch flight information. Please check the flight number.")
            st.stop()

        code = flight_info["airline_code"].strip().upper()

        # Airline code alias mapping
        code_aliases = {
            "PIA": "PK", "EMIRATES": "EK", "QATAR": "QR", "AIR INDIA": "AI",
            "BRITISH AIRWAYS": "BA", "SINGAPORE": "SQ", "LUFTHANSA": "LH",
            "TURKISH": "TK", "AIR FRANCE": "AF", "UNITED": "UA", "DELTA": "DL",
            "AMERICAN": "AA", "ETHIOPIAN": "ET", "CATHAY": "CX", "QANTAS": "QF",
            "ETIHAD": "EY", "SAUDI": "SV", "ANA": "NH", "KLM": "KL", "AIR CANADA": "AC",
            "UAE": "EK"
        }
        code = code_aliases.get(code, code)

        # --- Display Flight Info ---
        st.subheader("✈️ Flight Information")
        st.markdown(f"**Airline:** {flight_info['airline_name']} ({code})")
        st.markdown(f"**Status:** `{flight_info['status']}`")
        st.markdown(f"**Route:** `{flight_info['departure_airport']}` ➔ `{flight_info['arrival_airport']}`")

        # --- Airline Safety Check ---
        df = pd.read_csv("data/airline_safety.csv")
        match = df[df["airline_code"].str.strip().str.upper() == code]

        if match.empty:
            st.error("❌ Airline not found in local safety database.")
            st.stop()

        airline = match.iloc[0]
        score = calculate_risk_score(airline['incidents'], airline['last_5_years_rating'])
        risk = get_risk_level(score)

        # --- Weather Risk Analysis ---
        arrival_city = flight_info["arrival_airport"].split(",")[0]
        weather_alert = get_weather_risk(arrival_city)

        if weather_alert:
            st.warning(f"⚠️ Weather Risk at Destination: {weather_alert}")
            score = max(0, score - 15)
            risk = get_risk_level(score)
        else:
            st.success("✅ Weather at destination is clear.")

        # --- Delay & Cancellation Prediction ---
        delay_df = pd.read_csv("data/airline_delay.csv")
        delay_match = delay_df[delay_df["airline_code"].str.strip().str.upper() == code]

        if not delay_match.empty:
            delay_data = delay_match.iloc[0]
            st.subheader("⏱️ Delay & Cancellation Prediction")
            st.metric("Average Delay (mins)", delay_data["avg_delay_minutes"])
            st.metric("Cancellation Rate", f"{float(delay_data['cancellation_rate'])*100:.2f}%")

            delay_level = "Low"
            if delay_data["avg_delay_minutes"] > 30 or delay_data["cancellation_rate"] > 0.08:
                delay_level = "High"
            elif delay_data["avg_delay_minutes"] > 20 or delay_data["cancellation_rate"] > 0.05:
                delay_level = "Moderate"

            st.write(f"**Risk of delay/cancellation:** :orange[{delay_level}]" if delay_level == "Moderate"
                     else f"**Risk of delay/cancellation:** :red[{delay_level}]" if delay_level == "High"
                     else f"**Risk of delay/cancellation:** :green[{delay_level}]")
        else:
            st.warning("⚠️ Delay and cancellation data not available for this airline.")

        # --- Store Session Data ---
        st.session_state.flight_data = {
            "flight_number": flight_number,
            "airline_name": airline["airline_name"],
            "score": score,
            "risk": risk,
            "weather_alert": weather_alert
        }

        # --- Display Safety Score ---
        st.subheader("📊 Safety Score")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Incident Reports", airline['incidents'])
            st.metric("Safety Rating (5 Yrs)", f"⭐ {airline['last_5_years_rating']}/5")
        with col2:
            st.metric("Adjusted Score", f"{score}/100")
            st.metric("Risk Level", risk)

        # --- Incident Trend Chart ---
        trend_df = pd.read_csv("data/incident_trend.csv")
        trend_airline = trend_df[trend_df["airline_code"].str.strip().str.upper() == code]

        if not trend_airline.empty:
            st.subheader("📈 Incident History (Past 4 Years)")
            fig = px.bar(
                trend_airline,
                x="year",
                y="incidents",
                title=f"{airline['airline_name']} - Yearly Incident Trend",
                labels={"year": "Year", "incidents": "Incident Count"},
                color_discrete_sequence=["#4da6ff"]
            )
            fig.update_layout(
                xaxis=dict(tickmode='linear', tick0=2020, dtick=1),
                yaxis=dict(tickvals=[0, 1, 3, 5])
            )
            st.plotly_chart(fig, use_container_width=True)

# --- PDF Download ---
if "flight_data" in st.session_state:
    data = st.session_state.flight_data
    st.markdown("---")
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
