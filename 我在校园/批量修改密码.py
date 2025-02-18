import requests
import yaml
import json

# 加载 daka.yaml 文件中的用户信息
def load_users_from_yaml(yaml_file="daka.yaml"):
    with open(yaml_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)['users']

# 加载 jwsessions.json 文件中的 JWSESSION 信息
def load_jwsessions(jws_file="jwsessions.json"):
    with open(jws_file, "r", encoding="utf-8") as file:
        return json.load(file)

# 批量修改密码函数
def change_password_for_all_users():
    users = load_users_from_yaml()
    jwsessions = load_jwsessions()

    url = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/my/changePassword"
    
    for user in users:
        username = user['username']
        password = user['password']  # 原密码
        new_password = password  # 使用原密码作为新密码

        # 获取对应的 JWSESSION
        jws = jwsessions.get(username)
        if not jws:
            print(f"没有找到 {username} 对应的 JWSESSION，跳过...")
            continue

        # 设置请求的 headers
        headers = {
            "Host": "gw.wozaixiaoyuan.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua-platform": '""',
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 14; zh-cn; 2211133C Build/UKQ1.230804.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.118 Mobile Safari/537.36 XiaoMi/MiuiBrowser/18.2.200429 Edg/126.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "JWSESSION": jws,  # 使用对应的 JWSESSION
            "Content-Type": "application/json;charset=UTF-8",
            "sec-ch-ua": '""',
            "sec-ch-ua-mobile": "?1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://gw.wozaixiaoyuan.com/h5/mobile/basicinfo/index/my/changePassword",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": f"JWSESSION={jws}; WZXYSESSION={jws}"
        }

        # 设置请求的参数，使用相同的旧密码和新密码
        params = {
            "newPassword": new_password,
            "oldPassword": password,
            "code": ""  # 如果不需要验证码，保持空
        }

        # 发送修改密码请求
        response = requests.get(url, headers=headers, params=params)
        
        # 解析响应的内容
        try:
            response_json = response.json()
            code = response_json.get("code")
            message = response_json.get("message", "")
            
            if code == 0:
                print(f"{username} 的密码修改成功！")
            elif code == 1:
                print(f"{username} 的密码修改失败：{message}。")
            else:
                print(f"{username} 的密码修改失败，返回信息: {response_json}")
        except ValueError:
            print(f"解析 {username} 的响应时出错，返回内容: {response.text}")

# 执行批量修改密码
change_password_for_all_users()
