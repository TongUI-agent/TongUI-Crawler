import json
import os
import yt_dlp
import subprocess
from typing import Optional
import requests

cx = ""
key = ""

def google_custom_search(query: str, cx: str, key: str, i: int, filter_year: Optional[int] = None):
    print("call search", query, cx, key)
    endpoint = "https://customsearch.googleapis.com/customsearch/v1"
    params = {"q": query, 
              "cx": cx,
              "key": key,
              "filter": 1,
              "start": i,
              "siteSearch": "www.youtube.com",
              "siteSearchFilter": "i"}
    if filter_year is not None:
        params["tbs"] = f"cdr:1,cd_min:01/01/{filter_year},cd_max:12/31/{filter_year}"
    response = requests.get(endpoint, params=params)
    return response.json()

def save_video_urls(app, op_file, max_results=50):
    # Base path for saving URL files
    url_path = f"./urls/{app}"
    os.makedirs(url_path, exist_ok=True)
    
    # Read operations from file
    try:
        with open(op_file, "r", encoding="utf-8") as file:
            operations = [line.lstrip("-").strip() for line in file if line.strip()]
    except:
        with open(op_file, "r", encoding="GBK") as file:
            operations = [line.lstrip("-").strip() for line in file if line.strip()]

    # Process each operation
    for op in operations:
        url_file = os.path.join(url_path, f"{op}.txt")
        if os.path.exists(url_file):
            print(f"Target url path {url_file} already exists, skipping search.")
            continue
        
        # Search for videos
        query = f"{app} {op}"

        video_urls = []
        for page in range((max_results + 9) // 10):
            try:
                result = google_custom_search(query, cx, key, page*10+1)
                items = result.get('items', [])
                video_urls.extend(item["link"] for item in items)
                if len(video_urls) >= max_results:
                    video_urls = video_urls[:max_results]
                    break
            except Exception as e:
                print(f"Search error on page {page + 1}: {e}")
                break
        
        # Save video URLs to a file
        with open(url_file, "w") as url_file_obj:
            url_file_obj.writelines(f"{url}\n" for url in video_urls)
        
        print(f"Video urls saved to {url_file}")

def run_yt_dlp_command(command, success_msg, error_msg, video_url):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"{success_msg}: {video_url}")
    else:
        raise RuntimeError(f"{error_msg}: {video_url}\nDetails: {result.stderr}")
    return result

def download_metadata(video_url, output_path=".", cookies="cookies.txt"):
    command = [
        "yt-dlp", video_url,
        "--cookies", cookies,
        "-o", os.path.join(output_path, '%(title)s~~%(id)s'),
        "--write-info-json",
        "--skip-download"
    ]
    result = run_yt_dlp_command(command, "Metadata downloaded", "Metadata download failed", video_url)

    if result.returncode == 0:
        video_id = video_url.split('=')[-1]
        for file in os.listdir(output_path):
            if file.endswith(".info.json") and f"~~{video_id}." in file:
                metadata_file_path = os.path.join(output_path, file)
                break

        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        filesize_bytes = metadata.get('filesize') or metadata.get('filesize_approx')
        if filesize_bytes:
            return filesize_bytes / (1024 ** 3) <= 0.5
    else:
        return False

def download_video(video_url, output_path=".", cookies="cookies.txt"):
    command = [
        "yt-dlp", video_url,
        "--cookies", cookies,
        "-o", os.path.join(output_path, '%(title)s~~%(id)s.%(ext)s'),
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
        "--merge-output-format", "mp4",
        "--no-overwrites"
    ]
    run_yt_dlp_command(command, "Video downloaded successfully", "Video download failed", video_url)

def download_subtitles(video_url, output_path=".", lang_code="en", cookies="cookies.txt"):
    command = [
        "yt-dlp", video_url,
        "--cookies", cookies,
        "-o", os.path.join(output_path, '%(title)s~~%(id)s.%(ext)s'),
        "--write-subs", "--sub-lang", lang_code, "--skip-download", "--no-overwrites"
    ]
    run_yt_dlp_command(command, "Subtitles downloaded successfully", "Subtitle download failed", video_url)


def download_videos_from_urls(app, op, url_file, cookies, output_base_path="./videos"):
    video_path = os.path.join(output_base_path, "videos", app, op)
    meta_path = os.path.join(output_base_path, "metadata", app, op)
    subtitle_path = os.path.join(output_base_path, "subtitles", app, op)
    
    os.makedirs(video_path, exist_ok=True)
    os.makedirs(meta_path, exist_ok=True)
    os.makedirs(subtitle_path, exist_ok=True)
    
    with open(url_file, "r") as file:
        video_urls = [line.strip() for line in file if line.strip()]

    i = 0
    for index, url in enumerate(video_urls, start=1):
        if "www.youtube.com/watch" not in url:
            continue
        if i>=20:
            break
        print(f"Downloading video {index}/{len(video_urls)}...")

        try:
            should_download = download_metadata(url, meta_path, cookies=cookies)
            if not should_download:
                print(f"Video exceeds, skipping: {url}")
                continue

            download_video(url, video_path, cookies=cookies)
            download_subtitles(url, subtitle_path, lang_code="en", cookies=cookies)
        except Exception as e:
            print(e)
            continue
        i += 1

if __name__ == "__main__":
    app = "word"
    op_file = f"op/{app}_operations.txt"

    save_video_urls(app, op_file, max_results=50)
    
    url_path = f"./urls/{app}"
    for url_file in os.listdir(url_path):
        cookies = "cookies.txt"
        url_file_path = os.path.join(url_path, url_file)
        op_name = os.path.splitext(url_file)[0]
        download_videos_from_urls(app, op_name, url_file_path, cookies)
