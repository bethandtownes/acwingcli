import acwingcli
import sys
import os
import argparse


from .readfile import get_string_from_file
from .login import submit

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--submit", help = 'submit file')

def main():
    args = vars(ap.parse_args())
    if not args.get('submit') is None:
        code = get_string_from_file(args['submit']).decode('utf-8')
        submit('https://www.acwing.com/problem/content/description/1/', code)



if __name__ == '__main__':
    # args = vars(ap.parse_args())
    # print(args)
    main()
