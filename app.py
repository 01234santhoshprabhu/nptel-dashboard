import streamlit as st
import pandas as pd
import plotly.express as px
import re
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Santhosh | NPTEL Analytics", layout="wide")

# ---------------- BACKGROUND STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/en/0/00/NPTEL_logo.png");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 350px;
    background-attachment: fixed;
}
.block-container {
    background-color: rgba(255,255,255,0.95);
    padding: 2rem;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- PAGE NAVIGATION ----------------
page = st.sidebar.radio(
    "Select Page",
    ["📊 Dashboard", "📧 Email Cleaner", "📱 Mobile Intelligence"]
)

# ==========================================================
# ===================== MOBILE TOOL ========================
# ==========================================================

if page == "📱 Mobile Intelligence":

    st.title("📱 Mobile Intelligence Tool")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:

        df = pd.read_csv(uploaded_file, dtype=str)
        df.columns = df.columns.str.strip()

        mobile_col = st.selectbox("Select Mobile Column", df.columns)

        def process_mobile(number):
            if pd.isna(number):
                return None, "Null"

            number = re.sub(r"\D", "", str(number))

            if len(number) < 10:
                return None, "Less than 10 digits"

            number = number[-10:]

            if len(number) != 10:
                return None, "Invalid Length"

            if number[0] not in ["6", "7", "8", "9"]:
                return None, "Invalid Start Digit"

            return number, "Valid"

        processed = df[mobile_col].apply(process_mobile)

        df["Filtered_Mobile"] = processed.apply(lambda x: x[0])
        df["Status"] = processed.apply(lambda x: x[1])

        valid_df = df[df["Status"] == "Valid"].copy()

        freq = valid_df["Filtered_Mobile"].value_counts().reset_index()
        freq.columns = ["Filtered_Mobile", "Frequency"]

        valid_df = valid_df.merge(freq, on="Filtered_Mobile", how="left")

        unique_df = valid_df.drop_duplicates(subset=["Filtered_Mobile"])
        unique_df["Mobile_With_91"] = "91" + unique_df["Filtered_Mobile"]

        duplicate_df = valid_df[valid_df["Frequency"] > 1]
        invalid_df = df[df["Status"] != "Valid"]

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", len(df))
        c2.metric("Valid Mobiles", len(valid_df))
        c3.metric("Unique Mobiles", len(unique_df))
        c4.metric("Duplicate Entries", len(duplicate_df))

        st.divider()

        st.subheader("✅ Unique Valid Numbers")
        st.dataframe(unique_df[[mobile_col, "Filtered_Mobile", "Mobile_With_91"]], use_container_width=True)

        st.subheader("🔁 Duplicate Numbers")
        st.dataframe(duplicate_df[[mobile_col, "Filtered_Mobile", "Frequency"]], use_container_width=True)

        st.subheader("❌ Invalid Numbers")
        st.dataframe(invalid_df[[mobile_col, "Status"]], use_container_width=True)

        # Download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            unique_df.to_excel(writer, sheet_name="Unique", index=False)
            duplicate_df.to_excel(writer, sheet_name="Duplicates", index=False)
            invalid_df.to_excel(writer, sheet_name="Invalid", index=False)

        st.download_button(
            "⬇ Download Mobile Report",
            output.getvalue(),
            "Mobile_Report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("⬆ Upload CSV to analyze mobile numbers")

# ==========================================================
# Keep your existing Dashboard and Email Cleaner code below
# (NO CHANGE to your existing logic)
# ==========================================================
