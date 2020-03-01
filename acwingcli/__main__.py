import acwingcli
import sys
import os
import argparse

# from multiprocessing import Process
from time import sleep
import subprocess
from colorama import Fore, Back, Style, init

from .readfile import get_string_from_file
from .login import submit, get_submission, display_submission_result
from .persistent_session import runserver
from .update import problem_list

import acwingcli.problembook as problembook
import acwingcli.update as update
from acwingcli.utils import *
import os

ap = argparse.ArgumentParser()
ap.add_argument('-s', '--submit', help = 'submit file')
ap.add_argument('-f', '--files', nargs = '+',  help = 'submit file')
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

import acwingcli.commandline_writer as cmdwrite

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


def display_run_status(response:dict, problem_id:str, test_data:str, expected_answer:str):
    if response['status'] == 'FINISHED':
        if response.get('stdout', '').strip() == expected_answer.strip():
            cmdwrite.judge_status('[✓] Judge Status: ' + 'Correct'  + ' (' + camelize(response['status']) + ')',
                                  linebreak = True, color = Fore.GREEN)
            cmdwrite.judge_status('[✓] Testcase: ' + test_data.strip(), linebreak = True, color = Fore.GREEN)
            cmdwrite.judge_status('[✓] Answer: ' + response.get('stdout', 'N/A').strip(), linebreak = True, color = Fore.GREEN)
            cmdwrite.judge_status('[✓] Expected answer: ' + expected_answer.strip(), linebreak = True, color = Fore.GREEN)
        else:
            cmdwrite.judge_status('[✗] Judge Status: ' + 'Wrong'  + ' (' + camelize(response['status']) + ')',
                                  linebreak = True, color = Fore.RED)
            cmdwrite.judge_status('[✗] Testcase: ' + test_data.strip(), linebreak = True, color = Fore.RED)
            cmdwrite.judge_status('[✗] Answer: ' + response.get('stdout', 'N/A').strip(), linebreak = True, color = Fore.RED)
            cmdwrite.judge_status('[✗] Expected answer: ' + expected_answer.strip(), linebreak = True, color = Fore.RED)
    elif response['status'] == 'COMPILE_ERROR':
        sys.stdout.write(Fore.RED + Style.BRIGHT + '\r[✗] Judge Status: ' + camelize(response['status']) + '\n' + Style.RESET_ALL)
        sys.stdout.flush()
        cmdwrite.judge_status('[✗] Testcase: ' + test_data.strip(), linebreak = True, color = Fore.RED)
        cmdwrite.judge_status('[✗] Expected answer: ' + expected_answer.strip(), linebreak = True, color = Fore.RED)
        cmdwrite.judge_status(response.get('compilation_log', '').strip(), linebreak = True, color = Fore.RED)
    elif response['status'] in {'MEMORY_LIMITED_EXCEEDED', 'TIME_LIMIT_EXCEEDED', 'RUNTIME_ERROR'}:
        sys.stdout.write(Fore.RED + Style.BRIGHT + '\r[✗] Judge Status: ' + camelize(response['status']) + '\n' + Style.RESET_ALL)
        sys.stdout.flush()
        cmdwrite.judge_status('[✗] Testcase: ' + test_data.strip(), linebreak = True, color = Fore.RED)
        cmdwrite.judge_status('[✗] Answer: ' + response.get('stdout', 'N/A').strip(), linebreak = True, color = Fore.RED)
        cmdwrite.judge_status('[✗] Expected answer: ' + expected_answer.strip(), linebreak = True, color = Fore.RED)
        cmdwrite.judge_status('[✗] Stderr: ' + response.get('stderr', 'N/A').strip(), linebreak = True, color = Fore.RED)
    else:
        sys.stdout.write(Fore.YELLOW + Style.BRIGHT + '\r[-] Judge Status: ' + response['status'] + Style.RESET_ALL)
        sys.stdout.flush()
        return False
    return True


def log_run_status(response:dict, problem_id:str, test_data:str, expected_answer:str):
    if response['status'] == 'FINISHED':
        if response.get('stdout', '').strip() == expected_answer.strip():
            return '\n'.join([Fore.GREEN + Style.BRIGHT,
                              '[✓] Judge Status: Correct ({})'.format(camelize(response['status'])),
                              '[✓] Testcase: {}'.format(test_data.strip()),
                              '[✓] Answer: {}'.format(response.get('stdout', 'N/A').strip()),
                              '[✓] Expected: {}'.format(expected_answer.strip()),
                              '[✓] StdErr: {}'.format(response.get('stderr', 'N/A').strip())]) + Style.RESET_ALL
        else:
            return '\n'.join([Fore.RED + Style.BRIGHT,
                              '[✗] Judge Status: Wrong ({})'.format(camelize(response['status'])),
                              '[✗] Testcase: {}'.format(test_data.strip()),
                              '[✗] Answer: {}'.format(response.get('stdout', 'N/A').strip()),
                              '[✗] Expected: {}'.format(expected_answer.strip()),
                              '[✗] StdErr: {}'.format(response.get('stderr', 'N/A').strip())]) + Style.RESET_ALL
    elif response['status'] == 'COMPILE_ERROR':
        with early_terminate.get_lock():
            early_terminate.value = True
        return '\n'.join([Fore.RED + Style.BRIGHT,
                          '[✗] Judge Status: {}'.format(camelize(response['status'])),
                          '[✗] Testcase: {}'.format(test_data.strip()),
                          '[✗] Expected: {}'.format(expected_answer.strip()),
                          '[✗] {}'.format(response.get('compilation_log', '').strip())]) + Style.RESET_ALL
    elif response['status'] in {'MEMORY_LIMITED_EXCEEDED', 'TIME_LIMIT_EXCEEDED', 'RUNTIME_ERROR'}:
        return '\n'.join([Fore.RED + Style.BRIGHT,
                          '[✗] Judge Status: {}'.format(camelize(response['status'])),
                          '[✗] Testcase: {}'.format(test_data.strip()),
                          '[✗] Answer: {}'.format(response.get('stdout', 'N/A').strip()),
                          '[✗] Expected: {}'.format(expected_answer.strip()),
                          '[✗] StdErr: {}'.format(response.get('stderr', 'N/A').strip())]) + Style.RESET_ALL
    else:
        return 'UNKNOWN STATUS'
    
def display_debug_message(response):
    print('local_debug_message: %s' % response['local_debug_message'])


from .login import prepare_session, make_runcode_header, trait_finished_running

import websocket
from .headers import socket_header


def runcode(problem_id, code, input_data, output_data):
    if early_terminate.value == True:
        return    
    try:
        s, cook = prepare_session()
        url = config.problem_cache[eval(problem_id)]['link']
        ws = websocket.create_connection('wss://www.acwing.com/wss/chat/',
                                         header = socket_header,
                                         cookie = cook)
        ws.settimeout(20)
        ws.send(json.dumps(make_runcode_header(url, code, input_data)))
        try:
            while True:
                message = ws.recv()
                if trait_finished_running(message) != None:
                    ws.close()
                    with finished_cases.get_lock():
                        finished_cases.value += 1
                        cmdwrite.progress(str(finished_cases.value) + '/' + str(total_cases))
                        return log_run_status(json.loads(message), problem_id, input_data, output_data)
        except:
            pass
        ws.close()
    except Exception as e:
        raise(Exception(e.message))
    
def serverrun_single(problem_id, code, input_data, output_data):
    url = config.problem_cache[eval(problem_id)]['link']
    address = ('localhost', 6001)
    conn = Client(address, authkey=b'1234')
    local_server_message = {'activity' : 'run',
                            'url' : url,
                            'code' : code,
                            'input_data' : input_data}    
    conn.send(json.dumps(local_server_message))
    while True:
        early_exit = False
        if conn.poll(20) == True:
            response = json.loads(conn.recv())
            if 'local_debug_message' in response.keys():
                display_debug_message(response)
            elif 'status' in response.keys():
                early_exit = display_run_status(response, problem_id, input_data, output_data)
        else:
            sys.stdout.write(Fore.GREEN + Style.BRIGHT + 'TIME OUT' + Style.RESET_ALL)
            sys.stdout.flush()
        if early_exit == True:
            break
    conn.close()

    

def serversubmit(problem_id, code):
    url = config.problem_cache[eval(problem_id)]['link']
    address = ('localhost', 6001)
    conn = Client(address, authkey=b'1234')
    local_server_message = {'activity' : 'send',
                            'url' : url,
                            'code' : code}
    conn.send(json.dumps(local_server_message))
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

from multiprocessing import Pool, TimeoutError, Lock, Value

def global_context(lock_, total_cases_, finished_cases_, early_terminate_):
    global lock
    global total_cases
    global finished_cases
    global early_terminate
    lock = lock_
    total_cases = total_cases_
    finished_cases = finished_cases_
    early_terminate = early_terminate_
    

def main():
    args = vars(ap.parse_args())
    if not args.get('submit') is None:
        code = get_string_from_file(args['submit']).decode('utf-8')
        submit('https://www.acwing.com/problem/content/description/1/', code)
    elif not args.get('run') is None:
        file_abspath = os.path.abspath(args['run'])
        code = get_string_from_file(file_abspath).decode('utf-8')
        problem_id = get_problem_id_from_file(args['run'])
        if not args.get('files') is None:
            N = len(args.get('files'))
            l = Lock()
            total_cases = N
            finished_cases = Value('i', 0)
            early_terminate = Value('i', 0)
            all_samples = list(map(lambda f : [get_string_from_file(f).decode('utf-8'),
                                               get_string_from_file(f.replace('in', 'out')).decode('utf-8')],
                                   args['files']))
            funcall_args = [(problem_id, code, sample_in, sample_out,) for sample_in, sample_out in all_samples]
            with Pool(min(N, 5), initializer = global_context, initargs = (l, total_cases, finished_cases, early_terminate)) as pool:
                try:
                    exec_result = pool.starmap(runcode, funcall_args)
                    for r in exec_result:
                        print(r)
                except Exception as e:
                    print(e.message)
                    pool.close()
                    pool.terminate()
                    del pool
                finally:
                    pool.close()
                    pool.terminate()
                    del pool
    elif not args.get('serversubmit') is None:
        file_abspath = os.path.abspath(args['serversubmit'])
        code = get_string_from_file(file_abspath).decode('utf-8')
        problem_id = get_problem_id_from_file(args['serversubmit'])
        serversubmit(problem_id, code)
    elif not args.get('initserver') is None and args['initserver'] == True:
        p = subprocess.Popen(['acwingcli', '-runserver'], stdout=subprocess.PIPE)
    elif not args.get('get') is None:
        problembook.get_problem(args['get'])
    elif not args.get('updateproblems') is None and args['updateproblems'] == True:
        problem_list()
    elif not args.get('runserver') is None:
        runserver()


if __name__ == '__main__':
    main()
