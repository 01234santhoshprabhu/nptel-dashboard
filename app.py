# ==========================================================
# ===================== DASHBOARD ==========================
# ==========================================================
if page == "📊 Dashboard":

    st.title("📊 Assignment Dump Filtering Dashboard")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], key="dash_upload")

    if uploaded_file:

        df = pd.read_csv(uploaded_file, encoding="latin1", low_memory=False)
        df.columns = df.columns.str.strip()
        df_original = df.copy()

        email_col = [c for c in df.columns if "email" in c.lower()][0]
        course_col = [c for c in df.columns if "course" in c.lower()][0]

        df["out_of_25"] = pd.to_numeric(df["out_of_25"], errors="coerce")

        # ---------------- KPI METRICS ----------------
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Candidates", df_original[email_col].nunique())
        k2.metric("Unique Courses", df_original[course_col].nunique())
        k3.metric("Total Records", len(df_original))
        k4.metric("Average Score", round(df_original["out_of_25"].mean(), 2))

        st.divider()

        df_filtered = df_original.copy()

        # ---------------- GLOBAL SEARCH ----------------
        search = st.text_input("🔍 Global Search")
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
            default=all_courses,
            key="course_filter"
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

        # ---------------- PERFORMANCE CHART ----------------
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

        # ---------------- FILTERED DATA ----------------
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
