from colorama import Fore, Back, Style, init
import acwingcli.commandline_writer as cmdwrite
import sys
import os
import json

package_data_file = os.path.join(os.path.dirname(__file__), 'assets/data.json')


def input_with_default(title_name, default):
    path = default
    if str(input(Fore.LIGHTCYAN_EX + Style.BRIGHT + 'default {} is {}, accept? [y/n] '.format(title_name, path))).lower() == 'n':
        path = str(input('enter custom {}: '.format(title_name)))
    sys.stdout.write(Style.RESET_ALL)
    sys.stdout.flush()
    return path


def setup_assistant():
    print()
    config_path = input_with_default('config path',
                                     os.path.join(os.path.expanduser('~'), '.acwing/'))
    cache_path = os.path.join(config_path, 'cache')
    problembook_path = input_with_default('problembook path',
                                          os.path.join(os.path.expanduser('~'), 'acwing-problembook/'))
    submission_template_path = input_with_default('submission template path',
                                                  os.path.join(problembook_path, 'submission_templates/'))
    default_language = input_with_default('default language', 'C++')
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    if not os.path.exists(problembook_path):
        os.makedirs(problembook_path)
    if not os.path.exists(submission_template_path):
        os.makedirs(submission_template_path)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    with open(os.path.join(os.path.dirname(__file__), 'assets/data.json'), 'w') as f:
        json.dump({'config_path' : config_path}, f)
        f.close()
    with open(config_path + 'config.json', 'w') as f:
        json.dump({'path_problem_book_folder' : problembook_path,
                   'path_problem_cache_file' : os.path.join(config_path, 'cache/problem.json'),
                   'path_cookie_file' : os.path.join(config_path, 'cache/cookie'),
                   'path_submission_template_files' : submission_template_path,
                   'default_language' : default_language}, f)
        f.close()


def load_problem_cache(path):
    try:
        with open(path, 'r') as f:
            problem_cache = dict(map(lambda kv : (int(kv[0]), kv[1]), json.load(f).items()))
            return problem_cache
    except FileNotFoundError:
        return {}
        

def load_package_data():
    try:
        with open(package_data_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None


    
def load_config_data():
    package_data = load_package_data()
    if package_data is None or not 'config_path' in package_data.keys():
        setup_assistant()
    package_data = load_package_data()
    if not os.path.exists(package_data['config_path']):
        os.makedirs(package_data['config_path'])
    config_file_path = os.path.join(package_data['config_path'], 'config.json')
    with open(config_file_path, 'r') as f:
        config_data = json.load(f)
        problem_cache_file_path = config_data['path_problem_cache_file']
        path_problem_book = config_data['path_problem_book_folder']
        path_cookie = config_data['path_cookie_file']
        cmdwrite.client_debug('config data: {}'.format(config_data))
        problem_cache = load_problem_cache(problem_cache_file_path)
        if problem_cache == {}:
            import acwingcli.update
            acwingcli.update.problem_list(problem_cache_file_path, path_cookie)
            problem_cache = load_problem_cache(problem_cache_file_path)
            # cmdwrite.client_debug('cache updated, ' + str(problem_cache))
        return (config_data,
                problem_cache_file_path,
                path_problem_book,
                path_cookie,
                problem_cache)


config_data, problem_cache_file_path, path_problem_book, path_cookie, problem_cache = load_config_data()        


    
def reload():
    config_data, problem_cache_file_path, path_problem_book, path_cookie, problem_cache = load_config_data()            
