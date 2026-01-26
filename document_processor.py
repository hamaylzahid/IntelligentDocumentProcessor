import os, re, json, warnings
import cv2
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
import easyocr
import camelot

warnings.filterwarnings("ignore")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\PMYLS\Downloads\tesseract-ocr-w64-setup-5.5.0.20241111.exe"

# -------------------------------
# Preload EasyOCR reader (once)
# -------------------------------
OCR_LANGUAGES = ["en"]
ocr_reader = None
def get_ocr_reader():
    global ocr_reader
    if ocr_reader is None:
        # Preload models without downloading during user processing
        ocr_reader = easyocr.Reader(OCR_LANGUAGES, gpu=False, download_enabled=False)
    return ocr_reader

# -------------------------------
# File Loading
# -------------------------------
def load_images(file):
    images = []
    if file.lower().endswith(".pdf"):
        pages = convert_from_path(file, dpi=200)
        for page in pages:
            images.append(cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR))
    elif file.lower().endswith((".png", ".jpg", ".jpeg")):
        images.append(cv2.imread(file))
    else:
        raise ValueError("Unsupported file type")
    return images, file

# -------------------------------
# Preprocessing
# -------------------------------
def preprocess_for_tesseract(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

def preprocess_for_easyocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    return cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )

# -------------------------------
# OCR Extraction
# -------------------------------
def extract_text(img):
    # Try Tesseract first
    try:
        text = pytesseract.image_to_string(preprocess_for_tesseract(img), config="--oem 1 --psm 6")
    except:
        text = ""

    # Fallback to EasyOCR if Tesseract fails or too short
    if len(text.strip()) < 40:
        reader = get_ocr_reader()
        processed_img = preprocess_for_easyocr(img)
        text = "\n".join(reader.readtext(processed_img, detail=0))
    return normalize_text(text)

def normalize_text(text):
    return re.sub(r"\s+", " ", text).strip()

# -------------------------------
# Structuring & Extraction
# -------------------------------
def split_paragraphs(text, max_len=250):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paragraphs, buffer = [], ""
    for s in sentences:
        buffer += s + " "
        if len(buffer) >= max_len:
            paragraphs.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        paragraphs.append(buffer.strip())
    return paragraphs

def detect_headings(text):
    lines = text.split(". ")
    return [l.strip() for l in lines if 5 < len(l) < 80 and l[0].isupper() and not l.endswith(".")]

def extract_key_values(text):
    kv = {}
    for line in text.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            kv[k.strip()] = v.strip()
    return kv

def extract_contacts(text):
    return {
        "emails": re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text),
        "phones": re.findall(r'\b\d{7,15}\b', text),
        "urls": re.findall(r'https?://\S+', text)
    }

def extract_tables(pdf_path, text):
    if not pdf_path.lower().endswith(".pdf") or not any(k in text.lower() for k in ["table", "total", "amount", "price"]):
        return []
    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
    result = []
    for i, table in enumerate(tables):
        result.append(table.df.to_dict(orient="records"))
    return result

def build_abstract(text, keywords):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    matched = [s for s in sentences if any(k.lower() in s.lower() for k in keywords)]
    summary = " ".join(matched[:4]) if matched else "The document content is limited. Provided keywords indicate the primary subject matter."
    return {
        "keywords": keywords,
        "summary": summary,
        "evidence_sentences": matched[:6]
    }

# -------------------------------
# Main Processing Pipeline
# -------------------------------
def process_document(file, keywords_text):
    try:
        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
        images, path = load_images(file)
        pages_data = []
        full_text = ""
        for i, img in enumerate(images, start=1):
            text = extract_text(img)
            full_text += text + " "
            pages_data.append({
                "page": i,
                "headings": detect_headings(text),
                "paragraphs": split_paragraphs(text),
                "key_values": extract_key_values(text),
                "contacts": extract_contacts(text),
                "raw_text": text
            })

        abstract = build_abstract(full_text, keywords)
        tables = extract_tables(path, full_text)

        result = {
            "abstract": abstract,
            "tables": tables,
            "pages": pages_data
        }

        with open(f"{OUTPUT_DIR}/output.json", "w") as f:
            json.dump(result, f, indent=4)

        return result

    except Exception as e:
        return {"error": str(e)}


