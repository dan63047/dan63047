import random, datetime, os
from string import Template

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(zero:datetime.datetime, dtfrom:datetime.datetime) -> str:
    if zero < dtfrom:
        tdelta = dtfrom - zero
        t = DeltaTemplate('-%H:%M:%S')
    else:
        tdelta = zero - dtfrom
        t = DeltaTemplate('%H:%M:%S')
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    hours += d["D"]*24
    d["H"] = '{:02,d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    return t.substitute(**d)

def count_bar_lentgh(min, max, currect, len):
    try:
        bar_offset = ((max - min) - (max - currect)) / (max - min) * len
    except ZeroDivisionError:
        bar_offset = 0
    return int(bar_offset)

def clear(): 
    _ = os.system('cls') if os.name == 'nt' else os.system('clear') 

def main_loop():
    randomes = 0
    randnum = None
    last_randnum = None
    same_as_last = 0
    l = 20
    same_as_last_max = 0
    array_of_counters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    start = datetime.datetime.now()
    need = True
    clear()
    print("\033[?25l")
    while need:
        try:
            last_randnum = randnum
            randnum = random.randint(0, 9)
            if last_randnum == randnum:
                same_as_last += 1
                if same_as_last > same_as_last_max:
                    same_as_last_max = same_as_last
            else:
                same_as_last = 0
            array_of_counters[randnum] += 1
            randomes += 1
            time_passed = strfdelta(datetime.datetime.now(), start)
            min_max_diff = max(array_of_counters) - min(array_of_counters)
            print("\033[H")
            print(f"Time passed: {time_passed}\nRandom numbers: {randomes:,d}\n")
            i = 0
            while i <= 9:
                bar_l = count_bar_lentgh(min(array_of_counters), max(array_of_counters), array_of_counters[i], l)
                print(f"{i}: {array_of_counters[i]:11,d} " + "█"*bar_l + " "*(l-bar_l))
                i += 1
            print(f"\nDifference between {array_of_counters.index(min(array_of_counters))} and {array_of_counters.index(max(array_of_counters))}: {min_max_diff:,d}     ")
            print(f"Same number in a row: {same_as_last:,d}, max: {same_as_last_max:,d}   ")
        except KeyboardInterrupt:
            need = False

if __name__ == "__main__":
    main_loop()
    print("\033[18H")