import json
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

# 配置变量
ClassID = '106428'  # 班级ID
X = '34.105225'     # 纬度
Y = '108.886025'    # 经度
ACC = ''            # 高度，未知
MyCookies = [
    'wxid=ollOC0atsaFyJBxh3jLC9g5UK9Y8$1730899462$7d93c01d563c659f9940b4e1a5a7a80d; s=jPl9yxd79c5BmmuNH2VZofoHWGZ3w0BHplsU1WBQ; remember_student_59ba36addc2b2f9401580f014c7f58ea4e30989d=3174165%7CxwFWa866RUDXNojh4Ai45rE0igf4auDTzBwCIPQvMPiCzYzH2RNaE3HtdrW5%7C; Hm_lvt_362de400d3fe4117e8e3513a52c0da9d=1728478331,1730899464; HMACCOUNT=236B1084897AECE1; Hm_lpvt_362de400d3fe4117e8e3513a52c0da9d=1730899474',
    'Hm_lpvt_362de400d3fe4117e8e3513a52c0da9d=1732173745; Hm_lvt_362de400d3fe4117e8e3513a52c0da9d=1732156646,1732173738; s=I8ngB7wCLoWymxvqXDg97ye9MQb8W5SlKY51l3iD; HMACCOUNT=08080ADB532AA300; remember_student_59ba36addc2b2f9401580f014c7f58ea4e30989d=3174085%7ClzUwKSgLw9HUoXg0pfqAkb2nqGO7TYsD2ZXJbPFvvku5gWuuqB8psqcvHghX%7C; wxid=ollOC0ZCXGRoj4MFucvCm9GLJE24$1732173736$1dbfba4f133db3db9766d548455f4fb2',
    # 你可以继续添加更多的 MyCookie
]
url = f'http://k8n.cn/student/course/{ClassID}/punchs'
headers_template = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; AKT-AK47 Build/USER-AK47; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36',
    'Referer': f'http://k8n.cn/student/course/{ClassID}',
    'X-Requested-With': 'com.tencent.mm',
    'Accept-Encoding': 'gzip, deflate',
}

# 遍历每个用户的 Cookie 并签到
for idx, MyCookie in enumerate(MyCookies, start=1):
    print(f"\n正在处理第 {idx} 个用户...")

    # 更新请求头中的 Cookie
    headers = headers_template.copy()
    headers['Cookie'] = MyCookie

    # 获取签到任务
    response = requests.get(url, headers=headers)
    print("响应状态码:", response.status_code)

    if response.status_code != 200:
        print("获取签到任务失败，跳过当前用户。")
        continue

    # 使用 BeautifulSoup 解析任务页面
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找 GPS 定位签到任务
    gps_pattern = re.compile(r'punch_gps\((\d+)\)')
    gps_tasks = gps_pattern.findall(response.text)
    print("找到 GPS 定位签到任务:", gps_tasks)

    # 查找扫码签到任务
    qr_pattern = re.compile(r'punchcard_(\d+)')
    qr_tasks = qr_pattern.findall(response.text)
    print("找到扫码签到任务:", qr_tasks)

    # 合并所有签到任务
    tasks = gps_tasks + qr_tasks
    if not tasks:
        print("未找到签到任务，跳过当前用户。")
        continue

    # 执行签到任务
    for task_id in tasks:
        sign_url = f"http://k8n.cn/student/punchs/course/{ClassID}/{task_id}"
        payload = {
            'id': task_id,
            'lat': X,
            'lng': Y,
            'acc': ACC,
            'res': '',
            'gps_addr': ''
        }

        sign_response = requests.post(sign_url, headers=headers, data=payload)
        if sign_response.status_code == 200:
            print(f"任务 {task_id} 签到成功！")
        else:
            print(f"任务 {task_id} 签到失败，状态码: {sign_response.status_code}。")

print("\n所有用户签到处理完成，程序结束。")
