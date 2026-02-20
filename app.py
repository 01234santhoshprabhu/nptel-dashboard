import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Santhosh | NPTEL Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- MODERN LIGHT UI + NPTEL WATERMARK ----------------
st.markdown("""
<style>

/* Force light background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}

/* NPTEL Watermark */
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/en/0/00/NPTEL_logo.png");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 420px;
    background-attachment: fixed;
}

/* Main Container Card */
.block-container {
    background: rgba(255,255,255,0.96);
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#ffffff,#f1f5f9);
}

/* KPI Cards */
[data-testid="metric-container"] {
    background: #ffffff;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    transition: 0.3s ease;
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
    border: none;
}
.stButton>button:hover {
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ---------------- PAGE NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📧 Email Cleaner"]
)

# ==========================================================
# ===================== DASHBOARD ==========================
# ==========================================================

if page == "📊 Dashboard":

    st.title("📊 NPTEL Analytics Dashboard")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:

        df = pd.read_csv(uploaded_file, encoding="latin1", low_memory=False)
        df.columns = df.columns.str.strip()

        # Detect important columns
        email_col = [c for c in df.columns if "email" in c.lower()][0]
        course_col = [c for c in df.columns if "course" in c.lower()][0]

        if "out_of_25" not in df.columns:
            st.error("Column 'out_of_25' not found.")
            st.stop()

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        # KPI Section
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Candidates", df[email_col].nunique())
        k2.metric("Unique Courses", df[course_col].nunique())
        k3.metric("Total Records", len(df))
        k4.metric("Average Score", round(df["out_of_25"].mean(), 2))

        st.divider()

        # Sidebar Filters
        st.sidebar.header("Filters")
        all_courses = sorted(df[course_col].dropna().unique())

        selected_courses = st.sidebar.multiselect(
            "Select Course ID",
            options=all_courses,
            default=all_courses
        )

        df_filtered = df[df[course_col].isin(selected_courses)]

        # Performance Category
        def performance(score):
            if pd.isna(score) or score < 10:
                return "Low"
            elif score < 18:
                return "Medium"
            else:
                return "High"

        df_filtered["Performance"] = df_filtered["out_of_25"].apply(performance)

        # Performance Chart
        st.subheader("📊 Performance Distribution")

        perf_df = df_filtered["Performance"].value_counts().reset_index()
        perf_df.columns = ["Category", "Count"]

        fig_perf = px.bar(
            perf_df,
            x="Category",
            y="Count",
            color="Category",
            text_auto=True
        )

        st.plotly_chart(fig_perf, use_container_width=True)

        st.divider()

        # Filtered Data Table
        st.subheader("📋 Filtered Data")
        st.dataframe(df_filtered, use_container_width=True)

        st.download_button(
            "⬇ Download Filtered CSV",
            df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

        st.divider()

        # Full Data
        st.subheader("📂 Full Dataset")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("⬆ Upload CSV file to start analysis")

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

        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], key="cleaner")

        if uploaded_file:

            df = pd.read_csv(uploaded_file, dtype=str)
            df.columns = df.columns.str.strip()

            email_col = st.selectbox("Select Email Column", df.columns)

            if email_col:

                extracted = []
                for value in df[email_col].fillna("").astype(str):
                    extracted.extend(re.findall(email_pattern, value))

                df_clean = pd.DataFrame({"Cleaned Email": extracted})
                df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
                df_clean = df_clean.drop_duplicates()

                c1, c2 = st.columns(2)
                c1.metric("Original Rows", f"{len(df):,}")
                c2.metric("Unique Clean Emails", f"{len(df_clean):,}")

                st.dataframe(df_clean, use_container_width=True)

                st.download_button(
                    "⬇ Download Cleaned Emails",
                    df_clean.to_csv(index=False).encode("utf-8"),
                    file_name="cleaned_emails.csv",
                    mime="text/csv"
                )

    else:

        pasted_text = st.text_area(
            "Paste Emails Here",
            height=250,
            placeholder="example1@gmail.com, example2@gmail.com\nexample3@gmail.com"
        )

        if pasted_text:

            extracted = re.findall(email_pattern, pasted_text)

            df_clean = pd.DataFrame({"Cleaned Email": extracted})
            df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
            df_clean = df_clean.drop_duplicates()

            c1, c2 = st.columns(2)
            c1.metric("Total Extracted Emails", f"{len(extracted):,}")
            c2.metric("Unique Clean Emails", f"{len(df_clean):,}")

            st.dataframe(df_clean, use_container_width=True)

            st.download_button(
                "⬇ Download Cleaned Emails",
                df_clean.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_emails.csv",
                mime="text/csv"
            )
