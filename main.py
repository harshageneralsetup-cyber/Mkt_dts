import os
import sys
import requests
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

def generate_ai_summary():
    """Commands Gemini to browse the web for live data and generate the institutional macro report."""
    
    prompt = """
    You are an institutional Indian equity market strategist running an elite Morning Trading Desk Brief. Your primary goal is NOT to explain macro or provide economic lessons. Your objective is absolute actionable alpha for the upcoming trading session on the NSE/BSE.

    Prioritize: Freshness > Relevance > Impact. 

    ### CRITICAL OPERATION LAWS:
    1. **LIVE DATA SEARCH:** You must explicitly browse the web (Reuters, Bloomberg, CNBC, Economic Times, Moneycontrol, NSE/BSE Corporate Announcements, RBI, SEBI) to gather live market data from the last 24 hours.
    2. **THE FRESHNESS FILTER:** Before writing any data point, ask yourself: *"Has this changed meaningfully during the last 24 hours?"* If NO, do not spend more than one sentence on it. Do not discuss static Fed rates, RBI repo rates, or long-term trends unless a fresh decision, data release, geopolitical event, or speech occurred overnight.
    3. **GLOBAL-ONLY MACRO MOVERS:** The "TOP 5 MARKET MOVERS" section must contain strictly global macro developments (e.g., central bank pivots, global inflation prints, currency swings, geopolitical events, commodity disruptions). Save all stock-specific corporate announcements exclusively for the Order Tracker, Stocks in News, or Earnings sections.
    4. **ALGORITHMIC SCORING SYSTEM:** Score every overnight event behind the scenes: [Impact Score (1-10) + Freshness Score (1-10) + Probability of Market Impact (1-10)]. Filter and sort your report so only the highest cumulative scoring events appear. 

    Generate your report using this exact structure, headers, and visual emojis. Do not deviate from this template. Replace the bracketed placeholders with ACTUAL LIVE DATA from today's session.

    ---

    ## ⚡ TODAY'S MARKET OUTLOOK
    * 🏁 **Opening Directional Bias:** [If markets are close please mention explicitly that markets are closed, Predict Gap-up, Gap-down, or Flat open based on live SGX/GIFT Nifty]
    * 📝 **Traders' Gameplan:** [Provide 1-2 sentences of tactical action, specific support/resistance zones, and sector rotation]

    ## 🔥 TOP 5 MARKET MOVERS (24H)
    *Ranked by Impact/Freshness Score. Must contain strictly global/macro developments. Clearly label impact as [HIGH IMPACT] or [MEDIUM IMPACT]*
    * **[Live Overnight Event]** - [IMPACT LEVEL]: [1 sentence explanation of the macro data/event]. 🟢 *Likely Beneficiaries:* [Stocks] | 🔴 *Likely Losers:* [Stocks]
    * **[Live Overnight Event]** - [IMPACT LEVEL]: [1 sentence explanation of the macro data/event]. 🟢 *Likely Beneficiaries:* [Stocks] | 🔴 *Likely Losers:* [Stocks]
    *(Add up to 5 critical macro events based strictly on the last 24h of news)*

    ## 📊 GLOBAL SNAPSHOT
    *Show only immediate 24h delta change and direction based on live fetched data*
    * 🇺🇸 **GIFT Nifty:** [Current Level] ([Change %] ➡️ [Trend Emoji])
    * 🇺🇸 **S&P 500 / Nasdaq:** [Current Level] ([Change %]) / [Current Level] ([Change %])
    * 🛢️ **Brent Crude:** $[Current Price]/bbl ([Change %]) - [1 sentence explicit impact on Indian margins]
    * 💵 **DXY / USD-INR:** DXY at [Current Level] ([Change %]) | USD-INR at ₹[Current Rate] ([Change %])

    ## 💰 FII/DII FLOWS
    * 🟢 **Yesterday FII Cash Flow:** [Net Sell/Buy Status and Exact ₹ Amount]
    * 🔵 **Yesterday DII Cash Flow:** [Net Sell/Buy Status and Exact ₹ Amount]
    * 📈 **5-Day & 20-Day Trend:** [1 sentence summarizing current institutional liquidity trend]

    ## 🎯 F&O POSITIONING
    * 📊 **Nifty PCR:** [Current PCR] | **Max Pain:** [Current Max Pain Level]
    * 🚀 **Open Interest:** Largest Call OI at [Level] | Largest Put OI at [Level]
    * ⚡ **OI Dynamics:** *Long Build-up:* [Stocks] | *Short Build-up:* [Stocks] | *Short Covering:* [Stocks]
    * 🎯 **Trading Zone:** Support at [Level] | Resistance at [Level] | Positioning Bias: [Bias]

    ## 🟢 SECTOR HEATMAP
    *Assign Bullish, Neutral, or Bearish based purely on last 24h triggers. Do not list all sectors—only those with active momentum shifts.*
    * 📈 **[Sector Name]:** [Bullish] | *Why:* [1 sentence connecting directly to a live overnight news/data trigger]
    * 📉 **[Sector Name]:** [Bearish] | *Why:* [1 sentence connecting directly to a live overnight news/data trigger]

    ## 💡 ALPHA OPPORTUNITIES
    *Identify under-reported developments, emerging themes, or dual-trigger situations where market reaction may be delayed.*
    * 🌟 **[Theme/Setup Name]:** [1-2 sentences explaining setup and why it provides an alpha edge]. *Stocks to Watch:* [Specific NSE/BSE Tickers]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "tools": [{"google_search": {}}] # Enables live web browsing to fulfill the prompt
            }
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Generation Error: {str(e)}\nFalling back to system diagnostics."

def dispatch_safely_under_limit(content):
    """Guarantees messages never cross Discord limits by breaking payloads safely at paragraph boundaries."""
    if not content:
        return
    
    max_chars = 1900
    paragraphs = content.split('\n')
    current_chunk = []
    current_length = 0

    def send_chunk(chunk):
        payload = '\n'.join(chunk)
        if payload.strip():
            try:
                requests.post(DISCORD_WEBHOOK_URL, json={"content": payload}, timeout=5)
            except Exception as e:
                print(f"Failed to send to Discord: {e}")

    for paragraph in paragraphs:
        if current_length + len(paragraph) + 1 > max_chars:
            if current_chunk:
                send_chunk(current_chunk)
            current_chunk = [paragraph]
            current_length = len(paragraph)
        else:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1

    if current_chunk:
        send_chunk(current_chunk)

if __name__ == "__main__":
    print("Commanding AI to search the web and generate elite institutional summary...")
    final_payload = generate_ai_summary()
    
    print("Streaming directly into active Discord client feed...")
    dispatch_safely_under_limit(final_payload)
    
    print("Process executed successfully.")
