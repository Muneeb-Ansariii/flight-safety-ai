def get_flight_info(flight_number, date_str):
    import os
    import requests

    API_KEY = os.getenv("AERODATABOX_API_KEY")
    HOST = "aerodatabox.p.rapidapi.com"

    url = f"https://{HOST}/flights/number/{flight_number}/{date_str}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": HOST
    }

    response = requests.get(url, headers=headers)
    print("📡 API URL:", response.url)

    try:
        data = response.json()
        print("📦 Raw JSON Response:", data)
    except Exception as e:
        print("❌ JSON Decode Error:", e)
        return None

    if isinstance(data, list) and len(data) > 0:
        flight = data[0]
        try:
            lat = flight["geography"]["latitude"]
            lon = flight["geography"]["longitude"]
            coordinates = {"lat": lat, "lon": lon}
        except:
            coordinates = None

        return {
            "airline_code": flight["airline"]["icao"],
            "airline_name": flight["airline"]["name"],
            "departure_airport": flight["departure"]["airport"]["name"],
            "arrival_airport": flight["arrival"]["airport"]["name"],
            "status": flight["status"],
            "coordinates": coordinates
        }

    print("❌ No flight found or unexpected format.")
    return None
