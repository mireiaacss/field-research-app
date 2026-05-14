import streamlit as st
import pandas as pd
from streamlit_gps_location import gps_location_button
from fpdf import FPDF

# Page configuration
st.set_page_config(
    page_title="Field Researcher App",
    layout="centered"
)

st.title("Field Researcher App")

# 1. User Information
st.subheader("Discovery Details")
name = st.text_input("Researcher Name")
title = st.text_input("Title of the Discovery")
description = st.text_area("Description / Notes")

# 2. GPS Location
st.subheader("Location")
location_data = gps_location_button(buttonText="Get my location")

# Variables to store coordinates for the PDF
lat, lon = None, None

# Only create the map if we have valid location data
if location_data is not None:
    st.write("Your location data:")
    st.json(location_data)

    # Ensure latitude and longitude are not None
    if location_data.get('latitude') is not None and location_data.get('longitude') is not None:
        lat = location_data['latitude']
        lon = location_data['longitude']
        map_data = pd.DataFrame({
            'lat': [lat],
            'lon': [lon]
        })
        st.subheader("Your location on the map")
        st.map(map_data)
else:
    st.info("Press 'Get my location' to see your location on the map.")

# 3. Visual Evidence
st.subheader("Visual Evidence")
photo = st.camera_input("Take a photo of the discovery")

# 4. PDF Report Generation & Validation
if st.button("Generate & Submit Report", use_container_width=True):
    # Ensure all required fields are completed
    if not name or not title or not description:
        st.error("Please complete all text fields (Name, Title, Description).")
    elif lat is None or lon is None:
        st.error("Please capture your GPS location.")
    elif photo is None:
        st.error("Please take a photo to provide visual evidence.")
    else:
        try:
            # Initialize PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Field Research Discovery Report", ln=True, align='C')
            
            # Metadata
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Researcher: {name}", ln=True)
            pdf.cell(200, 10, txt=f"Title: {title}", ln=True)
            pdf.cell(200, 10, txt=f"Coordinates: Latitude {lat}, Longitude {lon}", ln=True)
            
            # Description
            pdf.ln(5)
            pdf.multi_cell(0, 10, txt=f"Description:\n{description}")
            pdf.ln(5)
            
            # Write photo from memory to a local file so FPDF can read it
            with open("temp_evidence.jpg", "wb") as f:
                f.write(photo.getbuffer())
                
            # Add image to PDF
            pdf.image("temp_evidence.jpg", x=10, w=100)
            
            # Output PDF to byte string for Streamlit download
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            st.success(f"Hello {name}, your report is ready!")
            
            # Provide download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"{title.replace(' ', '_').lower()}_report.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            # Handle errors gracefully
            st.error(f"An error occurred while generating the PDF: {str(e)}")