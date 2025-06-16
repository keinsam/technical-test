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

    EVENT_CARD_COLOR = "#e0c3fc"  # lavande pâle uniforme

    if events:
        cols = st.columns(2)
        for i, ev in enumerate(events):
            emoji = EMOJI_MAP.get(ev.type, "💡")
            # même couleur pour tout le monde :
            card_color = EVENT_CARD_COLOR
            li_items = []
            if ev.type: li_items.append(f"<li><b>Type:</b> {ev.type.capitalize()}</li>")
            if ev.partners: li_items.append(f"<li><b>Partners:</b> {ev.partners}</li>")
            if ev.deal_value: li_items.append(f"<li><b>Value:</b> {ev.deal_value}</li>")
            if ev.product_name: li_items.append(f"<li><b>Product:</b> {ev.product_name}</li>")
            if ev.indication: li_items.append(f"<li><b>Indication:</b> {ev.indication}</li>")
            if ev.development_stage: li_items.append(f"<li><b>Stage:</b> {ev.development_stage}</li>")
            if ev.status: li_items.append(f"<li><b>Status:</b> {ev.status}</li>")
            if ev.mechanism_of_action: li_items.append(f"<li><b>MOA:</b> {ev.mechanism_of_action}</li>")
            if ev.competitors: li_items.append(f"<li><b>Competitors:</b> {ev.competitors}</li>")
            ul_html = f"<ul style='padding-left:1.2em;color:#111;'>{''.join(li_items)}</ul>"
            summary_html = f"<div style='margin-top:0.7em;font-size:0.97em;color:#111;'>{ev.summary}</div>"
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="background:{card_color};padding:1.2rem 1rem 1rem 1rem;border-radius:18px;box-shadow:0 2px 8px #0001;margin-bottom:1.2rem;color:#111;">
                        <h3 style="margin-bottom:0.3rem;color:#111;">{emoji} {ev.title}</h3>
                        <span style="font-size:0.9em;color:#222;">{ev.date or ''}</span>
                        {ul_html}
                        {summary_html}
                    </div>
                    """, unsafe_allow_html=True
                )
    else:
        st.info("No events found.")

    # --- Advisor report couleur distincte ---
    ADVISOR_BG = "#ffe5b4"  # beige orangé business

    if advisor_output:
        st.header("💼 Advisor Report")
        st.markdown(
            f"""
            <div style="background:{ADVISOR_BG};padding:1.5rem 1.3rem 1.2rem 1.3rem;border-radius:18px;box-shadow:0 3px 12px #aaa2;margin-bottom:1.2rem;color:#111;">
                <h2 style="margin-bottom:0.7em;color:#111;">📈 <span style="color:#8b6100;">Google Trends Score:</span> <span style="font-size:1.3em;color:#111;">{advisor_output['google_trends']} / 100</span> </h2>
                <h3 style="color:#1971c2;">🔎 Key Insights</h3>
                <div style="font-size:1.09em;color:#111;">{advisor_output['key_insights']}</div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#0ca678;">🏅 Key Takeaways</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.2em;'>{k}</li>" for k in advisor_output["key_takeaways"])}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#fab005;">⚠️ Risks & 💡 Opportunities</h3>
                <div style="margin-bottom:0.6em;color:#111;"><b>Risks:</b> <span style="color:#b42504;">{advisor_output['risks_and_opportunities']['risks']}</span></div>
                <div style="color:#111;"><b>Opportunities:</b> <span style="color:#086375;">{advisor_output['risks_and_opportunities']['opportunities']}</span></div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#495057;">✅ Recommendations</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.15em;'>{k}</li>" for k in advisor_output["recommendations"])}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
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
