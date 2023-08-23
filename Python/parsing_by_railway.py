import requests, time, os
from bs4 import BeautifulSoup

def clear(): 
    _ = os.system('cls') if os.name == 'nt' else os.system('clear') 

def main_loop():
    site = requests.get("https://pass.rw.by/be/route/?from=%D0%9D%D1%8F%D1%81%D1%8F%D1%82%D0%B0&from_exp=2100076&from_esr=157103&to=%D0%9C%D1%96%D0%BD%D1%81%D0%BA+%D0%9F%D0%B0%D1%81%D0%B0%D0%B6%D1%8B%D1%80%D1%81%D0%BA%D1%96&to_exp=2100001&to_esr=140210&front_date=25+%D0%BA%D1%80%D0%B0%D1%81.+2023&date=2023-04-25")
    if site.ok:
        soup = BeautifulSoup(site.content, features="html.parser")
        table = soup.select("#sch-route > div.col-md-9.col-xs-12 > div.sch-le-wrap > div.sch-table.js-schSort.js-schedule > div.sch-table__body-wrap > div")
        entrys = list(table[0].children)
        while True:
            try:
                entrys.remove("\n")
            except ValueError:
                break
        entrys = entrys[:-1]
        first_entry_text = [str for str in entrys[0].stripped_strings]
        text_entrys = []
        for e in entrys:
            ent = [str for str in e.stripped_strings]
            if ent[0] == "Самы хуткі" or ent[0] == "Самы недарагі":
                ent.pop(0)
            if ent[11] == "Месцаў няма":
                text_entrys.append(ent[4] + " - " + ent[6] + ": " + ent[11])
            else:
                cutting_the_edge = ent[11:]
                cutting_the_edge.pop()
                variants = ""
                for i in cutting_the_edge:
                    if i == "BYN":
                        variants += i+", "
                    else:
                        variants += i+" "
                text_entrys.append(ent[4] + " - " + ent[6] + ": " + variants)
        train_name = first_entry_text[0] + " " + first_entry_text[1] + " " + first_entry_text[2]
        print("\033[H", time.ctime(), train_name)
        for i in text_entrys:
            print(i, "  ")
        
    else:
        print("\033[H", time.ctime(), site.status_code)
    time.sleep(60)

if __name__ == "__main__":
    clear()
    print("\033[?25l")
    try:
        while True:
            main_loop()
    except KeyboardInterrupt:
        print("\033[18H")