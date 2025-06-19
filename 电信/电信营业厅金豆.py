import os
import re
import sys
import ssl
import time
import json
import execjs
import base64
import random
import certifi
import aiohttp
import asyncio
import certifi
import datetime
import requests
import binascii
from bs4 import BeautifulSoup

from http import cookiejar
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector
from concurrent.futures import ThreadPoolExecutor
run_num=os.environ.get('reqNUM') or "40"
diffValue=2
'''
变量: chinaTelecomAccount
格式: 手机号@服务密码
多个变量&隔开
'''
MAX_RETRIES = 3
RATE_LIMIT = 10  # 每秒请求数限制

class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate_limit
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.rate_limit)
            self.updated_at = now

class AsyncSessionManager:
    def __init__(self):
        self.session = None
        self.connector = None

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self.connector = TCPConnector(ssl=ssl_context, limit=1000)
        self.session = ClientSession(connector=self.connector)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()

async def retry_request(session, method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.sleep(1)
            async with session.request(method, url, **kwargs) as response:
                return await response.json() 
                # return await response.json() 
            
        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"请求失败，第 {attempt + 1} 次重试: {e}")
            if attempt == MAX_RETRIES - 1:
                raise 
            await asyncio.sleep(2 ** attempt)

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
    
def printn(m):  
    print(f'\n{m}')

context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书

class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

requests.packages.urllib3.disable_warnings()
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
ss = requests.session()
ss.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}    
ss.mount('https://', DESAdapter())       
ss.cookies.set_policy(BlockAll())
runTime = 0
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''
public_key_xbk = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB",
-----END PUBLIC KEY-----'''
public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


public_key_xbk = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB
-----END PUBLIC KEY-----'''

def get_first_three(value):
    # 处理数字情况
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")

def run_Time(hour,miute,second):    
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time

def encrypt(text):    
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()
    
def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()

    

    
    

def encrypt_para(plaintext):
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    
    # 计算密钥参数
    key_size = public_key.size_in_bytes()  # 获取密钥实际字节长度
    max_chunk = key_size - 11  # 计算单块最大长度
    
    # 分块加密
    ciphertext = b""
    for i in range(0, len(plaintext.encode()), max_chunk):
        chunk = plaintext.encode()[i:i+max_chunk]
        ciphertext += cipher.encrypt(chunk)
    
    return binascii.hexlify(ciphertext).decode() 
    
def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def xbkb64(plaintext):
    public_key = RSA.import_key(public_key_xbk)
    cipher = PKCS1_v1_5.new(public_key)
    
    # 计算密钥参数
    key_size = public_key.size_in_bytes()  # 获取密钥实际字节长度
    max_chunk = key_size - 11  # 计算单块最大长度
    
    # 分块加密
    ciphertext = b""
    for i in range(0, len(plaintext.encode()), max_chunk):
        chunk = plaintext.encode()[i:i+max_chunk]
        ciphertext += cipher.encrypt(chunk)
    
    return base64.b64encode(ciphertext).decode()

# AES加密函数
def aes_encrypt(data, key =  "34d7cb0bcdf07523"):
    if type(data) == dict:
        data = json.dumps(data)
    key_bytes = key.encode('utf-8')
    data_bytes = data.encode('utf-8')
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
    return ct_bytes.hex()



def getApiTime(api_url):
        try:
             with requests.get(api_url) as response:
                if(not response or not response.text):
                    return time.time()
                json_data = json.loads(response.text)
                if (json_data.get("api")and json_data.get("api")not in("time") ):
                    timestamp_str = json_data.get('data', {}).get('t', '')
                else:
                    timestamp_str = json_data.get('currentTime', {}) 
                timestamp = int(timestamp_str) / 1000.0  # 将毫秒转为秒
                difftime=time.time()-timestamp
                return difftime;   
        except Exception as e:
            print(f"获取时间失败: {e}")
            return 0; 


def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}},verify=certifi.where()).json()
    l = r['responseData']['data']['loginSuccessResult']
    if l:
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = get_ticket(phone,l['userId'],l['token']) 
        return ticket
    return False
def ascii_add_2(number_str):	
    transformed = ''.join(chr(ord(char) + 2) for	char in number_str)
    return transformed	
def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
   
    
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#10.5.0#channel1#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": encode_phone(phone)}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "1", "systemVersion": "13", "authentication": encode_phone(password)}}}).json()    
    l = r['responseData']['data']
    
    if l and l.get('loginSuccessResult'):
        l = l.get('loginSuccessResult')
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = get_ticket(phone,l['userId'],l['token']) 
        return ticket
    else:
        print(r)
       
    return False
async def exchangeForDay(phone, session, run_Time, rid, stime):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await conversionRights(phone, rid,session)
    tasks = [asyncio.create_task(delayed_conversion(i * stime)) for i in range(int(run_Time))]
    await asyncio.gather(*tasks)
def get_ticket(phone,userId,token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},verify=certifi.where())
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:        
        return False
    return decrypt(tk[0])

async def exchange(s, phone, title, aid,jsexec, ckvalue):
    try:
        url="https://wapact.189.cn:9001/gateway/stand/detailNew/exchange"
        # getck = await asyncio.to_thread(jsexec.call, "getck") # 两种方式，一种用ck，一种用后缀
        # getck = getck.split(';')[0].split('=')
        # ckvalue[getck[0]] = getck[1]

        # async with s.post(url, cookies=ckvalue, json={"activityId": aid}) as response:

        # 通过 retry_request 实现重试机制
        # response = await retry_request(s, 'POST', get_url, cookies=ckvalue, json={"activityId": aid})

        get_url = await asyncio.to_thread(jsexec.call,"getUrl", "POST",url)
        async with s.post(get_url, cookies=ckvalue, json={"activityId": aid}) as response:
            pass
    except Exception as e:
        print(e)

       


async def userCoinInfo(phone,session):
    value = {
        "phone": phone
    }
    paraV=encrypt_para(value)
    bd=await asyncio.to_thread(js.call, "main")
    bd = bd.split("=")
    ck[bd[0]] = bd[1]
    data = session.post('https://wappark.189.cn/jt-sign/api/home/userCoinInfo',json={"para":paraV},cookies=ck).json()
    if data.get('code') == 401:
        print(f"获取失败:{data},原因大概是sign过期了")
        return None
    print(f'金豆余额:{data.get("totalCoin")}')
    return data
async def conversionRights(phone, aid,session):

    value = {
        "phone": phone,
        "rightsId": aid
    }
    paraV=encrypt_para(value)
    bd=await asyncio.to_thread(js.call, "main")
    bd = bd.split("=")
    ck[bd[0]] = bd[1]
    response = session.post('https://wappark.189.cn/jt-sign/paradise/conversionRights',json={"para":paraV},cookies=ck)
    print("dh", response.text)
    return
    login = response.json()
    printn(f"{get_first_three(phone)},{str(datetime.datetime.now())[11:23]}:{login} ")

async def getLevelRightsList(phone,session):
    value = {
        "phone": phone
    }
    paraV=encrypt_para(value)
    bd=await asyncio.to_thread(js.call, "main")
    bd = bd.split("=")
    ck[bd[0]] = bd[1]
    data = session.post('https://wappark.189.cn/jt-sign/paradise/getLevelRightsList',json={"para":paraV},cookies=ck).json()
    if data.get('code') == 401:
        print(f"获取失败:{data},原因大概是sign过期了")
        return None
    current_level = int(data['currentLevel'])
    key_name = 'V' + str(current_level)
    for item in data.get(key_name, []):
        if "金豆" in item['righstName'] or "话费" in item['righstName']:
            value = {
                "phone": phone,
                "rightsId": item['id'],
                "receiveCount":item['receiveType'] 
            }
            paraV=encrypt_para(value)
            bd=await asyncio.to_thread(js.call, "main")
            bd = bd.split("=")
            ck[bd[0]] = bd[1]
            response = session.post('https://wappark.189.cn/jt-sign/paradise/getConversionRights',json={"para":paraV},cookies=ck)           
            
            if response.json().get("rightsStatus", "已领取") in "已领取#已兑换":
                print(f"等级权益:{item['righstName']}已兑换")
            else:
                print(f"领取等级权益:{item['righstName']}")
                await conversionRights(phone, item['id'] ,session)        
                await asyncio.sleep(10)
        
    

async def continueSignRecords(phone, session):
    try:
        payload = {
            'phone': phone
        }
        encrypted_payload = encrypt_para(payload)
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/webSign/continueSignRecords',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        types = 0
        if res_code == 0:
            if data.get('continue15List'):
                types='15'
            
            if data.get('continue28List'):
                types= '28'
            if types != 0:
                payload = {
                    'phone': phone,
                    'type': types
                }
                encrypted_payload = encrypt_para(payload)
                bd=await asyncio.to_thread(js.call, "main")
                bd = bd.split("=")
                ck[bd[0]] = bd[1]
                response = session.post(
                    'https://wappark.189.cn/jt-sign/webSign/exchangePrize',
                    json={'para': encrypted_payload},
                    cookies=ck
                )
                
                try:
                    print("抽奖获得:"+response.json()['prizeDetail']['biz']['title'])
                except:
                    print("抽奖获得:"+response.text)
                
                
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询连签抽奖状态错误[{res_code}]: {error_message}')
    

    except Exception as e:
        print(e)


async def homepage(phone, session):
    try:
        payload = {
            'phone': phone,
            "shopId": "20001",
             "type": "hg_qd_zrwzjd"
        }
        encrypted_payload = encrypt_para(payload)
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/webSign/homepage',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            head_data = data.get('data', {}).get('head', {})
            code = head_data.get('code', -1)
            
            if code == 0:
                ad_items = data.get('data', {}).get('biz', {}).get('adItems', [])
                for ad_item in ad_items:
                    if ad_item.get('taskState') in ['0', '1']:
                        
                        content_one = ad_item.get('contentOne')
                        reward_id = ad_item.get('rewardId')
                        
                        if content_one == '3':
                            if reward_id:
                                await receive_reward(phone, session, ad_item)
                        elif content_one == '5':
                            await openMsg(phone, session, ad_item)
                        elif content_one == '6':
                            
                            await sharingGetGold(phone, session)
                        elif content_one in ['10', '13']:
                            continue
                            if not xtoken:
                                await get_usercode()
                            if xtoken:
                                await watch_live_init()
                        elif content_one == '18':
                            await polymerize(phone, session, ad_item)
                
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询连签抽奖状态错误[{res_code}]: {error_message}')
    

    except Exception as e:
        print(e)

async def receive_reward(phone, session, reward_info):
    try:
        title = reward_info.get('title', '').split(' ')[0] if reward_info.get('title') else ''
        payload = {
            'phone': phone,
            'rewardId': reward_info.get('rewardId', '')
        }
        
        encrypted_payload = encrypt_para(payload) 
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/receiveReward',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            result_msg = data.get('resoultMsg', '')
            print(f"领取任务[{title}]奖励成功: {result_msg}")
        else:
            error_message = error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f"领取任务[{title}]奖励错误[{res_code}]: {error_message}")
    
    except Exception as e:
        print(f"领取任务时发生错误: {e}")
async def polymerize(phone, session, reward_info):
    try:
        title = reward_info.get('title', '').split(' ')[0] if reward_info.get('title') else ''
        payload = {
            'phone': phone,
            'jobId': reward_info.get('taskId', '')
        }
        encrypted_payload = encrypt_para(payload)
        
        
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/webSign/polymerize',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            result_msg = data.get('resoultMsg', '')
            print(f"完成任务[{title}]成功: {result_msg}")
        else:
            error_message = error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f"完成任务[{title}]错误[{res_code}]: {error_message}")
    
    except Exception as e:
        print(f"完成任务发生错误: {e}")
async def openMsg(phone, session, reward_info):
    try:
        title = reward_info.get('title', '').split(' ')[0] if reward_info.get('title') else ''
        payload = {
            'phone': phone,
        }
        encrypted_payload = encrypt_para(payload)
        
        
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/openMsg',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            result_msg = data.get('resoultMsg', '')
            print(f"完成任务[{title}]成功: {result_msg}")
        else:
            error_message = error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f"完成任务[{title}]错误[{res_code}]: {error_message}")
    
    except Exception as e:
        print(f"完成任务发生错误: {e}")

async def sharingGetGold(phone, session):
    return
    try:
        timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        encrypted_payload={"headerInfos": {"code": "sharingGetGold", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": load_token[phone]['token'], "userLoginName": encode_phone(phone)}, "content": {"attach": "test", "fieldData": {"shareSource": "3", "userId": load_token[phone]['userId'], "account": encode_phone(phone)}}}
        response = session.post(
            'https://appfuwu.189.cn:9021/query/sharingGetGold',
            json={'para': data},          
        )
        data = response.json()
        print(data)
        res_code = data.get('responseData', {}).get('resultCode', response.status_code)
        if res_code == "0000":
            
            print("分享成功")
        else:
            
            print("分享失败")
    
    except Exception as e:
        print(f"分享失败: {e}")

async def getParadiseInfo(phone, session):
    try:
        payload = {
            'phone': phone
        }
        encrypted_payload = encrypt_para(payload)
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/getParadiseInfo',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        can_feed=1
        res_code = data.get('resoultCode', response.status_code)
        if res_code == "0":
            head_data = data.get('userInfo', {}).get('levelInfoMap', {})
            level = head_data.get('level', -1)
            
            await food(phone, session)
                
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询宠物等级失败[{res_code}]: {error_message}')
            return
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/paradise/getParadiseInfo',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        
        res_code = data.get('resoultCode', response.status_code)
        
        if res_code == "0":
            head_data = data.get('userInfo', {}).get('levelInfoMap', {})
            
            msg = f"宠物等级[Lv.{head_data.get('level', -1)}], 升级进度: {head_data.get('growthValue', -1)}/{head_data.get('fullGrowthCoinValue', -1)}"
            print(msg)
                
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询宠物等级失败[{res_code}]: {error_message}')
            return
    except Exception as e:
        print(e)
async def food(phone, session):
    try:
        payload = {
            'phone': phone
        }
        encrypted_payload = encrypt_para(payload)
        
        for feedtimes in range(10):
            bd=await asyncio.to_thread(js.call, "main")
            bd = bd.split("=")
            ck[bd[0]] = bd[1]
            response = session.post(
                'https://wappark.189.cn/jt-sign/paradise/food',
                json={'para': encrypted_payload},
                cookies=ck
            )
            feedtimes += 1
            
            data = response.json()
            
            res_code = data.get('resoultCode', response.status_code)
            if res_code == "0":
                print(f"第{feedtimes}次喂食: {data.get('resoultMsg', '成功')}")
                
                    
            else:
                error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
                print(f'第{feedtimes}次喂食失败[{res_code}]: {error_message}')
                return
    

    except Exception as e:
        print(e)
async def userStatusInfo(phone, session):
    try:
        payload = {
            'phone': phone
        }
        encrypted_payload = encrypt_para(payload)
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/api/home/userStatusInfo',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            head_data = data.get('data', {})
            
            if head_data.get('isSign', 1):
                print("今天已签到")
            else:
                await doSign(phone, session)

        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询账户签到状态错误[{res_code}]: {error_message}')
            return
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response = session.post(
            'https://wappark.189.cn/jt-sign/api/home/userStatusInfo',
            json={'para': encrypted_payload},
            cookies=ck
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == 0:
            head_data = data.get('data', {})
            
            print(f"已签到{head_data.get('continuousDay', 0)}天, 连签{head_data.get('signDay', 0)}天")
            if head_data.get('isSeven', 0):
                payload = {
                    'phone': phone,
                    'type': '7'
                }
                encrypted_payload = encrypt_para(payload)
                bd=await asyncio.to_thread(js.call, "main")
                bd = bd.split("=")
                ck[bd[0]] = bd[1]
                response = session.post(
                    'https://wappark.189.cn/jt-sign/webSign/exchangePrize',
                    json={'para': encrypted_payload},
                    cookies=ck
                )
                try:
                    print("抽奖获得:"+response.json()['prizeDetail']['biz']['title'])
                except:
                    print("抽奖获得:"+response.text)
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'查询账户签到状态错误[{res_code}]: {error_message}')
            return            
    except Exception as e:
        print(e)
async def doSign(phone, session):
    try:
        payload = {
            'phone': phone,
            "date": int(time.time()*1000),
            "sysType": "20004"
        }
        
        encrypted_payload = aes_encrypt(payload)
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        #https://wapside.189.cn/jt-sign/api/home/sign
        response = ss.post(
            'https://wappark.189.cn/jt-sign/api/home/sign',
            json={'encode': encrypted_payload},
            cookies=ck,headers=session.headers
        )
        
        data = response.json()
        res_code = data.get('resoultCode', response.status_code)
        if res_code == '0':
            head_data = data.get('data', {})
            
            if head_data.get('code', False):
                print(f"签到成功，获得{head_data.get('coin', 0)}金豆")
            else:
                print(f"签到失败[{head_data.get('code', 0)}]: {head_data.get('msg', '')}")

        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f"签到错误[{res_code}]: {error_message}")
            return

    except Exception as e:
        print(e)        
  
async def getSign(ticket,session):
    try:
        bd=await asyncio.to_thread(js.call, "main")
        bd = bd.split("=")
        ck[bd[0]] = bd[1]
        response_data = session.get('https://wappark.189.cn/jt-sign/ssoHomLogin?ticket=' + ticket,cookies=ck).json()
        if response_data.get('resoultCode') == '0':
            sign = response_data.get('sign')
            return sign
        else:
            print(f"获取sign失败[{response_data.get('resoultCode')}]: {response_data}")
    except Exception as e:
        print(e)
    return None

async def login_request(ss,url,payload):
    global ckvalue,js_codeRead
    url = "https://wapact.189.cn:9001/unified/user/login"
    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://wapact.189.cn:9001',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'Content-Type': 'application/json;charset=UTF-8'
    }
    response = ss.post(url, headers=headers, data=json.dumps(payload))
    rsCK = re.findall('yiUIIlbdQT3fO=([^;]+)',response.headers['Set-Cookie'])[0]
    # print(response.status_code)
    if response.status_code == 412:
        print("检测到瑞数特征码412,正在尝试调用js")
    else:
        print("未检测到瑞数.")
        return  response,None,rsCK
    html=etree.HTML(response.text)
    arg1=html.xpath('//meta/@content')[-1]
    arg2=html.xpath('//script/text()')[0]
    arg3=html.xpath('//meta/@id')[-1]
    js_code = js_codeRead.replace("contentCODE", arg1).replace('"tsCODE"', arg2).replace('"tsID"',f'"{arg3}"')
    
    jsexec = execjs.compile(js_code)
    ck=await asyncio.to_thread(jsexec.call, "getck")
    get_url=await asyncio.to_thread(jsexec.call,"getUrl","POST",url)
    def parse_cookies(ck):
        cookies = {}
        for part in ck.split(';'):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                if 'path' not in key and 'expires' not in key and 'Secure' not in key and 'SameSite' not in key:
                    cookies[key] = value
        return cookies
    ck=parse_cookies(ck)
    ck["yiUIIlbdQT3fO"] = rsCK
    ckvalue=ck
    res=ss.post(get_url, headers=headers,data=json.dumps(payload),cookies=ckvalue)
    if res.status_code == 200:
        print("瑞数返回状态码200,开始下一步.")
        return res,jsexec,ckvalue
    else:
        print("瑞数破解失败,调用重试机制")
        return res,jsexec,None
    # return res,jsexec,ckvalue#ckvalue这里直接返回，没直接塞session里面.
async def get_usercode(phone, session,ticket):
    
    try:
        timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        data = {"userID":ticket,
            "version": "9.3.3",
            "type": "room",
            "l": "renwu"
        }
        response = session.get(
            'https://xbk.189.cn/xbkapi/api/auth/jump',
            json=data,
            allow_redirects=False
        )
        l=response.headers["location"]
        usercode= l.split("usercode=")[1].split("&")[0]
        
        response = session.post(
            'https://xbk.189.cn/xbkapi/api/auth/userinfo/codeToken',
            json={"usercode":usercode},          
        )
        data = response.json()
        res_code = data.get("code", 0)
        
        if res_code == 0:
            xtoken = data.get("data", {}).get("token", "")
            xtoken = xbkb64(xtoken)   
            
            session.headers["Authorization"] = "Bearer " + xtoken
            return 1

        
    except Exception as e:
        print(f"星播客登录失败: {e}")
async def watchLiveInit(session):
    
    try:
        liveId = int(str(time.time())[-3:]) + 1000
        data = {"liveId":liveId,
            "period":"1"
        }
        response = session.post(
            'https://xbk.189.cn/xbkapi/lteration/liveTask/index/watchLiveInit',
            json=data,          
        )

        
        data = response.json()
        res_code = data.get("code", -1)
        if res_code == 0:
            print(f'开始观看直播[{liveId}],等待15s')
            await asyncio.sleep(15)
            await watchLive(session,liveId,data.get("data", ""))
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'开始观看直播[{liveId}]失败[{res_code}]: {error_message}')
            return         
    
    except Exception as e:
        print(f"开始观看直播失败: {e}")
async def watchLive(session, liveId, data):
    
    try:
        data = {"liveId":liveId,
            "period": "1",
            "key":data
        }
        response = session.post(
            'https://xbk.189.cn/xbkapi/lteration/liveTask/index/watchLive',
            json=data,          
        )

        
        data = response.json()
        res_code = data.get("code", -1)
        if res_code == 0:
            print(f"观看直播[{liveId}]成功");
            await watchLiveInit(session);
        else:
            error_message = data.get('msg') or data.get('resoultMsg') or data.get('error') or ''
            print(f'观看直播{liveId}失败[{res_code}]: {error_message}')
            return         
    
    except Exception as e:
        print(f"观看直播失败: {e}")
async def ks(phone, ticket):
    session = requests.Session()
    session.mount('https://', DESAdapter())
    session.cookies.set_policy(BlockAll())
    session.verify = False  # 禁用证书验证
    sign =await getSign(ticket,session)
    if sign:
        print(f"当前时间:{str(datetime.datetime.now())[11:23]}获取到了Sign:"+sign)
        session.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","sign":sign}
    else:
        print("未能获取sign。")
        return
    # await asyncio.sleep(10)直接延迟也行，或者用下面的等待一段时间。之所以这样是要先获取sign省一些步骤。
    await userCoinInfo(phone,session);
    await continueSignRecords(phone,session);
    await userStatusInfo(phone,session);
    #await getLevelRightsList(phone,session);
    await homepage(phone,session);
    await getParadiseInfo(phone,session);
    await userCoinInfo(phone,session);
    try:
        if await get_usercode(phone,session,ticket) == 1:
            await watchLiveInit(session)    
    except:
        pass

async def main():
    global js_codeRead
    tasks = []
    # with open("e:/work/vscode1/python/电信/rs6.js", "r", encoding="utf-8") as f:
    #     js_codeRead = f.read()
    phone_list = PHONES.split('&')  
    # diffValue=len(phone_list)
    for phoneV in phone_list:
        value = phoneV.split('#')
        phone, password = value[0], value[1]
        printn(f'{get_first_three(phone)}开始登录')
        ticket = False
        
        #ticket = get_userTicket(phone)  
        
        if phone in load_token:
            printn(f'{phone} 使用缓存登录')
            ticket = get_ticket(phone,load_token[phone]['userId'],load_token[phone]['token'])
        
        if ticket == False:
            printn(f'{phone} 使用密码登录')
            ticket = userLoginNormal(phone,password)
           
        if ticket:
            
            if dxc:
                tasks.append(ks(phone, ticket))
            else:
                await ks(phone, ticket)
        else:
            printn(f'{phone} 登录失败')
    if dxc:
        await asyncio.gather(*tasks)
def first_request(res=''):
    global js, fw
    url = 'https://wapside.189.cn:9001/jt-sign/ssoHomLogin?ticket='
    if res == '':
        response = ss.get(url)
        res =  response.text
    soup = BeautifulSoup(res, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in str(script):
            rsurl =  re.findall('src="([^"]+)"', str(script))[0]
            
        if '$_ts=window' in script.get_text():
            ts_code = script.get_text()
            
    
    urls  = url.split('/')
    rsurl = urls[0] + '//' + urls[2] + rsurl
    #print(rsurl)    
    ts_code += ss.get(rsurl).text
    content_code = soup.find_all('meta')[1].get('content')
    
    js_code = js_code_ym.replace('content_code', content_code).replace("'ts_code'", ts_code)
    js = execjs.compile(js_code) 

    for cookie in ss.cookies:
        ck[cookie.name] = cookie.value
    return content_code, ts_code, ck 
PHONES=os.environ.get('chinaTelecomAccount') or "17777777777@182838"


js_code_ym = '''
delete __filename
delete __dirname
ActiveXObject = undefined

window = global;


content="content_code"


navigator = {"platform": "Linux aarch64"}
navigator = {"userAgent": "CtClient;11.0.0;Android;13;22081212C;NTIyMTcw!#!MTUzNzY"}

location={
    "href": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html",
    "origin": "https://wapact.189.cn:9001",
    "protocol": "https:",
    "host": "wapact.189.cn:9001",
    "hostname": "wapact.189.cn",
    "port": "9001",
    "pathname": "/JinDouMall/JinDouMall_independentDetails.html",
    "search": "",
    "hash": ""
}
i = {length: 0}
base = {length: 0}
div = {
    getElementsByTagName: function (res) {
        console.log('div中的getElementsByTagName：', res)
        if (res === 'i') {
            return i
        }
    return '<div></div>'

    }
}

script = {

}
meta = [
    {charset:"UTF-8"},
    {
        content: content,
        getAttribute: function (res) {
            console.log('meta中的getAttribute：', res)
            if (res === 'r') {
                return 'm'
            }
        },
        parentNode: {
            removeChild: function (res) {
                console.log('meta中的removeChild：', res)
                
              return content
            }
        },
        
    }
]
form = '<form></form>'


window.addEventListener= function (res) {
        console.log('window中的addEventListener:', res)
        
    }
    

document = {

   
    createElement: function (res) {
        console.log('document中的createElement：', res)
        
        
       if (res === 'div') {
            return div
        } else if (res === 'form') {
            return form
        }
        else{return res}
            
        


    },
    addEventListener: function (res) {
        console.log('document中的addEventListener:', res)
        
    },
    appendChild: function (res) {
        console.log('document中的appendChild：', res)
        return res
    },
    removeChild: function (res) {
        console.log('document中的removeChild：', res)
    },
    getElementsByTagName: function (res) {
        console.log('document中的getElementsByTagName：', res)
        if (res === 'script') {
            return script
        }
        if (res === 'meta') {
            return meta
        }
        if (res === 'base') {
            return base
        }
    },
    getElementById: function (res) {
        console.log('document中的getElementById：', res)
        if (res === 'root-hammerhead-shadow-ui') {
            return null
        }
    }

}

setInterval = function () {}
setTimeout = function () {}
window.top = window


'ts_code'



function main() {
    cookie = document.cookie.split(';')[0]
    return cookie
}


'''   
load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
except:
    load_token = {}
ck = {}
tz = {}



dxc = 1
if __name__ == "__main__":
    ss = requests.session()
    ss.mount('https://', DESAdapter())       
    first_request()
    asyncio.run(main())
    print("所有任务都已执行完毕!")
    

