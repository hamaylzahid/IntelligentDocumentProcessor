import streamlit as st
import json
import tempfile
from document_processor import process_document  # adjust filename if needed

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Intelligent Document Understanding",
    page_icon=None,
    layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("📄 Intelligent Document Understanding System")
st.markdown(
    """
    Fast, CPU-friendly, keyword-driven document intelligence system  
    **Supports PDFs and Images | OCR + Tables + Structured Output**
    """
)

st.divider()

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    keywords_text = st.text_input(
        "Keywords (comma-separated)",
        placeholder="invoice, total, amount, date"
    )
    st.markdown(
        """
        **Tips**
        - Use meaningful keywords  
        - PDF works best for tables  
        - Images should be clear
        """
    )

# --------------------------------------------------
# File Upload
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload a document (PDF / PNG / JPG)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# --------------------------------------------------
# Process Button
# --------------------------------------------------
if uploaded_file and st.button("🚀 Process Document", use_container_width=True):

    with st.spinner("Analyzing document..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp.name = uploaded_file.name
            temp_file = tmp

        result = process_document(temp_file, keywords_text)

    st.success("✅ Document processed successfully!")

    # --------------------------------------------------
    # Error Handling
    # --------------------------------------------------
    if "error" in result:
        st.error(result["error"])

    else:
        # --------------------------------------------------
        # Abstract Section
        # --------------------------------------------------
        st.subheader("🧠 Document Abstract")
        st.json(result["abstract"])

        # --------------------------------------------------
        # Tables Section
        # --------------------------------------------------
        st.subheader("📊 Extracted Tables")

        if result["tables"]:
            for i, table in enumerate(result["tables"], 1):
                st.markdown(f"**Table {i}**")
                st.dataframe(table, use_container_width=True)
        else:
            st.info("No tables detected.")

        # --------------------------------------------------
        # Pages Section
        # --------------------------------------------------
        st.subheader("📄 Page-wise Analysis")

        for page in result["pages"]:
            with st.expander(f"Page {page['page']}"):
                st.markdown("**Headings**")
                st.write(page["headings"] or "—")

                st.markdown("**Key-Value Pairs**")
                st.json(page["key_values"] or {})

                st.markdown("**Contacts**")
                st.json(page["contacts"])

                st.markdown("**Paragraphs**")
                for p in page["paragraphs"]:
                    st.write("•", p)

        # --------------------------------------------------
        # Download Output
        # --------------------------------------------------
        st.divider()
        st.download_button(
            label="⬇️ Download Full JSON Output",
            data=json.dumps(result, indent=4),
            file_name="document_output.json",
            mime="application/json"
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("Built with Streamlit • OCR • NLP • Document Intelligence")
