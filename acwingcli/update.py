from .login import prepare_session
from .headers import base_header
from multiprocessing import Pool, TimeoutError, Lock, Value
import json
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init
import sys
import pickle
import time


import acwingcli.commandline_writer as cmdwrite
import glob
import os
import acwingcli.utils as utils


def process_table_item(item):
    item = list(map(lambda x : x, item))

def problem_id(entry):
    return eval(entry[1].find('span').text)

def problem_link(entry):
    return 'https://www.acwing.com' + entry[2].find('a')['href']

def problem_submission_link(entry):
    return problem_link(entry).replace('content', 'content/submission')

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
                                   'submission_link': problem_submission_link(entry),
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

def number_of_pages(path_cookie):
    session, cookie = prepare_session(path_cookie)
    soup = BeautifulSoup(session.get('https://www.acwing.com/problem/1/', headers = base_header).content, 'html5lib' )
    table = list(map(lambda x : eval(x.find('a')['id'].replace('page', '').replace('_', '')),
                     soup.find('ul', {'class' : 'pagination'}).findAll('li')))
    
    return max(table)

def testcases(problem_id:str, case_in:str, case_out:str):
    owd = os.getcwd()
    try:
        os.chdir(utils.get_or_create_problem_folder(problem_id))
        new_cases = {case_in : case_out}
        for sample_in, sample_out in map(lambda x: (x, x.replace('in', 'out')), glob.glob('sample*.in')):
            new_cases.update({utils.get_string_from_file(sample_in).decode('utf-8') : utils.get_string_from_file(sample_out).decode('utf-8')})
        for case_id, case in enumerate(new_cases.items()):
            with open('sample' + str(case_id) + '.in', 'w') as f:
                f.write(case[0])
                f.close()
            with open('sample' + str(case_id) + '.out', 'w') as f:
                f.write(case[1])
                f.close()
    finally:
        os.chdir(owd)

def problem_list(problem_cache_file_path = None, path_cookie = None):
    lock = Lock()
    cmdwrite.status('Acquiring Data')
    N = number_of_pages(path_cookie)
    cmdwrite.status('Initializing Process Pool')
    counter = Value('i', 0)
    urls = [('https://www.acwing.com/problem/' + str(i) + '/', path_cookie) for i in range(1, N + 1)]
    with Pool(min(N, 40), initializer = global_context, initargs = (lock, N, counter)) as pool:
        result = pool.starmap(update_problem_list, urls)
        final_result = {}
        for problems in result:
            final_result.update(problems)
        cmdwrite.status('Updating Cache File')
        time.sleep(0.3)
        if problem_cache_file_path == None:
            import acwingcli.config as config
            with open(config.problem_cache_file_path, 'w') as f:
                json.dump(final_result, f)
        else:
            with open(problem_cache_file_path, 'w') as f:
                json.dump(final_result, f)
        cmdwrite.status('Finished')
        print(Style.RESET_ALL)


def update_problem_list(url, path_cookie):
    res = {}
    session, cookie = prepare_session(path_cookie)
    soup = BeautifulSoup(session.get(url, headers = base_header).content, 'html5lib' )
    table = soup.find('table', {'class' : 'table-responsive'}).find('tbody').findAll('tr')
    table = list(map(lambda x : x.findAll('td'), table))
    for entry in table:
        res.update(process_problem_item(entry))
    with finished_pages.get_lock():
        finished_pages.value += 1
        cmdwrite.progress(str(finished_pages.value) + '/' + str(total_pages))

    return res


