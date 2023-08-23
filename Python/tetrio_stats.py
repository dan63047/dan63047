import requests
import argparse
import locale
import json
import datetime
import math
# locale.setlocale(locale.LC_ALL, ('en', 'UTF-8'))
parser = argparse.ArgumentParser(
    description='Insert nickname or id of player and get detalied stats into output')
parser.add_argument("nick", metavar="p", type=str,
                    help="Nickname or id of player")
args = parser.parse_args()
nick = args.nick.lower()

PROGRESSBAR_LENGTH = 80


def progressbar(start, end, current, length, start_text, end_text):
    bar = ""
    symbols = ("░", "▒", "▓", "█")
    states = 4*length - len(start_text) - len(end_text)
    length_left = length - len(start_text) - len(end_text) - 2
    full_bars = ((current - start) / (end - start)) * length_left
    d1 = full_bars
    bar += f"{start_text} "
    while full_bars >= 1:
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
    bar += f" {end_text}"
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
    reg = f"{datetime.datetime.fromisoformat(teto['data']['user']['ts'][:-1]).strftime('%c')} ({datetime.datetime.utcnow() - datetime.datetime.fromisoformat(teto['data']['user']['ts'][:-1])} ago)"
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

level = (teto['data']['user']['xp']/500)**0.6+(teto['data']['user']
                                               ['xp']/(5000+(max(0, teto['data']['user']['xp']-4*10**6)/5000)))+1
data_to_print = [
    (f"{request.status_code} {request.reason}", data_from.strftime('%c')),
    ("", ""),
    ("Nickname", teto['data']['user']['username']),
    ("Country", teto['data']['user']['country']),
    ("Registred", reg),
    ("Time played", tp),
    (teto['data']['user']['role'], supporter),
    (f"{gw} / {gp} Games", f"{friends} Friends"),
    (f'{progressbar(int(level), int(level)+1, level, PROGRESSBAR_LENGTH, locale.format_string("%.0f", teto["data"]["user"]["xp"], True)+" XP", f"lvl {int(level)}")}', "")
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
            print(
                f"{datetime.datetime.fromisoformat(badge['ts'][:-1]).strftime('%c'):25} {badge['label']}")

if teto["data"]["user"]["league"]['gamesplayed'] > 0:
    print("\n")
    if teto["data"]["user"]["league"]["rank"] == "z":
        if teto['data']['user']['league']['percentile_rank'] == "z":
            rank = "Played less than 10 mathes"
            gliko = f"{10 - teto['data']['user']['league']['gamesplayed']} matches until being rated"
            bestrank = "?"
        else:
            rank = f"Probably around {teto['data']['user']['league']['percentile_rank'].upper()} (top {(teto['data']['user']['league']['percentile']*100):.2f}%)  {teto['data']['user']['league']['rating']:.2f} TR"
            gliko = f"{teto['data']['user']['league']['glicko']:.2f}±{teto['data']['user']['league']['rd']:.2f} GLICKO"
            bestrank = teto['data']['user']['league']['bestrank'].upper()
        standing = "No standing"
    else:
        rank = teto["data"]["user"]["league"]["rank"].upper()
        rank = progressbar(teto['data']['user']['league']['prev_at'], teto['data']['user']['league']['next_at'], teto['data']['user']['league']['standing'],
                           PROGRESSBAR_LENGTH, f"{rank} (top {(teto['data']['user']['league']['percentile']*100):.2f}%)", f"{teto['data']['user']['league']['rating']:.2f} TR")
        gliko = f"{teto['data']['user']['league']['glicko']:.2f}±{teto['data']['user']['league']['rd']:.2f} GLICKO"
        if teto['data']['user']['country'] is not None:
            standing = f"№{teto['data']['user']['league']['standing']} (№{teto['data']['user']['league']['standing_local']} in {teto['data']['user']['country']})"
        else:
            standing = f"№{teto['data']['user']['league']['standing']}"
        bestrank = teto['data']['user']['league']['bestrank'].upper()

    apm = teto['data']['user']['league']['apm']
    pps = teto['data']['user']['league']['pps']
    vs = teto['data']['user']['league']['vs']
    if vs is None:
        vs = 0
    app = apm/(pps*60)
    vsapm = vs/apm
    vspps = vs/pps
    dss = (vs/100)-(apm/60)
    dsp = ((vs/100)-(apm/60))/pps
    cheese = (dsp*150) + (((vs/apm)-2)*50) + (0.6-app)*125
    gbe = ((app*dss)/pps)*2
    nyaapp = app - 5 * math.tan(math.radians((cheese/-30)+1))
    area = apm*1 + pps*45 + vs*0.444 + app*185 + dss*175 + dsp*450 + gbe*315
    srarea = (apm * 0) + (pps * 135) + (vs * 0) + (app * 290) + (dss * 0) + (dsp * 700) + (gbe * 0)
    statrank = 11.2 * math.atan((srarea-93)/130)+1
    if statrank <= 0:
        statrank = 0.001
    if teto['data']['user']['league']['percentile_rank'] == "z":
        esttr_atr = "0"
    else:
        estglicko = (4.0867 * srarea + 186.68)
        temp = (1500-estglicko)*3.14159
        temp2 = ((15.9056943314 * (teto['data']['user']['league']['rd']**2) + 3527584.25978)**0.5)
        temp3 = 1+(10**(temp/temp2))
        esttr = 25000/temp3
        atr = esttr - teto['data']['user']['league']['rating']
        esttr_atr = f"{esttr} ({atr:+f})"
    nmapm = ((apm/srarea)/((0.069*1.0017**((statrank**5)/4700))+statrank/360))-1
    nmpps = ((pps/srarea)/(0.0084264 *
                        (2.14**(-2*(statrank/2.7+1.03)))-statrank/5750+0.0067))-1
    nmvs = ((vs/srarea)/(0.1333*1.0021 **
                      (((statrank**7)*(statrank/16.5))/1400000)+statrank/133))-1
    nmapp = (app/(0.1368803292*1.0024**((statrank**5)/2800)+statrank/54))-1
    nmdss = (dss/(0.01436466667*(4.1)**((statrank-9.6)/2.9)+statrank/140+0.01))-1
    nmdsp = (dsp/(0.02136327583*(14**((statrank-14.75)/3.9))+statrank/152 + 0.022))-1
    nmgbe = (gbe/(statrank/350+0.005948424455*3.8**((statrank-6.1)/4)+0.006))-1
    nmvsapm = (vsapm/(-(((statrank-16)/36)**2)+2.133))-1
    opener = ((nmapm+nmpps*0.75+nmvsapm*-10+nmapp*0.75+nmdsp*-0.25)/3.5)+0.5
    plonk = ((nmgbe+nmapp+nmdsp*0.75+nmpps*-1)/2.73)+0.5
    stride = ((nmapm*-0.25+nmpps+nmapp*-2+nmdsp*-0.5)*0.79)+0.5
    infds = ((nmdsp+nmapp*-0.75+nmapm*0.5+nmvsapm*1.5+nmpps*0.5)*0.9)+0.5

    data_to_print = [
        ("", "Tetra League"),
        (rank, ""),
        (gliko, standing),
        (f"{teto['data']['user']['league']['gameswon']} / {teto['data']['user']['league']['gamesplayed']} Games",
         f"{teto['data']['user']['league']['gameswon']/teto['data']['user']['league']['gamesplayed']*100:.2f}% WR"),
        (f"{apm} APM  {pps} PPS  {vs} VS    Top Rank: {bestrank}", ""),
        ("", ""),
        ("", "For Nerds"),
        ("Attack Per Piece", app),
        ("VS/APM", vsapm),
        ("VS/PPS", vspps),
        ("DS/Second", dss),
        ("DS/Piece", dsp),
        ("APP+DS/Piece", dsp + app),
        ("Cheese Index", cheese),
        ("Garbage Efficiency", gbe),
        ("Area", area),
        ("NyaAPP", nyaapp),
        ("Est. TR", esttr_atr),
        ("", ""),
        ("", "Playstyle"),
        (progressbar(0, 1, opener, PROGRESSBAR_LENGTH,
         "Opener", f'{opener:7.2%}'), ""),
        (progressbar(0, 1, plonk, PROGRESSBAR_LENGTH,
         "Plonk ", f'{plonk:7.2%}'), ""),
        (progressbar(0, 1, stride, PROGRESSBAR_LENGTH,
         "Stride", f'{stride:7.2%}'), ""),
        (progressbar(0, 1, infds, PROGRESSBAR_LENGTH,
         "Inf ds", f'{infds:7.2%}'), "")
    ]

    for key, value in data_to_print:
        print(f'{key:25} {value}')

if teto_records['data']['records']['40l']['record'] is not None:
    print("\n")
    data_to_print = [
        ("", "40 Lines"),
        ("Time", datetime.timedelta(
            milliseconds=teto_records['data']['records']['40l']['record']['endcontext']['finalTime'])),
        ("Pieces", teto_records['data']['records']['40l']
         ['record']['endcontext']['piecesplaced']),
        ("Pieces per Second", teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced']/(
            teto_records['data']['records']['40l']['record']['endcontext']['finalTime']/1000)),
        ("Key presses", teto_records['data']['records']
         ['40l']['record']['endcontext']['inputs']),
        ("Key presses per Piece", teto_records['data']['records']['40l']['record']['endcontext']['inputs']/(
            teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced'])),
        ("Key presses per Second", teto_records['data']['records']['40l']['record']['endcontext']['inputs']/(
            teto_records['data']['records']['40l']['record']['endcontext']['finalTime']/1000)),
        ("Finnese", f"{(teto_records['data']['records']['40l']['record']['endcontext']['finesse']['perfectpieces']/teto_records['data']['records']['40l']['record']['endcontext']['piecesplaced']*100)}%, {teto_records['data']['records']['40l']['record']['endcontext']['finesse']['faults']} faults"),
        ("T-spins", teto_records['data']['records']
         ['40l']['record']['endcontext']['tspins']),
        ("Quads", teto_records['data']['records']['40l']
         ['record']['endcontext']['clears']['quads']),
        ("All clears", teto_records['data']['records']['40l']
         ['record']['endcontext']['clears']['allclear']),
        ("Replay ID", teto_records['data']
         ['records']['40l']['record']['replayid']),
        ("Timestamp",
         f"{datetime.datetime.fromisoformat(teto_records['data']['records']['40l']['record']['ts'][:-1]).strftime('%c')} ({datetime.datetime.utcnow() - datetime.datetime.fromisoformat(teto_records['data']['records']['40l']['record']['ts'][:-1])} ago)")
    ]
    if teto_records['data']['records']['40l']['rank'] is not None:
        data_to_print.append(
            ("Leaderboard standing", f"№{teto_records['data']['records']['40l']['rank']}"))
    for key, value in data_to_print:
        print(f'{key:25} {value}')

if teto_records['data']['records']['blitz']['record'] is not None:
    print("\n")
    data_to_print = [
        ("", "Blitz"),
        ("Score", locale.format_string(
            '%.0f', teto_records['data']['records']['blitz']['record']['endcontext']['score'], True)),
        ("Score per Piece", teto_records['data']['records']['blitz']['record']['endcontext']
         ['score']/teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']),
        ("Pieces", teto_records['data']['records']['blitz']
         ['record']['endcontext']['piecesplaced']),
        ("Pieces per Second", teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']/(
            teto_records['data']['records']['blitz']['record']['endcontext']['finalTime']/1000)),
        ("Key presses", teto_records['data']['records']
         ['blitz']['record']['endcontext']['inputs']),
        ("Key presses per Piece", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']/(
            teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced'])),
        ("Key presses per Second", teto_records['data']['records']['blitz']['record']['endcontext']['inputs']/(
            teto_records['data']['records']['blitz']['record']['endcontext']['finalTime']/1000))
    ]
    if "finesse" in teto_records['data']['records']['blitz']['record']['endcontext']:
        data_to_print.append(
            ("Finnese", f"{(teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['perfectpieces']/teto_records['data']['records']['blitz']['record']['endcontext']['piecesplaced']*100)}%, {teto_records['data']['records']['blitz']['record']['endcontext']['finesse']['faults']} faults"))
    data_to_print.append(
        ("Level", teto_records['data']['records']['blitz']['record']['endcontext']['level']))
    data_to_print.append(
        ("Quads", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['quads']))
    data_to_print.append(
        ("T-spins", teto_records['data']['records']['blitz']['record']['endcontext']['tspins']))
    data_to_print.append(
        ("All clears", teto_records['data']['records']['blitz']['record']['endcontext']['clears']['allclear']))
    data_to_print.append(
        ("Replay ID", teto_records['data']['records']['blitz']['record']['replayid']))
    data_to_print.append(
        ("Timestamp", f"{datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1]).strftime('%c')} ({datetime.datetime.utcnow() - datetime.datetime.fromisoformat(teto_records['data']['records']['blitz']['record']['ts'][:-1])} ago)"))
    if teto_records['data']['records']['blitz']['rank'] is not None:
        data_to_print.append(
            ("Leaderboard standing", f"№{teto_records['data']['records']['blitz']['rank']}"))
    for key, value in data_to_print:
        print(f'{key:25} {value}')

if teto_records['data']['zen'] is not None:
    print("\n")
    data_to_print = [
        ("", "Zen"),
        (f"Level {teto_records['data']['zen']['level']}", f"Score {locale.format_string('%.0f', teto_records['data']['zen']['score'], True)}")
    ]

    for key, value in data_to_print:
        print(f'{key:25} {value}')

if len(teto["data"]["user"]["connections"]) > 0:
    print("\n")
    data_to_print = [("", "Connections")]
    if "discord" in teto['data']['user']['connections']:
        data_to_print.append(
            ('Discord', f"{teto['data']['user']['connections']['discord']['username']}"))

    for key, value in data_to_print:
        print(f'{key:25} {value}')
