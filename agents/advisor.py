def format_report(company, analyst_output):
    report = f"# Market Pulse: {company}\n\n"
    report += f"**Google Trends Score (3mo):** {analyst_output.google_trends}\n\n"
    report += "## Executive Summary\n"
    report += f"{analyst_output.summary}\n\n"
    report += "## Events\n"

    if analyst_output.events:
        for ev in analyst_output.events:
            report += f"### {ev.title}\n"
            report += f"- Type: {ev.type}\n"
            if ev.date: report += f"- Date: {ev.date}\n"
            if ev.partners: report += f"- Partners: {ev.partners}\n"
            if ev.deal_value: report += f"- Value: {ev.deal_value}\n"
            if ev.product_name: report += f"- Product: {ev.product_name}\n"
            if ev.indication: report += f"- Indication: {ev.indication}\n"
            if ev.development_stage: report += f"- Stage: {ev.development_stage}\n"
            if ev.status: report += f"- Status: {ev.status}\n"
            if ev.mechanism_of_action: report += f"- MOA: {ev.mechanism_of_action}\n"
            if ev.competitors: report += f"- Competitors: {ev.competitors}\n"
            if ev.opportunity_score is not None:
                report += f"- Opportunity Score: {ev.opportunity_score}/5\n"
            report += f"- Summary: {ev.summary}\n\n"
    else:
        report += "No significant events found.\n"

    report += "\n## Competitors\n"
    if analyst_output.competitors:
        report += ", ".join(analyst_output.competitors)
    else:
        report += "No competitors listed.\n"
    return report