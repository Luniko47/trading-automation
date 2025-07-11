import os, requests, datetime as dt, pytz, telegram, json, asyncio

TG_TOKEN    = os.getenv("TG_TOKEN")
CHAT_ID     = os.getenv("CHAT_ID")
COINDAR_KEY = os.getenv("COINDAR_KEY")

BERLIN = pytz.timezone("Europe/Berlin")
TODAY  = dt.date.today()
HORIZON_DAYS = 90   # statt 60

KEYWORDS_HIGH   = ["list", "fork", "upgrade", "burn", "protocol", "hard fork"]
KEYWORDS_MEDIUM = ["partnership", "vote", "airdrop", "staking", "burn"]

def fetch_events():
    end_date = TODAY + dt.timedelta(days=HORIZON_DAYS)
    url = (
        f"https://coindar.org/api/v2/events?"
        f"access_token={COINDAR_KEY}"
        f"&date_start={TODAY}"
        f"&date_end={end_date}"
        f"&page=1"
    )
    resp = requests.get(url, timeout=20)
    try:
        js = resp.json()
    except ValueError:
        js = json.loads(resp.text)
    events = js.get("events") if isinstance(js, dict) else js
    for ev in events or []:
        title = ev.get("caption", "").lower()
        lvl = None
        if any(k in title for k in KEYWORDS_HIGH):
            lvl = "High"
        elif any(k in title for k in KEYWORDS_MEDIUM):
            lvl = "Medium"
        if lvl:
            yield ev, lvl

def fmt(dt_str):
    try:
        utc = pytz.utc.localize(dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
        return utc.astimezone(BERLIN).strftime("%d.%m.%Y %H:%M")
    except:
        return dt.datetime.strptime(dt_str[:10], "%Y-%m-%d").strftime("%d.%m.%Y")

def build_digest(evs):
    lines = []
    for ev, lvl in sorted(evs, key=lambda x: x[0].get("date_event", x[0].get("date_start"))):
        when = fmt(ev.get("date_event", ev.get("date_start", "")))
        lines.append(f"— [{lvl}] {when}  {ev.get('coin_symbol','').upper()} – {ev['caption']}")
    return "🗓️ Katalysatoren (90 Tage)\n" + "\n".join(lines)

def build_reminders(evs):
    nxt = TODAY + dt.timedelta(days=1)
    lines = [f"⚠️ Morgen ({nxt}):"]
    for ev, lvl in evs:
        d = ev.get("date_event", ev.get("date_start",""))
        if d.startswith(str(nxt)):
            lines.append(f"— {ev.get('coin_symbol','').upper()} – {ev['caption']}")
    return "\n".join(lines) if len(lines)>1 else None

async def main():
    evs = list(fetch_events())
    bot = telegram.Bot(token=TG_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=build_digest(evs))
    reminder = build_reminders(evs)
    if reminder:
        await bot.send_message(chat_id=CHAT_ID, text=reminder)

if __name__ == "__main__":
    asyncio.run(main())
