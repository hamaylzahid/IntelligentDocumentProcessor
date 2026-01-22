import streamlit as st
import pandas as pd
import tempfile
import json
from processor import process_document

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Intelligent Document Processor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Custom Styling (Professional Look)
# --------------------------------------------------
st.markdown("""
<style>
    .main { background-color: #fafafa; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    .metric-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar (Project Identity & Capabilities)
# --------------------------------------------------
with st.sidebar:
    st.title("Intelligent Document Processor")
    st.caption("Automated OCR & Structured Data Extraction")
    st.divider()

    st.markdown("### Features")
    st.markdown("""
    - OCR for printed and noisy text  
    - PDF / Image processing  
    - Key information extraction (contacts, tables, forms)  
    - Structured JSON output for further processing  
    """)

# --------------------------------------------------
# Main Header
# --------------------------------------------------
st.title("Intelligent Document Image Processing System")
st.subheader("Automated OCR | Structured Extraction | Clean Output")

st.markdown(
    "Upload documents to extract **clean text**, **key information**, "
    "and **structured data** using computer vision and OCR technology."
)

st.divider()

# --------------------------------------------------
# File Upload Section
# --------------------------------------------------
st.markdown("### Upload Document")

uploaded_file = st.file_uploader(
    "Supported formats: PDF, PNG, JPG, JPEG",
    type=["pdf", "png", "jpg", "jpeg"]
)

# --------------------------------------------------
# Document Processing
# --------------------------------------------------
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    with st.spinner("Processing document..."):
        results = process_document(file_path)

    st.success("Document processed successfully")

    # --------------------------------------------------
    # Metrics Overview
    # --------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div class='metric-box'><h3>{len(results)}</h3><p>Pages Processed</p></div>",
            unsafe_allow_html=True
        )

    total_paragraphs = sum(len(p["cleaned_paragraphs"]) for p in results)
    with col2:
        st.markdown(
            f"<div class='metric-box'><h3>{total_paragraphs}</h3><p>Clean Paragraphs</p></div>",
            unsafe_allow_html=True
        )

    total_contacts = sum(len(v) for p in results for v in p["contacts"].values())
    with col3:
        st.markdown(
            f"<div class='metric-box'><h3>{total_contacts}</h3><p>Detected Contacts</p></div>",
            unsafe_allow_html=True
        )

    st.divider()

    # --------------------------------------------------
    # Page-wise Results
    # --------------------------------------------------
    for idx, page in enumerate(results):
        st.markdown(f"## Page {idx + 1}")

        with st.expander("Raw Extracted Text"):
            st.text(page["text"])

        with st.expander("Cleaned Paragraphs"):
            for para in page["cleaned_paragraphs"]:
                st.markdown(f"- {para}")

        if any(page["contacts"].values()):
            st.markdown("### Detected Contact Information")
            st.json(page["contacts"])

        st.divider()

    # --------------------------------------------------
    # Download Structured Output
    # --------------------------------------------------
    st.markdown("### Export Results")

    with open("outputs/output.json") as f:
        json_data = f.read()

    st.download_button(
        label="Download Structured JSON",
        data=json_data,
        file_name="intelligent_document_output.json",
        mime="application/json"
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption(
    "© Intelligent Document Processor | Automated OCR & Structured Extraction System"
)
