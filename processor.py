# ============================================================
# Intelligent Document Image Processing System
# Production-Grade Core Logic 
# ============================================================

# -------------------------------
# Imports & Setup
# -------------------------------
import os
import re
import json
import uuid
import cv2
import pandas as pd
import pytesseract
import easyocr
import camelot
from pdf2image import convert_from_path

# -------------------------------
# Environment Setup
# -------------------------------
BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
ocr_reader = easyocr.Reader(['en'], gpu=False)

# -------------------------------
# File Utilities
# -------------------------------
def save_uploaded_file(uploaded_file):
    ext = uploaded_file.name.split(".")[-1]
    file_id = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    return file_path

def convert_pptx_to_pdf(pptx_path):
    os.system(f'libreoffice --headless --convert-to pdf "{pptx_path}" --outdir "{UPLOAD_DIR}"')
    return pptx_path.replace(".pptx", ".pdf")

def load_images(file_path):
    images = []

    if file_path.lower().endswith(".pptx"):
        file_path = convert_pptx_to_pdf(file_path)

    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=200)
        for i, page in enumerate(pages):
            img_path = os.path.join(UPLOAD_DIR, f"page_{i}.png")
            page.save(img_path, "PNG")
            images.append(img_path)

    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        images.append(file_path)

    else:
        raise ValueError("Unsupported file format")

    return images

# -------------------------------
# Image Preprocessing
# -------------------------------
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    return thresh

# -------------------------------
# OCR Engines
# -------------------------------
def extract_easyocr_text(image_path):
    lines = ocr_reader.readtext(image_path, detail=0)
    lines = [l for l in lines if len(l) > 2 and not re.match(r"^[^a-zA-Z0-9]+$", l)]
    return "\n".join(lines)

def extract_tesseract_text(image):
    return pytesseract.image_to_string(image, config="--oem 1 --psm 6")

def extract_handwritten_text(image):
    return pytesseract.image_to_string(image, config="--oem 1 --psm 6")

# -------------------------------
# Layout Analysis
# -------------------------------
def split_into_paragraphs(text):
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 10]

def detect_headings(text):
    return [l.strip() for l in text.split("\n") if l.isupper() and len(l) > 3]

def detect_multicolumn_text(image_path):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    left = img[:, :w//2]
    right = img[:, w//2:]
    return [
        extract_tesseract_text(left),
        extract_tesseract_text(right)
    ]

# -------------------------------
# Cleaning & Deduplication
# -------------------------------
def clean_headings(headings):
    return [h for h in headings if sum(c.isalpha() for c in h) > 2]

def clean_paragraphs(paragraphs):
    seen = set()
    cleaned = []

    for p in paragraphs:
        p = re.sub(r'[^a-zA-Z0-9\s,.]', '', p)
        p = re.sub(r'\s+', ' ', p).strip()

        if len(p) > 10 and p not in seen:
            cleaned.append(p)
            seen.add(p)

    return cleaned

def clean_columns(columns, paragraphs):
    para_set = set(paragraphs)
    cleaned = []

    for col in columns:
        lines = []
        for line in col.split("\n"):
            line = re.sub(r'[^a-zA-Z0-9\s,.]', '', line).strip()
            if len(line) > 5 and line not in para_set:
                lines.append(line)
        cleaned.append("\n".join(lines))

    return cleaned

# -------------------------------
# Document Intelligence
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
            k, v = line.split(":", 1)
            if 2 < len(k) < 40 and 1 < len(v) < 100:
                kv[k.strip()] = v.strip()
    return kv

def extract_contact_info(text):
    return {
        "urls": re.findall(r'(https?://\S+|www\.\S+)', text),
        "emails": re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text),
        "phones": re.findall(r'\b\d{7,15}\b', text)
    }

def extract_tables_from_pdf(pdf_path):
    if not pdf_path.lower().endswith(".pdf"):
        return []

    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
    outputs = []

    for i, table in enumerate(tables):
        csv_path = os.path.join(OUTPUT_DIR, f"table_{i}.csv")
        table.df.to_csv(csv_path, index=False)

        outputs.append({
            "table_index": i,
            "csv_path": csv_path,
            "data": table.df.to_dict(orient="records")
        })

    return outputs

# -------------------------------
#  MAIN PIPELINE 
# -------------------------------
def process_document(uploaded_file):
    file_path = save_uploaded_file(uploaded_file)

    image_paths = load_images(file_path)
    results = {
        "pages": [],
        "tables": extract_tables_from_pdf(file_path)
    }

    for img_path in image_paths:
        processed = preprocess_image(img_path)

        text = "\n".join([
            extract_easyocr_text(img_path),
            extract_tesseract_text(processed),
            extract_handwritten_text(processed)
        ]).strip()

        paragraphs = clean_paragraphs(split_into_paragraphs(text))
        headings = clean_headings(detect_headings(text))
        columns = clean_columns(detect_multicolumn_text(img_path), paragraphs)

        doc_type = detect_document_type(text)
        key_values = extract_key_values(text) if doc_type == "form" else {}

        results["pages"].append({
            "document_type": doc_type,
            "headings": headings,
            "paragraphs": paragraphs,
            "columns": columns,
            "key_value_pairs": key_values,
            "contacts": extract_contact_info(text),
            "text": text
        })

    with open(os.path.join(OUTPUT_DIR, "output.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return results
