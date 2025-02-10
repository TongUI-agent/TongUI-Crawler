#!/usr/bin/env Python
# -*- coding: utf-8 -*-

"""
使用requests请求代理服务器
请求http和https网页均适用
"""

import requests

# 提取代理API接口，获取1个代理IP
def get_proxy_host_port():
    token_url = "https://auth.kdlapi.com/api/get_secret_token"

    token_response = requests.post(token_url, data={
        "secret_id": "ouwnr4q7xvjxkfnh9vuy",
        "secret_key": "69fbz8w5nhm44j22drj684gkf1lu0lse"
    })
    token_data = token_response.json()
    print(token_data)
    secret_token = token_data["data"]["secret_token"]
    api_url = f"https://dps.kdlapi.com/api/getdps/?secret_id=ouwnr4q7xvjxkfnh9vuy&signature={secret_token}&num=1&pt=1&sep=1"
    # 获取API接口返回的代理IP
    proxy_ip = requests.get(api_url).text
    print("get proxy!",proxy_ip)
    return proxy_ip.split(":")

def get_proxy():
    token_url = "https://auth.kdlapi.com/api/get_secret_token"

    token_response = requests.post(token_url, data={
        "secret_id": "ouwnr4q7xvjxkfnh9vuy",
        "secret_key": "69fbz8w5nhm44j22drj684gkf1lu0lse"
    })
    token_data = token_response.json()
    print(token_data)
    secret_token = token_data["data"]["secret_token"]
    api_url = f"https://dps.kdlapi.com/api/getdps/?secret_id=ouwnr4q7xvjxkfnh9vuy&signature={secret_token}&num=1&pt=1&sep=1"
    # 获取API接口返回的代理IP
    proxy_ip = requests.get(api_url).text
    print("get proxy!",proxy_ip)
    username = "d1605622020"
    password = "by9sopwk"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    }
    return proxies


from selenium import webdriver
import string
import zipfile
import time

def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件

    args:
        proxy_host (str): 你的代理地址或者域名（str类型）
        proxy_port (int): 代理端口号（int类型）
        # 用户名密码认证(私密代理/独享代理)
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path




# 白名单方式（需提前设置白名单）
# proxies = {
#     "http": "http://%(proxy)s/" % {"proxy": proxy_ip},
#     "https": "http://%(proxy)s/" % {"proxy": proxy_ip}
# }

# # 要访问的目标网页
# target_url = "https://dev.kdlapi.com/testproxy"

# # 使用代理IP发送请求
# response = requests.get(target_url, proxies=proxies)

# # 获取页面内容
# if response.status_code == 200:
#     print(response.text)

if __name__ == "__main__":
    get_proxy()