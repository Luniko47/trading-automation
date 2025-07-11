import os, requests, datetime as dt, telegram, asyncio

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID  = os.getenv("CHAT_ID")
COINDAR_KEY = os.getenv("COINDAR_KEY")
TODAY = dt.date.today()

def fetch_today():
    url = (
        f"https://coindar.org/api/v2/events?"
        f"access_token={COINDAR_KEY}"
        f"&date_start={TODAY}"
        f"&days=1&page=1"
    )
    return requests.get(url, timeout=15).json()

async def main():
    data = fetch_today()
    raw_events = data.get("events") if isinstance(data, dict) else data
    if not raw_events:
        return

    # Filter: Nur Events, deren Datum wirklich heute ist
    events = []
    for ev in raw_events:
        d = ev.get("date_event", ev.get("date_start", ""))
        try:
            if d.startswith(str(TODAY)):
                events.append(ev)
        except: pass

    bot = telegram.Bot(token=TG_TOKEN)
    if not events:
        await bot.send_message(chat_id=CHAT_ID, text="Heute keine echten Events von Coindar verfügbar.")
        return

    for ev in events:
        date = ev.get("date_event", ev.get("date_start", "unbekannt"))
        symbol = ev.get("coin_symbol") or ev.get("coin_id") or "?"
        title  = ev.get("caption", "")
        text   = f"TODAY | {date} | {str(symbol).upper()} – {title}"
        await bot.send_message(chat_id=CHAT_ID, text=text)

if __name__ == "__main__":
    asyncio.run(main())
