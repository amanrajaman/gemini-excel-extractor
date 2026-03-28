import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialize the modern Client
client = genai.Client(api_key=api_key)

def extract_ledger_to_excel(image_path):
    print(f"Processing {image_path}...")
    
    # In the new SDK, we can pass the path directly in the contents list
    prompt = """
    Extract all handwritten rows from this 1902 NYC Real Estate ledger.
    Return ONLY a JSON array of objects. 
    Keys: Owner, Street_No, Lot_No, Size_Lot, Size_House, Stories, Value, Corrected_Amount.
    """

    # 3. Use the unified generate_content method
    # We use 'gemini-1.5-flash' which is the stable workhorse for OCR
   # Use the stable model with the generous free tier
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[
            prompt,
            types.Part.from_bytes(
                data=open(image_path, "rb").read(),
                mime_type="image/jpeg"
            )
        ]
    )

    # 4. Parse the response
    try:
        # Remove markdown code blocks if the model included them
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_json)
        
        # 5. Save to Excel
        df = pd.DataFrame(data)
        output_file = "extracted_ledger_data.xlsx"
        df.to_excel(output_file, index=False)
        print(f"✅ Success! Data saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        print("Raw response from AI:", response.text)

# Run the extraction
if __name__ == "__main__":
    # Ensure your filename matches exactly (check if it's .jpg or .jpeg)
    extract_ledger_to_excel("IMG_3991.jpeg")