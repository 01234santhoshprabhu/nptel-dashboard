import streamlit as st
import pandas as pd
import plotly.express as px
import re

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
    ["📊 Dashboard", "📧 Email Cleaner"]
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

        # Detect important columns
        email_col = [c for c in df.columns if "email" in c.lower()][0]
        course_col = [c for c in df.columns if "course" in c.lower()][0]

        if "out_of_25" not in df.columns:
            st.error("Column 'out_of_25' not found.")
            st.stop()

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        # ---------------- KPI SECTION ----------------
        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Total Candidates", df_original[email_col].nunique())
        k2.metric("Unique Courses", df_original[course_col].nunique())
        k3.metric("Total Records", len(df_original))
        k4.metric("Average Score", round(df_original["out_of_25"].mean(), 2))

        st.divider()

        df_filtered = df_original.copy()

        # ---------------- SEARCH ----------------
        search = st.text_input("🔍 Global Search (Filtered Section Only)")
        if search:
            df_filtered = df_filtered[
                df_filtered.apply(
                    lambda r: r.astype(str).str.contains(search, case=False).any(),
                    axis=1
                )
            ]

        # ---------------- SIDEBAR FILTER ----------------
        st.sidebar.header("Filters")

        all_courses = sorted(df_original[course_col].dropna().unique())

        selected_courses = st.sidebar.multiselect(
            "Select Course ID",
            options=all_courses,
            default=all_courses
        )

        if selected_courses:
            df_filtered = df_filtered[df_filtered[course_col].isin(selected_courses)]

        # ---------------- PERFORMANCE CATEGORY ----------------
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

        # ---------------- COURSE COMPARISON ----------------
        st.subheader("⚔ Compare Two Courses")

        search_course = st.text_input("🔎 Search Course ID (Comparison)")
        filtered_course_list = [
            c for c in all_courses if search_course.lower() in c.lower()
        ]

        if len(filtered_course_list) >= 2:

            c1, c2 = st.columns(2)
            course1 = c1.selectbox("Course 1", filtered_course_list, key="c1")
            course2 = c2.selectbox("Course 2", filtered_course_list, key="c2")

            compare_df = df_original[df_original[course_col].isin([course1, course2])]

            show_only_graph = st.checkbox("Show Only Graph (Hide Table)")
            show_distribution = st.checkbox("Show Detailed Distribution")

            if not show_distribution:
                avg_df = compare_df.groupby(course_col)["out_of_25"].mean().reset_index()

                fig_cmp = px.bar(
                    avg_df,
                    x=course_col,
                    y="out_of_25",
                    color=course_col,
                    text_auto=True,
                    title="Average Score Comparison"
                )
            else:
                fig_cmp = px.histogram(
                    compare_df,
                    x="out_of_25",
                    color=course_col,
                    barmode="overlay",
                    opacity=0.6,
                    title="Score Distribution Comparison"
                )

            st.plotly_chart(fig_cmp, use_container_width=True)

            if not show_only_graph:
                st.dataframe(compare_df, use_container_width=True)

        st.divider()

        # ---------------- ASSIGNMENT TREND ----------------
        st.subheader("📈 Assignment Trend")

        assignment_cols = [c for c in df.columns if c.startswith("A")]

        if assignment_cols:
            assign_avg = df_filtered[assignment_cols].mean().reset_index()
            assign_avg.columns = ["Assignment", "Average Score"]

            fig_assign = px.line(
                assign_avg,
                x="Assignment",
                y="Average Score",
                markers=True
            )

            st.plotly_chart(fig_assign, use_container_width=True)

        st.divider()

        # ---------------- FILTERED TABLE ----------------
        st.subheader("📋 Filtered Data")
        st.dataframe(df_filtered, use_container_width=True)

        st.download_button(
            "⬇ Download Filtered CSV",
            df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="Filtered_Data.csv",
            mime="text/csv"
        )

        st.divider()

        # ---------------- FULL DATA ----------------
        st.subheader("📂 Full Dataset")
        st.dataframe(df_original, use_container_width=True)

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

                original_series = df[email_col].fillna("").astype(str)

                extracted = []
                for value in original_series:
                    extracted.extend(re.findall(email_pattern, value))

                df_clean = pd.DataFrame({"Cleaned Email": extracted})
                df_clean["Cleaned Email"] = df_clean["Cleaned Email"].str.lower().str.strip()
                df_clean = df_clean.drop_duplicates()

                c1, c2 = st.columns(2)
                c1.metric("Original Rows", f"{len(original_series):,}")
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
