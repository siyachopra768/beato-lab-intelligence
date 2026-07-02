import streamlit as st
import tempfile
import os

from parser import extract_lab_values,extract_text,detect_format
from beato import flag_diabetes_values,explain_consequences, get_risk_score

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BeatO Lab Intelligence",
    page_icon="🩺",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🩺 BeatO Lab Intelligence")
st.caption("Upload a diabetes patient's lab report to get coaching insights")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://www.beatoapp.com/images/beato-logo.png", width=140)
    st.markdown("### About")
    st.info(
        "This tool reads lab reports and surfaces diabetes-relevant insights "
        "that BeatO's SugarGPT currently doesn't have access to — "
        "HbA1c trends, kidney health, nerve health, and more."
    )
    st.markdown("### Supported Tests")
    st.markdown("""
    - HbA1c
    - Fasting Glucose
    - Creatinine (kidney)
    - Vitamin B12 (nerves)
    - Vitamin D
    - Hemoglobin
    - TSH (thyroid)
    - Total Cholesterol
    """)
    st.markdown("---")
    language = st.selectbox("Report Language", ["English", "Hindi"])
    st.caption("Built as a feature demo for BeatO's coaching workflow")


uploaded_file = st.file_uploader(

    "Upload lab report PDF",
    type=["pdf"],
    help="Supports SRL, Metropolis, Thyrocare, and other Indian lab formats"
)

if uploaded_file:
    # Save to temp file so pdfplumber can open it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # ── Step 1: Detect format ─────────────────────────────────────────────
        with st.spinner("Checking report format..."):
            fmt = detect_format(tmp_path)

        if fmt == "scanned":
            st.warning(
                "⚠️ This appears to be a scanned PDF. "
                "Text extraction may be limited. "
                "For best results, upload a digital PDF from SRL/Metropolis/Thyrocare."
            )

        # ── Step 2: Extract text ──────────────────────────────────────────────
        with st.spinner("Reading report..."):
            raw_text = extract_text(tmp_path)

        if not raw_text:
            st.error("Could not extract text from this PDF. Please try a digital PDF.")
            st.stop()

        # ── Step 3: Parse lab values ──────────────────────────────────────────
        with st.spinner("Parsing lab values..."):
            lab_data = extract_lab_values(raw_text)

        # ── Step 4: Flag diabetes-relevant values ─────────────────────────────
        flagged = flag_diabetes_values(lab_data)

        # ── Step 5: Risk score ────────────────────────────────────────────────
        score, category = get_risk_score(flagged)

        # ── Display: Risk score ───────────────────────────────────────────────
        st.subheader("Diabetes Risk Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Risk Score", f"{score}/100")
        with col2:
            st.metric("Category", category)
        with col3:
            st.metric("Values Found", f"{len(flagged)} relevant tests")

        st.divider()

        # ── Display: Flagged values ───────────────────────────────────────────
        if flagged:
            st.subheader("Key Lab Values")

            # Show critical ones first
            critical = [v for v in flagged if v["is_critical"]]
            abnormal = [v for v in flagged if not v["is_critical"] and v["status"] != "Normal"]
            normal = [v for v in flagged if v["status"] == "Normal"]

            if critical:
                st.error("🔴 Critical Values — Needs immediate attention")
                cols = st.columns(len(critical))
                for i, item in enumerate(critical):
                    with cols[i]:
                        st.metric(
                            label=item["test"],
                            value=f"{item['value']} {item['unit']}",
                            delta=f"⚠️ {item['status']} — Critical",
                            delta_color="inverse"
                        )
                        st.caption(item["why_it_matters"])

            if abnormal:
                st.warning("🟡 Abnormal Values")
                cols = st.columns(min(len(abnormal), 4))
                for i, item in enumerate(abnormal):
                    with cols[i % 4]:
                        st.metric(
                            label=item["test"],
                            value=f"{item['value']} {item['unit']}",
                            delta=item["status"],
                            delta_color="inverse"
                        )
                        st.caption(item["why_it_matters"])

            if normal:
                st.success("🟢 Normal Values")
                cols = st.columns(min(len(normal), 4))
                for i, item in enumerate(normal):
                    with cols[i % 4]:
                        st.metric(
                            label=item["test"],
                            value=f"{item['value']} {item['unit']}",
                            delta="Normal"
                        )

            st.divider()

            # ── Display: BeatO coaching insights ─────────────────────────────
            st.subheader("💬 BeatO Coaching Insights")
            st.caption("AI-generated insights for BeatO's diabetes care team")
            
            
            with st.spinner("Generating insights..."):
                insights = explain_consequences(flagged, language)

            st.info(insights)

            # ── Display: Full data table ──────────────────────────────────────
            with st.expander("View all extracted lab values"):
                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Test": v["test"],
                        "Value": v["value"],
                        "Unit": v["unit"],
                        "Ref Low": v["ref_low"],
                        "Ref High": v["ref_high"],
                        "Status": v["status"],
                        "Critical": "Yes" if v["is_critical"] else "No"
                    }
                    for v in flagged
                ])
                st.dataframe(df, use_container_width=True)

        else:
            st.warning(
                "No diabetes-relevant values were found in this report. "
                "This could mean the report format is non-standard or "
                "doesn't contain the tests BeatO tracks."
            )

            with st.expander("View raw extracted text"):
                st.text(raw_text[:2000])

    finally:
        os.unlink(tmp_path)  # clean up temp file

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown("""
    ### How it works
    1. Upload any Indian lab report PDF (SRL, Metropolis, Thyrocare etc.)
    2. The app extracts diabetes-relevant values automatically
    3. Get BeatO-style coaching insights for the care team
    
    ### Why this matters
    BeatO's SugarGPT currently only sees glucometer readings.  
    This tool adds the full lab report picture — HbA1c trends, 
    kidney health, nerve health, and more — giving BeatO's coaches 
    a complete view of each patient.
    """)