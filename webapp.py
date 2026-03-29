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

# Injecting Custom CSS for a premium look
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A; /* Deep Blue */
        margin-bottom: 0rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Header Section ---
st.markdown('<p class="main-title">✨ VisionAI Document Digitizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Transform messy, handwritten legacy records into searchable, editable databases instantly.</p>', unsafe_allow_html=True)

# --- 3. Setup Gemini Client ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ API Key not found! Please check your Streamlit App Secrets.")
    st.stop()

try:
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
except Exception:
    client = genai.Client(api_key=api_key) 

# --- 4. Sidebar: Agency Branding & Settings ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103254.png", width=60) # Placeholder logo
    st.header("⚙️ Engine Settings")
    model_choice = st.selectbox(
        "AI Vision Model", 
        ["gemini-2.5-flash"],
        help="Select the AI engine. 1.5 is stable and fast. 2.0 is experimental."
    )
    st.divider()
    st.markdown("### About")
    st.info("Built for modern Real Estate workflows. Ensure your documents are well-lit for the highest accuracy.")

# --- 5. Main UI & File Uploader ---
st.info("💡 **Step 1:** Upload a physical property ledger, invoice, or handwritten form.")
uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    st.divider()
    
    # Create an attractive two-column layout
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("### 📄 Original Document")
        image = Image.open(uploaded_file)
        # Add a subtle border to the image
        st.image(image, use_container_width=True)

    with col2:
        st.markdown("### 📊 Extracted Data")
        
        # The extraction button with primary accent color
        if st.button("🚀 Digitize Document Now", use_container_width=True, type="primary"):
            with st.spinner("🧠 AI is analyzing the document structure and reading handwriting..."):
                try:
                    uploaded_file.seek(0)
                    img_bytes = uploaded_file.read()

                    # The dynamic universal prompt
                    prompt = """
                    Carefully analyze the uploaded document and extract all the tabular data.
                    
                    Step 1: Identify the column headers natively present in the document.
                    Step 2: Extract every row of handwritten or typed data.
                    
                    CRITICAL INSTRUCTIONS: 
                    - Return ONLY a valid JSON array of objects. 
                    - The keys for each object must be the column headers you identified (format them in snake_case, e.g., 'owner_name', 'lot_size').
                    - Do NOT include any explanations, warnings, or markdown formatting like ```json. Just return the raw JSON array.
                    """

                    response = client.models.generate_content(
                        model=model_choice,
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                        ]
                    )

                    # Parse JSON
                    clean_json = response.text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(clean_json)
                    df = pd.DataFrame(data)

                    # --- Success UI Updates ---
                    st.toast('Extraction Successful!', icon='🎉')
                    st.balloons()
                    
                    # Display Dashboard Metrics
                    metric_col1, metric_col2 = st.columns(2)
                    metric_col1.metric("Rows Extracted", len(df))
                    metric_col2.metric("Columns Detected", len(df.columns))

                    st.markdown("*(Double-click any cell below to edit the data before downloading)*")
                    
                    # The Interactive Data Editor
                    edited_df = st.data_editor(
                        df, 
                        use_container_width=True, 
                        num_rows="dynamic",
                        hide_index=True
                    )

                    st.divider()
                    
                    # Download Button using the EDITED dataframe
                    csv = edited_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Verified Data (CSV)",
                        data=csv,
                        file_name="digitized_records.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="primary"
                    )

                except json.JSONDecodeError:
                    st.error("❌ The AI did not return a valid format. Please try again.")
                    with st.expander("View Raw AI Output"):
                        st.write(response.text)
                except Exception as e:
                    st.error(f"❌ Connection Error: {e}")