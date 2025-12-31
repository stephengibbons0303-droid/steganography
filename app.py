import streamlit as st
from PIL import Image
import utils
import io

# --- Page Config ---
st.set_page_config(
    page_title="Steganography Pro",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global App Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(33, 33, 68) 0%, rgb(20, 20, 30) 90%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hiding Standard Header */
    header {visibility: hidden;}
    
    /* Typography Overrides */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        padding-bottom: 20px;
    }
    
    h2, h3, h4, label, .stMarkdown p {
        color: #f0f2f6 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Subheader sizing */
    h2 {
        font-size: 1.2rem !important;
        margin-bottom: 0.5rem !important;
        white-space: nowrap !important;
    }
    
    /* Fix Sidebar Background to match Theme */
    [data-testid="stSidebar"] {
        background-color: rgba(20, 20, 30, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Enhance Text Visibility in Sidebar */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
        font-weight: 500;
    }
    
    /* Glassmorphic Containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px;
        backdrop-filter: blur(10px);
    }
    
    /* File Uploader Cards */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        border: 1px dashed rgba(255, 255, 255, 0.2);
    }
    
    .stFileUploader:hover {
        border-color: #FF416C;
        background-color: rgba(255, 255, 255, 0.08);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
        color: white;
        border: none;
        padding: 0.6rem 2.0rem; /* Larger padding */
        border-radius: 50px;
        font-weight: 700;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(142, 84, 233, 0.5);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; /* Increased gap */
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px; /* Taller tabs */
        padding: 0 24px; /* Wider tabs */
        background-color: rgba(255,255,255,0.03);
        border-radius: 12px;
        color: #aaaaaa;
        font-weight: 600;
        border: 1px solid transparent;
        transition:all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.08);
        color: #ffffff;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.1);
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2);
        border-bottom: 3px solid #FF416C; /* Stronger accent */
    }
    
    /* Info Box Correction */
    .stAlert {
        background-color: rgba(71, 118, 230, 0.1);
        border: 1px solid rgba(71, 118, 230, 0.2);
        color: #e0e0e0;
    }
    
</style>
""", unsafe_allow_html=True)

# --- App Layout ---

st.title("Steganography Exp")
st.markdown("### 🕵️ Hide & Reveal Messages in Images")

with st.sidebar:
    st.header("Settings")
    n_bits = st.slider("Bits to Hide (Quality vs Capacity)", 1, 7, 2, 
                       help="More bits = better hidden image quality, simpler to detect. Fewer bits = noisier hidden image, harder to detect.")
    st.info(f"Using **{n_bits} bits** for the hidden image.\n\nCover image keeps **{8-n_bits} bits**.")

tab1, tab2 = st.tabs(["🔒 Hide Image", "🔓 Reveal Image"])

# --- HIDE IMAGE TAB ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Cover Image (Foreground)")
        cover_file = st.file_uploader("Upload the image that will be seen", type=['png', 'jpg', 'jpeg'], key="cover_up")
        if cover_file:
            cover_img = utils.load_image(cover_file)
            st.image(cover_img, use_column_width=True)
            
    with col2:
        st.subheader("2. Secret Image (Background)")
        hidden_file = st.file_uploader("Upload the image to hide", type=['png', 'jpg', 'jpeg'], key="hidden_up")
        if hidden_file:
            hidden_img = utils.load_image(hidden_file)
            st.image(hidden_img, use_column_width=True)

    if cover_file and hidden_file:
        st.markdown("---")
        
        # Use session state to persist the result across reruns (for download button)
        if 'steganography_result' not in st.session_state:
            st.session_state.steganography_result = None
            
        if st.button("✨ Hide Image", type="primary"):
            try:
                with st.spinner("Processing magic..."):
                    # Process
                    result_img = utils.encode_image(cover_img, hidden_img, n_bits)
                    st.session_state.steganography_result = result_img
                    st.success("Image hidden successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
        # Display from session state if available
        if st.session_state.steganography_result:
            result_img = st.session_state.steganography_result
            
            # Display Result
            st.subheader("Resulting Steganographic Image")
            st.image(result_img, caption="Encoded Image", use_column_width=True)
            
            # Buffer for download
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="⬇️ Download Encoded Image",
                data=byte_im,
                file_name="steganography_result.png",
                mime="image/png"
            )

# --- REVEAL IMAGE TAB ---
with tab2:
    st.subheader("Upload an encoded image")
    st.info(f"💡 **Tip:** Ensure the 'Bits to Hide' slider (currently **{n_bits}**) matches the value used when this image was created!")
    
    decode_file = st.file_uploader("Upload image to decode", type=['png', 'jpg', 'jpeg'], key="decode_up")
    
    if decode_file:
        st.image(decode_file, caption="Encoded Image", width=300)
        
        if st.button("🔍 Reveal Hidden Image", type="primary"):
            try:
                with st.spinner("Decoding..."):
                    encoded_img = utils.load_image(decode_file)
                    decoded_img = utils.decode_image(encoded_img, n_bits)
                    
                    st.success("Hidden image extracted!")
                    st.image(decoded_img, caption="Revealed Secret", use_column_width=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")

