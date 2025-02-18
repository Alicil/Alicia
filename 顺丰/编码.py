from urllib.parse import quote, unquote
import os

# 获取环境变量中的URL
url = os.environ.get('sfsyUrl')

if url:
    # 分割多账号
    urls = url.split('&')
    encoded_urls = []
    
    for single_url in urls:
        if not single_url:  # 跳过空值
            continue
            
        # 检查URL是否包含%3A或%253A (已编码的:)
        if '%253A' in single_url:
            # 双重解码
            decoded_url = unquote(unquote(single_url))
            # 重新编码
            encoded_url = quote(decoded_url, safe='')
        elif '%3A' in single_url:
            # 单重解码
            decoded_url = unquote(single_url)
            # 重新编码
            encoded_url = quote(decoded_url, safe='')
        elif single_url.startswith('https://mcs-mimp-web'):
            # 直接编码
            encoded_url = quote(single_url, safe='')
        else:
            print(f"URL格式不正确，需要以https://mcs-mimp-web开头: {single_url}")
            encoded_url = single_url
            
        encoded_urls.append(encoded_url)
    
    # 将编码后的多账号URL用&连接，设置回环境变量
    os.environ['sfsyUrl'] = '&'.join(encoded_urls)
else:
    print("未找到sfsyUrl环境变量")
