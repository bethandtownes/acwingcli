
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

import sys
import curses
import copy



from .headers import socket_header, socket_url, submission_result_header, base_header, submit_code_data, headers

def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

login_data = {'csrfmiddlewaretoken': 'TODO',
              'username' : '',
              'password' : '',
              'remember_me' : 'on'}



BASE_URL = 'https://www.acwing.com'


def login():
    s = requests.session()
    need_to_update_cookie = False
    with open('/home/jasonsun0310/.local/share/acwing/cookie', 'rb') as f:
        ck = pickle.load(f)
        for cj in ck:
            if cj.is_expired():
                print("[Cookie Expired]")
                need_to_update_cookies = True
                
        if need_to_update_cookie == False:
            s.cookies.update(ck)
            csrftoken = s.cookies.values()[0]
            sessionid = s.cookies.values()[1]
            cook = 'csrftoken=' + csrftoken + '; ' + 'sessionid=' + sessionid
            return (s, csrftoken, cook)  
    url = 'https://www.acwing.com/problem/content/1/'
    if need_to_update_cookie == True:
        r = s.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        token = soup.find('input', attrs = {'name' : 'csrfmiddlewaretoken'})['value']
        login_data['csrfmiddlewaretoken'] = token
        headers['X-CSRFToken'] = token
        headers['Cookie'] = 'csrftoken=' + token
        a = s.post('https://www.acwing.com/user/account/signin/', data = login_data, headers = headers)
        cook = 'csrftoken=' + a.cookies['csrftoken'] + '; ' + 'sessionid=' + a.cookies['sessionid']
        with open('/home/jasonsun0310/.local/share/acwing/cookie', 'wb') as f:
            pickle.dump(a.cookies, f)
            print('wrote cookies')
            print(a.cookies.values())
        return (s, token, cook)


def prepare_session():
    s = requests.session()
    need_to_update_cookie = False
    with open('/home/jasonsun0310/.local/share/acwing/cookie', 'rb') as f:
        ck = pickle.load(f)
        for cj in ck:
            if cj.is_expired():
                print("[Cookie Expired]")
                need_to_update_cookies = True
                
        if need_to_update_cookie == False:
            s.cookies.update(ck)
            csrftoken = s.cookies.values()[0]
            sessionid = s.cookies.values()[1]
            cook = 'csrftoken=' + csrftoken + '; ' + 'sessionid=' + sessionid
            return s    
    url = 'https://www.acwing.com/problem/content/1/'
    if need_to_update_cookie == True:
        r = s.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        token = soup.find('input', attrs = {'name' : 'csrfmiddlewaretoken'})['value']
        login_data['csrfmiddlewaretoken'] = token
        headers['X-CSRFToken'] = token
        headers['Cookie'] = 'csrftoken=' + token
        a = s.post('https://www.acwing.com/user/account/signin/', data = login_data, headers = headers)
        cook = 'csrftoken=' + a.cookies['csrftoken'] + '; ' + 'sessionid=' + a.cookies['sessionid']
        with open('/home/jasonsun0310/.local/share/acwing/cookie', 'wb') as f:
            pickle.dump(a.cookies, f)
            print('wrote cookies')
            print(a.cookies.values())
        return s

    
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


def trait_problem_content_url(url):
    url = url.replace('problem/content/description', 'problem/content')
    if url[-1] != '/':
        url = url + '/'
    return lift_optional(re.findall('\/problem\/content\/[0-9]+\/', url))


def trait_run_status(message) -> Optional[List[str]]:
    return lift_optional(re.findall('"status":\s+"*"?', message))


def trait_finished_judging(message) -> Optional[List[str]]:
    return lift_optional(list(map(lambda x:x(message), [trait_stderr, trait_run_status, trait_problem_submit_code_status])))


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
    s, token, cook = login()
    url = ensure_content_url(url)
    ws = websocket.create_connection('wss://www.acwing.com/wss/chat/',
                                      header = socket_header,
                                      cookie = cook)
    ws.settimeout(20)
    ws.send(json.dumps(make_submission_header(url, code)))
    for i in range(0, 100):
        time.sleep(0.3)
        msg = ws.recv()
        if not trait_finished_judging(msg) is None:
            display_submission_result(json.loads(msg), make_submission_url(url))
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


# def display_accepted_information(message, submission_detail):
#     logger = ['', '', '', '', '']
#     logger[0] = ('✓ Accepted')
#     for info in submission_detail:
#         title, data = info[0], info[1]
#         if title.find('通过') != -1:
#             logger[1] = '✓Test Cases Passed: ' + data
#         elif title.find('运行时间') != -1:
#             logger[2] = '✓ Running Time: ' + data
#         elif title.find('运行空间') != -1:
#             logger[3] = '✓ Memory Used: ' + data
#         elif title.find('提交') != -1:
#             logger[4] = '✓ Submission Time: ' + data.replace('秒前', ' seconds ago')
#     print(Fore.GREEN + Style.BRIGHT, '\n'.join(logger))
    
        
def display_compile_error_information(message):
    logger = ['']
    logger[0] = '✗ Compilation Error: ' + message['compilation_log'] 
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
    logger = ['', '', '', '', '']
    logger[0] = '✓ Accepted '+ ' (' + submission_detail['passed']+')'
    logger[1] = '✓ Submission Time: ' + submission_detail['submission_time']
    logger[2] = '✓ Running Time: ' + submission_detail['time']
    logger[3] = '✗ Memory Used: ' + submission_detail['memory']
    logger[4] = '✗ StdErr: ' + message['stderr']
    print(Fore.GREEN + Style.BRIGHT, '\n'.join(logger))        

def display_fail_information(message, submission_detail, title):
    logger = ['', '', '', '', '', '']
    logger[0] = '✗ ' + title + ' (' + submission_detail['passed']+')'
    logger[1] = '✗ Submission Time: ' + submission_detail['submission_time']
    logger[2] = '✗ Failed Testcase: ' + message['testcase_input'].strip()
    logger[3] = '✗ Answer: ' + message['testcase_user_output']
    logger[4] = '✗ Expected Answer: ' + message['testcase_output'].strip()
    logger[5] = '✗ StdErr: ' + message['stderr']
    print(Fore.RED + Style.BRIGHT, '\n'.join(logger))        

    
    
def display_submission_result(message, url):
    logger = []
    print(message)
    if message['status'] == 'ACCEPTED':
        submission_detail = get_submission(url)
        display_accepted_information(message, process_submission_detail(submission_detail))
    elif message['status'] == 'COMPILE_ERROR':
        display_compile_error_information(message)
    elif message['status'] == 'MEMORY_LIMIT_EXCEEDED':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Memory Limit Exceeded')
    elif message['status'] == 'TIME_LIMIT_EXCEEDED':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Time Limit Exceeded')
    elif message['status'] == 'RUNTIME_ERROR':
        display_fail_information(message, process_submission_detail(get_submission(url)), 'Runtime Error')
        
    
        
        


def get_latest_submission_detail_link(session, url):
    r = session.get(url, headers = submission_result_header)
    soup = BeautifulSoup(r.content, 'html5lib')
    return BASE_URL + soup.find_all('tr')[1].find_all('a')[0]['href']    


def split_into_pair(lst):
    return [lst[i:i + 2] for i in range(0, len(lst), 2)]


def parse_submission_detail(response):
    pool = response.findAll('div', attrs = {'class' : 'code-detail-information'})[0].findAll('span')
    return split_into_pair(list(map(lambda x : x.text, pool)))


def get_submission(url):
    session = prepare_session()
    print(Fore.YELLOW + Style.BRIGHT, '[Latest Submission URL: %s]' % get_latest_submission_detail_link(session, url))
    print(Style.RESET_ALL)
    response = session.get(get_latest_submission_detail_link(session, url),
                           headers = base_header)
    soup = BeautifulSoup(response.content, 'html5lib')
    session.close()
    return parse_submission_detail(soup)




def main():
    s, token, cook = login()
    print(Fore.LIGHTYELLOW_EX, '[Login Success]')
    submit('https://www.acwing.com/problem/content/submission/1/', '')


