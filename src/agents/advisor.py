import json

def format_report(company, analyst_output_json):
    data = json.loads(analyst_output_json)
    report = f"# Market Pulse: {company}\n\n"
    report += f"**Google Trends Score (3mo):** {data.get('google_trends', 'N/A')}\n\n"
    report += "## Executive Summary\n"
    report += f"{data.get('summary', 'No summary')}\n\n"
    report += "## Recent Key Deals\n"
    if data.get("deals"):
        for d in data["deals"]:
            report += f"- **{d.get('deal name', 'N/A')}**\n"
            report += f"    - Date: {d.get('date', 'N/A')}\n"
            report += f"    - Partner(s): {d.get('partners', 'N/A')}\n"
            report += f"    - Value: {d.get('deal value', 'N/A')}\n"
            report += f"    - Stage: {d.get('development stage', 'N/A')}\n"
            report += f"    - MOA: {d.get('MOA', 'N/A')}\n"
            report += f"    - Opportunity Score: {d.get('opportunity score', 'N/A')}\n"
            report += f"    - Summary: {d.get('summary', 'N/A')}\n"
    else:
        report += "No recent deals found.\n"
    report += "\n## Competitors\n"
    if data.get("competitors"):
        for comp in data["competitors"]:
            report += f"- {comp}\n"
    else:
        report += "No competitors listed.\n"
    return report
