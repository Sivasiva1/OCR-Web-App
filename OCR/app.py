import streamlit as st
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from docx import Document
import tempfile
import base64
import requests
import pdfplumber
import cv2

def set_background(image_url):
    """Sets a background image from a URL using Base64 encoding."""
    response = requests.get(image_url)
    if response.status_code == 200:
        encoded_string = base64.b64encode(response.content).decode()
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.error("❌ Failed to load background image!")

def add_footer():
    """Adds a stylish footer with the team name."""
    footer = """
    <style>
        .footer {{
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 16px;
            font-family: 'Arial', sans-serif;
        }}
    </style>
    <div class="footer">
         Developed by <b>Code Hackers</b> | AI-Powered OCR Web App
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

def extract_text_from_image(image_bytes):
    """Extracts text from an image using OpenCV and Pytesseract."""
    try:
        # Convert bytes to numpy array
        image_array = np.frombuffer(image_bytes.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Decode into an image

        if image is None:
            return "⚠ Error: Invalid image format!"

        # Convert to grayscale and apply OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        return text.strip() if text.strip() else "⚠ No text detected!"
    except Exception as e:
        return f"⚠ Error extracting text: {str(e)}"

def extract_text_from_pdf(pdf_bytes):
    """Extracts text from a PDF using pdfplumber."""
    extracted_text = ""
    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text if extracted_text else "No text found"

def extract_text_from_docx(docx_bytes):
    """Extracts text from a Word document (.docx)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(docx_bytes.read())
        tmp_path = tmp.name
    doc = Document(tmp_path)
    extracted_text = "\n".join([para.text for para in doc.paragraphs])
    return extracted_text

def main():
    set_background("https://raw.githubusercontent.com/Sivasiva1/OCR-Web-App/main/OCR/static/AI-1.jpeg")

    st.title("📄 AI-Powered OCR Web App")
    st.write("Upload an **image, PDF, or Word document** to extract text.")

    # UI: Upload file
    uploaded_file = st.file_uploader("Upload a file", type=["png", "jpg", "jpeg", "pdf", "docx"])

    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ["png", "jpg", "jpeg"]:
            extracted_text = extract_text_from_image(uploaded_file)
        elif file_extension == "pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif file_extension == "docx":
            extracted_text = extract_text_from_docx(uploaded_file)
        else:
            extracted_text = "⚠ Unsupported file format!"

        st.subheader("📝 Extracted Text:")
        st.text_area("", extracted_text, height=300)

    add_footer()

if __name__ == "__main__":
    main()
