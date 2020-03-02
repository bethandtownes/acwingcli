import os
import psutil
import acwingcli.config as config
import functools



def get_or_create_problem_folder(problem_id:str):
    problem_directory = (config.path_problem_book + problem_id + '.' + config.problem_cache[eval(problem_id)]['name'] + '/').replace(' ','')
    try:
        os.makedirs(problem_directory)
    except:
        pass
    return problem_directory

def get_problem_id_from_file(filepath:str):
    return os.path.basename(os.path.dirname(os.path.abspath(filepath))).split('.')[0]

def get_string_from_file(path):
    with open(path, 'rb') as f:
        return f.read()

def get_acwing_server_process():
    acc = []
    for process in psutil.process_iter():
        trait_acwing = functools.reduce(lambda x, y : x or y, map(lambda x : x.find('acwingcli') != -1, process.cmdline()), False)
        trait_server = functools.reduce(lambda x, y : x or y, map(lambda x : x.find('-runserver') != -1, process.cmdline()), False)
        if trait_acwing and trait_server:
            acc.append(process)
    return acc

def clean_up_server_processes():
    for process in get_acwing_server_process():
        process.kill()

