import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Gemini Extractor", page_icon="📄")
st.title("📄 AI Powered data to Excel Extractor")
st.write("Upload a photo of a handwritten ledger to convert it into a structured spreadsheet.")

# 2. Setup Gemini Client
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found! Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Sidebar & File Uploader
st.sidebar.header("Settings")
model_choice = st.sidebar.selectbox("Select Model", ["gemini-2.5-flash"])

uploaded_file = st.file_uploader("Choose a ledger image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Show a preview of the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Preview", use_container_width=True)
    
    if st.button("🚀 Start Extraction"):
        with st.spinner("Gemini is reading the handwriting... please wait."):
            try:
                # Convert uploaded file to bytes for Gemini
                uploaded_file.seek(0)
                img_bytes = uploaded_file.read()

                prompt = """
                    Carefully analyze the uploaded document and extract all the tabular data.
                    
                    Step 1: Identify the column headers natively present in the document.
                    Step 2: Extract every row of handwritten or typed data.
                    
                    CRITICAL INSTRUCTIONS: 
                    - Return ONLY a valid JSON array of objects. 
                    - The keys for each object must be the column headers you identified (format them in snake_case, e.g., 'owner_name', 'lot_size').
                    - Do NOT include any explanations, warnings, or markdown formatting like ```json. Just return the raw JSON array.
                    """

                # Call the API
                response = client.models.generate_content(
                    model=model_choice,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ]
                )

                # Clean and Parse JSON
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_json)
                df = pd.DataFrame(data)

                # 4. Display Results
                st.success("Extraction Complete!")
                st.subheader("Data Preview")
                st.dataframe(df) # Shows an interactive table in the browser

                # 5. Download Button
                # We save it to a buffer so the user can download it directly
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv,
                    file_name="extracted_ledger.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.error(f"An error occurred: {e}")