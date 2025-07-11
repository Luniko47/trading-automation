import os, requests, datetime as dt, telegram, asyncio

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID  = os.getenv("CHAT_ID")

def fetch_today():
    today = dt.date.today()
    url = (
        f"https://coindar.org/api/v2/events?"
        f"access_token={os.getenv('COINDAR_KEY')}"
        f"&date_start={today}"
        f"&days=1&page=1"
    )
    resp = requests.get(url, timeout=15).json()
    return resp.get("events") if isinstance(resp, dict) else resp

async def main():
    evs = fetch_today()
    bot = telegram.Bot(token=TG_TOKEN)
    if evs:
        for ev in evs:
            text = f"TODAY | {ev.get('date_event', ev.get('date_start'))} | {ev['coin_symbol'].upper()} – {ev['caption']}"
            await bot.send_message(chat_id=CHAT_ID, text=text)
    else:
        await bot.send_message(chat_id=CHAT_ID, text="Keine tagesaktuellen Events gefunden.")

if __name__ == "__main__":
    asyncio.run(main())
