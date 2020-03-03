
import os
import json
import shutil
import acwingcli.commandline_writer as cmdwrite

def input_with_default(title_name, default):
    path = default
    if str(input('default {} is {}, accept? [y/n]'.format(title_name, path))).lower() == 'n':
        path = str(input('enter custom {}: '.format(title_name)))
    return path


def setup_assistant():
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
    
def clean():
    cmdwrite.client_debug('clean procedure started')
    with open(os.path.join(os.path.dirname(__file__), 'assets/data.json'), 'r') as f:
        try:
            shutil.rmtree(json.load(f)['config_path'])
        except KeyError:
            cmdwrite.client_debug('no config path found, exit')
        else:
            print('config file cleaned')
        finally:
            f.close()
    with open(os.path.join(os.path.dirname(__file__), 'assets/data.json'), 'w') as f:
        f.write('{}')
        f.close()
