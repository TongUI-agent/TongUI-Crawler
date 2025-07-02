import os
import re
import time
import hashlib
import urllib.parse
import requests
from functools import reduce
from fake_useragent import UserAgent

MIXIN_KEY_ENC_TAB = []

def get_headers():
    return {
        'User-Agent': UserAgent().random,
        'Referer': 'https://www.bilibili.com/'
    }

def parse_cookies(cookie_str):
    return dict(pair.split("=", 1) for pair in cookie_str.split("; ") if "=" in pair)

def read_cookies(file_path="cookies.txt"):
    with open(file_path, "r") as f:
        return parse_cookies(f.read().strip())

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()

def get_mixin_key(orig):
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]

def sign_params(params, img_key, sub_key):
    mixin_key = get_mixin_key(img_key + sub_key)
    params['wts'] = round(time.time())
    sorted_params = {k: ''.join(filter(lambda c: c not in "!'()*", str(v))) for k, v in sorted(params.items())}
    query = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    sorted_params['w_rid'] = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return sorted_params

def get_wbi_keys():
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=get_headers())
    data = resp.json()['data']['wbi_img']
    return data['img_url'].split('/')[-1].split('.')[0], data['sub_url'].split('/')[-1].split('.')[0]

def request_json(url, params=None, cookies=None):
    resp = requests.get(url, params=params, headers=get_headers(), cookies=cookies)
    return resp.json()

def get_video_cid(bvid):
    json_data = request_json('https://api.bilibili.com/x/web-interface/view',
                             params={'bvid': bvid},
                             cookies=read_cookies())
    return str(json_data['data']['cid']) if json_data['code'] == 0 else None

def get_video_subtitle(bvid, cid):
    json_data = request_json('https://api.bilibili.com/x/player/v2',
                             params={'bvid': bvid, 'cid': cid},
                             cookies=read_cookies())
    return json_data['data']['subtitle']['subtitles'] if json_data['code'] == 0 else []

def search_bilibili_videos(query, max_results=10):
    img_key, sub_key = get_wbi_keys()
    params = sign_params({
        'keyword': query,
        'page': 1,
        'search_type': "video"
    }, img_key, sub_key)

    data = request_json('https://api.bilibili.com/x/web-interface/wbi/search/type',
                        params=params,
                        cookies=read_cookies())

    if data['code'] != 0:
        return [], []

    videos, details = [], []
    for item in data['data']['result']:
        bvid = item.get('bvid')
        title = item.get('title', '').replace("<em class=\"keyword\">", "").replace("</em>", "")
        cid = get_video_cid(bvid)
        if bvid and title and cid:
            videos.append(f"{title}~~{bvid}~~{cid}")
            details.append(item)

    return videos[:max_results], details[:max_results]

def save_video_urls(web, op_file, url_path, data_path, max_results=50):
    os.makedirs(url_path, exist_ok=True)
    os.makedirs(data_path, exist_ok=True)

    try:
        with open(op_file, encoding="utf-8") as f:
            operations = [line.strip("-").strip() for line in f if line.strip()]
    except:
        with open(op_file, encoding="gbk") as f:
            operations = [line.strip("-").strip() for line in f if line.strip()]

    for ops in operations:
        op, name = ops.split("##")
        query = f"{web} {op}"
        videos, data = search_bilibili_videos(query, max_results)

        with open(os.path.join(url_path, f"{name}.txt"), "w", encoding="utf-8") as f:
            f.writelines(f"{v}\n" for v in videos)

        with open(os.path.join(data_path, f"{name}_data.txt"), "w", encoding="utf-8") as f:
            f.writelines(f"{d}\n" for d in data)

def get_video_links(bvid, cid, use_dash=True):
    fnval = 16 if use_dash else 1
    params = {
        'bvid': bvid,
        'cid': cid,
        'qn': 80,
        'fnval': fnval,
        'fnver': 0,
        'fourk': 0
    }
    img_key, sub_key = get_wbi_keys()
    signed_params = sign_params(params, img_key, sub_key)

    json_data = request_json("https://api.bilibili.com/x/player/playurl",
                             params=signed_params,
                             cookies=read_cookies())

    if json_data['code'] != 0:
        return []

    data = json_data.get('data', {})
    if use_dash and 'dash' in data:
        v = max(data['dash']['video'], key=lambda x: x['height'] * x['width'])['baseUrl']
        a = max(data['dash']['audio'], key=lambda x: x['bandwidth'])['baseUrl']
        return [v, a]
    elif 'durl' in data:
        return [data['durl'][0]['url']] + data['durl'][0].get('backup_url', [])
    return []

def download_stream(url, output_path, filename, file_type="video"):
    filepath = os.path.join(output_path, filename)
    r = requests.get(url, headers=get_headers(), stream=True)
    if r.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

def download_and_save_videos(web, op_name, video_list_path, output_path, link_output_path):
    if os.path.exists(output_path):
        return
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(link_output_path, exist_ok=True)

    with open(video_list_path, encoding="utf-8") as f:
        video_list = [line.strip() for line in f if line.strip()]

    for video in video_list:
        title, bvid, cid = video.split("~~")
        title = sanitize_filename(title)
        links = get_video_links(bvid, cid, use_dash=True)
        if not links:
            continue

        with open(os.path.join(link_output_path, f"{title[:25]}_{bvid}.txt"), "w", encoding="utf-8") as f:
            f.writelines(f"{link}\n\n" for link in links)

        download_stream(links[0], output_path, f"{title}_{bvid}.mp4", "video")
        if len(links) > 1:
            download_stream(links[1], output_path, f"{title}_{bvid}.mp3", "audio")

        time.sleep(5)

if __name__ == "__main__":
    app = "tiktok"
    op_file = f"op/{app}_operations.txt"
    url_path = f"urls/{app}"
    data_path = f"data/{app}"
    output_base = f"videos/{app}"
    link_base = f"video_links/{app}"

    save_video_urls(app, op_file, url_path, data_path, max_results=20)

    for file in os.listdir(url_path):
        op_name = os.path.splitext(file)[0]
        video_list_path = os.path.join(url_path, file)
        output_path = os.path.join(output_base, app, op_name)
        link_output_path = os.path.join(link_base, app, op_name)

        download_and_save_videos(app, op_name, video_list_path, output_path, link_output_path)
