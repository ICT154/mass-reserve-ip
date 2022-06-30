import time
from attr import attr
import requests, json, socket 
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

session = requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0'})


class OReverse:
    def __init__(self, web_list: str=''):
        self.web_list = web_list
        self.threads = 25
        self.black_list = [_.rstrip() for _ in open('blacklist.txt','r').readlines()]
        self.endpoint_url = 'https://sonar.omnisint.io/reverse/{}'
    
    
    def clean_url(self, d):
        
        if '://' in d:
            return urlparse(d).netloc

        return d 
    
    def start(self):
        with ThreadPoolExecutor(max_workers=self.threads) as worker:
            list_domain = [self.clean_url(x.rstrip()) for x in open(self.web_list,'r').readlines()]
            worker.map(self.rev_ip, list_domain)
    
    def rev_ip(self, item):

        octet = item.split('.')
        if len(octet) != 4:
            item = self.getip(item)
        
        if not item:
            print('[-] invalid ip address at ', item)
            return 0
        
        item = item + ''

        response = session.get(self.endpoint_url.format(item)).text 
        is_valid = self.validate_result(response)
        if not is_valid:
            print('[-] invalid result  ', item)
        
    def validate_result(self, response_text):
        try:
            j = json.loads(response_text)

            if j.get('error'):
                return None 
            
            result = []
            for k, v in j.items():
                for vv in v:
                    for b in self.black_list:
                        vv = vv.replace(b, '')
                    
                    result.append(vv)

            s_r = set(result)
            open('results.txt','a').write('\n'.join(s_r)+'\n')
            print(len(s_r), ' Domains Added :D')
            return True 
            
        except Exception as e:
            return None
    


    def getip(self, s):
        try:
            return socket.gethostbyname(s)
        except Exception as e:
            return None 
o = OReverse(input('IP List : '))
o.start()