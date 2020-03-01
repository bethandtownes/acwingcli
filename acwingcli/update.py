from .login import prepare_session
from .headers import base_header
from multiprocessing import Pool, TimeoutError, Lock, Value
import json
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init
import sys
import pickle
import time

import acwingcli.config as config
import acwingcli.commandline_writer as cmdwrite


def process_table_item(item):
    item = list(map(lambda x : x, item))

def problem_id(entry):
    return eval(entry[1].find('span').text)

def problem_link(entry):
    return 'https://www.acwing.com' + entry[2].find('a')['href']

def problem_rate(entry):
    return entry[3].find('span').text

def problem_difficulty(entry):
    data = entry[4].find('span').text
    if data == '简单':
        return 'easy'
    elif data == '中等':
        return 'medium'
    elif data == '困难':
        return 'hard'

def problem_name(entry):
    return entry[2].find('a').text.strip()
    
def problem_status(entry):
    if entry[0].find('span') is None:
        return 'unattemped'
    else:
        title = entry[0].find('span')['title']
        if title.find('已通过') != -1:
            return 'passed'
        elif title.find('尝试过') != -1:
             return 'attempted'
        else:
            return title
    
def process_problem_item(entry):
    return { problem_id(entry) : { 'link' : problem_link(entry),
                                   'name' : problem_name(entry),
                                   'rate' : problem_rate(entry),
                                   'status' : problem_status(entry),
                                   'difficulty' : problem_difficulty(entry)}}

def global_context(lock_, total_pages_, finished_pages_):
    global lock
    global finished_pages
    global total_pages
    lock = lock_
    total_pages  = total_pages_
    finished_pages = finished_pages_

def number_of_pages():
    session, cookie = prepare_session()
    soup = BeautifulSoup(session.get('https://www.acwing.com/problem/1/', headers = base_header).content, 'html5lib' )
    table = list(map(lambda x : eval(x.find('a')['id'].replace('page', '').replace('_', '')),
                     soup.find('ul', {'class' : 'pagination'}).findAll('li')))
    
    return max(table)


def problem_list():
    lock = Lock()
    cmdwrite.status('Acquiring Data')
    N = number_of_pages()
    cmdwrite.status('Initializing Process Pool')
    counter = Value('i', 0)
    urls = ['https://www.acwing.com/problem/' + str(i) + '/' for i in range(1, N + 1)]
    with Pool(min(N, 40), initializer = global_context, initargs = (lock, N, counter)) as pool:
        result = pool.map(update_problem_list, urls)
        final_result = {}
        for problems in result:
            final_result.update(problems)
        cmdwrite.status('Updating Cache File')
        time.sleep(0.3)
        with open(config.problem_cache_file_path, 'w') as f:
            json.dump(final_result, f)
        cmdwrite.status('Finished')
        print(Style.RESET_ALL)


def update_problem_list(url):
    res = {}
    session, cookie = prepare_session()
    soup = BeautifulSoup(session.get(url, headers = base_header).content, 'html5lib' )
    table = soup.find('table', {'class' : 'table-responsive'}).find('tbody').findAll('tr')
    table = list(map(lambda x : x.findAll('td'), table))
    for entry in table:
        res.update(process_problem_item(entry))
    with finished_pages.get_lock():
        finished_pages.value += 1
        cmdwrite.progress(str(finished_pages.value) + '/' + str(total_pages))

    return res
