import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re

st.set_page_config(
    page_title="Santhosh | Data Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- ENTERPRISE LIGHT UI ----------------
st.markdown("""
<style>

/* Light background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}

/* Main container */
.block-container {
    background: white;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

/* KPI Cards */
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

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#3b82f6);
    border-radius: 10px;
    color: white;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📧 Email Cleaner", "📱 Mobile Number Cleaner"]
)

# ==========================================================
# ===================== DASHBOARD ==========================
# ==========================================================

if page == "📊 Dashboard":

    st.title("📊 Santhosh Analytics Dashboard")

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

        st.sidebar.header("Filters")

        all_courses = sorted(df_original[course_col].dropna().unique())

        selected_courses = st.sidebar.multiselect(
            "Select Course ID",
            options=all_courses,
            default=all_courses
        )

        if selected_courses:
            df_filtered = df_filtered[df_filtered[course_col].isin(selected_courses)]

        def performance(score):
            if pd.isna(score):
                return "Low"
            elif score < 10:
                return "Low"
            elif score < 18:
                return "Medium"
            else:
                return "High"

        df_filtered["Performance"] = df_filtered["out_of_25"].apply(performance)

        st.subheader("📊 Performance Distribution")

        perf_df = df_filtered["Performance"].value_counts().reset_index()
        perf_df.columns = ["Category", "Count"]

        fig_perf = px.bar(
            perf_df,
            x="Count",
            y="Category",
            orientation="h",
            color="Category",
            text_auto=True
        )

        st.plotly_chart(fig_perf, use_container_width=True)

        st.divider()

        st.subheader("📋 Filtered Data")
        st.dataframe(df_filtered, use_container_width=True)

        st.download_button(
            "⬇ Download Filtered CSV",
            df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

    else:
        st.info("Upload CSV file to start.")

# ==========================================================
# ===================== EMAIL CLEANER ======================
# ==========================================================

elif page == "📧 Email Cleaner":

    st.title("📧 Email Cleaning Tool")

    input_method = st.radio(
        "Choose Input Method",
        ["📂 Upload CSV", "📋 Copy & Paste Emails"]
    )

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    if input_method == "📂 Upload CSV":

        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

        if uploaded_file:

            df = pd.read_csv(uploaded_file, dtype=str)
            email_col = st.selectbox("Select Email Column", df.columns)

            original_series = df[email_col].fillna("").astype(str)

            extracted = []
            for value in original_series:
                extracted.extend(re.findall(email_pattern, value))

            df_clean = pd.DataFrame({"Cleaned Email": extracted})
            df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
            df_clean = df_clean.drop_duplicates()

            c1, c2 = st.columns(2)
            c1.metric("Original Rows", len(original_series))
            c2.metric("Unique Clean Emails", len(df_clean))

            st.dataframe(df_clean, use_container_width=True)

            st.download_button(
                "⬇ Download Cleaned Emails",
                df_clean.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_emails.csv",
                mime="text/csv"
            )

    else:

        pasted_text = st.text_area("Paste Emails", height=200)

        if pasted_text:
            extracted = re.findall(email_pattern, pasted_text)

            df_clean = pd.DataFrame({"Cleaned Email": extracted})
            df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
            df_clean = df_clean.drop_duplicates()

            c1, c2 = st.columns(2)
            c1.metric("Total Extracted Emails", len(extracted))
            c2.metric("Unique Clean Emails", len(df_clean))

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

    st.title("📱 Enterprise Mobile Number Cleaner")

    def process_numbers(raw_numbers):

        valid_numbers = []
        invalid_count = 0

        for num in raw_numbers:

            digits = re.sub(r"\D", "", str(num))

            if digits.startswith("91") and len(digits) > 10:
                digits = digits[-10:]

            if len(digits) == 10 and digits[0] in ["6", "7", "8", "9"]:
                valid_numbers.append(digits)
            else:
                invalid_count += 1

        unique_numbers = list(dict.fromkeys(valid_numbers))
        duplicate_removed = len(valid_numbers) - len(unique_numbers)

        numbers_with_91 = ["91" + num for num in unique_numbers]

        df_result = pd.DataFrame({
            "Filtered (10 Digit Valid)": unique_numbers,
            "With 91": numbers_with_91
        })

        return df_result, len(raw_numbers), len(unique_numbers), invalid_count, duplicate_removed

    method = st.radio(
        "Choose Input Method",
        ["📂 Upload CSV/Excel", "📋 Copy & Paste Numbers"]
    )

    all_numbers = []

    if method == "📂 Upload CSV/Excel":

        uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])

        if uploaded_file:

            if uploaded_file.name.endswith("csv"):
                df = pd.read_csv(uploaded_file, dtype=str)
            else:
                df = pd.read_excel(uploaded_file, dtype=str)

            column = st.selectbox("Select Mobile Number Column", df.columns)

            if column:
                all_numbers = df[column].dropna().astype(str).tolist()

    else:

        text = st.text_area("Paste Numbers", height=200)

        if text:
            all_numbers = re.split(r"[,\s\n]+", text.strip())

    if all_numbers:

        result_df, total_uploaded, total_valid, invalid_count, duplicate_removed = process_numbers(all_numbers)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Numbers Uploaded", total_uploaded)
        k2.metric("Valid Unique Numbers", total_valid)
        k3.metric("Invalid Numbers Removed", invalid_count)
        k4.metric("Duplicates Removed", duplicate_removed)

        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            "⬇ Download SMS Ready CSV",
            result_df.to_csv(index=False).encode("utf-8"),
            file_name="sms_ready_numbers.csv",
            mime="text/csv"
        )

    else:
        st.info("Upload or paste numbers to begin.")
