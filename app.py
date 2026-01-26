# ============================================================
# Streamlit App for Intelligent Document Understanding System
# ============================================================

import streamlit as st
import tempfile, os, json
from document_processor import process_document  # Your backend logic

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
                temp_path = tmp.name  # This is the path we'll pass to backend

            # Process document
            with st.spinner("Processing document... This may take a few seconds."):
                result = process_document(temp_path, keywords_text)

            # Remove temp file to save space
            os.remove(temp_path)

            # Display results
            if "error" in result:
                st.error(f"❌ Error during processing: {result['error']}")
            else:
                st.success("✅ Document processed successfully!")

                # Abstract / Summary
                st.subheader("📌 Abstract / Summary")
                st.json(result.get("abstract", {}), expanded=True)

                # Tables (if any)
                if result.get("tables"):
                    st.subheader("📊 Extracted Tables")
                    for i, table in enumerate(result["tables"], start=1):
                        st.write(f"Table {i}")
                        st.json(table, expanded=False)

                # Page-wise details
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

                # Download structured JSON
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
