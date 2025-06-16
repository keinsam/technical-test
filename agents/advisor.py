def format_report(company, analyst_output):
    report = f"# Market Pulse: {company}\n\n"
    report += f"**Google Trends Score (3mo):** {analyst_output.google_trends}\n\n"
    report += "## Executive Summary\n"
    report += f"{analyst_output.summary}\n\n"
    report += "## Recent Key Deals\n"
    if analyst_output.deals:
        for d in analyst_output.deals:
            report += f"### {d.deal_name}\n"
            report += f"- Date: {d.date}\n"
            report += f"- Partner(s): {d.partners}\n"
            report += f"- Value: {d.deal_value}\n"
            report += f"- Stage: {d.development_stage}\n"
            report += f"- MOA: {d.moa}\n"
            report += f"- Competitors: {d.competitors}\n"
            report += f"- Opportunity Score: {d.opportunity_score}/5\n"
            report += f"- Summary: {d.summary}\n\n"
    else:
        report += "No recent deals found.\n"
    report += "\n## Competitors\n"
    if analyst_output.competitors:
        report += ", ".join(analyst_output.competitors)
    else:
        report += "No competitors listed.\n"
    return report
