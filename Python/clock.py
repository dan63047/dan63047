import datetime
import os


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

need = True
while need:
    try:
        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")
        print(f" {now}", end="\r")
    except KeyboardInterrupt:
        need = False
        print("\n")
