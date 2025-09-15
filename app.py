import streamlit as st
import img2pdf
import io
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(
    page_title="Pro-Max PDF Converter", 
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for a sleek, modern look with refined colors
st.markdown("""
<style>
    /* Overall page styling */
    .stApp {
        background-color: #F8F9FA; /* A very light gray */
        color: #212529; /* Dark gray for text */
    }
    /* Headers */
    h1 {
        text-align: center;
        color: #007BFF; /* A vibrant blue */
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #495057;
    }
    /* Button styling */
    .stButton>button {
        border-radius: 25px;
        border: none;
        background-color: #007BFF;
        color: white;
        box-shadow: 0 4px 10px rgba(0, 123, 255, 0.25);
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-3px);
    }
    /* Secondary buttons (Clear) */
    .stButton[data-testid="stButton-secondary"]>button {
        background-color: #E9ECEF;
        color: #495057;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    .stButton[data-testid="stButton-secondary"]>button:hover {
        background-color: #CED4DA;
    }
    /* Download button */
    .stDownloadButton>button {
        background-color: #28A745; /* A success green */
        border-color: #28A745;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.25);
    }
    .stDownloadButton>button:hover {
        background-color: #218838;
    }
    /* Information boxes */
    .st-emotion-cache-1c7er92 a {
        background-color: #E6F3FF !important;
        border-color: #B3D9FF !important;
    }
    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.8rem;
        color: #888888;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("<h1>Pro-Max PDF Converter</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555;'>Quickly convert images to a single, high-quality PDF with advanced controls.</p>", unsafe_allow_html=True)

# Main content container
main_container = st.container(border=True)

with main_container:
    uploaded_files = st.file_uploader(
        "📂 Select your images:",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    # Store uploaded files in session state to maintain their order
    if uploaded_files:
        if 'file_list' not in st.session_state or len(st.session_state.file_list) != len(uploaded_files):
            st.session_state.file_list = uploaded_files
        
        st.subheader("Reorder your pages:")
        
        # Display images with reordering buttons
        for i, file in enumerate(st.session_state.file_list):
            col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
            
            with col1:
                st.write(f"**{i+1}.**")
                
            with col2:
                # Use a BytesIO object for displaying the image
                file_bytes = io.BytesIO(file.getvalue())
                st.image(file_bytes, width=150)
                
            with col3:
                if i > 0:
                    if st.button("⬆️", key=f"up_{i}"):
                        # Move the file up
                        st.session_state.file_list[i], st.session_state.file_list[i-1] = st.session_state.file_list[i-1], st.session_state.file_list[i]
                        st.rerun()
            
            with col4:
                if i < len(st.session_state.file_list) - 1:
                    if st.button("⬇️", key=f"down_{i}"):
                        # Move the file down
                        st.session_state.file_list[i], st.session_state.file_list[i+1] = st.session_state.file_list[i+1], st.session_state.file_list[i]
                        st.rerun()
            st.markdown("---")
            
        # Display total file size
        total_size_mb = sum(len(file.getvalue()) for file in st.session_state.file_list) / (1024 * 1024)
        st.info(f"Total files: **{len(st.session_state.file_list)}** | Combined size: **{total_size_mb:.2f} MB**")

    st.markdown("---")
    
    # Custom filename input
    pdf_name = st.text_input("📝 PDF Filename:", "my_document", help="Enter a name for your PDF. The '.pdf' extension will be added automatically.")

    # PDF Metadata and Compression options
    st.subheader("PDF Options")
    col_meta, col_comp = st.columns(2)
    with col_meta:
        pdf_title = st.text_input("PDF Title:", "", help="Add a title to the PDF metadata.")
    with col_comp:
        compress_pdf = st.checkbox("Compress PDF for smaller size", value=False, help="This will reduce the file size, which might slightly reduce quality.")


    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        convert_button = st.button("✨ Convert to PDF", type="primary", use_container_width=True)
    
    with col3:
        clear_button = st.button("🗑️ Clear Files", use_container_width=True)

    if clear_button:
        if 'file_list' in st.session_state:
            del st.session_state['file_list']
        st.rerun()

    # --- 3. Conversion Logic ---
    if convert_button:
        if not uploaded_files:
            st.error("Please upload at least one image to convert.")
        else:
            with st.spinner("Processing your images... this may take a moment"):
                try:
                    # Get the uploaded file objects in the sorted order
                    sorted_image_bytes = [file.getvalue() for file in st.session_state.file_list]

                    # Step 1: Convert images to PDF
                    pdf_bytes_converted = img2pdf.convert(sorted_image_bytes)
                    final_pdf_bytes = BytesIO(pdf_bytes_converted)

                    # Step 2: Add metadata and compress if requested
                    if pdf_title or compress_pdf:
                        pdf_reader = PdfReader(final_pdf_bytes)
                        pdf_writer = PdfWriter()

                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)

                        # Add metadata (title)
                        if pdf_title:
                            pdf_writer.add_metadata({
                                "/Title": pdf_title,
                                "/Producer": "Image to PDF Converter by Gemini"
                            })

                        # Compress the PDF
                        if compress_pdf:
                            pdf_writer.compress_pages()

                        # Write the final PDF to a new buffer
                        final_pdf_bytes_processed = BytesIO()
                        pdf_writer.write(final_pdf_bytes_processed)
                        final_pdf_bytes_processed.seek(0)
                        
                        download_data = final_pdf_bytes_processed
                    else:
                        download_data = final_pdf_bytes

                    st.success("PDF created successfully! Ready for download.")
                    st.balloons()
                    
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=download_data,
                        file_name=f"{pdf_name}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Conversion failed: {e}")

# --- 4. Sidebar for Advanced Controls ---
with st.sidebar:
    st.header("⚙️ Advanced Settings")
    st.markdown("Adjust these options for custom results.")
    
    # Image quality slider
    quality = st.slider(
        "Image Quality", 
        min_value=10, max_value=100, value=75, step=5,
        help="Lower quality reduces file size. Higher quality results in a larger file."
    )
    st.info(f"Current quality: {quality}%")

    st.markdown("---")
    st.header("How to Use")
    st.info("""
            1. Upload images in the main section.
            2. **Use the ⬆️ and ⬇️ buttons to reorder pages.**
            3. Adjust settings like quality in this sidebar.
            4. Enter a custom filename.
            5. Click 'Convert to PDF'.
            6. Download your file!
            """)

# --- 5. Footer ---
st.markdown("<div class='footer'>Created with Streamlit | Powered by img2pdf & PyPDF2</div>", unsafe_allow_html=True)