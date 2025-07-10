import os, requests, telegram, datetime as dt
TOK      = os.getenv("TOKEN", "arkm")           # Coin-Ticker
THRESH   = int(os.getenv("THRESHOLD", 50000))   # USD-Schwelle
CHAT_ID  = os.getenv("CHAT_ID")                 # Zahl oder @Channel
TG_TOKEN = os.getenv("TG_TOKEN")                # Telegram-Bot-Token
ARKHAM   = os.getenv("ARKHAM_KEY")              # später nachtragen
if not ARKHAM:
    telegram.Bot(token=TG_TOKEN).send_message(
        chat_id=CHAT_ID,
        text="Bot-Ping: Telegram-Token und Chat-ID funktionieren ✔"
    )
    exit(0)

bot  = telegram.Bot(token=TG_TOKEN)
head = {"Authorization": f"Bearer {ARKHAM}"}
url  = f"https://arkham.network/api/v2/token/{TOK}/flows?interval=1d"

resp   = requests.get(url, headers=head, timeout=15).json()
inflow = sum(x["amountUsd"] for x in resp if x.get("direction") == "inflow")

if inflow > THRESH:
    ts  = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    bot.send_message(chat_id=CHAT_ID,
        text=f"{TOK.upper()} inflow {inflow:,.0f} USD  ({ts} UTC)")
