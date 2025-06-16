def format_report(company, analyst_output):
    report = f"# Market Pulse: {company}\n\n"
    report += f"**Google Trends Score (3mo):** {analyst_output.google_trends}\n\n"
    report += "## Key Insights\n"
    report += f"{analyst_output.key_insights}\n\n"
    report += "## Key Takeaways\n"
    if analyst_output.key_takeaways:
        for item in analyst_output.key_takeaways:
            report += f"- {item}\n"
    else:
        report += "No key takeaways available.\n"
    report += "\n## Events\n"
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
    report += "\n## Risks and Opportunities\n"
    report += f"**Risks:** {analyst_output.risks_and_opportunities.risks}\n\n"
    report += f"**Opportunities:** {analyst_output.risks_and_opportunities.opportunities}\n\n"
    report += "## Recommendations\n"
    if analyst_output.recommendations:
        for rec in analyst_output.recommendations:
            report += f"- {rec}\n"
    else:
        report += "No recommendations available.\n"
    report += "\n## Conclusion\n"
    report += f"{analyst_output.conclusion}\n"
    return report