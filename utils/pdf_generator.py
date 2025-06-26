from fpdf import FPDF
from io import BytesIO

def generate_report(flight_number, airline, score, risk, weather_alert):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Flight Safety Report", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Flight Number: {flight_number}", ln=True)
    pdf.cell(200, 10, txt=f"Airline: {airline}", ln=True)
    pdf.cell(200, 10, txt=f"Score: {score}/100", ln=True)
    pdf.cell(200, 10, txt=f"Risk Level: {risk}", ln=True)

    weather_text = "Yes" if weather_alert else "No"
    pdf.cell(200, 10, txt=f"Weather Alert: {weather_text}", ln=True)

    # Return PDF as byte stream
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_bytes)
    return buffer
