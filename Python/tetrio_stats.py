import requests, argparse, locale, json, datetime, math

#           'prev_rank': None,
#           'prev_at': -1,
#           'next_rank': None,
#           'next_at': -1,

locale.setlocale(locale.LC_ALL, ('en', 'UTF-8'))
parser = argparse.ArgumentParser(description='Insert nickname or id of player and get detalied stats into output')
parser.add_argument("nick", metavar="p", type=str, help="Nickname or id of player")
args = parser.parse_args()
nick = args.nick.lower()

request = requests.get(f"https://ch.tetr.io/api/users/{nick}")
if not request.ok:
    exit(f"Request error: {request.status_code} {request.reason}")
teto_record = json.loads(request.content)
if not teto_record['success']:
    exit(f"Unsuccessful request: {teto_record['error']}")
locale
data_from = datetime.datetime.fromtimestamp(teto_record['cache']['cached_at']/1000)
nothing = ""
if teto_record['data']['user']['gametime'] == -1:
    tp = "???"
else:
    tp = datetime.timedelta(seconds=teto_record['data']['user']['gametime'])
if "ts" in teto_record['data']['user']:
    reg = f"{datetime.datetime.fromisoformat(teto_record['data']['user']['ts'][:-1]).strftime('%c')} ({datetime.datetime.now() - datetime.datetime.fromisoformat(teto_record['data']['user']['ts'][:-1])} ago)"
else:
    reg = "Since the beginning"
data_to_print = [
    (f"{request.status_code} {request.reason}", data_from.strftime('%c')),
    ("", ""),
    ("Nickname:", teto_record['data']['user']['username']),
    ("Country:", teto_record['data']['user']['country']),
    ("Registred:", reg),
    ("Time played:", tp),
    ("XP:", f"{teto_record['data']['user']['xp']:.0f} (lvl {(teto_record['data']['user']['xp']/500)**0.6+(teto_record['data']['user']['xp']/(5000+(max(0, teto_record['data']['user']['xp']-4*10**6)/5000)))+1})"),
    ("Role:", teto_record['data']['user']['role']),
    ("", "")
]
for key, value in data_to_print:
    print(f'{key:25} {value}')

if len(teto_record["data"]["user"]["badges"]) > 0:
    print(f"{nothing:25} Bages")
    for badge in teto_record["data"]["user"]["badges"]:
        if "ts" not in badge or badge["ts"] is None:
            print(f"{'Unknown date':25} {badge['label']}")
        else:
            print(f"{datetime.datetime.fromisoformat(badge['ts'][:-1]).strftime('%c'):25} {badge['label']}")

    print("\n")

if teto_record["data"]["user"]["league"]['gamesplayed'] > 0:
    if teto_record["data"]["user"]["league"]["rank"] == "z":
        rank = f"Probably around {teto_record['data']['user']['league']['percentile_rank']}"
        standing = "No"
    else:
        rank = teto_record["data"]["user"]["league"]["rank"]
        if teto_record['data']['user']['country'] is not None:
            standing = f"№{teto_record['data']['user']['league']['standing']} (№{teto_record['data']['user']['league']['standing_local']} in {teto_record['data']['user']['country']})"
        else:
            standing = f"№{teto_record['data']['user']['league']['standing']}"

    apm = teto_record['data']['user']['league']['apm']
    pps = teto_record['data']['user']['league']['pps']
    vs = teto_record['data']['user']['league']['vs']
    app = apm/(pps*60)
    vsapm = vs/apm
    dss = (vs/100)-(apm/60)
    dsp = ((vs/100)-(apm/60))/pps
    cheese = (dsp*150) + (((vs/apm)-2)*50) + (0.6-app)*125
    gbe = ((app*dss)/pps)*2
    area = apm + pps*45 + vs*0.444 + app*185 + dss*175 + dsp*450 + gbe*315
    nyaapp = app - 5 * math.tan(math.radians((cheese/-30)+1))

    data_to_print = [
        ("", "Tetra League"),
        ("Rank:", f"{rank} (top {teto_record['data']['user']['league']['percentile']*100}%)"),
        ("Tetra Rating:", teto_record['data']['user']['league']['rating']),
        ("Gliko Rating:", teto_record['data']['user']['league']['glicko']),
        ("Rating Deviation:", teto_record['data']['user']['league']['rd']),
        ("Leaderboard standing:", standing),
        ("Games played:", teto_record['data']['user']['league']['gamesplayed']),
        ("Games won:", f"{teto_record['data']['user']['league']['gameswon']} ({teto_record['data']['user']['league']['gameswon']/teto_record['data']['user']['league']['gamesplayed']*100}%)"),
        ("Attack Per Minute:", apm),
        ("Pieces Per Second:", pps),
        ("Versus Score:", vs),
        ("Attack Per Piece:", app),
        ("VS/APM:", vsapm),
        ("DS/Second:", dss),
        ("DS/Piece:", dsp),
        ("APP+DS/Piece:", dsp + app),
        ("Cheese Index:", cheese),
        ("Garbage Efficiency:", gbe),
        ("Area:", area),
        ("NyaAPP:", nyaapp)
    ]

    for key, value in data_to_print:
        print(f'{key:25} {value}')