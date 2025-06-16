
import streamlit as st
from agents.crawler import fetch_news
from agents.analyst import extract_events
from agents.advisor import get_advisor_output

EMOJI_MAP = {
    "deal": "🤝",
    "pipeline": "🧬",
    "other": "📰"
}

st.set_page_config(page_title="Market Pulse", page_icon="🩺", layout="wide")
st.title("Market Pulse 🚀")

with st.sidebar:
    st.header("Settings")
    company = st.text_input("🔎 Enter company name", value="GSK")
    debug = st.checkbox("Debug mode", value=True)

if st.button("Run Market Pulse"):
    debug_logs = {}

    with st.spinner("📰 Fetching news..."):
        articles = fetch_news(company, max_articles=3, debug=True, debug_logs=debug_logs)

    with st.spinner("🧠 Extracting events..."):
        analyst_output, analyst_debug = extract_events(company, articles, debug=debug)
        debug_logs.update(analyst_debug)

    with st.spinner("🦾 Advisor report..."):
        advisor_output, advisor_debug = get_advisor_output(company, analyst_output.events, debug=debug)
        debug_logs.update(advisor_debug)

    st.header("✨ Extracted Events")
    events = analyst_output.events

    if events:
        cols = st.columns(2)  # 2 cards per row for style
        for i, ev in enumerate(events):
            emoji = EMOJI_MAP.get(ev.type, "💡")
            card_color = "#e7f5ff" if ev.type == "deal" else ("#e6fcf5" if ev.type == "pipeline" else "#fff9db")
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="background:{card_color};padding:1.2rem 1rem 1rem 1rem;border-radius:18px;box-shadow:0 2px 8px #0001;margin-bottom:1.2rem;color:#111;">
                        <h3 style="margin-bottom:0.3rem;color:#111;">{emoji} {ev.title}</h3>
                        <span style="font-size:0.9em;color:#222;">{ev.date or ''}</span>
                        <ul style="padding-left:1.2em;color:#111;">
                            {"<li><b>Type:</b> " + ev.type.capitalize() + "</li>" if ev.type else ""}
                            {"<li><b>Partners:</b> " + str(ev.partners) + "</li>" if ev.partners else ""}
                            {"<li><b>Value:</b> " + str(ev.deal_value) + "</li>" if ev.deal_value else ""}
                            {"<li><b>Product:</b> " + str(ev.product_name) + "</li>" if ev.product_name else ""}
                            {"<li><b>Indication:</b> " + str(ev.indication) + "</li>" if ev.indication else ""}
                            {"<li><b>Stage:</b> " + str(ev.development_stage) + "</li>" if ev.development_stage else ""}
                            {"<li><b>Status:</b> " + str(ev.status) + "</li>" if ev.status else ""}
                            {"<li><b>Mechanism:</b> " + str(ev.mechanism_of_action) + "</li>" if ev.mechanism_of_action else ""}
                            {"<li><b>Competitors:</b> " + str(ev.competitors) + "</li>" if ev.competitors else ""}
                        </ul>
                        <div style="margin-top:0.7em;font-size:0.97em;color:#111;">{ev.summary}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
    else:
        st.info("No events found.")

    if advisor_output:
        st.header("💼 Advisor Report")
        st.markdown(
            f"""
            <div style="background:#f3f0ff;padding:1.5rem 1.3rem 1.2rem 1.3rem;border-radius:18px;box-shadow:0 3px 12px #aaa2;margin-bottom:1.2rem;color:#111;">
                <h2 style="margin-bottom:0.7em;color:#111;">📈 <span style="color:#6741d9;">Google Trends Score:</span> <span style="font-size:1.3em;color:#111;">{advisor_output['google_trends']} / 100</span> </h2>
                <h3 style="color:#1971c2;">🔎 Key Insights</h3>
                <div style="font-size:1.09em;color:#111;">{advisor_output['key_insights']}</div>
                <hr style="border:1px solid #eee;margin:0.8em 0;">
                <h3 style="color:#0ca678;">🏅 Key Takeaways</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.2em;'>{k}</li>" for k in advisor_output["key_takeaways"])}</ul>
                <hr style="border:1px solid #eee;margin:0.8em 0;">
                <h3 style="color:#fab005;">⚠️ Risks & 💡 Opportunities</h3>
                <div style="margin-bottom:0.6em;color:#111;"><b>Risks:</b> <span style="color:#e8590c;">{advisor_output['risks_and_opportunities']['risks']}</span></div>
                <div style="color:#111;"><b>Opportunities:</b> <span style="color:#087f5b;">{advisor_output['risks_and_opportunities']['opportunities']}</span></div>
                <hr style="border:1px solid #eee;margin:0.8em 0;">
                <h3 style="color:#495057;">✅ Recommendations</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.15em;'>{k}</li>" for k in advisor_output["recommendations"])}</ul>
                <hr style="border:1px solid #eee;margin:0.8em 0;">
                <h3 style="color:#5f3dc4;">📝 Conclusion</h3>
                <div style="font-size:1.11em;font-weight:500;color:#111;">{advisor_output["conclusion"]}</div>
            </div>
            """, unsafe_allow_html=True
        )

    if debug:
        with st.expander("DEBUG INFO", expanded=False):
            for k, v in debug_logs.items():
                st.markdown(f"### {k}")
                st.code(v if isinstance(v, str) else str(v))



