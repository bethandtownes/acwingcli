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
import colorama


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

login_data = {'csrfmiddlewaretoken': 'TODO',
              'username' : 'JasonSun',
              'password' : 'Sdq17163!',
              'remember_me' : 'on'}



BASE_URL = 'https://www.acwing.com'

code = """
#include <iostream>

using namespace std;

int main() {
  int a; int b;
  cin >> a >> b;
  cout << a + b << endl;
  return 0;
}
"""


mode = 'normal'
record = '[]'
ptime = 0

PROBLEM_ID = 1

submit_code_data = {'activity': "problem_submit_code",
                    'problem_id': PROBLEM_ID,
                    'code': code,
                    'language': 'C++',
                    'mode': mode,
                    'record': record,
                    'program_time': ptime}


headers = {'Host': 'www.acwing.com',
           'Connection': 'keep-alive',
           'Content-Length': '138',
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Origin': 'https://www.acwing.com',
           'X-Requested-With' : 'XMLHttpRequest',
           'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
           'Sec-Fetch-Site' : 'same-origin',
           'Sec-Fetch-Mode' : 'cors',
           'Referer' : 'https://www.acwing.com/',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6'}


socket_header = {
    'Host': 'www.acwing.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-WebSocket-Version': '13',
    'Origin': 'https://www.acwing.com',
    'Sec-WebSocket-Extensions': 'permessage-deflate',
    'Sec-WebSocket-Key': 'oc5FCR520cbuwj92DAEIow==',
    'Connection': 'keep-alive, Upgrade',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade': 'websocket'
}

socket_url = 'https://www.acwing.com/wss/chat/'

submission_result_header = {
    'Host' : 'www.acwing.com',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.5',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Connection' : 'keep-alive',
    'Referer' : 'https://www.acwing.com/problem/content/1/',
    'Cookie' : 'csrftoken=7hsfFvGPBmPAXFKJBP4ebTzS6Wu0zkYDVPYIEAmrxznOenkNz3r80vBWjS2A1NXx; sessionid=lqliv4h5nn3eqv0hvxuxd8apzx1hcxmf; file_341775_readed=""; file_341979_readed=""',
    'Upgrade-Insecure-Requests': '1'
    }



base_header = {
    'Host' : 'www.acwing.com',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.5',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Connection' : 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }


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
            print('[Using Cookie]')
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

def trait_run_status(message) -> Optional[List[str]]:
    return lift_optional(re.findall('"status":\s+"*"?', message))
    
def trait_finished_judging(message) -> Optional[List[str]]:
    return lift_optional(list(map(lambda x:x(message), [trait_stderr, trait_run_status, trait_problem_submit_code_status])))

def submit(cookie, code = ''):
    ws =  websocket.create_connection('wss://www.acwing.com/wss/chat/',
                                      header = socket_header,
                                      cookie = cookie)
    ws.settimeout(7)
    ws.send(json.dumps(submit_code_data))
    for i in range(0, 100):
        time.sleep(0.3)
        msg = ws.recv()
        if not trait_finished_judging(msg) is None:
            print(trait_finished_judging(msg))
            print(json.loads(msg))
            display_submission_result(json.loads(msg))
            break


def display_submission_result(message):
    logger = ""
    if message['status'] == 'ACCEPTED':
        logger
        
        

        

def get_latest_submission_detail_link(session, url):
    r = session.get(url, headers = submission_result_header)
    soup = BeautifulSoup(r.content, 'html5lib')
    return BASE_URL + soup.find_all('tr')[1].find_all('a')[0]['href']    



def split_into_pair(lst):
    return [lst[i:i + 2] for i in range(0, len(lst), 2)]

def parse_submission_detail(response):
    pool = response.findAll('div', attrs = {'class' : 'code-detail-information'})[0].findAll('span')
    return split_into_pair(list(map(lambda x : x.text, pool)))

def get_submission(session, cookie = None, url = None):
    print('[Latest Submission URL: %s]' % get_latest_submission_detail_link(session, url))
    response = session.get(get_latest_submission_detail_link(session, url),
                           headers = base_header)
    soup = BeautifulSoup(response.content, 'html5lib')
    print(parse_submission_detail(soup))
    # res = soup.findAll('div', attrs = {'class' : 'code-detail-information'})[0].findAll('span')w
    
    
    # print(soup)xx
    return soup
                           

        

def main():
    s, token, cook = login()
    print('[Login Success!]')
    submit(cook)
    return get_submission(s, None, 'https://www.acwing.com/problem/content/submission/1/')
    
    
    

if __name__ == "__main__":
    main()

