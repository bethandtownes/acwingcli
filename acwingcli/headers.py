socket_header = {
    'Host': 'www.acwing.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-WebSocket-Version': '13',
    'Origin': 'https://www.acwing.com',
    'Sec-WebSocket-Extensions': 'permessage-deflate',
    'Sec-WebSocket-Key': 'oc5FCR520cbuwj92DAEIow==',
    'Connection': 'keep-alive, Upgrade',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade': 'websocket'
}

socket_url = 'https://www.acwing.com/wss/chat/'

submission_result_header = {
    'Host' : 'www.acwing.com',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.5',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Connection' : 'keep-alive',
    'Referer' : 'https://www.acwing.com/problem/content/1/',
    'Cookie' : 'csrftoken=7hsfFvGPBmPAXFKJBP4ebTzS6Wu0zkYDVPYIEAmrxznOenkNz3r80vBWjS2A1NXx; sessionid=lqliv4h5nn3eqv0hvxuxd8apzx1hcxmf; file_341775_readed=""; file_341979_readed=""',
    'Upgrade-Insecure-Requests': '1'
    }



base_header = {
    'Host' : 'www.acwing.com',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.5',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Connection' : 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }


code = """
#include <iostream>

using namespace std;

int main() {
  int a; int b;
  cin >> a >> b;
  cout << a + b << endl;
  return 0;
}
"""

mode = 'normal'
record = '[]'
ptime = 0

PROBLEM_ID = 1


submit_code_data = {'activity': "problem_submit_code",
                    'problem_id': PROBLEM_ID,
                    'code': code,
                    'language': 'C++',
                    'mode': mode,
                    'record': record,
                    'program_time': ptime}


headers = {'Host': 'www.acwing.com',
           'Connection': 'keep-alive',
           'Content-Length': '138',
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Origin': 'https://www.acwing.com',
           'X-Requested-With' : 'XMLHttpRequest',
           'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
           'Sec-Fetch-Site' : 'same-origin',
           'Sec-Fetch-Mode' : 'cors',
           'Referer' : 'https://www.acwing.com/',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6'}
