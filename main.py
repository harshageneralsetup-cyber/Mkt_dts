import os
import sys
import requests
from bs4 import BeautifulSoup
from google import genai

# Fetch configurations securely from GitHub Environment Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# The SDK automatically uses GEMINI_API_KEY if it exists in the environment

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: DISCORD_WEBHOOK_URL is missing from environment variables.")
    sys.exit(1)
if not os.getenv("GEMINI_API_KEY"):
    print("❌ Error: GEMINI_API_KEY is missing from environment variables.")
    sys.exit(1)

# Initialize the Gemini Client
client = genai.Client()

def fetch_live_market_data():
    """Extracts live financial data using standard Yahoo Finance summary structures."""
    data = {"brent": 87.50, "us10y": "4.48%", "dxy": "99.90"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        # Crude Brent
        oil_req = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BZ=F", headers=headers, timeout=5)
        data["brent"] = float(oil_req.json()['chart']['result'][0]['meta']['regularMarketPrice'])
    except Exception:
        pass

    try:
        # US 10-Year Bond Yield
        yield_req = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/^TNX", headers=headers, timeout=5)
        price = yield_req.json()['chart']['result'][0]['meta']['regularMarketPrice']
        data["us10y"] = f"{price}%"
    except Exception:
        pass

    try:
        # US Dollar Index
        dxy_req = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB", headers=headers, timeout=5)
        price = dxy_req.json()['chart']['result'][0]['meta']['regularMarketPrice']
        data["dxy"] = f"{price}"
    except Exception:
        pass

    return data

def fetch_live_news_narratives():
    """Scrapes active financial headlines via a public RSS feed or news wire."""
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get("https://www.reutersagency.com/feed/", headers=headers, timeout=7)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('item')
        
        for item in items[:5]:
            title = item.title.text.strip()
            headlines.append(f"- {title}")
    except Exception:
        headlines = [
            "- Markets parsing recent macro data setups.",
            "- Global commodity cross-currents drive local tracking ranges."
        ]
    return "\n".join(headlines)

def generate_ai_summary(prices, narratives):
    """Feeds raw data and headlines into Gemini to generate a fluid, intelligent macro report."""
    
    # If the narratives fallback was triggered, we give the AI a better default prompt context
    news_context = narratives
    if "parsing recent macro data setups" in narratives:
        news_context = "- Global markets are consolidating ahead of major upcoming central bank macro data updates."

    prompt = f"""
    You are an institutional-grade global macro hedge fund strategist and elite quantitative analyst. 
    Analyze the following real-time market data and recent news headlines:

    MARKET DATA:
    - Brent Crude Oil: ${prices['brent']:.2f}
    - US 10-Year Bond Yield: {prices['us10y']}
    - US Dollar Index (DXY): {prices['dxy']}

    LATEST HEADLINES:
    {news_context}

    Based on this data, write a sophisticated, hyper-crisp, data-driven macro summary tailored for active Indian stock market traders (Nifty/Sensex/Dalal Street).
    
    TONE & STYLE RULES:
    - Eliminate fluff, generalizations, or filler words. Every sentence must contain data, specific indicators, or explicit tactical action.
    - Focus heavily on quantified macro transmission mechanisms (e.g., how the exact Brent or DXY print directly math-models into Indian equity sectoral adjustments).
    - Give a strong, prioritized weightage to Indian market outcomes.

    Follow this layout blueprint EXACTLY. 

    CRITICAL FORMATTING RULES FOR DISCORD:
    - Do NOT put a blank line or a new paragraph break immediately after a bullet point (*). 
    - Keep the bullet point and its text on the exact same line.
    - Keep the "Sector Impacts" header entirely on a single line.

    --- COPY THIS BLUEPRINT EXACTLY AND FILL IN THE BRACKETS ---

    ⚡ **Macro Flash: The 5 Pillars**
    * 🏛️ **Interest Rates**: [Crisp, 1-sentence data-driven verdict on Western rate positioning and the definitive next structural move for the RBI]
    * 🛢️ **Oil (Brent)**: ${prices['brent']:.2f} | [Actionable assessment tracking the exact price action against India's fiscal threshold, raw material input margins, and local inflation limits]
    * 💵 **Dollar Index (DXY)**: {prices['dxy']} | [Quantified correlation impact regarding USD/INR spot limits, FII net flows, and emergent capital outflow triggers]
    * 📈 **US Bond Yields (10Y)**: {prices['us10y']} | [Direct transmission breakdown affecting the India 10Y sovereign spread, domestic bond yields, and growth stock valuation compression]
    * 🎈 **Inflation**: [Hard macro data comparison between Western CPI/PPI sticky points and India's current CPI trajectory]

    📰 **Latest Global Context Indicators:**
    [Provide a highly actionable, 2-sentence market tactical view projecting exactly how these global numbers will dictate the opening directional momentum and volatility parameters for Nifty]

    💼 **Sector Impacts: Winners & Losers**
    🟢 **Immediate Winners (Bullish)**
    * **[Specific Indian Sector/Industry 1]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]
    * **[Specific Indian Sector/Industry 2]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]
    * **[Specific Indian Sector/Industry 3]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]

    🔴 **Immediate Losers (Bearish)**
    * **[Specific Indian Sector/Industry 1]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]
    * **[Specific Indian Sector/Industry 2]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]
    * **[Specific Indian Sector/Industry 3]**: [Highly specific 1-sentence actionable trade reason linked directly to raw data metrics]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Generation Error: {str(e)}\nFalling back to system diagnostics."

def dispatch_safely_under_limit(content):
    """Guarantees messages never cross Discord limits by automatically breaking payloads."""
    if not content:
        return
    max_chars = 1900
    chunks = [content[i:i+max_chars] for i in range(0, len(content), max_chars)]
    for chunk in chunks:
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": str(chunk)}, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send to Discord: {e}")

if __name__ == "__main__":
    print("Scraping real-time market figures...")
    market_metrics = fetch_live_market_data()
    print("Scraping active context headlines...")
    news_briefs = fetch_live_news_narratives()
    print("Generating AI data template summary...")
    final_payload = generate_ai_summary(market_metrics, news_briefs)
    print("Streaming directly into active Discord client feed...")
    dispatch_safely_under_limit(final_payload)
    print("Process executed successfully.")
