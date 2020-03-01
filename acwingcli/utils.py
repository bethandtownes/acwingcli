import os
import acwingcli.config as config


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
