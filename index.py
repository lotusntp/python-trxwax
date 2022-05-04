from datetime import datetime
from re import M
from rich.console import Console
from rich.theme import Theme
import json
import sys
import cloudscraper
from time import gmtime, strftime
import time
import traceback
from functions import create_trx
custom_theme = Theme({"success": "green"})
console = Console(theme=custom_theme)
scraper = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})

f = open('setting.json')
data = json.load(f)

if not data['session']: sys.exit()
cookies = {'session_token': data['session']}
def login():

    return scraper.get("https://api-idm.wax.io/v1/accounts/auto-accept/login", cookies=cookies, headers={"origin":"https://wallet.wax.io"}).text
def GetUserInfo(user):
    data = {
        "account_name": user
    }
    return scraper.post("https://chain.wax.io/v1/chain/get_account", json.dumps(data), cookies=cookies, headers={"origin":"https://wallet.wax.io"}).text

def timestamp():
    nowTime = int(datetime.timestamp(datetime.now()))
    timeUnit = datetime.fromtimestamp(nowTime).strftime('%Y-%m-%d %H:%M:%S')
    fomat_dt = f'[{timeUnit}]'
    return fomat_dt

def main():
    start_time = time.time()
    try:
        logincheck = json.loads(login());
    except Exception as e:
        logincheck = json.loads(login());

    try:
        if logincheck['userAccount']:
            waxuser = logincheck['userAccount']
            waxsession = data['session']
            sender = {
            'id': waxuser,
            'session': waxsession
            }
            userinfo = json.loads(GetUserInfo(waxuser));
            print(timestamp()+" [#PORSERVER]["+logincheck['userAccount']+"] => Account Balance => " + userinfo['core_liquid_balance'])
            print(timestamp()+" [#PORSERVER]["+logincheck['userAccount']+"] => Cpu Info (use/max) => " + str(userinfo['cpu_limit']['used']) + "/" + str(userinfo['cpu_limit']['max']) + " | Available => " + str(userinfo['cpu_limit']['available']))
            if userinfo['cpu_limit']['used'] >= userinfo['cpu_limit']['max']:
                print(timestamp()+" [#PORSERVER]"+"["+logincheck['userAccount']+"] CPU OVERLOAD PLASE Staked")
                exit()
            start = create_trx(scraper, sender)
            print(timestamp()+" [#PORSERVER]["+logincheck['userAccount']+"] => ADD TX SUCCESS : "+start)
            print("--- %s seconds ---" % (time.time() - start_time))
        else:
            print(strftime("[%H:%M:%S]", gmtime())+" [#PORSERVER] => CHECK_COOKIE ERROR")
            traceback.print_exc()
            time.sleep(99999)
    except Exception as e:
        
        print(strftime("[%H:%M:%S]", gmtime())+" [#PORSERVER]["+logincheck['userAccount']+"] => NO DROP ID OR ERROR (EXIT IN 10 SECONDS)")
        time.sleep(10)
        exit()

main()