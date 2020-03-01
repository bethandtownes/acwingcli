import sys
from colorama import Fore, Back, Style, init

def status(s, width = 100):
    sys.stdout.write('\r' + ' ' * width)
    sys.stdout.write('\r' + Fore.YELLOW +Style.BRIGHT + '[Status] ' + s + Style.RESET_ALL)
    sys.stdout.flush()

def error(s, width = 100):
    sys.stdout.write('\r' + ' ' * width)
    sys.stdout.write('\r' + Fore.RED +Style.BRIGHT + '[Error] ' + s + Style.RESET_ALL)
    sys.stdout.flush()    


def progress(s, width = 100):
    sys.stdout.write('\r' + ' ' * width)
    sys.stdout.write('\r' + Fore.YELLOW +Style.BRIGHT + '[Progress] ' + s + Style.RESET_ALL)
    sys.stdout.flush()


def judge_status(s:str, width = 100, color = Fore.YELLOW, style = Style.BRIGHT, linebreak = False):
    sys.stdout.write('\r' + ' ' * width)
    sys.stdout.write('\r' + color + style + s + Style.RESET_ALL)
    sys.stdout.flush()
    if linebreak == True:
        sys.stdout.write('\n')
        
            
def log_judge_status(s:str, color = Fore.YELLOW, style = Style.BRIGHT, linebreak = False):
    log = color + style + s + Style.RESET_ALL
    if linebreak == True:
        log += '\n'
    return log
