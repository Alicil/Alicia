import json
import urllib.parse
from base64 import b64encode

import yaml
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


# AES 加密函数
def encrypt(text, key):
    text = str(text)
    key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    padded_text = pad(text.encode('utf-8'), AES.block_size)
    encrypted_text = cipher.encrypt(padded_text)
    return b64encode(encrypted_text).decode('utf-8')


# 从 JSON 文件加载 JWSESSION
def load_jwsessions():
    if not os.path.exists("jwsessions.json"):
        return {}

    try:
        with open("jwsessions.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, ValueError):
        return {}


def save_jwsessions(jwsessions, file_path='jwsessions.json'):
    with open(file_path, 'w') as file:
        json.dump(jwsessions, file, indent=4)


def load_users_from_yaml():
    with open("daka.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# 登录函数
def Login(username, password, school):
    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/119.0.0.0"
    }
    url_school_list = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/getSchoolList"
    response_school = requests.get(url_school_list, headers=headers)
    school_data = response_school.json()['data']

    school_id = next((item['id'] for item in school_data if item['name'] == school), None)
    if not school_id:
        print(f"未找到学校 '{school}'。")
        return False

    key = (str(username) + "0000000000000000")[:16]
    encrypted_password = encrypt(password, key)

    login_url = 'https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username'
    params = {
        "schoolId": school_id,
        "username": username,
        "password": encrypted_password
    }
    login_response = requests.post(login_url, data=params, headers=headers)
    login_data = login_response.json()

    if login_data['code'] == 0:
        print(f"{username} 登录成功！")
        jws = login_response.headers['Set-Cookie'].split('JWSESSION=')[1].split(';')[0]
        return jws
    else:
        print(f"{username} 登录失败。")
        return False


def get_areaJSON(areaList):
    if not areaList:
        return {}
    area = areaList[0]
    areaJSON = {
        'type': area.get("shape", 0),
        'circle': {
            'latitude': area.get("latitude", ""),
            'longitude': area.get("longitude", ""),
            'radius': area.get("radius", 0)
        },
        'id': area.get("id", ""),
        'name': area.get("name", "")
    }
    return areaJSON


# 请求逆地理编码并生成打卡数据
def request_address(location, areaJSON, timeout=3000):
    location = location.split(',')
    url = f"https://apis.map.qq.com/ws/geocoder/v1/?key=4G6BZ-HWECZ-GWFX6-ZSFA7-JW34J-C6FRZ&location={location[1]},{location[0]}"

    try:
        response = requests.get(url, timeout=timeout / 1000)
        result = response.json()
        if result['status'] == 0:
            print("地址信息获取成功。")
            address_component = result['result']['address_component']
            address_reference = result['result']['address_reference']
            ad_info = result['result']['ad_info']
            data = {
                "inArea": "1",
                "longitude": location[0],
                "province": address_component['province'],
                "latitude": location[1],
                "streetcode": address_reference['street']['id'],
                "street": areaJSON['name'],
                "areaJSON": json.dumps(areaJSON, ensure_ascii=False),
                "citycode": ad_info['city_code'],
                "city": address_component['city'],
                "nationcode": ad_info['nation_code'],
                "adcode": ad_info['adcode'],
                "district": address_component['district'],
                "country": '中国',
                "towncode": address_reference['town']['id'],
                "township": address_reference['town']['title']
            }
            # print(data)
            # return data
            return json.dumps(data, ensure_ascii=False)
        else:
            print("地址信息获取失败。")
            return None
    except requests.exceptions.RequestException as e:
        print(f"错误：{e}")
        return None


# 获取打卡日志并进行打卡
def get_sign_logs(jws, page=1, size=10):
    sign_url = "https://gw.wozaixiaoyuan.com/sign/mobile/receive/getMySignLogs"
    headers = {
        "JWSESSION": jws,
        "User-Agent": "Mozilla/5.0"
    }
    params = {"page": page, "size": size}
    response = requests.get(sign_url, params=params, headers=headers)
    sign_data = response.json()
    # print(sign_data)

    if sign_data['code'] == 0:
        return sign_data
    else:
        print("获取打卡日志失败。")
        return None


# 签到函数
import os
import requests
from datetime import datetime


def doPunchIn(jws, log_id, school_id, sign_id, sign, miao_code, name,timeout=3000):
    url = f"https://gw.wozaixiaoyuan.com/sign/mobile/receive/doSignByArea?id={log_id}&schoolId={school_id}&signId={sign_id}"
    headers = {
        "Cookie": f"JWSESSION={jws}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=sign.encode('utf-8'), timeout=timeout / 1000)
    result = response.json()
    print(result)

    nowtime = datetime.now()  # 获取当前时间以用于通知

    if result['code'] == 0:
        print("打卡成功！")
        punch_status = "成功😊"
        #punch_status = "今天打卡成功了哦😊😊😊"
    else:
        message = result.get('message', '未知错误')
        print(f"打卡失败，原因: {result}")
        punch_status = f"失败😭，因为{message}"
        #punch_status = f"打卡失败😝😝😝，因为： {result}"

    # 如果提供了 MIAO_CODE，则通过喵推送发送通知
    if miao_code:
        baseurl = "https://miaotixing.com/trigger"
        body = {
            "id": miao_code,
            "text": "{}同学今天打卡{}\n打卡时间：{}".format(name,
                punch_status, nowtime.strftime("%Y-%m-%d %H:%M:%S")
            ),
        }
        requests.post(baseurl, data=body)
        print("消息已通过 喵推送 进行通知，请检查推送结果")
    else:
        print("未设置 MIAO_CODE，跳过通知。")


def is_jwsession_expired(jws):
    check_url = "https://gw.wozaixiaoyuan.com/health/mobile/health/getBatch"
    headers = {
        "Host": "gw.wozaixiaoyuan.com",
        "Cookie": f"JWSESSION={jws}",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(check_url, headers=headers)
    result = response.json()

    if result['code'] == 103:
        print("JWSESSION 已过期。")
        return True
    elif result['code'] == 0:
        print("JWSESSION 有效。")
        return False
    else:
        print(f"检测 JWSESSION 时出错: {result}")
        return True  # 默认为过期状态


def main():
    users = load_users_from_yaml()
    jwsessions = load_jwsessions()

    for user in users['users']:
        username = user['username']
        password = user['password']
        school = user['school']
        miao_code = user.get('MIAO_CODE')
        name = user.get('name')
        jws = jwsessions.get(username)

        if jws and not is_jwsession_expired(jws):
            print(f"使用保存的 JWSESSION 登录 {username}。")
        else:
            jws = Login(username, password, school)
            if jws:
                jwsessions[username] = jws
                save_jwsessions(jwsessions)
            else:
                print(f"{username} 登录失败，跳过...")
                continue

        sign_logs = get_sign_logs(jws)
        if sign_logs:
            first_log = sign_logs['data'][0]  # 获取第一个签到信息
            for area in first_log['areaList']:
                sign_data = request_address(f"{area['longitude']},{area['latitude']}",
                                            get_areaJSON(first_log.get('areaList', [])))
                if sign_data:
                    doPunchIn(jws, first_log['id'], first_log['schoolId'], first_log['signId'], sign_data, miao_code, name)
                else:
                    print("无法获取地址信息，跳过打卡...")
        else:
            print(f"未能获取 {username} 的打卡日志，跳过...")


if __name__ == "__main__":
    main()