# Technical Test

---

## Overview

This project is a biotech business intelligence web application.  
It extracts business deals, pipeline events, and competitor mapping for a given company using news and web articles.  
Prototype uses **Streamlit** (web), **LangChain** (LLM orchestration), and **OpenAI API**/**HuggingFaceAPI**/**Ollama** (LLM extraction).

---

## How to Run

**Requirements:**
- Docker & Docker Compose (Mac (Apple Silicon/Intel) or Windows 11, ≤16 GB RAM)
- OpenAI API key or Ollama

**Steps:**
1. **Clone the repository:**
    ```bash
    git clone https://github.com/keinsam/technical-test.git
    cd technical-test
    ```
2. **Add your OpenAI API Key or HF Token in a `.env` file:**
    ```
    OPENAI_API_KEY=sk-...
    HF_TOKEN=hf_...
    ```
3. **Build and run the app in Docker:**
    ```bash
    docker-compose build
    docker-compose up
    ```
    App available at [http://localhost:8501](http://localhost:8501).

---

## Data

- **Mock data only** (for Minimum Viable Product):  
  Only three companies available:  
  - GSK  
  - Atraverse Medical  
  - NextCure  
  Data is hardcoded and meant to show extraction/analysis flow.

---

## Design & Architecture

- **Frontend:** Streamlit UI for input/results.
- **Backend:** Python with LangChain for prompt structuring, parsing, and orchestration.
- **LLM:** OpenAI or HuggingFace API or Ollama, used via LangChain for event extraction.
- **Container:** Fully dockerized for portability.

---

## AI-assisted Coding

- `[AI]` in commit comments = AI (ChatGPT, Copilot) helped with code/design.
- AI was useful for:
  - Fast changes in Streamlit UI and project structure
  - Prototyping LLM prompts & LangChain chains
  - Troubleshooting and quick code snippets
  - Drafting early versions (esp. before requirements were 100% clear)
- **But:**  
  - I refactored a lot (especially for MVP clarity, and to distinguish deals vs pipelines cleanly)
  - Manual work was required for latest LangChain APIs, agent chaining, robust data handling, and integration details (Docker, Streamlit errors, etc.)

---

## Notes

- Minimum Viable Product (MVP) with mock data for demo purposes—focus is on logic, not data crawling.
- Runs the same on Mac/Windows (Intel/Apple Silicon).
- See code comments and commit history for details.
