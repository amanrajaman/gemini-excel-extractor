# Gemini Ledger Extractor 📄➡️📊

An automated Python service that uses the **Google Gemini Vision API** to transcribe historical handwritten ledgers and export them directly into structured Excel files.

## 🚀 Overview

Extracting structured data from old, handwritten documents is notoriously difficult for traditional OCR. This project leverages the multimodal capabilities of the new `google-genai` SDK to "read" an image of a 1902 NYC Real Estate Assessment ledger, extract the specific columns, and format the output into a clean, ready-to-use `.xlsx` spreadsheet.

## 🛠️ Tech Stack

* **LLM:** Google Gemini API (Multimodal Vision)
* **Language:** Python 3.x
* **Data Processing:** Pandas, OpenPyxl
* **Environment Management:** `venv`, Python-dotenv

## 📁 Project Structure

```text
gemini-excel-extractor/
├── app.py              # Main extraction logic & API interaction
├── .env                # Private API Key (Not uploaded to GitHub)
├── .gitignore          # Prevents venv and .env from being committed
├── requirements.txt    # List of project dependencies
└── README.md           # Project documentation

⚙️ Setup & Installation
1. Clone the repository:

Bash
git clone [https://github.com/yourusername/gemini-excel-extractor.git](https://github.com/yourusername/gemini-excel-extractor.git)
cd gemini-excel-extractor
2. Set up the Virtual Environment:

Bash
python -m venv venv

# Windows Activation:
.\venv\Scripts\activate

# Mac/Linux Activation:
source venv/bin/activate
3. Install Dependencies:

Bash
pip install -r requirements.txt
4. Add your API Key:
Create a file named exactly .env in the root folder and add your Google Gemini API key:

Plaintext
GEMINI_API_KEY=your_actual_api_key_here
📖 How to Use
Place your target image (e.g., IMG_3991.jpg) into the project folder.

Update the image filename at the bottom of app.py if necessary.

Run the script:

Bash
python app.py
A new file named extracted_ledger_data.xlsx will be generated in your folder containing the structured data.

⚠️ Troubleshooting
Windows PowerShell Error: "running scripts is disabled"
If you get an error when trying to activate the virtual environment on Windows, you need to update your execution policy. Run this command once in your VS Code terminal (Run as Administrator is not required for CurrentUser scope):

PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### Your Next Step
Before you push this to GitHub, we need to make sure your `requirements.txt` file is generated so the `pip install -r requirements.txt` command in the README actually works for others.

Make sure your `(venv)` is active in the terminal, and run this:
```bash
pip freeze > requirements.txt
