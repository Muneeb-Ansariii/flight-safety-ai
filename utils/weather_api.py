import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather_risk(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        # Basic risk logic (you can expand this later)
        weather = data["weather"][0]["main"].lower()
        wind_speed = data["wind"]["speed"]

        if "storm" in weather or "thunder" in weather:
            return "⚡ Storm/Turbulence Risk"
        elif wind_speed > 15:
            return "💨 High Wind Risk"
        elif "rain" in weather:
            return "🌧️ Rain Risk"
        else:
            return None

    except Exception as e:
        print("Weather API error:", e)
        return None
