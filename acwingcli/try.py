from multiprocessing.connection import Listener
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
import threading

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time


import queue


q = queue.Queue()

def on_message(ws, message):
    q.put(message)
    # print('enque' + str(q.qsize()))
    # import sys
    # sys.stdout = open('/home/jasonsun0310/acwingcli/logfile3.log', 'w')
    # sys.stdout.write(message)
    # print(message)

    
def on_error(ws, error):
    print(error)

    
def on_close(ws):
    print("### closed ###")


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



def prepare_session():
    s = requests.session()
    need_to_update_cookie = False
    if os.path.exists('/home/jasonsun0310/.local/share/acwing/cookie'):
        with open('/home/jasonsun0310/.local/share/acwing/cookie', 'rb') as f:
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
        username = str(input('Enter your Acwing username:'))
        password = str(getpass.getpass(prompt = 'Enter your Acwing password:'))
        response = BeautifulSoup(s.get(url).content, 'html5lib')
        login = copy.deepcopy(login_data)
        login['username'] = username
        login['password'] = password
        login['csrfmiddlewaretoken'] = response.find('input', attrs = {'name' : 'csrfmiddlewaretoken'})['value']
        header = copy.deepcopy(headers)
        a = s.post('https://www.acwing.com/user/account/signin/', data = login, headers = header)
        token = a.cookies['csrftoken']
        cook = 'csrftoken=' + a.cookies['csrftoken'] + '; ' + 'sessionid=' + a.cookies['sessionid']
        with open('/home/jasonsun0310/.local/share/acwing/cookie', 'wb') as f:
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
        with open('/home/jasonsun0310/.local/share/acwing/cookie', 'wb') as f:
            pickle.dump(a.cookies, f)
            print('wrote cookies')
            print(a.cookies.values())
        return (s, cook)


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
    
def handle(wc, a):
    wc.send(json.dumps(submit_code_data))

    # wc.run_forever()



def get_Q():
    try:
        # print('now ' + str(q.qsize()))
        element = q.get(True, 5)
        return element
    except:
        return None
    
    
    
if __name__ == '__main__':
    s, cook = prepare_session()
    acwing_socket = websocket.WebSocketApp('wss://www.acwing.com/wss/chat/',
                                           header = socket_header,
                                           cookie = cook,
                                           on_message = on_message,
                                           on_error = on_error,
                                           on_close = on_close)
    wst = threading.Thread(target = acwing_socket.run_forever)
    wst.daemon = True
    wst.start()

    while True:
        msg = str(input("Enter: "))
        if msg == 'try':
            thread.start_new_thread(handle, (acwing_socket, 1))
            # print('wait for queue')
            # print('now ' + str(q.qsize()))
            while True:
                a = get_Q()
                if a is None:
                    break
                print(a)
                
                
            # try:
            #     print('now ' + str(q.qsize()))
            #     element = q.get(True, 2)
            #     print(element)
            # except:
            #     pass
            # print('after ' + str(q.qsize()))
            # while q.empty() == False:
            #     print(q.get(False))
            # wst = threading.Thread(target = acwing_socket.run_forever)
            # wst.daemon = True
            # wst.start()
        else:
            print('got ' + msg)
            
        
    
    # acwing_socket.run_forever()
