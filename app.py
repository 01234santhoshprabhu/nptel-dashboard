import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re

# PDF Watermark Imports
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Santhosh | Data Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# ENTERPRISE LIGHT UI
# -------------------------------------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}
.block-container {
    background: white;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
[data-testid="metric-container"] {
    background: #ffffff;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    transition: 0.3s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#3b82f6);
    border-radius: 10px;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📧 Email Cleaner",
        "📱 Mobile Number Cleaner",
        "📄 PDF Watermark Tool"
    ]
)

# ==========================================================
# ===================== DASHBOARD ==========================
# ==========================================================
if page == "📊 Dashboard":

    st.title("📊 Assignment Dump Filtering Dashboard")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:

        df = pd.read_csv(uploaded_file, encoding="latin1", low_memory=False)
        df.columns = df.columns.str.strip()
        df_original = df.copy()

        email_col = [c for c in df.columns if "email" in c.lower()][0]
        course_col = [c for c in df.columns if "course" in c.lower()][0]

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Candidates", df_original[email_col].nunique())
        k2.metric("Unique Courses", df_original[course_col].nunique())
        k3.metric("Total Records", len(df_original))
        k4.metric("Average Score", round(df_original["out_of_25"].mean(), 2))

        st.divider()

        df_filtered = df_original.copy()

        search = st.text_input("🔍 Global Search")
        if search:
            df_filtered = df_filtered[
                df_filtered.apply(
                    lambda r: r.astype(str).str.contains(search, case=False).any(),
                    axis=1
                )
            ]

        st.subheader("📋 Filtered Data")
        st.dataframe(df_filtered, use_container_width=True)

# ==========================================================
# ===================== EMAIL CLEANER ======================
# ==========================================================
elif page == "📧 Email Cleaner":

    st.title("📧 Email Cleaner")

    pasted_text = st.text_area("Paste Emails", height=200)

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    if pasted_text:
        extracted = re.findall(email_pattern, pasted_text)

        df_clean = pd.DataFrame({"Cleaned Email": extracted})
        df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
        df_clean = df_clean.drop_duplicates()

        st.dataframe(df_clean, use_container_width=True)

        st.download_button(
            "⬇ Download Cleaned Emails",
            df_clean.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_emails.csv",
            mime="text/csv"
        )

# ==========================================================
# ================= MOBILE NUMBER CLEANER ==================
# ==========================================================
elif page == "📱 Mobile Number Cleaner":

    st.title("📱 Mobile Number Cleaner")

    text = st.text_area("Paste Numbers", height=200)

    if text:
        numbers = re.split(r"[,\s\n]+", text.strip())

        valid_numbers = []
        for num in numbers:
            digits = re.sub(r"\D", "", str(num))
            if digits.startswith("91") and len(digits) > 10:
                digits = digits[-10:]
            if len(digits) == 10 and digits[0] in ["6", "7", "8", "9"]:
                valid_numbers.append(digits)

        unique_numbers = list(dict.fromkeys(valid_numbers))
        numbers_with_91 = ["91" + num for num in unique_numbers]

        df_result = pd.DataFrame({
            "10 Digit": unique_numbers,
            "With 91": numbers_with_91
        })

        st.dataframe(df_result, use_container_width=True)

        st.download_button(
            "⬇ Download SMS Ready CSV",
            df_result.to_csv(index=False).encode("utf-8"),
            file_name="sms_ready_numbers.csv",
            mime="text/csv"
        )

# ==========================================================
# ================= PDF WATERMARK TOOL =====================
# ==========================================================
elif page == "📄 PDF Watermark Tool":

    st.title("📄 PDF Image Watermark Tool")
    st.markdown("Upload a PDF and apply your logo watermark to all pages.")

    pdf_file = st.file_uploader("Upload PDF File", type=["pdf"])
    logo_file = st.file_uploader("Upload Logo Image (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if pdf_file and logo_file:

        st.subheader("⚙ Watermark Settings")

        size_percent = st.slider("Watermark Size (% of page width)", 10, 80, 40)
        opacity = st.slider("Transparency", 0.05, 1.0, 0.2)
        rotation = st.slider("Rotation (Degrees)", -180, 180, 0)

        position = st.selectbox(
            "Position",
            ["Center", "Top Center", "Bottom Center"]
        )

        def add_watermark(input_pdf, watermark_image):

            reader = PdfReader(input_pdf)
            writer = PdfWriter()

            for page in reader.pages:

                packet = BytesIO()
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)

                c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                img = ImageReader(watermark_image)

                watermark_width = page_width * (size_percent / 100)
                watermark_height = watermark_width

                if position == "Center":
                    x = (page_width - watermark_width) / 2
                    y = (page_height - watermark_height) / 2
                elif position == "Top Center":
                    x = (page_width - watermark_width) / 2
                    y = page_height - watermark_height - 50
                else:
                    x = (page_width - watermark_width) / 2
                    y = 50

                c.saveState()
                c.translate(page_width / 2, page_height / 2)
                c.rotate(rotation)
                c.translate(-page_width / 2, -page_height / 2)
                c.setFillAlpha(opacity)

                c.drawImage(
                    img,
                    x,
                    y,
                    width=watermark_width,
                    height=watermark_height,
                    mask='auto'
                )

                c.restoreState()
                c.save()

                packet.seek(0)
                watermark_pdf = PdfReader(packet)
                page.merge_page(watermark_pdf.pages[0])
                writer.add_page(page)

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            return output

        if st.button("🚀 Apply Watermark"):

            with st.spinner("Applying watermark..."):
                output_pdf = add_watermark(pdf_file, logo_file)

            st.success("Watermark Applied Successfully!")

            st.download_button(
                "⬇ Download Watermarked PDF",
                output_pdf,
                file_name="watermarked_output.pdf",
                mime="application/pdf"
            )

    else:
        st.info("Upload both PDF and Logo Image to continue.")
