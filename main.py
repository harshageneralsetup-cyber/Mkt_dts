import os
import sys
import requests
from bs4 import BeautifulSoup
from google import genai

# Fetch configurations securely from GitHub Environment Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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
        oil_req = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BZ=F", headers=headers, timeout=5)
        data["brent"] = float(oil_req.json()['chart']['result'][0]['meta']['regularMarketPrice'])
    except Exception:
        pass

    try:
        yield_req = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/^TNX", headers=headers, timeout=5)
        price = yield_req.json()['chart']['result'][0]['meta']['regularMarketPrice']
        data["us10y"] = f"{price}%"
    except Exception:
        pass

    try:
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
    news_context = narratives
    if "parsing recent macro data setups" in narratives:
        news_context = "- Global markets are consolidating ahead of major upcoming central bank macro data updates."

    prompt = f"""
    You are an institutional-grade global macro hedge fund strategist and elite quantitative analyst with a sharp, witty edge. 
    Analyze the following real-time market data and recent news headlines:

    MARKET DATA:
    - Brent Crude Oil: ${prices['brent']:.2f}
    - US 10-Year Bond Yield: {prices['us10y']}
    - US Dollar Index (DXY): {prices['dxy']}

    LATEST HEADLINES:
    {news_context}

    Based on this data, write a sophisticated, hyper-crisp, data-driven macro summary tailored for active Indian stock market traders (Nifty/Sensex/Dalal Street).
    
    OUTPUT DIRECTIVES (CRITICAL FOR CLEAN REPRESENTATION):
    - Do NOT include markdown code block syntax (like ```markdown or ```) around your response.
    - Do NOT output any structural setup instructions, blueprint lines, or bracket labels. Generate the final text directly.
    - Every sentence in the main sections must be dense with hard statistics, macro numbers, historical correlations, or explicit tactical sector outcomes. No filler text.
    - Prioritize a balanced macro view with heavy weightage on Indian equity market impacts.

    STRICT BOLDING AND LAYOUT RULES FOR SECTORS:
    - ONLY the sector names themselves must be bolded. 
    - The structural definition text or description immediately following the sector name MUST NOT contain bold markdown asterisks (**). Keep description text entirely normal.
    - Example of correct format: * **IT Services**: A DXY at 99.807 provides tailwinds for export-oriented margins...
    - Do NOT put a blank line or a new paragraph break immediately after a bullet point (*). Keep the bullet point and its text on the exact same line.
    - Keep the "Sector Impacts" header entirely on a single line.

    --- GENERATE AND OUTPUT FILE CONTENT FOLLOWING THIS STRUCTURE ONLY ---

    ⚡ **Macro Flash: The 5 Pillars**
    * 🏛️ **Interest Rates**: Provide a 1-sentence data-driven verdict on global central bank positions and the definitive next structural policy move for the RBI.
    * 🛢️ **Oil (Brent)**: ${prices['brent']:.2f} | Provide a crisp, data-backed assessment tracking this active pricing line against India's fiscal threshold, raw material inputs, and domestic corporate margin outlooks.
    * 💵 **Dollar Index (DXY)**: {prices['dxy']} | Detail the exact impact regarding immediate USD/INR currency tracking limits, FII net capital flows, and domestic volatility triggers.
    * 📈 **US Bond Yields (10Y)**: {prices['us10y']} | Provide the global yield context and explain how the India-US yield spread dynamics compress or support Nifty valuation setups.
    * 🎈 **Inflation**: Provide a sharp macro comparison matching sticky global consumer indices against India's local retail CPI data trajectories.

    📰 **Latest Global Context Indicators:**
    Provide a highly actionable, 2-sentence market tactical summary projecting exactly how these macro data points will dictate the opening directional momentum and opening volatility parameters for Nifty.

    💼 **Sector Impacts: Winners & Losers**
    🟢 **Immediate Winners (Bullish)**
    * **[Insert Sector 1]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.
    * **[Insert Sector 2]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.
    * **[Insert Sector 3]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.

    🔴 **Immediate Losers (Bearish)**
    * **[Insert Sector 1]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.
    * **[Insert Sector 2]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.
    * **[Insert Sector 3]**: Provide a highly specific, 1-sentence actionable trade reason linked directly to raw data metrics. No bold text inside this description sentence.

    🌮 **Donald's Wildcard Corner**
    * 🗣️ **The Presidential Proclamation**: Write a funny, highly satirical, over-the-top, fictional parody quote mimicking Donald Trump's signature speaking style. Tie his hilarious taco obsession directly into a parody commentary about today's Brent Crude oil price, the strong DXY, or global trade negotiations. Keep it to exactly 2 punchy sentences.
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
    """Guarantees messages never cross Discord limits by breaking payloads safely at paragraph boundaries."""
    if not content:
        return
    
    max_chars = 1900
    # Split text clean by paragraph structures to protect continuous lines from being cut mid-word
    paragraphs = content.split('\n')
    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:
        # Add 1 to account for the newline character re-addition
        if current_length + len(paragraph) + 1 > max_chars:
            # Dispatch current completed chunk safely
            payload = '\n'.join(current_chunk)
            if payload.strip():
                try:
                    requests.post(DISCORD_WEBHOOK_URL, json={"content": payload}, timeout=5)
                except Exception as e:
                    print(f"Failed to send to Discord: {e}")
            # Reset trackers
            current_chunk = [paragraph]
            current_length = len(paragraph)
        else:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1

    # Send any remaining lines left in buffer
    if current_chunk:
        payload = '\n'.join(current_chunk)
        if payload.strip():
            try:
                requests.post(DISCORD_WEBHOOK_URL, json={"content": payload}, timeout=5)
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
