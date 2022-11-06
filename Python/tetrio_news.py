import requests, argparse, locale, json, datetime, math
locale.setlocale(locale.LC_ALL, ('en', 'UTF-8'))
parser = argparse.ArgumentParser(description='Insert nickname or id of player and get detalied stats into output')
parser.add_argument("nick", metavar="p", type=str, help="Nickname or id of player")
args = parser.parse_args()
nick = args.nick.lower()

user_r = requests.get(f"https://ch.tetr.io/api/users/{nick}")
if not user_r.ok:
    exit(f"{user_r.url} request error: {user_r.status_code} {user_r.reason}")
user = json.loads(user_r.content)
if not user['success']:
    exit(f"Unsuccessful {user_r.url} request: {user['error']}")

request = requests.get(f"https://ch.tetr.io/api/news/user_{user['data']['user']['_id']}?limit=100")
if not request.ok:
    exit(f"{request.url} request error: {request.status_code} {request.reason}")
teto = json.loads(request.content)
if not teto['success']:
    exit(f"Unsuccessful {request.url} request: {teto['error']}")

data_from = datetime.datetime.fromtimestamp(teto['cache']['cached_at']/1000)
nothing = ""
gtype = {
    "40l": "40 LINES",
    "blitz": "BLITZ",
    "5mblast": "5,000,000 BLAST"
}

for entry in teto['data']['news']:
    timestamp = datetime.datetime.fromisoformat(entry['ts'][:-1]).strftime('%c')
    if entry['type'] == "personalbest":
        thing = f"Got a new personal best in {gtype[entry['data']['gametype']]}:"
        if entry['data']['gametype'] != "blitz":
            result = datetime.timedelta(milliseconds=entry['data']['result'])
        else:
            result = locale.format_string("%d", entry["data"]["result"], True)
        thing += f" {result}"
    elif entry['type'] == "rankup":
        thing = f"Achieved {entry['data']['rank'].upper()} rank in TETRA LEAGUE"
    elif entry['type'] == "badge":
        thing = f"Received the \"{entry['data']['label']}\" badge"
    elif entry['type'] == "supporter_gift":
        thing = "Has received the gift of TETR.IO Supporter"
    else:
        thing = f"{entry['type']}"
    print(f"{timestamp}: {thing}")