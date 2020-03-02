
import json


config_directory = None
config_file_path = '/home/jasonsun0310/.acwing/config.json'

with open(config_file_path) as config_file:
    config_data = json.load(config_file)


    
problem_cache_file_path = config_data['path_problem_cache_file']

with open(problem_cache_file_path, 'r') as f:
     problem_cache = dict(map(lambda kv : (int(kv[0]), kv[1]), json.load(f).items()))

path_problem_book = config_data['path_problem_book_folder']     


client_debug_mode = False
server_debug_mode = False
