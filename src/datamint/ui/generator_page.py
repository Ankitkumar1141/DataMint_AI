from __future__ import annotations

import streamlit as st

from datamint.services.dataset import generate_dataset, save_dataset_metadata, to_excel_bytes

TASKS = [
    "Classification",
    "Regression",
    "Clustering",
    "Time Series",
    "NLP / Text Classification",
    "Anomaly Detection",
    "Recommendation",
]

DOMAINS = [
    "Healthcare",
    "Finance",
    "Education",
    "Defense",
    "E-commerce",
    "Agriculture",
    "Transportation",
    "Manufacturing",
    "Energy",
    "Real Estate",
    "HR & Recruitment",
    "Cybersecurity",
    "Retail",
    "Sports Analytics",
    "Environment & Climate",
]


def render_generator_page() -> None:
    user = st.session_state.user
    left, right = st.columns([5, 1])
    left.title("DataForge AI")
    left.caption(f"Logged in as **{user['username']}**")
    if right.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    with st.form("dataset_form"):
        c1, c2 = st.columns(2)
        features = c1.slider("Features", 2, 20, 5)
        rows = c2.slider("Rows", 10, 1000, 100)
        task = st.selectbox("ML Task", TASKS)
        domain = st.selectbox("Domain", DOMAINS)
        description = st.text_area(
            "Describe the dataset",
            placeholder="Example: Patient data to predict diabetes from glucose, BMI, age, etc.",
        )
        submitted = st.form_submit_button("Generate Dataset", type="primary")

    if submitted:
        with st.spinner("Generating dataset..."):
            try:
                df = generate_dataset(features, rows, task, domain, description)
                save_dataset_metadata(user["id"], task, domain, rows, features, description, list(df.columns))
                st.session_state.df = df
                st.success("Dataset generated successfully.")
            except Exception as exc:
                st.error(str(exc))

    if "df" in st.session_state:
        df = st.session_state.df
        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        b1, b2 = st.columns(2)
        b1.download_button(
            "Download CSV",
            df.to_csv(index=False),
            file_name="dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )
        b2.download_button(
            "Download Excel",
            to_excel_bytes(df),
            file_name="dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
