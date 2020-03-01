from .login import prepare_session, make_submission_header, trait_finished_judging, ensure_content_url
from .headers import socket_header
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

from .login import trait_finished_judging

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

import queue
q = queue.Queue()


def on_message(ws, message):
    data = json.loads(message)
    if data['activity'] == 'problem_submit_code_status':
        q.put(json.dumps(data))
    elif data['activity'] == 'problem_run_code_status':
        q.put(json.dumps(data))

    
def on_error(ws, error):
    return 
    
def on_close(ws):
    return

def get_Q():
    try:
        element = q.get(True, 20)
        return element
    except:
        return None
    

def server_submit(acwing_socket, local_client, url, code = ''):
    acwing_socket.send(json.dumps(make_submission_header(ensure_content_url(url), code)))
    while not (response := get_Q()) is None:
        local_client.send(response)
        if trait_finished_judging(response):
            break
    return

def handle(conn, acwing_socket):
    try:
        while True:
            msg = conn.recv()
            if msg == 'close':
                conn.close()
                acwing_socket.close()
                break
            elif msg.find('send') != -1:
                op, url, code = msg.split('$$')
                server_submit(acwing_socket, conn, url, code)
            else:
                pass
    except EOFError:
        return
    except BrokenPipeError:
        return
    except ConnectionResetError:
        return         


def send_debug_message(conn, message):
    conn.send(json.dumps({'local_debug_message' : message}))
    
    
def runserver():
    s, cook = prepare_session()
    acwing_socket = websocket.WebSocketApp('wss://www.acwing.com/wss/chat/',
                                           header = socket_header,
                                           cookie = cook,
                                           on_message = on_message,
                                           on_error = on_error,
                                           on_close = on_close)
    wst = threading.Thread(target = acwing_socket.run_forever, kwargs = {'ping_interval' : 60})
    wst.daemon = True
    wst.start()
    address = ('localhost', 6001)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey=b'1234')
    while True:
        conn = listener.accept()
        send_debug_message(conn, 'welcome')
        send_debug_message(conn, str(listener.last_accepted))
        # conn.send('welcome')
        # conn.send(str(listener.last_accepted))
        t = threading.Thread(target = handle, args = (conn,acwing_socket))
        t.daemon = True
        t.start()
    listener.close()

