import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import requests
import sys

# Set tesseract path (for Windows only)
# Uncomment and adjust path if needed:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

VALIDATION_API_URL = "https://example.com/api/validate"  # Replace with your API endpoint

def extract_text_from_image(image_path):
    """Extract text from image using Tesseract"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Could not process image {image_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Convert each page of PDF to image and extract text"""
    try:
        pages = convert_from_path(pdf_path)
        text = ""
        for i, page in enumerate(pages):
            text += pytesseract.image_to_string(page)
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Could not process PDF {pdf_path}: {e}")
        return ""

def validate_text_with_api(text):
    """Send extracted text to validation API"""
    try:
        payload = {"text": text}  # Change key based on your API
        response = requests.post(VALIDATION_API_URL, json=payload)
        if response.status_code == 200:
            print("✅ Validation successful! Status: 200")
        else:
            print(f"❌ Validation failed. Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] API request failed: {e}")

def process_file(file_path):
    """Process a single file (image or PDF)"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png']:
        text = extract_text_from_image(file_path)
    elif ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    else:
        print(f"[SKIP] Unsupported file type: {file_path}")
        return

    if text:
        print(f"\nExtracted text from {os.path.basename(file_path)}:\n{text[:200]}...\n")
        validate_text_with_api(text)
    else:
        print("[INFO] No text extracted.")

def process_folder(folder_path):
    """Process all files in a folder"""
    for root, _, files in os.walk(folder_path):
        for file in files:
            process_file(os.path.join(root, file))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_validator.py <file_or_folder_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    if os.path.isdir(input_path):
        process_folder(input_path)
    elif os.path.isfile(input_path):
        process_file(input_path)
    else:
        print("Invalid path provided.")
