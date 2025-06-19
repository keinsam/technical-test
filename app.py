import streamlit as st
from datetime import datetime
from agents.state import PipelineState
from agents.graph import fetch_news_node, analyst_node, advisor_node

from gtts import gTTS
import io

st.set_page_config(page_title="Market Pulse", page_icon="🩺", layout="wide")
st.title("Market Pulse 🚀")

with st.sidebar:
    st.header("Settings")
    company = st.text_input("🔎 Enter company name", value="GSK")
    debug = st.checkbox("Debug mode", value=True)

def advisor_report_to_markdown(advisor_output, company, events, report_date):
    takeaways = "\n".join(f"- {k}" for k in advisor_output["key_takeaways"])
    recos = "\n".join(f"- {k}" for k in advisor_output["recommendations"])
    event_table = (
        "| Type | Title | Date | Partners | Value | Product | Indication | Stage | Status | MOA | Competitors |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    for ev in events:
        event_table += "|"
        event_table += " | ".join([
            str(ev.get("type", "")),
            str(ev.get("title", "")),
            str(ev.get("date", "")),
            str(ev.get("partners", "")),
            str(ev.get("deal_value", "")),
            str(ev.get("product_name", "")),
            str(ev.get("indication", "")),
            str(ev.get("development_stage", "")),
            str(ev.get("status", "")),
            str(ev.get("mechanism_of_action", "")),
            str(ev.get("competitors", ""))
        ])
        event_table += "|\n"
    return (
        f"# Advisor Report: {company}\n\n"
        f"**Date**: {report_date}\n\n"
        f"**Google Trends Score**: {advisor_output['google_trends']} / 100\n\n"
        f"## 🔎 Key Insights\n"
        f"{advisor_output['key_insights']}\n\n"
        f"## 🏅 Key Takeaways\n"
        f"{takeaways}\n\n"
        f"## ✨ Extracted Events\n"
        f"{event_table}\n"
        f"## ⚠️ Risks & 💡 Opportunities\n"
        f"**Risks:** {advisor_output['risks_and_opportunities']['risks']}\n\n"
        f"**Opportunities:** {advisor_output['risks_and_opportunities']['opportunities']}\n\n"
        f"## ✅ Recommendations\n"
        f"{recos}\n\n"
        f"## 📝 Conclusion\n"
        f"{advisor_output['conclusion']}\n"
    )

def generate_audio_summary(advisor_output, company: str, report_date: str, lang: str = "en") -> io.BytesIO:
    summary_text = (
        f"Advisor Report for {company}, dated {report_date}. "
        f"Google Trends Score: {advisor_output['google_trends']} out of 100. "
        f"Key insights: {advisor_output['key_insights']}. "
        f"Main takeaways: {', '.join(advisor_output['key_takeaways'])}. "
        f"Risks: {advisor_output['risks_and_opportunities']['risks']}. "
        f"Opportunities: {advisor_output['risks_and_opportunities']['opportunities']}. "
        f"Recommendations: {', '.join(advisor_output['recommendations'])}. "
        f"Conclusion: {advisor_output['conclusion']}"
    )
    tts = gTTS(text=summary_text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

if st.button("Run Market Pulse"):
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(
        f"<h2 style='color:#1751a3;font-weight:700'>{company} "
        f"<span style='font-size:0.6em;color:#666;'>{report_date}</span></h2>",
        unsafe_allow_html=True
    )

    # Initialize pipeline state
    state = PipelineState(company=company)

    # --- Fetch news ---
    with st.spinner("📰 Fetching news..."):
        try:
            state = fetch_news_node(state)
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            st.stop()

    # --- Extract events ---
    with st.spinner("🧠 Extracting events..."):
        try:
            state = analyst_node(state)
        except Exception as e:
            st.error(f"Error extracting events: {e}")
            st.stop()

    # --- Generate report ---
    with st.spinner("🦾 Generating report..."):
        try:
            state = advisor_node(state)
        except Exception as e:
            st.error(f"Error generating advisor report: {e}")
            st.stop()

    # Convert state to dict for Streamlit access
    state = state.dict()
    events = state["events"]
    advisor_output = state["advisor_report"]

    # === Show Extracted Events ===
    st.header("✨ Extracted Events")
    cols = st.columns(2)
    EMOJI_MAP = {"deal": "🤝", "pipeline": "🧬", "other": "📰"}

    if events:
        for i, ev in enumerate(events):
            emoji = EMOJI_MAP.get(ev.get("type", ""), "💡")
            li_items = [
                f"<li><b>{label}:</b> {ev.get(attr, '')}</li>"
                for label, attr in [
                    ("Type", "type"),
                    ("Partners", "partners"),
                    ("Value", "deal_value"),
                    ("Product", "product_name"),
                    ("Indication", "indication"),
                    ("Stage", "development_stage"),
                    ("Status", "status"),
                    ("MOA", "mechanism_of_action"),
                    ("Competitors", "competitors")
                ] if ev.get(attr)
            ]
            summary_html = f"<div style='margin-top:0.7em;font-size:0.97em;color:#111;'>{ev.get('summary', '')}</div>"
            source_html = (
                f"<div style='margin-top:0.7em;font-size:0.9em;color:#3371c2;'>"
                f"🔗 Source: <a href='{ev.get('source_url', '')}' target='_blank' style='color:#3371c2;text-decoration:underline'>{ev.get('source_url', '')}</a></div>"
                if ev.get("source_url") else ""
            )
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="background:#e0c3fc;padding:1.2rem 1rem 1rem 1rem;border-radius:18px;
                    box-shadow:0 2px 8px #0001;margin-bottom:1.2rem;color:#111;">
                        <h3 style="margin-bottom:0.3rem;color:#111;">{emoji} {ev.get('title', '')}</h3>
                        <span style="font-size:0.9em;color:#222;">{ev.get('date', '')}</span>
                        <ul style='padding-left:1.2em;color:#111;'>{''.join(li_items)}</ul>
                        {summary_html}
                        {source_html}
                    </div>
                    """, unsafe_allow_html=True
                )
    else:
        st.info("No events found.")

    # === BUSINESS REPORT ===
    if advisor_output:
        st.header("💼 Advisor Report")
        st.markdown(
            f"""
            <div style="background:#ffe5b4;padding:1.5rem 1.3rem 1.2rem 1.3rem;border-radius:18px;
            box-shadow:0 3px 12px #aaa2;margin-bottom:1.2rem;color:#111;">
                <h3 style="margin-bottom:0.2em;color:#333;">{company} <span style='font-size:0.8em;color:#555;'>({report_date})</span></h3>
                <h2 style="margin-bottom:0.7em;color:#111;">📈 <span style="color:#8b6100;">Google Trends Score:</span>
                <span style="font-size:1.3em;color:#111;">{advisor_output['google_trends']} / 100</span></h2>
                <h3 style="color:#1971c2;">🔎 Key Insights</h3>
                <div style="font-size:1.09em;color:#111;">{advisor_output['key_insights']}</div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#0ca678;">🏅 Key Takeaways</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.2em;'>{k}</li>" for k in advisor_output['key_takeaways'])}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#fab005;">⚠️ Risks & 💡 Opportunities</h3>
                <div style="margin-bottom:0.6em;color:#111;"><b>Risks:</b> <span style="color:#b42504;">{advisor_output['risks_and_opportunities']['risks']}</span></div>
                <div style="color:#111;"><b>Opportunities:</b> <span style="color:#086375;">{advisor_output['risks_and_opportunities']['opportunities']}</span></div>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#495057;">✅ Recommendations</h3>
                <ul style="color:#111;">{"".join(f"<li style='margin-bottom:0.15em;'>{k}</li>" for k in advisor_output['recommendations'])}</ul>
                <hr style="border:1px solid #f7ba6b;margin:0.8em 0;">
                <h3 style="color:#5f3dc4;">📝 Conclusion</h3>
                <div style="font-size:1.11em;font-weight:500;color:#111;">{advisor_output['conclusion']}</div>
            </div>
            """, unsafe_allow_html=True
        )

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
            audio_fp = generate_audio_summary(advisor_output, company, report_date)
            st.audio(audio_fp, format="audio/mp3")

    if debug:
        with st.expander("DEBUG INFO", expanded=False):
            for k, v in state["debug_logs"].items():
                st.markdown(f"### {k}")
                st.code(v if isinstance(v, str) else str(v))
