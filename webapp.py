import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types
from PIL import Image

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(
    page_title="VisionAI Ledger Digitizer", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title { font-size: 2.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0rem; }
    .sub-title { font-size: 1.2rem; color: #6B7280; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">✨ VisionAI Document Digitizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Batch process handwritten legacy records into unified, searchable databases.</p>', unsafe_allow_html=True)

# --- 2. Setup Gemini Client ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ API Key not found! Please check your Streamlit App Secrets.")
    st.stop()

try:
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
except Exception:
    client = genai.Client(api_key=api_key) 

# --- 3. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103254.png", width=60)
    st.header("⚙️ Engine Settings")
    model_choice = st.selectbox("AI Vision Model", ["gemini-2.5-flash"])
    st.divider()
    st.info("💡 **Pro Tip:** You can upload multiple pages at once. The AI will stitch them into a single master database.")

# --- 4. Main UI & Bulk File Uploader ---
# UPDATED: accept_multiple_files=True allows batch uploading
uploaded_files = st.file_uploader(
    "Upload Images (JPG/PNG) - Select multiple files at once", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files: # If the list is not empty
    st.divider()
    
    st.info(f"📁 **{len(uploaded_files)} document(s) queued for processing.**")
    
    # Show a small preview of the first document to confirm upload
    with st.expander("Preview First Document"):
        st.image(Image.open(uploaded_files[0]), use_container_width=True)

    if st.button("🚀 Digitize Entire Batch Now", use_container_width=True, type="primary"):
        
        # Initialize our Master Database and UI elements
        master_df = pd.DataFrame()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Loop through every uploaded image
        for index, file in enumerate(uploaded_files):
            status_text.markdown(f"**Processing ({index + 1}/{len(uploaded_files)}):** `{file.name}` ...")
            
            try:
                file.seek(0)
                img_bytes = file.read()

                prompt = """
                Carefully analyze the uploaded document and extract all the tabular data.
                Step 1: Identify the column headers natively present in the document.
                Step 2: Extract every row of handwritten or typed data.
                CRITICAL INSTRUCTIONS: 
                - Return ONLY a valid JSON array of objects. 
                - The keys for each object must be the column headers you identified (format them in snake_case).
                - Do NOT include any explanations or markdown. Just the raw JSON array.
                """

                response = client.models.generate_content(
                    model=model_choice,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ]
                )

                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_json)
                
                # Convert this single image's data to a DataFrame
                temp_df = pd.DataFrame(data)
                
                # DATA LINEAGE: Add a column to track which image this row came from
                temp_df.insert(0, 'source_file', file.name)
                
                # Stitch it into the Master Database
                master_df = pd.concat([master_df, temp_df], ignore_index=True)

            except Exception as e:
                st.error(f"⚠️ Error processing `{file.name}`. Skipping this file. Error: {e}")
            
            # Update the progress bar
            progress_bar.progress((index + 1) / len(uploaded_files))

        # --- Display Final Results ---
        status_text.empty() # Clear the status text
        
        if not master_df.empty:
            st.toast('Batch Extraction Complete!', icon='🎉')
            st.balloons()
            
            st.markdown("### 📊 Master Digitized Database")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Total Rows Extracted", len(master_df))
            metric_col2.metric("Total Columns", len(master_df.columns))
            metric_col3.metric("Documents Processed", len(uploaded_files))

            st.markdown("*(Double-click any cell below to edit before downloading)*")
            edited_df = st.data_editor(master_df, use_container_width=True, num_rows="dynamic", hide_index=True)

            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Master Database (CSV)",
                data=csv,
                file_name="master_digitized_records.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        else:
            st.error("❌ Failed to extract data from the uploaded batch. Please check the images and try again.")
