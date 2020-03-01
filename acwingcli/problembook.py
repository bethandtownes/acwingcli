from bs4 import BeautifulSoup
import acwingcli.config as config
from .login import prepare_session
from .login import split_into_pair
from typing import List
import os
import acwingcli.commandline_writer as cmdwrite
import time
def sample_cases_sanity_check(sample_cases : List[str]):
    if len(sample_cases) % 2 != 0:
        return False
    else:
        return True
    

def get_problem(problem_id : str):
    if problem_id.isdigit():
        session, cookie = prepare_session()
        cmdwrite.status('Request sent, waiting for response.')
        problem_body = BeautifulSoup(session.get(config.problem_cache[eval(problem_id)]['link']).content, 'html5lib')
        cmdwrite.status('Generating sample cases')
        time.sleep(0.3)
        print(config.problem_cache[eval(problem_id)]['name'])
        sample_cases = list(map(lambda x : x.text, problem_body.find_all('code')))
        problem_directory = (config.path_problem_book + problem_id + '.' + config.problem_cache[eval(problem_id)]['name'] + '/').replace(' ','')
        
        print(problem_directory)
        try:
            os.makedirs(problem_directory)
        except:
            pass
        if sample_cases_sanity_check(sample_cases) == True:
            for case_id, sample_case in enumerate(split_into_pair(sample_cases)):
                sample_in, sample_out = sample_case
                with open(problem_directory + 'sample' + str(case_id) + '.in', 'w') as f:
                    f.write(sample_in)
                    f.close()
                with open(problem_directory + 'sample' + str(case_id) + '.out', 'w') as f:
                    f.write(sample_out)
                    f.close()
        cmdwrite.status('Success')
        print()
        print(sample_cases)
        
        
    
