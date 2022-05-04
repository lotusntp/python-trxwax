
from cloudscraper import CloudScraper as CS
import cloudscraper
import requests
from requests.exceptions import Timeout, ConnectionError, ChunkedEncodingError
import time
from time import gmtime, strftime
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from decimal import Decimal


def getcoin():
    try:
        req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
        info = req.post(
            f"https://api-asia.happyland.finance/api/farm-happyland-finace/getPlayerInfo",
            json={
                "landTokenId": "696"
            },
            timeout=30
        )
    except Exception as e:
        time.sleep(5)
        return getcoin()
    data = info.json()["rows"][0]
    return data
def getBlock() -> dict:
    req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
    data = dict()
    try:
        info = req.get(f"https://chain.wax.io/v1/chain/get_info")
        if info.status_code in [429, 502, 503, 504]:
            print('Get info data err. try again')
            time.sleep(1)
            return getBlock()
        data['ref_block_num'] = info.json()['head_block_num'] - 3
        # time.sleep(0.5)
        block = req.post(
            f"https://chain.wax.io/v1/chain/get_block",
            json={
                "block_num_or_id": data['ref_block_num']
            },
            timeout=120
        )
        if block.status_code in [429, 502, 503, 504]:
            print('Get block data err. try again')
            time.sleep(1)
            return getBlock()
        try:
            data['ref_block_prefix'] = block.json()['ref_block_prefix']
        except:
            time.sleep(5)
            return getBlock()
    except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
        print('Connection(getblock) error. try again in 5 sec')
        time.sleep(5)
        return getBlock()
    return data


def json_to_bin(obj: dict) -> str:
    req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
    try:
        bin = req.post(
            f"https://chain.wax.io/v1/chain/abi_json_to_bin",
            json=obj,
            timeout=30
        )
        if bin.status_code not in [202, 200]:
            print('json_to_bin err. try again')
            print(f'code >>>>>>>>>>>>>>>>>>>{bin.status_code}')
            url = bin.url.split(".")
            print(
                f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
            print(f'res >>>>>>>>>>>>>>>>>>>{bin.text}')
            time.sleep(3)
            return json_to_bin(obj)
        return bin.json()['binargs']
    except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
        print('Connection(json_to_bin) error. try again in 5 sec')
        time.sleep(5)
        return json_to_bin(obj)


def pushTx(sign: list, tx: bytearray) -> dict:
    req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
    try:
        push_tx = req.post(
            f"https://chain.wax.io/v1/chain/push_transaction",
            json={
                "signatures": sign,
                "compression": 0,
                "packed_context_free_data": "",
                "packed_trx": tx.hex()
            },
            timeout=30
        )
        if push_tx.status_code not in [202, 200]:
            if push_tx.status_code in [429, 502, 503, 504]:
                print('Push Tx err. try again')
                print(f'code >>>>>>>>>>>>>>>>>>>{push_tx.status_code}')
                url = push_tx.url.split(".")
                print(
                    f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
                print(f'res >>>>>>>>>>>>>>>>>>>{push_tx.text}')
                return pushTx(sign, tx)
            try:
                err = push_tx.json()["error"]  # ["what"]
                print(f'url {push_tx.url}')
                return {
                    'error': err,
                    'transaction_id': ''
                }
            except:
                print('push err')
                print(f'code >>>>>>>>>>>>>>>>>>>{push_tx.status_code}')
                url = push_tx.url.split(".")
                print(
                    f'endpoint >>>>>>>>>>>>>>>>>>>{url[1] if len(url) == 3 else url[2]}')
                print(f'res >>>>>>>>>>>>>>>>>>>{push_tx.text}')
                return pushTx(sign, tx)
        return push_tx.json()
    except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
        print('Connection(pushTx) error. try again in 5 sec')
        time.sleep(5)
        return pushTx(sign, tx)


def byteArrToArr(bArr)-> list:
    return [x for x in bArr]


class TxConverter(object):

    def __init__(self, params):
        self.bytes_list = bytearray()

        self.push_int(params["expiration"] & 0xFFFFFFFF)
        self.push_short(params["ref_block_num"] & 0xFFFF)
        self.push_int(params["ref_block_prefix"] & 0xFFFFFFFF)
        self.push_variableUInt(params["max_net_usage_words"])
        self.push_variableUInt(params["max_cpu_usage_ms"])
        self.push_variableUInt(params["delay_sec"])
        self.push_actiones(list())  # TODO packfreedata
        self.push_actiones(params["actions"])
        self.push_variableUInt(0)  # TODO packexdata

    def char_to_symbol(self, c):
        if (ord(c) >= ord('a') and ord(c) <= ord('z')):
            return chr(((ord(c) - ord('a')) + 6))

        if (ord(c) >= ord('1') and ord(c) <= ord('5')):
            return chr(((ord(c) - ord('1')) + 1))
        return chr(0)

    def type_name_to_long(self, type_name):
        if type_name == None or type_name == "":
            return 0
        c = 0
        value = 0
        type_name_len = len(type_name)
        for i in range(12 + 1):
            if (i < type_name_len and i <= 12):
                c = ord(self.char_to_symbol(type_name[i]))
            if (i < 12):
                c &= 0x1f
                c <<= 64 - 5 * (i + 1)
            else:
                c &= 0x0f
            value |= c
        return value

    def push_base(self, val, iteration):
        for i in iteration:
            self.bytes_list.append(0xFF & val >> i)

    def push_short(self, val):
        self.push_base(val, range(0, 9, 8))

    def push_int(self, val):
        self.push_base(val, range(0, 25, 8))

    def push_long(self, val):
        self.push_base(val, range(0, 57, 8))

    def push_char(self, val):
        self.bytes_list.append(int(val))

    def push_variableUInt(self, val):
        b = int((val) & 0x7f)
        val = val >> 7
        b = b | (((val > 0) if 1 else 0) << 7)
        self.push_char(b)
        while val:
            b = int((val) & 0x7f)
            val = val >> 7
            b = b | (((val > 0) if 1 else 0) << 7)
            self.push_char(b)

    def push_actiones(self, val_list):
        self.push_variableUInt(len(val_list))
        for i in val_list:
            self.push_long(self.type_name_to_long(i["account"]))
            self.push_long(self.type_name_to_long(i["name"]))
            self.push_permission(i["authorization"])
            if i["data"]:
                self.push_data(i["data"])
            else:
                self.push_variableUInt(0)

    def push_permission(self, val_list):
        self.push_variableUInt(len(val_list))
        for i in val_list:
            self.push_long(self.type_name_to_long(i["actor"]))
            self.push_long(self.type_name_to_long(i["permission"]))

    def push_data(self, val):
        bytes = bytearray.fromhex(val)
        self.push_variableUInt(len(bytes))
        for i in bytes:
            self.bytes_list.append(i)

    def push_transaction_extensions(self, val_list):
        self.push_variableUInt(len(val_list))

def create_trx(req: CS, sender: dict) -> int:
    id = sender['id']
    session_token = sender['session']
    block_data = getBlock()
    tx = TxConverter({
        "expiration": int(time.time() + 60),
        "ref_block_num": block_data['ref_block_num'],
        "ref_block_prefix": block_data['ref_block_prefix'],
        "max_net_usage_words": 0,
        "max_cpu_usage_ms": 0,
        "delay_sec": 1,
        "context_free_actions": [],
        "actions": [{
            "account": 'eosio.token',
            "name": 'transfer',
            "authorization": [{
                "actor": id,
                "permission": "active"
            }],
            "data": json_to_bin({
                "code": "eosio.token",
                "action": "transfer",
                "args": {
                    "from": id,
                    "to": "55cs.wam",
                    "quantity": "1.00000000 WAX",
                    "memo": ""
                }
            })
        }],
        "transaction_extensions":[]
    }).bytes_list
    #signatures = nft.sign_payer(req, tx.hex())
    try:
        req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
        req.options("https://public-wax-on.wax.io/wam/sign", headers={"origin":"https://all-access.wax.io"}, cookies={'session_token': session_token})
        signed = req.post(
            "https://public-wax-on.wax.io/wam/sign",
            headers={
                'origin': 'https://all-access.wax.io',
                'referer': 'https://all-access.wax.io/',
                'x-access-token': session_token,
                'content-type': 'application/json;charset=UTF-8',
            },
            json={
                "serializedTransaction": byteArrToArr(tx),
                "website": "wallet.wax.io",
                "description": "jwt is insecure",
                "freeBandwidth": True
            },
            timeout=120
        )
        if signed.status_code in [429, 502, 503, 504]:
            print("Sign createOffer Tx Server err. try again")
            raise ConnectionError
        if signed.status_code == 403:
            print("Sign createOffer tx CF 1020. try again in 30 sec")
            print(signed.text)
            raise ConnectionError
        if signed.status_code != 200:
            try:
                if signed.json()['message'] == 'Recaptcha token is invalid.':
                    print(signed.json()['message'])
                    print(f'try to solve Recaptcha again...')
                    raise ConnectionError
                elif signed.json()['message'] == 'Session Token is invalid or missing.':
                    print('sender Session Token is invalid or expire')
                    time.sleep(9999)
                else:
                    print(signed.json())
                    time.sleep(999999)
            except:
                print('sign createOffer err')
                print(f'code >>>>>>>>>>>>>>>>>>>{signed.status_code}')
                print(f'res >>>>>>>>>>>>>>>>>>>{signed.text}')
                time.sleep(99999)
        signatures = signed.json()["signatures"]
        push_create_offer = pushTx(signatures, tx)
        if push_create_offer['transaction_id'] == '':
            if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                print('Error: CPU usage limit!!')
                time.sleep(60)
            elif push_create_offer['error']["what"] == 'Expired Transaction':
                print('Error: Expired Transaction!!')
            else:
                print(
                    f'Error: {push_create_offer["error"]["details"][0]["message"]}')
                print('try again in 3 sec')
            raise ConnectionError
        return push_create_offer["transaction_id"]
    except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
        return create_tran(req, sender)


def create_tran(req: CS, sender: dict, dropseiei: dict) -> int:
    id = sender['id']
    session_token = sender['session']
    quantitysp = dropseiei['quantity'].split()
    try:
        if quantitysp[1] == "USD":
            getwax = getcoin()
            xxx = float(Decimal(quantitysp[0])) / float(Decimal("0."+str(getwax["median"])))
            zeros = '.8f'
            xnxx = f"{xxx:,{zeros}}"
            quantity = str(xnxx)+" WAX"
            # print(strftime("[%H:%M:%S]", gmtime())+" [#PORSERVER] => USD CONVERTER => "+quantitysp[0]+" USD <=> "+quantity)
            quantitysp = quantity.split()
            median = getwax["median"]
            # time.sleep(300000)
        else:
            median = 0
    except Exception as e:
        print(e)
    if dropseiei['count'] == 1:
        quantity = quantitysp[0]+" "+quantitysp[1]
    else:
        quantitys = Decimal(quantitysp[0]) * dropseiei['count']
        quantity = str(quantitys)+" "+quantitysp[1]
    block_data = getBlock()
    tx = TxConverter({
        "expiration": int(time.time() + 60),
        "ref_block_num": block_data['ref_block_num'],
        "ref_block_prefix": block_data['ref_block_prefix'],
        "max_net_usage_words": 0,
        "max_cpu_usage_ms": 0,
        "delay_sec": 1,
        "context_free_actions": [],
        "actions": [{
            "account": 'atomicdropsx',
            "name": 'assertdrop',
            "authorization": [{
                "actor": id,
                "permission": "active"
            }],
            "data": json_to_bin({
                "code": "atomicdropsx",
                "action": "assertdrop",
                "args": {
                    "drop_id": dropseiei['drop_id'],
                    "assets_to_mint_to_assert": [{
                        "template_id": dropseiei['template_id'],
                        "tokens_to_back": []
                    }],
                    "listing_price_to_assert": dropseiei['quantity'],
                    "settlement_symbol_to_assert": dropseiei['symbol']
                }
            })
        },{
            "account": 'eosio.token',
            "name": 'transfer',
            "authorization": [{
                "actor": id,
                "permission": "active"
            }],
            "data": json_to_bin({
                "code": "eosio.token",
                "action": "transfer",
                "args": {
                    "from": id,
                    "to": "atomicdropsx",
                    "quantity": quantity,
                    "memo": "deposit"
                }
            })
        },{
            "account": 'atomicdropsx',
            "name": 'claimdrop',
            "authorization": [{
                "actor": id,
                "permission": "active"
            }],
            "data": json_to_bin({
                "code": "atomicdropsx",
                "action": "claimdrop",
                "args": {
                    "claimer": id,
                    "drop_id": dropseiei['drop_id'],
                    "claim_amount": dropseiei['count'],
                    "intended_delphi_median": median,
                    "referrer": "atomichub",
                    "country": "TH"
                }
            })
        }],
        "transaction_extensions":[]
    }).bytes_list
    #signatures = nft.sign_payer(req, tx.hex())
    try:
        req = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})
        req.options("https://public-wax-on.wax.io/wam/sign", headers={"origin":"https://all-access.wax.io"}, cookies={'session_token': session_token})
        signed = req.post(
            "https://public-wax-on.wax.io/wam/sign",
            headers={
                'origin': 'https://all-access.wax.io',
                'referer': 'https://all-access.wax.io/',
                'x-access-token': session_token,
                'content-type': 'application/json;charset=UTF-8',
            },
            json={
                "serializedTransaction": byteArrToArr(tx),
                "website": "wallet.wax.io",
                "description": "jwt is insecure",
                "freeBandwidth": True
            },
            timeout=120
        )
        if signed.status_code in [429, 502, 503, 504]:
            print("Sign createOffer Tx Server err. try again")
            raise ConnectionError
        if signed.status_code == 403:
            print("Sign createOffer tx CF 1020. try again in 30 sec")
            print(signed.text)
            raise ConnectionError
        if signed.status_code != 200:
            try:
                if signed.json()['message'] == 'Recaptcha token is invalid.':
                    print(signed.json()['message'])
                    print(f'try to solve Recaptcha again...')
                    raise ConnectionError
                elif signed.json()['message'] == 'Session Token is invalid or missing.':
                    print('sender Session Token is invalid or expire')
                    time.sleep(9999)
                else:
                    print(signed.json())
                    time.sleep(999999)
            except:
                print('sign createOffer err')
                print(f'code >>>>>>>>>>>>>>>>>>>{signed.status_code}')
                print(f'res >>>>>>>>>>>>>>>>>>>{signed.text}')
                time.sleep(99999)
        signatures = signed.json()["signatures"]
        push_create_offer = pushTx(signatures, tx)
        if push_create_offer['transaction_id'] == '':
            if push_create_offer['error']["what"] == 'Transaction exceeded the current CPU usage limit imposed on the transaction':
                print('Error: CPU usage limit!!')
                time.sleep(60)
            elif push_create_offer['error']["what"] == 'Expired Transaction':
                print('Error: Expired Transaction!!')
            else:
                print(
                    f'Error: {push_create_offer["error"]["details"][0]["message"]}')
                print('try again in 3 sec')
            raise ConnectionError
        return push_create_offer["transaction_id"]
    except (ConnectionError, Timeout, JSONDecodeError, ChunkedEncodingError, IndexError):
        return create_tran(req, sender, dropseiei)