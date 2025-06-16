import streamlit as st
from agents.crawler import fetch_news
from agents.analyst import extract_events
from agents.advisor import get_advisor_output

st.title("Market Pulse (Biotech Business Intelligence)")

company = st.text_input("Enter company name (e.g., Sanofi):", value="Sanofi")
debug = st.checkbox("Debug mode", value=True)

if st.button("Run Market Pulse"):
    debug_logs = {}
    with st.spinner("Fetching news..."):
        articles = fetch_news(company, max_articles=3, debug=True, debug_logs=debug_logs)
    with st.spinner("Extracting events..."):
        analyst_output, analyst_debug = extract_events(company, articles, debug=debug)
        debug_logs.update(analyst_debug)
    with st.spinner("Advisor report..."):
        advisor_output, advisor_debug = get_advisor_output(company, analyst_output.events, debug=debug)
        debug_logs.update(advisor_debug)

    st.header("Extracted Events")
    st.json([ev.dict() for ev in analyst_output.events])

    if advisor_output:
        st.header("Advisor Report")
        st.markdown(f"**Google Trends Score:** {advisor_output['google_trends']}")
        st.subheader("Key Insights")
        st.write(advisor_output["key_insights"])
        st.subheader("Key Takeaways")
        st.write("\n".join(f"- {k}" for k in advisor_output["key_takeaways"]))
        st.subheader("Risks and Opportunities")
        st.markdown(f"**Risks:** {advisor_output['risks_and_opportunities']['risks']}")
        st.markdown(f"**Opportunities:** {advisor_output['risks_and_opportunities']['opportunities']}")
        st.subheader("Recommendations")
        st.write("\n".join(f"- {k}" for k in advisor_output["recommendations"]))
        st.subheader("Conclusion")
        st.write(advisor_output["conclusion"])

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