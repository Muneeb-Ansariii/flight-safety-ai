# utils/parser.py

def extract_airline_code(flight_number: str) -> str:
    """Extracts the first 2 characters of the flight number as airline code"""
    return flight_number[:2].upper()

