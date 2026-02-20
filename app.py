import streamlit as st
import pandas as pd
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Santhosh | NPTEL Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SIMPLE CLEAN UI ----------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}

.block-container {
    background: white;
    padding: 2rem;
    border-radius: 14px;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CACHE FUNCTION ----------------
@st.cache_data(show_spinner=False)
def load_data(file):
    df = pd.read_csv(
        file,
        encoding="latin1",
        low_memory=False
    )
    df.columns = df.columns.str.strip()
    return df


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

        df = load_data(uploaded_file)

        # Detect columns safely
        email_cols = [c for c in df.columns if "email" in c.lower()]
        course_cols = [c for c in df.columns if "course" in c.lower()]

        if not email_cols or not course_cols or "out_of_25" not in df.columns:
            st.error("Required columns not found (email, course, out_of_25)")
            st.stop()

        email_col = email_cols[0]
        course_col = course_cols[0]

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        # ---------------- KPI SECTION ----------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Candidates", f"{df[email_col].nunique():,}")
        col2.metric("Unique Courses", f"{df[course_col].nunique():,}")
        col3.metric("Total Records", f"{len(df):,}")
        col4.metric("Average Score", round(df["out_of_25"].mean(), 2))

        st.divider()

        # ---------------- FILTER ----------------
        st.sidebar.header("Filters")

        courses = sorted(df[course_col].dropna().unique())

        selected_courses = st.sidebar.multiselect(
            "Select Course ID",
            options=courses,
            default=courses[:10]  # Load only first 10 by default (performance)
        )

        if selected_courses:
            df_filtered = df[df[course_col].isin(selected_courses)]
        else:
            df_filtered = df

        # ---------------- DATA DISPLAY (LIMITED) ----------------
        st.subheader("📋 Filtered Data (First 5000 rows only)")

        st.dataframe(
            df_filtered.head(5000),
            use_container_width=True
        )

        st.info("Showing first 5000 rows for performance. Download full file below.")

        # ---------------- DOWNLOAD ----------------
        st.download_button(
            "⬇ Download Filtered CSV",
            df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

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

                # VECTORISED (FAST)
                extracted = (
                    df[email_col]
                    .fillna("")
                    .str.findall(email_pattern)
                    .explode()
                    .dropna()
                )

                df_clean = pd.DataFrame({"Cleaned Email": extracted})
                df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
                df_clean = df_clean.drop_duplicates()

                c1, c2 = st.columns(2)
                c1.metric("Original Rows", f"{len(df):,}")
                c2.metric("Unique Clean Emails", f"{len(df_clean):,}")

                st.dataframe(df_clean.head(5000), use_container_width=True)
                st.info("Showing first 5000 rows only.")

                st.download_button(
                    "⬇ Download Cleaned Emails",
                    df_clean.to_csv(index=False).encode("utf-8"),
                    file_name="cleaned_emails.csv",
                    mime="text/csv"
                )

    else:

        pasted_text = st.text_area(
            "Paste Emails Here",
            height=250
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
