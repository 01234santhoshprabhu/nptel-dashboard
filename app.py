import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(
    page_title="Enterprise Data Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- LIGHT ENTERPRISE UI ----------------
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
    padding: 16px;
    border-radius: 12px;
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

# ---------------- SIDEBAR NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["📊 AI Data Validation", "📱 Mobile SMS Cleaner"]
)

# ==========================================================
# ================= AI DATA VALIDATION =====================
# ==========================================================

if page == "📊 AI Data Validation":

    st.title("🧠 AI Data Validation & Filtering System")

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        # Load file
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()

        st.success("File Uploaded Successfully")

        # KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", len(df))
        col2.metric("Total Columns", len(df.columns))
        col3.metric("Missing Values", df.isnull().sum().sum())
        col4.metric("Duplicate Rows", df.duplicated().sum())

        st.divider()

        # AI SUMMARY
        st.subheader("🤖 AI Generated Summary")

        total_rows = len(df)
        total_cols = len(df.columns)
        missing_total = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()

        summary = f"""
        Dataset contains {total_rows:,} rows and {total_cols} columns.
        Missing values detected: {missing_total:,}.
        Duplicate rows detected: {duplicate_rows:,}.
        """

        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_cols:
            col = numeric_cols[0]
            mean = df[col].mean()
            summary += f"\nColumn '{col}' average value is {mean:.2f}."

        st.success(summary)

        st.divider()

        # GLOBAL SEARCH
        st.subheader("🔎 Global Search")

        search_text = st.text_input("Search Across Dataset")

        filtered_df = df.copy()

        if search_text:
            filtered_df = filtered_df[
                filtered_df.astype(str)
                .apply(lambda row: row.str.contains(search_text, case=False).any(), axis=1)
            ]

        # DYNAMIC FILTER
        st.subheader("🎛 Column Filters")

        for col in df.columns:

            if df[col].dtype == "object":

                unique_vals = df[col].dropna().unique()

                if len(unique_vals) < 50:
                    selected = st.multiselect(
                        f"Filter {col}",
                        unique_vals,
                        default=unique_vals
                    )
                    filtered_df = filtered_df[filtered_df[col].isin(selected)]

            elif np.issubdtype(df[col].dtype, np.number):

                min_val = float(df[col].min())
                max_val = float(df[col].max())

                selected_range = st.slider(
                    f"Range for {col}",
                    min_val,
                    max_val,
                    (min_val, max_val)
                )

                filtered_df = filtered_df[
                    (filtered_df[col] >= selected_range[0]) &
                    (filtered_df[col] <= selected_range[1])
                ]

        st.subheader("📋 Filtered Data")
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            "⬇ Download Filtered CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

    else:
        st.info("Upload Excel or CSV to begin.")

# ==========================================================
# ================= MOBILE SMS CLEANER =====================
# ==========================================================

elif page == "📱 Mobile SMS Cleaner":

    st.title("📱 Enterprise Bulk SMS Number Cleaner")

    def process_numbers(raw_numbers):

        valid_numbers = []
        invalid_count = 0

        for num in raw_numbers:

            digits = re.sub(r"\D", "", str(num))

            # Remove country code if exists
            if digits.startswith("91") and len(digits) > 10:
                digits = digits[-10:]

            # Strict Indian mobile validation
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

        text = st.text_area("Paste Mobile Numbers", height=200)

        if text:
            all_numbers = re.split(r"[,\s\n]+", text.strip())

    if all_numbers:

        result_df, total_uploaded, total_valid, invalid_count, duplicate_removed = process_numbers(all_numbers)

        st.divider()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Numbers Uploaded", total_uploaded)
        k2.metric("Valid Unique Numbers", total_valid)
        k3.metric("Invalid Numbers Removed", invalid_count)
        k4.metric("Duplicates Removed", duplicate_removed)

        st.divider()

        st.subheader("📋 Cleaned SMS Ready Numbers")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            "⬇ Download SMS Ready CSV",
            result_df.to_csv(index=False).encode("utf-8"),
            file_name="sms_ready_numbers.csv",
            mime="text/csv"
        )

    else:
        st.info("Upload file or paste numbers to begin.")
