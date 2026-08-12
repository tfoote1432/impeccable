import os
import json
import logging
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# 1. WEB SCRAPER: Extracts readable text from any business website
# ---------------------------------------------------------------------------
def scrape_website_content(url: str) -> str:
    """Scrapes raw web page text content while ignoring scripts and styling."""
    logging.info(f"Extracting web data from: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Timeout set to handle slow loading sites safely
            page.goto(url, wait_until="networkidle", timeout=30000)
            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, "html.parser")

        # Strip clutter (scripts, styles, nav bars, footers if unnecessary)
        for element in soup(["script", "style", "nav", "footer", "noscript"]):
            element.decompose()

        # Extract clean text lines
        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        clean_text = " ".join(chunk for chunk in lines if chunk)

        # Limit token overhead (truncate long pages to ~12k characters)
        return clean_text[:12000]

    except Exception as err:
        logging.error(f"Failed to scrape website {url}: {str(err)}")
        return ""

# ---------------------------------------------------------------------------
# 2. META-FACTORY: Ingests raw scraped text & auto-configures an agent
# ---------------------------------------------------------------------------
class AgentFactory:
    """Processes scraped website context and creates a fully customized AI agent."""

    @staticmethod
    def create_agent_from_url(url: str) -> Dict[str, Any]:
        website_data = scrape_website_content(url)

        if not website_data:
            raise ValueError(f"Could not extract viable context from URL: {url}")

        logging.info("Analyzing business data and engineering tailored agent prompt...")

        meta_prompt = f"""
        You are an expert AI Systems Architect. Analyze the raw website context provided below for a client business.

        Extract their key details (Business Name, Industry, Services offered, Target Tone/Audience)
        and construct a custom System Prompt for an autonomous AI Assistant representing this company.

        WEBSITE CONTENT:
        \"\"\"
        {website_data}
        \"\"\"

        OUTPUT FORMAT: Return strict JSON only with these exact keys:
        {{
            "business_name": "Extracted Business Name",
            "industry": "Identified Industry",
            "agent_name": "Suggested Agent Name (e.g. Acme Support Bot)",
            "system_prompt": "A complete, direct system prompt setting tone, company knowledge, services, and operational constraints.",
            "temperature": 0.1
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": meta_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        config = json.loads(response.choices[0].message.content)
        logging.info(f"Successfully generated agent for: {config.get('business_name')}")
        return config

# ---------------------------------------------------------------------------
# 3. DYNAMIC AGENT ENGINE: Operates using the scraped knowledge
# ---------------------------------------------------------------------------
class ScrapedBusinessAgent:
    """The auto-generated agent powered purely by scraped business data."""

    def __init__(self, config: Dict[str, Any]):
        self.name = config["agent_name"]
        self.system_prompt = config["system_prompt"]
        self.temperature = config.get("temperature", 0.1)
        self.memory: List[Dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]

    def handle_customer_query(self, query: str) -> str:
        self.memory.append({"role": "user", "content": query})

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.memory,
                temperature=self.temperature,
            )
            reply = response.choices[0].message.content
            self.memory.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            logging.error(f"Execution Error in {self.name}: {str(e)}")
            return f"Error executing task: {str(e)}"

# ---------------------------------------------------------------------------
# EXECUTION DEMO: Run on any URL
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Pass in any live website URL
    TARGET_WEBSITE_URL = os.getenv("TARGET_WEBSITE_URL", "https://www.openai.com")

    print(f"\n--- Instantiating Agent from URL: {TARGET_WEBSITE_URL} ---")

    # 1. Scrape URL and automatically extract business persona/rules
    agent_config = AgentFactory.create_agent_from_url(TARGET_WEBSITE_URL)

    # 2. Spawn customized worker agent
    auto_agent = ScrapedBusinessAgent(agent_config)

    # 3. Test the auto-generated agent
    user_question = "What products or solutions do you offer?"
    agent_response = auto_agent.handle_customer_query(user_question)

    print(f"\n[Generated Agent: {agent_config['agent_name']}]")
    print(f"[Industry: {agent_config['industry']}]")
    print(f"\nUser: {user_question}")
    print(f"\nAgent Answer:\n{agent_response}")
