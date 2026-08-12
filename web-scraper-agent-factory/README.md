# Web Scraper Agent Factory

Scrapes a business website and auto-configures a customer-support AI agent
from the scraped content.

## How it works

1. `scrape_website_content(url)` renders the page with Playwright and
   extracts clean text with BeautifulSoup (scripts/styles/nav/footer
   stripped, truncated to ~12k chars).
2. `AgentFactory.create_agent_from_url(url)` sends that text to an LLM
   (`gpt-4o` via the OpenAI API) with a meta-prompt that extracts the
   business name, industry, and a tailored system prompt, returned as JSON.
3. `ScrapedBusinessAgent` wraps that generated system prompt in a
   conversational agent with its own message memory, ready to answer
   customer queries.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
export OPENAI_API_KEY=sk-...
```

## Run

```bash
python agent_factory.py
# or target a specific site:
TARGET_WEBSITE_URL=https://example.com python agent_factory.py
```

## Notes

- Requires an `OPENAI_API_KEY` with access to `gpt-4o`.
- `scrape_website_content` returns an empty string on any scrape failure;
  `AgentFactory.create_agent_from_url` raises `ValueError` in that case.
- Only point this at websites you're authorized to scrape.
