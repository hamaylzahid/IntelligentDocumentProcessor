# ============================================================
# Streamlit App for Intelligent Document Understanding System
# ============================================================

import streamlit as st
import tempfile, os, json
from document_processor import process_document  # Your backend logic
from PIL import Image
import pytesseract
import time

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Intelligent Document Processor",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Intelligent Document Understanding System")
st.markdown(
    """
Fast, CPU-friendly, keyword-driven, layout-aware document processing system.
Upload a PDF or image, provide keywords, and get structured insights!
"""
)

# -------------------------------
# OCR Fallback Actor
# -------------------------------
# -------------------------------
# OCR Fallback Actor
# -------------------------------
def ocr_actor(file, actor_type="easyocr"):
    try:
        if actor_type == "easyocr":
            from document_processor import get_ocr_reader
            reader = get_ocr_reader()  # Uses preloaded model
            st.info("Using EasyOCR...")
            result = []
            image = Image.open(file)
            processed_img = np.array(image)
            for i, text in enumerate(reader.readtext(processed_img, detail=0)):
                result.append(text)
                st.write(f"Line {i+1}: {text}")
            return "\n".join(result)

        elif actor_type == "pytesseract":
            st.info("Using pytesseract as fallback...")
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
            st.write(text)
            return text

        else:
            st.warning(f"Actor {actor_type} not supported. Using fallback.")
            return ocr_actor(file, actor_type="pytesseract")

    except Exception as e:
        st.error(f"Actor {actor_type} crashed: {e}")
        if actor_type != "pytesseract":
            return ocr_actor(file, actor_type="pytesseract")
        else:
            return "All OCR actors failed!"


# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload your PDF/Image document",
    type=["pdf", "png", "jpg", "jpeg"]
)

keywords_text = st.text_input(
    "Enter keywords (comma-separated)",
    placeholder="e.g., AI, Machine Learning, Resume"
)

process_button = st.button("Process Document")

# -------------------------------
# Processing
# -------------------------------
if process_button:
    if uploaded_file is None:
        st.error("Please upload a PDF or image first!")
    else:
        if not keywords_text.strip():
            st.warning("Consider adding keywords for a better summary.")

        try:
            # Save uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            # For images, run streaming OCR before full backend processing
            if uploaded_file.type.startswith("image/"):
                st.subheader("🔍 OCR Preview (Streaming)")
                with open(temp_path, "rb") as f:
                    ocr_text = ocr_actor(f)
                st.text_area("Detected Text", ocr_text, height=250)

            # Process document using backend
            with st.spinner("Processing document... This may take a few seconds."):
                result = process_document(temp_path, keywords_text)

            os.remove(temp_path)

            # Display results
            if "error" in result:
                st.error(f"❌ Error during processing: {result['error']}")
            else:
                st.success("✅ Document processed successfully!")

                st.subheader("📌 Abstract / Summary")
                st.json(result.get("abstract", {}), expanded=True)

                if result.get("tables"):
                    st.subheader("📊 Extracted Tables")
                    for i, table in enumerate(result["tables"], start=1):
                        st.write(f"Table {i}")
                        st.json(table, expanded=False)

                st.subheader("📝 Page-wise Content")
                for page in result.get("pages", []):
                    st.markdown(f"### Page {page['page']}")
                    st.markdown("**Headings:**")
                    st.write(page.get("headings", []))
                    st.markdown("**Paragraphs:**")
                    st.write(page.get("paragraphs", []))
                    st.markdown("**Key-Value Pairs:**")
                    st.write(page.get("key_values", {}))
                    st.markdown("**Contacts:**")
                    st.write(page.get("contacts", {}))

                st.subheader("💾 Download Output")
                json_data = json.dumps(result, indent=4)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="document_output.json",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")

