import streamlit as st
from agents.crawler import fetch_news
from agents.analyst import extract_events
from agents.advisor import format_report

st.title("Market Pulse (Biotech Business Intelligence)")

company = st.text_input("Enter company name (e.g., Sanofi):", value="Sanofi")
use_mock = st.checkbox("Mock Data (dev/test)", value=True)
debug = st.checkbox("Debug mode", value=True)

if st.button("Run Market Pulse"):
    debug_logs = {}
    with st.spinner("Fetching news..."):
        articles = fetch_news(company, max_articles=3, debug=True, debug_logs=debug_logs)
    with st.spinner("Analyzing events and opportunities..."):
        analyst_output, analyst_debug = extract_events(company, articles, debug=debug)
        debug_logs.update(analyst_debug)
    with st.spinner("Generating report..."):
        report = format_report(company, analyst_output)
        st.markdown(report)
    if analyst_output.events:
        st.subheader("Event Opportunity Scores (if any)")
        scores = [ev.opportunity_score for ev in analyst_output.events if ev.opportunity_score is not None]
        if scores:
            st.bar_chart(scores)
    if debug:
        with st.expander("DEBUG INFO", expanded=True):
            for k, v in debug_logs.items():
                st.markdown(f"### {k}")
                st.code(v if isinstance(v, str) else str(v))