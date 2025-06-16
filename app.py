import io
import streamlit as st
from datetime import datetime
from gtts import gTTS
from agents.crawler import fetch_news
from agents.analyst import extract_events
from agents.advisor import get_advisor_output


EMOJI_MAP = {
    "deal": "🤝",
    "pipeline": "🧬",
    "other": "📰"
}

def advisor_report_to_markdown(advisor_output, company, events, report_date):
    takeaways = "\n".join(f"- {k}" for k in advisor_output.key_takeaways)
    recos = "\n".join(f"- {k}" for k in advisor_output.recommendations)
    event_table = (
        "| Type | Title | Date | Partners | Value | Product | Indication | Stage | Status | MOA | Competitors |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    for ev in events:
        event_table += "|"
        event_table += " | ".join([
            str(ev.type or ""),
            str(ev.title or ""),
            str(ev.date or ""),
            str(ev.partners or ""),
            str(ev.deal_value or ""),
            str(ev.product_name or ""),
            str(ev.indication or ""),
            str(ev.development_stage or ""),
            str(ev.status or ""),
            str(ev.mechanism_of_action or ""),
            str(ev.competitors or "")
        ])
        event_table += "|\n"
    md = (
        f"# Advisor Report: {company}\n\n"
        f"**Date**: {report_date}\n\n"
        f"**Google Trends Score**: {advisor_output.google_trends} / 100\n\n"
        f"## 🔎 Key Insights\n"
        f"{advisor_output.key_insights}\n\n"
        f"## 🏅 Key Takeaways\n"
        f"{takeaways}\n\n"
        f"## ✨ Extracted Events\n"
        f"{event_table}\n"
        f"## ⚠️ Risks & 💡 Opportunities\n"
        f"**Risks:** {advisor_output.risks_and_opportunities['risks']}\n\n"
        f"**Opportunities:** {advisor_output.risks_and_opportunities['opportunities']}\n\n"
        f"## ✅ Recommendations\n"
        f"{recos}\n\n"
        f"## 📝 Conclusion\n"
        f"{advisor_output.conclusion}\n"
    )
    return md

def generate_audio_summary(advisor_output, company, report_date, lang="en"):
    summary_text = (
        f"Advisor Report for {company}, dated {report_date}. "
        f"Google Trends Score: {advisor_output.google_trends} out of 100. "
        f"Key insights: {advisor_output.key_insights}. "
        f"Main takeaways: {', '.join(advisor_output.key_takeaways)}. "
        f"Risks: {advisor_output.risks_and_opportunities['risks']}. "
        f"Opportunities: {advisor_output.risks_and_opportunities['opportunities']}. "
        f"Recommendations: {', '.join(advisor_output.recommendations)}. "
        f"Conclusion: {advisor_output.conclusion}"
    )
    tts = gTTS(text=summary_text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

st.set_page_config(page_title="Market Pulse", page_icon="🩺", layout="wide")
st.title("Market Pulse 🚀")

with st.sidebar:
    st.header("Settings")
    company = st.text_input("🔎 Enter company name", value="GSK")
    debug = st.checkbox("Debug mode", value=True)

if st.button("Run Market Pulse"):
    debug_logs = {}
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # st.markdown(f"<h2 style='color:#222;'>{company} <span style='font-size:0.6em;color:#666;'>({report_date})</span></h2>", unsafe_allow_html=True)
    st.markdown(
        f"<h2 style='color:#1751a3;font-weight:700'>{company} "
        f"<span style='font-size:0.6em;color:#666;'>{report_date}</span></h2>",
        unsafe_allow_html=True
    )
    
    with st.spinner("📰 Fetching news..."):
        docs = fetch_news(company, max_articles=3, debug=True, debug_logs=debug_logs)

    with st.spinner("🧠 Extracting events..."):
        analyst_output, analyst_debug = extract_events(company, docs, debug=debug)
        debug_logs.update(analyst_debug)

    with st.spinner("🦾 Report..."):
        advisor_output, advisor_debug = get_advisor_output(company, analyst_output.events, debug=debug)
        debug_logs.update(advisor_debug)

    events = analyst_output.events

    # === Présentation principale ===
    st.header("✨ Extracted Events")
    EVENT_CARD_COLOR = "#e0c3fc"

    if events:
        cols = st.columns(2)
        for i, ev in enumerate(events):
            emoji = EMOJI_MAP.get(ev.type, "💡")
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
                source_html = (
                    f"<div style='margin-top:0.7em;font-size:0.9em;color:#3371c2;'>"
                    f"🔗 Source: <a href='{ev.source_url}' target='_blank' style='color:#3371c2;text-decoration:underline'>{ev.source_url}</a>"
                    f"</div>" if getattr(ev, "source_url", None) else ""
                )
                st.markdown(
                    f"""
                    <div style="background:{card_color};padding:1.2rem 1rem 1rem 1rem;border-radius:18px;box-shadow:0 2px 8px #0001;margin-bottom:1.2rem;color:#111;">
                        <h3 style="margin-bottom:0.3rem;color:#111;">{emoji} {ev.title}</h3>
                        <span style="font-size:0.9em;color:#222;">{ev.date or ''}</span>
                        {ul_html}
                        {summary_html}
                        {source_html}
                    </div>
                    """, unsafe_allow_html=True
                )

    else:
        st.info("No events found.")

    # === Rapport business/présentation ===
    if advisor_output:
        ADVISOR_BG = "#ffe5b4"
        st.header("💼 Advisor Report")
        st.markdown(
            f"""
            <div style="background:{ADVISOR_BG};padding:1.5rem 1.3rem 1.2rem 1.3rem;border-radius:18px;box-shadow:0 3px 12px #aaa2;margin-bottom:1.2rem;color:#111;">
                <h3 style="margin-bottom:0.2em;color:#333;">{company} <span style='font-size:0.8em;color:#555;'>({report_date})</span></h3>
                <h2 style="margin-bottom:0.7em;color:#111;">📈 <span style="color:#8b6100;">Google Trends Score:</span> <span style="font-size:1.3em;color:#111;">{advisor_output.google_trends} / 100</span> </h2>
                <h3 style="color:#1971c2;">🔎 Key Insights</h3>
                <div style="font-size:1.09em;color:#111;">{advisor_output.key_insights}</div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#0ca678;">🏅 Key Takeaways</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.2em;'>{k}</li>" for k in advisor_output.key_takeaways)}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#fab005;">⚠️ Risks & 💡 Opportunities</h3>
                <div style="margin-bottom:0.6em;color:#111;"><b>Risks:</b> <span style="color:#b42504;">{advisor_output.risks_and_opportunities['risks']}</span></div>
                <div style="color:#111;"><b>Opportunities:</b> <span style="color:#086375;">{advisor_output.risks_and_opportunities['opportunities']}</span></div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#495057;">✅ Recommendations</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.15em;'>{k}</li>" for k in advisor_output.recommendations)}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#5f3dc4;">📝 Conclusion</h3>
                <div style="font-size:1.11em;font-weight:500;color:#111;">{advisor_output.conclusion}</div>
            </div>
            """, unsafe_allow_html=True
        )

        # === SECTION "EXPORT & AUDIO" ===
        st.markdown("---")
        st.subheader("📤 Markdown & Audio summary")
        md_report = advisor_report_to_markdown(advisor_output, company, events, report_date)
        st.download_button(
            label="⬇️ Download Advisor Report (Markdown)",
            data=md_report,
            file_name=f"{company}_advisor_report_{report_date.replace(' ','_').replace(':','-')}.md",
            mime="text/markdown"
        )
        with st.expander("🔊 Listen to Audio Summary", expanded=False):
            audio_fp = generate_audio_summary(advisor_output, company, report_date, lang="en")
            st.audio(audio_fp, format="audio/mp3")

    # --- DEBUG INFO ---
    if debug:
        with st.expander("DEBUG INFO", expanded=False):
            for k, v in debug_logs.items():
                st.markdown(f"### {k}")
                st.code(v if isinstance(v, str) else str(v))