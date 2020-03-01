import acwingcli
import sys
import os
import argparse

# from multiprocessing import Process
from time import sleep
import subprocess
from colorama import Fore, Back, Style, init

from .readfile import get_string_from_file
from .login import submit, runcode, get_submission, display_submission_result
from .persistent_session import runserver
from .update import problem_list

import acwingcli.problembook as problembook
import acwingcli.update as update
import os

ap = argparse.ArgumentParser()
ap.add_argument('-s', '--submit', help = 'submit file')
ap.add_argument('-r', '--run', help = 'run code')
ap.add_argument('-g', '--get', help = 'get problem')
ap.add_argument('-c', '--serversubmit', help = 'run code')
ap.add_argument('-initserver', action = 'store_true')
ap.add_argument('-updateproblems', action = 'store_true')
ap.add_argument('-runserver', action = 'store_true')

from multiprocessing.connection import Client
import json
import acwingcli.config as config
import threading

def make_submission_url(url):
    return url.replace('content', 'content/submission')


def camelize(words):
    return ' '.join(list(map(lambda x : x[0].capitalize() + x[1:].lower(), words.split('_'))))


def has_valid_testcase(response: dict):
    if 'testcase_input' in response.keys() and 'testcase_output' in response.keys() and \
       min(len(response['testcase_input']), len(response['testcase_output'])) >= 1:
        return True
    else:
        return False
    
def display_judge_status(response : dict, problem_id:str):
    url = config.problem_cache[eval(problem_id)]['submission_link']
    if response['status'] == 'ACCEPTED':
        sys.stdout.write(Fore.GREEN + Style.BRIGHT + '\r[✓] Judge Status: Accepted\n' + Style.RESET_ALL)
        sys.stdout.flush()
        display_submission_result(response, url)
        return True
    elif response['status'] in {'WRONG_ANSWER', 'MEMORY_LIMITED_EXCEEDED', 'TIME_LIMIT_EXCEEDED', 'RUNTIME_ERROR', 'COMPILE_ERROR'}:
        sys.stdout.write(Fore.RED + Style.BRIGHT + '\r[✗] Judge Status: ' + camelize(response['status']) + '\n' + Style.RESET_ALL)
        sys.stdout.flush()
        display_submission_result(response, url)
        if has_valid_testcase(response):
            update.testcases(problem_id, response['testcase_input'], response['testcase_output'])
        return True
    else:
        sys.stdout.write(Fore.YELLOW + Style.BRIGHT + '\r[-] Judge Status: ' + response['status'] + Style.RESET_ALL)
        sys.stdout.flush()
        return False

    

def display_debug_message(response):
    print('local_debug_message: %s' % response['local_debug_message'])
        
    
def serversubmit(problem_id, code):
    url = config.problem_cache[eval(problem_id)]['link']
    address = ('localhost', 6001)
    conn = Client(address, authkey=b'1234')
    submission_data = 'send' + '$$' + url + '$$' + code
    conn.send(submission_data)
    while True:
        early_exit = False
        if conn.poll(20) == True:
            response = json.loads(conn.recv())
            if 'local_debug_message' in response.keys():
                display_debug_message(response)
            elif 'status' in response.keys():
                early_exit = display_judge_status(response, problem_id)
        else:
            sys.stdout.write(Fore.GREEN + Style.BRIGHT + '\r[✓] Judge Status: Accepted\n' + Style.RESET_ALL)
            sys.stdout.flush()
        if early_exit == True:
            break
    conn.close()




from acwingcli.utils import *
    
def main():
    args = vars(ap.parse_args())
    if not args.get('submit') is None:
        code = get_string_from_file(args['submit']).decode('utf-8')
        submit('https://www.acwing.com/problem/content/description/1/', code)
    elif not args.get('run') is None:
        code = get_string_from_file(args['run']).decode('utf-8')
        runcode('https://www.acwing.com/problem/content/description/1/', code, '3 4\n')
    elif not args.get('serversubmit') is None:
        file_abspath = os.path.abspath(args['serversubmit'])
        code = get_string_from_file(file_abspath).decode('utf-8')
        problem_id = get_problem_id_from_file(args['serversubmit'])
        serversubmit(problem_id, code)
    elif not args.get('initserver') is None and args['initserver'] == True:
        p = subprocess.Popen(['acwingcli', '-runserver'], stdout=subprocess.PIPE)
    elif not args.get('get') is None:
        a = 'a'
        problembook.get_problem(args['get'])
    elif not args.get('updateproblems') is None and args['updateproblems'] == True:
        problem_list()
        
    elif not args.get('runserver') is None:
        runserver()


if __name__ == '__main__':
    main()
