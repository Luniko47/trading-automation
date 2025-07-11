import os, json, requests, datetime as dt, pytz, telegram

TG_TOKEN    = os.getenv("TG_TOKEN")
CHAT_ID     = os.getenv("CHAT_ID")
COINDAR_KEY = os.getenv("COINDAR_KEY")

BERLIN = pytz.timezone("Europe/Berlin")
TODAY  = dt.date.today()
HORIZON_DAYS = 60

HIGH = {"listing", "protocol_upgrade", "smart_money_inflow", "regulatory_decision"}
MED  = {"partnership", "governance_vote", "token_burn"}

def fetch_events():
    url = (
        f"https://coindar.org/api/v2/events?"
        f"access_token={COINDAR_KEY}&date_start={TODAY}"
        f"&days={HORIZON_DAYS}&page=1"
    )
    resp = requests.get(url, timeout=20)
    js = json.loads(resp.text)
    for ev in js["events"]:
        cat = ev.get("category", "").lower()
        if cat in HIGH or cat in MED:
            yield ev, ("High" if cat in HIGH else "Medium")

def fmt(dt_str):
    try:
        utc = pytz.utc.localize(dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
        return utc.astimezone(BERLIN).strftime("%d.%m.%Y %H:%M")
    except:
        return dt.datetime.strptime(dt_str[:10], "%Y-%m-%d").strftime("%d.%m.%Y")

def build_digest(evs):
    lines = []
    for ev, lvl in sorted(evs, key=lambda x: x[0]["date_event"]):
        when = fmt(ev["date_event"])
        lines.append(f"— [{lvl}] {when}  {ev['coin_symbol'].upper()} – {ev['title']}")
    return "🗓️ Katalysatoren (60 Tage)\n" + "\n".join(lines)

def build_reminders(evs):
    nxt = TODAY + dt.timedelta(days=1)
    lines = [
        f"⚠️ Morgen ({nxt}):",
        *[f"— {ev['coin_symbol'].upper()} – {ev['title']}"
          for ev, _ in evs if ev["date_event"].startswith(str(nxt))]
    ]
    return "\n".join(lines) if len(lines) > 1 else None

def main():
    evs = list(fetch_events())
    bot = telegram.Bot(token=TG_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=build_digest(evs))
    reminder = build_reminders(evs)
    if reminder:
        bot.send_message(chat_id=CHAT_ID, text=reminder)

if __name__ == "__main__":
    main()
