# backendd/analysis.py

def calculate_risk_score(incidents: int, rating: float) -> int:
    """
    Simple scoring formula:
    - Start from 100
    - Subtract 5 points per incident
    - Subtract penalty for low rating (e.g., (5 - rating) * 10)
    """
    score = 100
    score -= incidents * 5
    score -= (5 - rating) * 10
    return max(0, min(100, int(score)))  # Bound between 0-100


def get_risk_level(score: int) -> str:
    if score >= 80:
        return "Low Risk"
    elif score >= 50:
        return "Moderate Risk"
    else:
        return "High Risk"
    
import random

def get_weather_alert() -> bool:
    """Simulates weather alert randomly (mocking real API)"""
    return random.choice([True, False])

