from agents.crawler import fetch_news
from agents.analyst import extract_deals
from agents.advisor import format_report

def run_market_pulse(company):
    print(f"Fetching news for: {company}")
    articles = fetch_news(company)
    print("Analyzing deals and opportunities...")
    analyst_output_json = extract_deals(company, articles)
    print("Formatting executive report...\n")
    report = format_report(company, analyst_output_json)
    print(report)

if __name__ == "__main__":
    company = input("Enter company name (e.g., Sanofi): ")
    run_market_pulse(company)
