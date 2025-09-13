import streamlit as st
import os
import base64
from process_pdf import extract_structured_data, parse_text_into_sections
from agent import format_context_for_llm, answer_query
import fitz  # PyMuPDF

# Sidebar with project information
st.sidebar.title("ℹ️ Project Info")
st.sidebar.info("""
**PDF Q&A & Analysis Assistant**

- Upload any PDF document.
- Extract structured text sections & tables.
- Extract and display embedded images.
- Ask smart questions (e.g., What language is this?).
- Translate document content (Marathi → Hindi or others).
""")
# Helper function to extract images from PDF
def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = []
    pdf_doc = fitz.open(pdf_path)

    for page_index in range(len(pdf_doc)):
        page = pdf_doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = os.path.join(output_folder, f"page{page_index+1}_img{img_index+1}.{image_ext}")

            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

            image_files.append(image_filename)

    return image_files


# Helper function to convert image to Base64
def convert_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    return b64_string


# Streamlit App Interface
st.set_page_config(page_title="📄 PDF Q&A & Analysis Assistant", layout="wide")
st.title("📚 PDF Q&A & Analysis Assistant")
st.write("Upload a PDF file, explore its sections, tables, images, and ask questions including language identification, translation, or content insights.")

uploaded_file = st.file_uploader("📂 Upload your PDF file", type=["pdf"])

if uploaded_file:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # Extract sections and tables
    sections, tables = extract_structured_data("uploaded.pdf")

    # Display Sections
    st.subheader("🗂 Extracted Sections:")
    if sections:
        for header, content in sections.items():
            with st.expander(header):
                st.write(content)
    else:
        st.write("No sections detected.")

    # Display Tables
    st.subheader("📊 Extracted Tables:")
    if tables:
        for i, table in enumerate(tables):
            st.write(f"Table {i+1}")
            st.table(table)
    else:
        st.write("No tables detected.")

    # Display Images in Grid with Hover Effect
    st.subheader("🖼 Extracted Images:")
    image_files = extract_images_from_pdf("uploaded.pdf")
    if image_files:
        images_html = """
        <style>
        .image-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .image-grid img {
            width: 250px;
            height: auto;
            transition: transform 0.3s ease;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .image-grid img:hover {
            transform: scale(2);
            z-index: 10;
            position: relative;
        }
        </style>
        <div class="image-grid">
        """

        for img_path in image_files:
            images_html += f'<img src="data:image/jpeg;base64,{convert_image_to_base64(img_path)}" />'

        images_html += "</div>"

        st.markdown(images_html, unsafe_allow_html=True)
    else:
        st.write("No images found in the document.")

    # Prepare context for LLM
    full_context = format_context_for_llm(sections, tables)

    # Q&A Section
    st.subheader("💬 Ask a Question:")
    user_query = st.text_input("Enter your question about the document (e.g., What language is this? Translate to Hindi, What type of document is this?)")

    if st.button("🤖 Get Answer"):
        if user_query.strip():
            with st.spinner("Generating answer..."):
                llm_answer = answer_query(user_query, full_context)
            st.subheader("🔔 Answer:")
            st.write(llm_answer)
        else:
            st.warning("Please enter a question to get started.")


