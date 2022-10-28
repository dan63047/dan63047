import requests, argparse, locale, json, datetime, math
locale.setlocale(locale.LC_ALL, ('en', 'UTF-8'))
parser = argparse.ArgumentParser(description='Insert nickname or id of player and get detalied stats into output')
parser.add_argument("nick", metavar="p", type=str, help="Nickname or id of player")
args = parser.parse_args()
nick = args.nick.lower()

def progressbar(start, end, current, length, start_text, end_text):
    bar = ""
    symbols = ("░", "▒", "▓", "█")
    states = 4*length - len(start_text) - len(end_text)
    length_left = length - len(start_text) - len(end_text) - 2
    full_bars = ((current - start) / (end - start)) * length_left
    d1 = full_bars
    bar += start_text + " "
    while full_bars >=1:
        bar += symbols[3]
        length_left -= 1
        full_bars -= 1
        if length_left == 0:
            break
    if full_bars > 0 and length_left > 0:
        bar += symbols[int(full_bars/len(symbols)-1)]
        length_left -= 1
    while length_left > 0:
        bar += " "
        length_left -= 1
    bar += " " + end_text
    return bar

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

if teto['data']['user']['gameswon'] == -1:
    gw = "???"
else:
    gw = teto['data']['user']['gameswon']

if teto['data']['user']['gamesplayed'] == -1:
    gp = "???"
else:
    gp = teto['data']['user']['gamesplayed']

if "friend_count" in teto['data']['user']:
    friends = teto['data']['user']['friend_count']
else:
    friends = "???"

if teto['data']['user']['supporter_tier'] > 0:
    supporter = f"Supporter tier {teto['data']['user']['supporter_tier']}"
else:
    supporter = "Not a supporter"

level = (teto['data']['user']['xp']/500)**0.6+(teto['data']['user']['xp']/(5000+(max(0, teto['data']['user']['xp']-4*10**6)/5000)))+1
data_to_print = [
    (f"{request.status_code} {request.reason}", data_from.strftime('%c')),
    ("", ""),
    ("Nickname", teto['data']['user']['username']),
    ("Country", teto['data']['user']['country']),
    ("Registred", reg),
    ("Time played", tp),
    (teto['data']['user']['role'], supporter),
    (f"{gw} / {gp} Games", f"{friends} Friends"),
    (f'{progressbar(int(level), int(level)+1, level, 80, locale.format_string("%.0f", teto["data"]["user"]["xp"], True)+" XP", f"lvl {int(level)}")}', "")
]
for key, value in data_to_print:
    print(f'{key:25} {value}')

if "distinguishment" in teto["data"]["user"]:
    print("\n")
    print(f"{nothing:25} Distinguishment")
    data_to_print = [
        ("Header", teto['data']['user']['distinguishment']["header"]),
        ("Footer", teto['data']['user']['distinguishment']['footer']),
        ("Type", teto['data']['user']['distinguishment']['type']),
        ("Detali", teto['data']['user']['distinguishment']['detail'])
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
        else:
            rank = f"Probably around {teto['data']['user']['league']['percentile_rank'].upper()} (top {(teto['data']['user']['league']['percentile']*100):.2f}%)"
            gliko = f"{teto['data']['user']['league']['glicko']:.2f}±{teto['data']['user']['league']['rd']:.2f} GLICKO"
        standing = "No standing"
    else:
        rank = teto["data"]["user"]["league"]["rank"].upper()
        rank = progressbar(teto['data']['user']['league']['prev_at'], teto['data']['user']['league']['next_at'], teto['data']['user']['league']['standing'], 80, f"{rank} (top {(teto['data']['user']['league']['percentile']*100):.2f}%)", f"{teto['data']['user']['league']['rating']:.2f} TR")
        gliko = f"{teto['data']['user']['league']['glicko']:.2f}±{teto['data']['user']['league']['rd']:.2f} GLICKO"
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
        (rank, ""),
        (gliko, standing),
        (f"{teto['data']['user']['league']['gameswon']} / {teto['data']['user']['league']['gamesplayed']} Games", f"{teto['data']['user']['league']['gameswon']/teto['data']['user']['league']['gamesplayed']*100:.2f}% WR"),
        (f"{apm} APM, {pps} PPS, {vs} VS", ""),
        ("", ""),
        ("", "For Nerds"),
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
        ("Key presses per Second", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']/(teto_records['data']['records']['blitz']['record']['endcontext']['finalTime']/1000))   
    ]
    if "finesse" in teto_records['data']['records']['blitz']['record']['endcontext']:
        data_to_print.append(("Finnese", f"{(teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['perfectpieces']/teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']*100)}%, {teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['faults']} faults"))
    data_to_print.append(("Level", teto_records['data']['records']['blitz']['record']['endcontext']['level']))
    data_to_print.append(("Quads", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['quads']))
    data_to_print.append(("T-spins", teto_records['data']['records']['blitz']['record']['endcontext']['tspins']))
    data_to_print.append(("All clears", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['allclear']))
    data_to_print.append(("Replay ID", teto_records['data']['records']['blitz']['record']['replayid']))
    data_to_print.append(("Timestamp", f"{datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1]).strftime('%c')} ({datetime.datetime.now() - datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1])} ago)"))
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

if len(teto["data"]["user"]["connections"]) > 0:
    print("\n")
    data_to_print = [("", "Connections")]
    if "discord" in teto['data']['user']['connections']:
        data_to_print.append(('Discord', f"{teto['data']['user']['connections']['discord']['username']}"))
    
    for key, value in data_to_print:
        print(f'{key:25} {value}')
