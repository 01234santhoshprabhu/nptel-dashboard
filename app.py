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

# ---------------- MODERN ANIMATED UI ----------------
st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #111827);
    color: white;
    animation: fadeIn 0.8s ease-in;
}

/* ===== FADE ANIMATION ===== */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

/* ===== GLASS CARD STYLE ===== */
.block-container {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem;
}

/* ===== SIDEBAR STYLE ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1f2937);
}

/* ===== BUTTON STYLE ===== */
.stButton>button {
    background: linear-gradient(90deg,#3b82f6,#6366f1);
    border-radius: 12px;
    color: white;
    font-weight: 600;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(99,102,241,0.5);
}

/* ===== METRIC CARD ANIMATION ===== */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 15px;
    transition: 0.3s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
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

        email_col = [c for c in df.columns if "email" in c.lower()][0]
        course_col = [c for c in df.columns if "course" in c.lower()][0]

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        # KPI CARDS
        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Total Candidates", df[email_col].nunique())
        k2.metric("Unique Courses", df[course_col].nunique())
        k3.metric("Total Records", len(df))
        k4.metric("Average Score", round(df["out_of_25"].mean(), 2))

        st.divider()

        # PERFORMANCE CHART
        def performance(score):
            if score < 10:
                return "Low"
            elif score < 18:
                return "Medium"
            else:
                return "High"

        df["Performance"] = df["out_of_25"].apply(performance)

        perf_df = df["Performance"].value_counts().reset_index()
        perf_df.columns = ["Category", "Count"]

        fig = px.bar(
            perf_df,
            x="Category",
            y="Count",
            color="Category",
            text_auto=True
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

    else:
        st.info("Upload CSV to start analysis")

# ==========================================================
# ===================== EMAIL CLEANER ======================
# ==========================================================

elif page == "📧 Email Cleaner":

    st.title("📧 Smart Email Cleaner")

    method = st.radio(
        "Input Method",
        ["📂 Upload CSV", "📋 Copy & Paste"]
    )

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    if method == "📂 Upload CSV":

        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

        if uploaded_file:

            df = pd.read_csv(uploaded_file, dtype=str)
            email_col = st.selectbox("Select Email Column", df.columns)

            if email_col:

                extracted = []
                for value in df[email_col].fillna("").astype(str):
                    extracted.extend(re.findall(email_pattern, value))

                df_clean = pd.DataFrame({"Email": extracted})
                df_clean["Email"] = df_clean["Email"].str.lower().str.strip()
                df_clean = df_clean.drop_duplicates()

                c1, c2 = st.columns(2)
                c1.metric("Original Rows", len(df))
                c2.metric("Unique Emails", len(df_clean))

                st.dataframe(df_clean, use_container_width=True)

                st.download_button(
                    "⬇ Download Cleaned Emails",
                    df_clean.to_csv(index=False).encode("utf-8"),
                    file_name="cleaned_emails.csv"
                )

    else:

        text = st.text_area("Paste Emails Here", height=200)

        if text:

            extracted = re.findall(email_pattern, text)

            df_clean = pd.DataFrame({"Email": extracted})
            df_clean["Email"] = df_clean["Email"].str.lower().str.strip()
            df_clean = df_clean.drop_duplicates()

            c1, c2 = st.columns(2)
            c1.metric("Extracted Emails", len(extracted))
            c2.metric("Unique Emails", len(df_clean))

            st.dataframe(df_clean, use_container_width=True)

            st.download_button(
                "⬇ Download Cleaned Emails",
                df_clean.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_emails.csv"
            )
