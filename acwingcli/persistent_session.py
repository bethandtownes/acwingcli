from .login import prepare_session, make_submission_header, trait_finished_judging, ensure_content_url, make_runcode_header
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

from .login import trait_finished_judging, trait_finished_running

import websocket
try:
    import thread
except ImportError:
    import _thread as thread


import queue
q = queue.Queue()


def on_message(ws, message):
    data = json.loads(message)
    if data['activity'] == 'problem_submit_code_status':
        q.put(json.dumps(data))
    elif data['activity'] == 'problem_run_code_status':
        q.put(json.dumps(data))
    else:
        pass
        # q.put(json.dumps(data))

    
def on_error(ws, error):
    return 
    
def on_close(ws):
    return

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

def get_Q():
    try:
        element = q.get(True, 20)
        return element
    except:
        return None


def server_submit(acwing_socket, local_client, url, code):
    total_attempt = 0
    while total_attempt <= 10:
        try:
            total_attempt += 1
            local_client.send(json.dumps({'local_debug_message': 'submission attempt {}'.format(total_attempt)}))
            acwing_socket.send(json.dumps(make_submission_header(ensure_content_url(url), code)))
            while not (response := get_Q()) is None:
                local_client.send(response)
                if trait_finished_judging(response):
                    break
            return
        except Exception as e:
            local_client.send(json.dumps({'local_debug_message' : '[server submit] got exception ' + str(e.args)}))
            if total_attempt > 10:
                local_client.send(json.dumps({'local_debug_message': 'maxed out attemp'}))
                return
            time.sleep(1)
            


def stopserver(acwing_socket, conn, listener):
    conn.send(json.dumps({'local_debug_message' : 'preparing to close acwing websocket'}))
    acwing_socket.close()
    del acwing_socket
    conn.send(json.dumps({'local_debug_message' : 'acwing websocket closed'}))
    conn.send(json.dumps({'local_debug_message' : 'preparing to close connection'}))
    conn.close()
    

    
def server_run(acwing_socket, local_client, url, code, input_data):
    acwing_socket.send(json.dumps(make_runcode_header(ensure_content_url(url), code, input_data)))
    while not (response := get_Q()) is None:
        local_client.send(response)
        if trait_finished_running(response):
            break
    return


import json
def handle(conn, acwing_socket, listener):
    try:
        while True:
            msg = json.loads(conn.recv())
            if msg['activity'] == 'close':
                conn.close()
                acwing_socket.close()
                break
            elif msg['activity'] == 'send':
                url = msg['url']
                code = msg['code']
                server_submit(acwing_socket, conn, url, code)
            elif msg['activity'] == 'run':
                url = msg['url']
                code = msg['code']
                input_data = msg['input_data']
                server_run(acwing_socket, conn, url, code, input_data)
            elif msg['activity'] == 'stopserver':
                conn.send(json.dumps({'local_debug_message' : 'preparing to stopserver'}))
                stopserver(acwing_socket, conn, listener)
                break
            else:
                pass
    except EOFError:
        conn.close()
        del conn
        return
    except BrokenPipeError:
        conn.close()
        del conn
        return
    except ConnectionResetError:
        conn.close()
        del conn
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
    try:
        while True:
            conn = listener.accept()
            send_debug_message(conn, 'welcome')
            send_debug_message(conn, str(listener.last_accepted))
            t = threading.Thread(target = handle, args = (conn, acwing_socket, listener))
            t.daemon = True
            t.start()
    except:
        pass
    listener.close()
