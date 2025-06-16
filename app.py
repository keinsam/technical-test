import streamlit as st
from agents.crawler import fetch_news
from agents.analyst import extract_deals
from agents.advisor import format_report

st.title("Market Pulse (Biotech Business Intelligence)")

company = st.text_input("Enter company name (e.g., Sanofi):", value="Sanofi")
use_mock = st.checkbox("Mock Data (dev/test)", value=True)
debug = st.checkbox("Debug mode", value=True)  # NEW

if st.button("Run Market Pulse"):
    debug_logs = {}
    with st.spinner("Fetching news..."):
        articles = fetch_news(company, max_articles=3, debug=True, debug_logs=debug_logs)
    with st.spinner("Analyzing deals and opportunities..."):
        analyst_output, analyst_debug = extract_deals(company, articles, debug=debug)
        debug_logs.update(analyst_debug)
    with st.spinner("Generating report..."):
        report = format_report(company, analyst_output)
        st.markdown(report)
    if analyst_output.deals:
        st.subheader("Deal Opportunity Scores")
        st.bar_chart([d.opportunity_score for d in analyst_output.deals])
    # Affichage Debug
    if debug:
        with st.expander("DEBUG INFO", expanded=True):
            for k, v in debug_logs.items():
                st.markdown(f"### {k}")
                st.code(v if isinstance(v, str) else str(v))