import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_flight_info(flight_number):
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&flight_iata={flight_number}"

    try:
        response = requests.get(url)
        data = response.json()

        if data and "data" in data and len(data["data"]) > 0:
            flight_data = data["data"][0]
            return {
                "airline_name": flight_data["airline"]["name"],
                "airline_code": flight_data["airline"]["iata"],
                "departure_airport": flight_data["departure"]["airport"],
                "arrival_airport": flight_data["arrival"]["airport"],
                "status": flight_data["flight_status"]
            }
        else:
            return None

    except Exception as e:
        print("Error fetching flight data:", e)
        return None
