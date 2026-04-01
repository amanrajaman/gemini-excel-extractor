import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from streamlit_cropper import st_cropper

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
st.markdown('<p class="sub-title">Batch process or precision-crop legacy records into searchable databases.</p>', unsafe_allow_html=True)

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
    model_choice = st.selectbox("AI Vision Model", [ "gemini-2.5-flash"])
    st.divider()
    st.info("💡 **Smart Upload:** Upload 1 image to use the Precision Cropper, or multiple images for Auto-Batching.")

# --- 4. Main UI & Smart File Uploader ---
uploaded_files = st.file_uploader(
    "Upload Images (JPG/PNG)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.divider()
    
    images_to_process = [] # This will hold the final images (cropped or original)
    
    # --- THE SMART UX LOGIC ---
    if len(uploaded_files) == 1:
        # Precision Cropper Mode
        st.markdown("### ✂️ Step 2: Precision Crop")
        st.info("Drag the blue box to outline ONLY the data table. This removes background noise and improves accuracy.")
        
        col1, col2 = st.columns([1.5, 1])
        with col1:
            # Load and fix color profile
            img = Image.open(uploaded_files[0])
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Render the interactive cropper
            cropped_img = st_cropper(img, realtime_update=True, box_color='#1E3A8A')
            
        with col2:
            st.markdown("**Cropped Preview:**")
            st.image(cropped_img, use_container_width=True)
            
        images_to_process.append((uploaded_files[0].name, cropped_img))

    else:
        # Batch Mode
        st.info(f"📁 **{len(uploaded_files)} documents queued for high-speed batch processing.**")
        with st.expander("Preview First Document"):
            st.image(Image.open(uploaded_files[0]), use_container_width=True)
            
        for file in uploaded_files:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images_to_process.append((file.name, img))

    # --- THE EXTRACTION ENGINE ---
    if st.button("🚀 Digitize Data Now", use_container_width=True, type="primary"):
        
        master_df = pd.DataFrame()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, (filename, img) in enumerate(images_to_process):
            status_text.markdown(f"**Processing ({index + 1}/{len(images_to_process)}):** `{filename}` ...")
            
            try:
                # OPTIMIZATION: Shrink and compress the image before sending to AI
                img.thumbnail((2000, 2000))
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_bytes = img_byte_arr.getvalue()

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
                
                temp_df = pd.DataFrame(data)
                temp_df.insert(0, 'source_file', filename)
                master_df = pd.concat([master_df, temp_df], ignore_index=True)

            except Exception as e:
                st.error(f"⚠️ Error processing `{filename}`. Error: {e}")
            
            progress_bar.progress((index + 1) / len(images_to_process))

        # --- FINAL RESULTS DISPLAY ---
        status_text.empty() 
        
        if not master_df.empty:
            st.toast('Extraction Complete!', icon='🎉')
            st.balloons()
            st.markdown("### 📊 Digitized Database")
            
            edited_df = st.data_editor(master_df, use_container_width=True, num_rows="dynamic", hide_index=True)
            csv = edited_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Verified Database (CSV)",
                data=csv,
                file_name="digitized_records.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
