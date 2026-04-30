from __future__ import annotations

import streamlit as st

from datamint.services.dataset import (
    generate_dataset,
    save_dataset_metadata,
    to_excel_bytes,
)

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
    left.title("DataMint AI")
    left.caption(f"Logged in as **{user['username']}**")

    if right.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    with st.form("dataset_form"):
        c1, c2 = st.columns(2)

        features = c1.slider(
            "Features",
            min_value=2,
            max_value=20,
            value=5,
            step=1,
            help="Number of columns/features in the generated dataset.",
        )

        rows = c2.slider(
            "Rows",
            min_value=10,
            max_value=5000,
            value=100,
            step=10,
            help=(
                "Mistral generates only the schema. "
                "Python generates the full dataset locally, so larger row counts are supported."
            ),
        )

        task = st.selectbox("ML Task", TASKS)
        domain = st.selectbox("Domain", DOMAINS)

        description = st.text_area(
            "Describe the dataset",
            placeholder=(
                "Example: Customer loan approval dataset with age, income, "
                "loan amount, credit score, employment status, and approval status."
            ),
            height=120,
        )

        st.info(
            "Mistral AI generates the dataset schema. "
            "Python then generates the full dataset locally for faster and more reliable output."
        )

        submitted = st.form_submit_button("Generate Dataset", type="primary")

    if submitted:
        if not description.strip():
            st.warning("Please describe the dataset before generating.")
            st.stop()

        with st.spinner("Generating dataset..."):
            try:
                df = generate_dataset(
                    features=features,
                    rows=rows,
                    task=task,
                    domain=domain,
                    description=description.strip(),
                )

                save_dataset_metadata(
                    user_id=user["id"],
                    task=task,
                    domain=domain,
                    rows=rows,
                    features=features,
                    description=description.strip(),
                    columns=list(df.columns),
                )

                st.session_state.df = df
                st.success(
                    f"Dataset generated successfully with {df.shape[0]} rows and {df.shape[1]} columns."
                )

            except Exception as exc:
                st.error(f"Dataset generation failed: {exc}")

    if "df" in st.session_state:
        df = st.session_state.df

        st.subheader("Preview")
        st.caption(f"Dataset shape: **{df.shape[0]} rows × {df.shape[1]} columns**")
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