ANALYST_PROMPT = """
Analyze the following news articles about {company}. 
Extract a list of unique, significant events directly supported by the articles, such as business deals, pipeline updates, or other relevant news.

Return EXACTLY and ONLY a single valid JSON object with this structure:

{{
  "events": [
    {{
      "type": "deal" | "pipeline" | "other",      // REQUIRED, choose only one
      "title": string,                            // REQUIRED, concise headline
      "date": string or null,
      "partners": string or null,
      "deal_value": string or null,
      "product_name": string or null,
      "indication": string or null,
      "development_stage": string or null,
      "status": string or null,
      "mechanism_of_action": string or null,
      "competitors": string or null,
      "summary": string                          // REQUIRED, summary of the event based ONLY on the articles
      "source_url": string or null                // REQUIRED, URL of the article
    }}
    // ... more events
  ]
}}

STRICT RULES:
- For each event, fill as many fields as possible directly from the articles. If a value is missing, use null (not "null", not empty string).
- Only include events and details actually present in the articles provided.
- DO NOT include comments, explanations, markdown, code fences, or any text before or after the JSON object.
- DO NOT include trailing commas.
- DO NOT invent or infer any events or details beyond what is clearly supported by the articles.
- Output MUST be a valid JSON object with key "events" (list of objects).

BEGIN ARTICLES:
{context}
END ARTICLES.

Provide ONLY the JSON object and nothing else.
"""

ADVISOR_PROMPT = """
You are a professional biotech business advisor. Based on the following list of structured events for {company}, produce a single valid JSON object containing ALL of these fields:

- "google_trends": integer (estimate if needed)
- "key_insights": string (3–5 business-oriented sentences)
- "key_takeaways": list of 3 to 5 bullet points (each 1–2 sentences)
- "risks_and_opportunities": {{ "risks": string, "opportunities": string }} (short paragraphs)
- "recommendations": list of 2–3 practical recommendations (bulleted)
- "conclusion": string (overall assessment)

STRICT RULES:
- Base your content ONLY on the provided events. If a field cannot be filled from them, state so or make a reasonable estimate.
- Return ONLY the JSON object, with NO markdown, comments, or explanation before or after.
- DO NOT include trailing commas.

BEGIN EVENTS:
{events_json}
END EVENTS.

Output ONLY the JSON object and nothing else.
"""
