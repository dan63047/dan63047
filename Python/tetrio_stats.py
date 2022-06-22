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
    exit(f"{request.url} request error: {request.status_code} {request.reason}")
teto = json.loads(request.content)
if not teto['success']:
    exit(f"Unsuccessful {request.url} request: {teto['error']}")
request = requests.get(f"https://ch.tetr.io/api/users/{nick}/records")
if not request.ok:
    exit(f"{request.url} request error: {request.status_code} {request.reason}")
teto_records = json.loads(request.content)
if not teto['success']:
    exit(f"Unsuccessful {request.url} request: {teto['error']}")
data_from = datetime.datetime.fromtimestamp(teto['cache']['cached_at']/1000)
nothing = ""
if teto['data']['user']['gametime'] == -1:
    tp = "???"
else:
    tp = datetime.timedelta(seconds=teto['data']['user']['gametime'])
if "ts" in teto['data']['user']:
    reg = f"{datetime.datetime.fromisoformat(teto['data']['user']['ts'][:-1]).strftime('%c')} ({datetime.datetime.now() - datetime.datetime.fromisoformat(teto['data']['user']['ts'][:-1])} ago)"
else:
    reg = "Since the beginning"
data_to_print = [
    (f"{request.status_code} {request.reason}", data_from.strftime('%c')),
    ("", ""),
    ("Nickname", teto['data']['user']['username']),
    ("Country", teto['data']['user']['country']),
    ("Registred", reg),
    ("Time played", tp),
    ("XP", f"{locale.format_string('%.0f', teto['data']['user']['xp'], True)} (lvl {(teto['data']['user']['xp']/500)**0.6+(teto['data']['user']['xp']/(5000+(max(0, teto['data']['user']['xp']-4*10**6)/5000)))+1})"),
    ("Role", teto['data']['user']['role'])
]
for key, value in data_to_print:
    print(f'{key:25} {value}')

if len(teto["data"]["user"]["badges"]) > 0:
    print("\n")
    print(f"{nothing:25} Bages")
    for badge in teto["data"]["user"]["badges"]:
        if "ts" not in badge or badge["ts"] is None:
            print(f"{'Unknown date':25} {badge['label']}")
        else:
            print(f"{datetime.datetime.fromisoformat(badge['ts'][:-1]).strftime('%c'):25} {badge['label']}")


if teto["data"]["user"]["league"]['gamesplayed'] > 0:
    print("\n")
    if teto["data"]["user"]["league"]["rank"] == "z":
        if teto['data']['user']['league']['percentile_rank'] == "z":
            rank = "Played less than 10 mathes"
            gliko = f"{10 - teto['data']['user']['league']['gamesplayed']} matches until being rated"
            rd = "Big"
        else:
            rank = f"Probably around {teto['data']['user']['league']['percentile_rank'].upper()}"
            gliko = teto['data']['user']['league']['glicko']
            rd = teto['data']['user']['league']['rd']
        standing = "No"
    else:
        rank = teto["data"]["user"]["league"]["rank"].upper()
        gliko = teto['data']['user']['league']['glicko']
        rd = teto['data']['user']['league']['rd']
        if teto['data']['user']['country'] is not None:
            standing = f"№{teto['data']['user']['league']['standing']} (№{teto['data']['user']['league']['standing_local']} in {teto['data']['user']['country']})"
        else:
            standing = f"№{teto['data']['user']['league']['standing']}"

    apm = teto['data']['user']['league']['apm']
    pps = teto['data']['user']['league']['pps']
    vs = teto['data']['user']['league']['vs']
    if vs is None:
        vs = 0
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
        ("Rank", f"{rank} (top {teto['data']['user']['league']['percentile']*100}%)"),
        ("Tetra Rating", teto['data']['user']['league']['rating']),
        ("Gliko Rating",  gliko),
        ("Rating Deviation", rd),
        ("Leaderboard standing", standing),
        ("Games played", teto['data']['user']['league']['gamesplayed']),
        ("Games won", f"{teto['data']['user']['league']['gameswon']} ({teto['data']['user']['league']['gameswon']/teto['data']['user']['league']['gamesplayed']*100}%)"),
        ("Attack Per Minute", apm),
        ("Pieces Per Second", pps),
        ("Versus Score", vs),
        ("Attack Per Piece", app),
        ("VS/APM", vsapm),
        ("DS/Second", dss),
        ("DS/Piece", dsp),
        ("APP+DS/Piece", dsp + app),
        ("Cheese Index", cheese),
        ("Garbage Efficiency", gbe),
        ("Area", area),
        ("NyaAPP", nyaapp)
    ]

    for key, value in data_to_print:
        print(f'{key:25} {value}')
    
if teto_records['data']['records']['40l']['record'] is not None:
    print("\n")
    data_to_print = [
        ("", "40 Lines"),
        ("Time", datetime.timedelta(milliseconds=teto_records['data']['records']['40l']['record']['endcontext']['finalTime'])),
        ("Pieces", teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced']),
        ("Pieces per Second", teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced']/(teto_records['data']['records']['40l']['record']['endcontext']['finalTime']/1000)),
        ("Key presses", teto_records['data']['records']['40l']['record']['endcontext']['inputs']),
        ("Key presses per Piece", teto_records['data']['records']['40l']['record']['endcontext']['inputs']/(teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced'])),
        ("Key presses per Second", teto_records['data']['records']['40l']['record']['endcontext']['inputs']/(teto_records['data']['records']['40l']['record']['endcontext']['finalTime']/1000)),
        ("Finnese", f"{(teto_records['data']['records']['40l']['record']['endcontext']['finesse']['perfectpieces']/teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced']*100)}%, {teto_records['data']['records']['40l']['record']['endcontext']['finesse']['faults']} faults"),
        ("T-spins", teto_records['data']['records']['40l']['record']['endcontext']['tspins']),
        ("All clears", teto_records['data']['records']['40l']['record']['endcontext']['clears']['allclear']),
        ("Replay ID", teto_records['data']['records']['40l']['record']['replayid']),
        ("Timestamp", f"{datetime.datetime.fromisoformat(teto_records['data']['records']['40l']['record']['ts'][:-1]).strftime('%c')} ({datetime.datetime.now() - datetime.datetime.fromisoformat(teto_records['data']['records']['40l']['record']['ts'][:-1])} ago)")
    ]
    if teto_records['data']['records']['40l']['rank'] is not None:
        data_to_print.append(("Leaderboard standing", f"№{teto_records['data']['records']['40l']['rank']}"))
    for key, value in data_to_print:
        print(f'{key:25} {value}')

if teto_records['data']['records']['blitz']['record'] is not None:
    print("\n")
    data_to_print = [
        ("", "Blitz"),
        ("Score", locale.format_string('%.0f', teto_records['data']['records']['blitz']['record']['endcontext']['score'], True)),
        ("Score per Piece", teto_records['data']['records']['blitz']['record']['endcontext']['score']/teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']),
        ("Pieces", teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']),
        ("Pieces per Second", teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']/(teto_records['data']['records']['blitz']['record']['endcontext']['finalTime']/1000)),
        ("Key presses", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']),
        ("Key presses per Piece", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']/(teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced'])),
        ("Key presses per Second", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']/(teto_records['data']['records']['blitz']['record']['endcontext']['finalTime']/1000)),
        ("Replay ID", teto_records['data']['records']['blitz']['record']['replayid']),
        ("Level", teto_records['data']['records']['blitz']['record']['endcontext']['level']),
        ("Quads", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['quads']),
        ("T-spins", teto_records['data']['records']['blitz']['record']['endcontext']['tspins']),
        ("All clears", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['allclear']),
        ("Timestamp", f"{datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1]).strftime('%c')} ({datetime.datetime.now() - datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1])} ago)")
    ]
    if "finesse" in teto_records['data']['records']['blitz']['record']['endcontext']:
        data_to_print.append(("Finnese", f"{(teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['perfectpieces']/teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']*100)}%, {teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['faults']} faults"))
    if teto_records['data']['records']['blitz']['rank'] is not None:
        data_to_print.append(("Leaderboard standing", f"№{teto_records['data']['records']['blitz']['rank']}"))
    for key, value in data_to_print:
        print(f'{key:25} {value}')

if teto_records['data']['zen'] is not None:
    print("\n")
    data_to_print = [
        ("", "Zen"),
        ("Level", teto_records['data']['zen']['level']),
        ("Score", locale.format_string('%.0f', teto_records['data']['zen']['score'], True))
    ]

    for key, value in data_to_print:
        print(f'{key:25} {value}')
        