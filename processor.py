# ============================================================

# Intelligent Document Image Processing System (Streamlit-ready)
# ============================================================

import os
import re
import json
import cv2
import pandas as pd
import pytesseract
import easyocr
import camelot
from PIL import Image
from pdf2image import convert_from_path

# -------------------------------
# OCR Setup
# -------------------------------
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # adjust if needed
ocr_reader = easyocr.Reader(['en'], gpu=False)
os.makedirs("outputs", exist_ok=True)

# -------------------------------
# Helper Functions
# -------------------------------
def convert_pptx_to_pdf(pptx_path):
    os.system(f'libreoffice --headless --convert-to pdf "{pptx_path}" --outdir .')
    return pptx_path.replace(".pptx", ".pdf")

def load_images(file_path):
    images = []
    if file_path.lower().endswith(".pptx"):
        file_path = convert_pptx_to_pdf(file_path)
    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=200)
        for i, page in enumerate(pages):
            img_path = f"page_{i}.png"
            page.save(img_path, "PNG")
            images.append(img_path)
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        images.append(file_path)
    else:
        raise ValueError("Unsupported file format")
    return images

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    return thresh

# -------------------------------
# OCR Functions
# -------------------------------
def extract_easyocr_text(image_path):
    lines = ocr_reader.readtext(image_path, detail=0)
    lines = [l for l in lines if len(l) > 2 and not re.match(r"^[^a-zA-Z0-9]+$", l)]
    return "\n".join(lines)

def extract_tesseract_text(image):
    config = "--oem 1 --psm 6"
    return pytesseract.image_to_string(image, config=config)

def extract_handwritten_text(image):
    config = "--oem 1 --psm 6"
    return pytesseract.image_to_string(image, config=config)

# -------------------------------
# Layout / Structure Helpers
# -------------------------------
def split_into_paragraphs(text):
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 10]

def detect_headings(text):
    return [line.strip() for line in text.split("\n") if len(line) > 3 and line.isupper()]

def detect_multicolumn_text(image_path):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    left = img[:, :w//2]
    right = img[:, w//2:]
    return [extract_tesseract_text(left), extract_tesseract_text(right)]

# -------------------------------
# Cleaning Functions
# -------------------------------
def clean_headings(headings):
    cleaned = []
    for h in headings:
        letters = sum(c.isalpha() for c in h)
        if letters > 2:
            cleaned.append(h)
    return cleaned

def clean_paragraphs(paragraphs):
    seen = set()
    cleaned = []
    for p in paragraphs:
        p_clean = re.sub(r'[^a-zA-Z0-9\s,.]', '', p)
        p_clean = re.sub(r'\s+', ' ', p_clean).strip()
        if len(p_clean) > 10 and p_clean not in seen:
            cleaned.append(p_clean)
            seen.add(p_clean)
    return cleaned

def clean_columns(columns, paragraphs):
    cleaned_columns = []
    para_set = set(paragraphs)
    for col in columns:
        col_clean = []
        for line in col.split('\n'):
            line_clean = re.sub(r'[^a-zA-Z0-9\s,.]', '', line).strip()
            if len(line_clean) > 5 and line_clean not in para_set:
                col_clean.append(line_clean)
        cleaned_columns.append("\n".join(col_clean))
    return cleaned_columns

# -------------------------------
# Document / Table / Form Extraction
# -------------------------------
def detect_document_type(text):
    t = text.lower()
    if "certificate" in t or "has successfully completed" in t:
        return "certificate"
    if ":" in t and "date" in t:
        return "form"
    return "generic"

def extract_key_values(text):
    kv = {}
    for line in text.split("\n"):
        if ":" in line:
            k,v = line.split(":",1)
            if 2 < len(k) < 40 and 1 < len(v) < 100:
                kv[k.strip()] = v.strip()
    return kv

def extract_tables_from_pdf(pdf_path):
    if not pdf_path.lower().endswith(".pdf"): return []
    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
    outputs = []
    for i, table in enumerate(tables):
        csv_path = f"outputs/table_{i}.csv"
        table.df.to_csv(csv_path, index=False)
        outputs.append({"table_index": i, "csv_path": csv_path, "data": table.df.to_dict(orient="records")})
    return outputs

def extract_contact_info(text):
    urls = re.findall(r'\b(?:https?://)?(?:www\.)?[\w\-]+\.[\w\.\-]+\b', text, re.IGNORECASE)
    emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    phones = re.findall(r'\b\d{7,15}\b', text)
    categories = re.findall(r'Pet Supplies|Games n Toys', text, re.IGNORECASE)
    return {"urls": urls, "emails": emails, "phones": phones, "categories": categories}

# -------------------------------
# Full Pipeline
# -------------------------------
def process_document(file_path):
    """
    Main function to process a document.
    Returns a list of pages compatible with app.py
    """
    if not file_path.lower().endswith((".pdf", ".pptx", ".png", ".jpg", ".jpeg")):
        return []

    # Load images from PDF, PPTX, or image
    image_paths = load_images(file_path)
    results = {"pages": [], "tables": extract_tables_from_pdf(file_path)}

    for img_path in image_paths:
        processed_img = preprocess_image(img_path)
        easy_text = extract_easyocr_text(img_path)
        tess_text = extract_tesseract_text(processed_img)
        handwritten_text = extract_handwritten_text(processed_img)
        combined_text = "\n".join([easy_text, tess_text, handwritten_text]).strip()
        multicol_texts = detect_multicolumn_text(img_path)

        # Clean & structured
        paragraphs = clean_paragraphs(split_into_paragraphs(combined_text))
        headings = clean_headings(detect_headings(combined_text))
        columns = clean_columns(multicol_texts, paragraphs)
        doc_type = detect_document_type(combined_text)
        key_values = extract_key_values(combined_text) if doc_type == "form" else {}
        contact_info = extract_contact_info(combined_text)

        results["pages"].append({
            "document_type": doc_type,
            "headings": headings,
            "paragraphs": paragraphs,
            "columns": columns,
            "key_value_pairs": key_values,
            "contacts": contact_info,
            "text": combined_text
        })

    # Save JSON for download
    os.makedirs("outputs", exist_ok=True)
    json_path = "outputs/output.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    # Build the list compatible with app.py
    pages_list = []
    for page in results["pages"]:
        pages_list.append({
            "text": page["text"],
            "cleaned_paragraphs": page["paragraphs"],
            "contacts": page["contacts"],
            "headings": page["headings"],
            "columns": page["columns"],
            "key_value_pairs": page["key_value_pairs"]
        })

    return pages_list

