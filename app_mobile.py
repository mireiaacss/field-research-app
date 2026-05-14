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
            
            # 1. Green Header Box
            pdf.set_fill_color(15, 135, 45) # Dark green matching the example
            pdf.set_text_color(255, 255, 255) # White text
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 20, txt="FIELD REPORT", ln=True, align='C', fill=True)
            pdf.ln(10)
            
            # 2. Researcher & Date Row
            current_date = pd.Timestamp.now().strftime("%d/%m/%Y") # Using pandas to avoid new imports
            pdf.set_text_color(0, 0, 0) # Back to black text
            pdf.set_font("Arial", 'B', 10)
            
            # Save Y position to keep them on the same line
            y_before = pdf.get_y()
            pdf.cell(100, 5, txt=f"Researcher: {name}", align='L')
            
            # Move to the right side for the date
            pdf.set_xy(100, y_before)
            pdf.cell(0, 5, txt=f"Date: {current_date}", align='R', ln=True)
            
            # 3. Coordinates
            pdf.set_font("Arial", '', 8)
            pdf.cell(0, 5, txt=f"Coordinates: Lat {lat}, Lon {lon}", ln=True)
            pdf.ln(3)
            
            # 4. Divider Line
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            # 5. Finding & Observations Text
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, txt=f"Finding: {title}", ln=True)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, txt="Observations:", ln=True)
            
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, txt=description)
            pdf.ln(10)
            
            # Write photo from memory to a local file so FPDF can read it
            with open("temp_evidence.jpg", "wb") as f:
                f.write(photo.getbuffer())
                
            pdf.image("temp_evidence.jpg", x=55, w=100)
            
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
