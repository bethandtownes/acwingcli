import sys
from colorama import Fore, Back, Style, init

def status(s, width = 100):
    sys.stdout.write('\r' + ' ' * 100)
    sys.stdout.write('\r' + Fore.YELLOW +Style.BRIGHT + '[Status] ' + s + Style.RESET_ALL)
    sys.stdout.flush()


def progress(s, width = 100):
    sys.stdout.write('\r' + ' ' * 100)
    sys.stdout.write('\r' + Fore.YELLOW +Style.BRIGHT + '[Progress] ' + s + Style.RESET_ALL)
    sys.stdout.flush()
