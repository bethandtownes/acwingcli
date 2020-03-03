import requests
from bs4 import BeautifulSoup
import json
import websocket
import asyncio
import time 
import re
import http.cookiejar
from typing import Mapping, Optional, List
import pickle
from colorama import Fore, Back, Style, init
import os
import sys
import curses
import copy
import getpass


from .headers import socket_header, socket_url, submission_result_header, base_header, submit_code_data, headers

def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

login_data = {'csrfmiddlewaretoken': 'TODO',
              'username' : '',
              'password' : '',
              'remember_me' : 'on'}

BASE_URL = 'https://www.acwing.com'


def prepare_session(path_cookie = None):
    if path_cookie is None:
        import acwingcli.config
        path_cookie = acwingcli.config.path_cookie
    s = requests.session()
    need_to_update_cookie = False
    if os.path.exists(path_cookie):
        with open(path_cookie, 'rb') as f:
            ck = pickle.load(f)
            for cj in ck:
                if cj.is_expired():
                    print("[Cookie Expired]")
                    need_to_update_cookies = True
                    break
        if need_to_update_cookie == False:
            s.cookies.update(ck)
            csrftoken = s.cookies.values()[0]
            sessionid = s.cookies.values()[1]
            cook = 'csrftoken=' + csrftoken + '; ' + 'sessionid=' + sessionid
            return (s, cook)
    else:
        url = 'https://www.acwing.com/'
        print()
        username = str(input('[Login] Enter your Acwing username:'))
        password = str(getpass.getpass(prompt = '[Login] Enter your Acwing password:'))
        response = BeautifulSoup(s.get(url).content, 'html5lib')
        login = copy.deepcopy(login_data)
        login['username'] = username
        login['password'] = password
        login['csrfmiddlewaretoken'] = response.find('input', attrs = {'name' : 'csrfmiddlewaretoken'})['value']
        header = copy.deepcopy(headers)
        a = s.post('https://www.acwing.com/user/account/signin/', data = login, headers = header)
        token = a.cookies['csrftoken']
        cook = 'csrftoken=' + a.cookies['csrftoken'] + '; ' + 'sessionid=' + a.cookies['sessionid']
        with open(path_cookie, 'wb') as f:
            pickle.dump(a.cookies, f)
        return (s, cook)

    if need_to_update_cookie == True:
        url = 'https://www.acwing.com/'
        r = s.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        token = soup.find('input', attrs = {'name' : 'csrfmiddlewaretoken'})['value']
        login_data['csrfmiddlewaretoken'] = token
        headers['X-CSRFToken'] = token
        headers['Cookie'] = 'csrftoken=' + token
        a = s.post('https://www.acwing.com/user/account/signin/', data = login_data, headers = headers)
        cook = 'csrftoken=' + a.cookies['csrftoken'] + '; ' + 'sessionid=' + a.cookies['sessionid']
        with open(path.cookie, 'wb') as f:
            pickle.dump(a.cookies, f)
            print('wrote cookies')
            print(a.cookies.values())
        return (s, cook)

    
def lift_optional(x):
    if (type(x) == list):
        if len(x) == 0:
            return None
        for elm in x:
            if elm is None:
                return None
        return x


def trait_stderr(message) -> Optional[List[str]]:
    return lift_optional(re.findall('"stderr"', message))


def trait_problem_submit_code_status(message) -> Optional[List[str]]: 
    return lift_optional(re.findall('"activity":\s+"problem_submit_code_status"', message))

def trait_problem_run_code_status(message) -> Optional[List[str]]: 
    return lift_optional(re.findall('"activity":\s+"problem_run_code_status"', message))

def trait_problem_content_url(url):
    url = url.replace('problem/content/description', 'problem/content')
    if url[-1] != '/':
        url = url + '/'
    return lift_optional(re.findall('\/problem\/content\/[0-9]+\/', url))

def trait_run_status(message) -> Optional[List[str]]:
    return lift_optional(re.findall('"status":\s+"*"?', message))


def trait_finished_judging(message) -> Optional[List[str]]:
    return lift_optional(list(map(lambda x:x(message), [trait_stderr, trait_run_status, trait_problem_submit_code_status])))


def trait_finished_running(message) -> Optional[List[str]]:
    return lift_optional(list(map(lambda x:x(message), [trait_stderr, trait_run_status, trait_problem_run_code_status])))


def make_submission_header(url, code):
    res = copy.deepcopy(submit_code_data)
    res['code'] = code
    res['problem_id'] = get_problem_id(url)
    return res

def make_submission_url(url):
    return url.replace('content', 'content/submission')

def ensure_content_url(url):
    if not trait_problem_content_url(url) is None and len(trait_problem_content_url(url)) == 1:
        return BASE_URL + trait_problem_content_url(url)[0]
    else:
        return None
  
def submit(url, code = ''):
    s, cook = prepare_session()
    url = ensure_content_url(url)
    ws = websocket.create_connection('wss://www.acwing.com/wss/chat/',
                                      header = socket_header,
                                      cookie = cook)
    ws.settimeout(20)
    ws.send(json.dumps(make_submission_header(url, code)))
    sys.stdout.write(Fore.YELLOW +Style.BRIGHT + '[ ] Code sent, waiting for result')
    sys.stdout.flush()
    for i in range(0, 100):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.3)
        msg = ws.recv()
        if not trait_finished_judging(msg) is None:
            display_submission_result(json.loads(msg), make_submission_url(url))
            break
    ws.close()
    

def make_runcode_header(url, code, input_data):
    res = copy.deepcopy(submit_code_data)
    res['activity'] = 'problem_run_code'
    res['code'] = code
    res['problem_id'] = get_problem_id(url)
    res['input'] = input_data
    return res

    
def runcode(url, code, input_data):
    s, cook = prepare_session()
    url = ensure_content_url(url)
    ws = websocket.create_connection('wss://www.acwing.com/wss/chat/',
                                      header = socket_header,
                                      cookie = cook)
    ws.settimeout(20)
    ws.send(json.dumps(make_runcode_header(url, code, input_data)))
    sys.stdout.write(Fore.YELLOW +Style.BRIGHT + '[ ] Code sent, waiting for result')
    sys.stdout.flush()
    for i in range(0, 100):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.3)
        msg = ws.recv()
        print(msg)
        if not trait_finished_running(msg) is None:
            display_runcode_result(json.loads(msg))
            break
    ws.close()    



def get_problem_id(url):
    if url[-1] != '/':
        url = url + '/'
    match = lift_optional(re.findall('\/problem\/content\/[0-9]+\/', url))
    if not match is None and len(match) == 1:
        return re.findall('[0-9]+', match[0])[0]
    else:
        print("URL is " + url)
        raise NameError('could not parse url')

        
def display_compile_error_information(message):
    logger = ['']
    logger[0] = '\r[✗] Compilation Log: ' + message['compilation_log'] 
    print(Fore.RED + Style.BRIGHT, '\n'.join(logger))


def process_submission_detail(submission_detail):
    res = {}
    for info in submission_detail:
        title, data = info[0], info[1]
        if title.find('通过') != -1:
            res['passed'] = data
        elif title.find('运行时间') != -1:
            res['time'] = data
        elif title.find('运行空间') != -1:
            res['memory'] = data
        elif title.find('提交') != -1:
            res['submission_time'] = data.replace('秒前', ' seconds ago')
    return res


def display_accepted_information(message, submission_detail):
    logger = ['', '', '']
    logger[0] = '\r[✓] ' + submission_detail['passed'] + ' cases passed' + ' (' + submission_detail['time'] + ')'
    logger[1] = '\r[✓] Memory Used: ' + submission_detail['memory']
    logger[2] = '\r[✓] Submission Time: ' + submission_detail['submission_time']
    print(Fore.GREEN + Style.BRIGHT, '\n'.join(logger) + Style.RESET_ALL)

    
def display_fail_information(message, submission_detail, title):
    logger = ['', '', '', '', '', '']
    logger[0] = '\r[✗] ' + submission_detail['passed'] + ' cases passed' + ' (' + submission_detail['time'] + ', ' + submission_detail['memory'] + ')'
    logger[1] = '\r[✗] Failed Testcase: ' + message['testcase_input'].strip()
    logger[2] = '\r[✗] Answer: ' + message['testcase_user_output'].strip()
    logger[3] = '\r[✗] Expected Answer: ' + message['testcase_output'].strip()
    logger[4] = '\r[✗] StdErr: ' + message['stderr'].strip()
    logger[5] = '\r[✗] Submission Time: ' + submission_detail['submission_time']
    print(Fore.RED + Style.BRIGHT, '\n'.join(logger) + Style.RESET_ALL)        

    
def display_submission_result(message, url):
    logger = []
    if message['status'] == 'ACCEPTED':
        display_accepted_information(message, process_submission_detail(get_submission(url)))
    elif message['status'] == 'COMPILE_ERROR':
        display_compile_error_information(message)
    elif message['status'] == 'MEMORY_LIMIT_EXCEEDED':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Memory Limit Exceeded')
    elif message['status'] == 'TIME_LIMIT_EXCEEDED':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Time Limit Exceeded')
    elif message['status'] == 'RUNTIME_ERROR':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Runtime Error')
    elif message['status'] == 'WRONG_ANSWER':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Wrong Answer')
        

def get_latest_submission_detail_link(session, url):
    r = session.get(url, headers = submission_result_header)
    # sys.stdout.write('.')
    # sys.stdout.flush()
    soup = BeautifulSoup(r.content, 'html5lib')
    return BASE_URL + soup.find_all('tr')[1].find_all('a')[0]['href']    


def split_into_pair(lst):
    return [lst[i:i + 2] for i in range(0, len(lst), 2)]


def parse_submission_detail(response):
    pool = response.findAll('div', attrs = {'class' : 'code-detail-information'})[0].findAll('span')
    return split_into_pair(list(map(lambda x : x.text, pool)))


def get_submission(url):
    session, cookie = prepare_session()
    submission_url = get_latest_submission_detail_link(session, url)
    response = session.get(get_latest_submission_detail_link(session, url),
                           headers = base_header)
    print(Fore.YELLOW + Style.BRIGHT, '\rLatest Submission URL: %s' % submission_url + Style.RESET_ALL)
    soup = BeautifulSoup(response.content, 'html5lib')
    session.close()
    return parse_submission_detail(soup)
