import os
import requests
from datetime import datetime, timedelta
import logging
import glob
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Bilibili API endpoint and collection ID from environment variables or default values
API_FAV = os.getenv('BILIBILI_API_FAV', 'https://api.bilibili.com/x/v3/fav/resource/list')
# API_CID = os.getenv('BILIBILI_API_CID', 'https://api.bilibili.com/x/player/pagelist?bvid={}')
# API_SUB = os.getenv('BILIBILI_API_SUB', 'https://api.bilibili.com/x/player/v2?bvid={}&cid={}')
COLLECTION_ID = os.getenv('BILIBILI_COLLECTION_ID', '213411584')

USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
SESSDATA = os.getenv('SESSDATA', 'Your SESSDATA')
CACHE_FILE = './bvid_cache.txt'
headers = {
    'User-Agent': USER_AGENT,
}
cookies = {'SESSDATA': SESSDATA}

def check_existing_files(directory):
    return bool(glob.glob(f"{directory}/**/*.md", recursive=True))

def read_bvid_cache(cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return set(file.read().splitlines())
    return set()

def write_bvid_cache(cache_file, bvids):
    with open(cache_file, 'a') as file:
        for bvid in bvids:
            file.write(bvid + '\n')

# Function to get videos from Bilibili collection with pagination
def get_videos_from_collection(collection_id, page_size=20, max_page=50 ,max_try=50):
    all_videos = []
    page = 1
    try_cnt = 0
    while True:
        if try_cnt > max_try or page > max_page:
            break
        try_cnt += 1
        time.sleep(2)
        params = {
            "media_id": collection_id,
            "ps": page_size,
            "pn": page
        }
        try:
            response = requests.get(API_FAV, params=params, headers=headers, cookies=cookies, timeout=10)
            if response.status_code == 200:
                data = response.json()['data']['medias']
                if not data:
                    break
                all_videos.extend(data)
                print(f"page: {page} process down")
                page += 1
            else:
                logging.error(f"Error fetching data from Bilibili: {response.status_code}")
                break
        except:
            logging.error(f"request data from Bilibili ERROR")
    return all_videos

# Function to filter videos added since the last run
def filter_recent_videos(videos, days=1):
    last_run = datetime.now() - timedelta(days=days)
    return [video for video in videos if datetime.fromtimestamp(video['fav_time']) > last_run]

# Function to create or update a Markdown file with video details
def update_markdown_file(video_data):
    for video in video_data:
        # Extract collection time and convert it to year and month
        collection_time = datetime.fromtimestamp(video['fav_time'])
        creation_time = datetime.fromtimestamp(video['ctime'])
        year = collection_time.strftime("%Y")
        month = collection_time.strftime("%m")
        directory = f"./Bilibili_Collections/{year}"
        filename = f"{directory}/{year}-{month}.md"

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, "a") as file:
            title = video['title']
            video_url = f"https://www.bilibili.com/video/{video['bvid']}"  # Assuming 'bvid' is the video ID
            author = video['upper']['name']
            author_url = f"https://space.bilibili.com/{video['upper']['mid']}"  # Assuming 'mid' is the author ID
            cover_image = video['cover']
            intro = video['intro']
            collection_time = collection_time.strftime("%Y-%m-%d %H:%M:%S")
            creation_time = creation_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = round(video['duration']/60, 2)

            file.write(f"### [{title}]({video_url})\n")
            file.write(f"- **Bvid:** {video['bvid']}\n")
            file.write(f"- **Author:** [{author}]({author_url})\n")
            file.write(f"- **Cover Image:** ![image]({cover_image})\n")
            file.write(f"- **Intro:** {intro}\n")
            file.write(f"- **Collection Time:** {collection_time}\n")
            file.write(f"- **Creation Time:** {creation_time}\n")
            file.write(f"- **Duration:** {duration}\n\n")



# Main execution
if __name__ == "__main__":
    
    has_existing_files = check_existing_files("./Bilibili_Collections")
    try:
        # Fetch videos based on the presence of existing files
        if not has_existing_files:
            # Backtrack and process all past videos
            all_videos = get_videos_from_collection(COLLECTION_ID)
            if all_videos:
                update_markdown_file(all_videos)
                all_bvids = {video['bvid'] for video in all_videos}
                write_bvid_cache(CACHE_FILE, all_bvids)
                logging.info(f"Processed {len(all_videos)} past videos.")
        else:
            # Update with new videos only
            processed_bvids = read_bvid_cache(CACHE_FILE)
            videos = get_videos_from_collection(COLLECTION_ID, max_page=2)
            new_videos = [video for video in videos if video['bvid'] not in processed_bvids]
            if new_videos:
                update_markdown_file(new_videos)
                new_bvids = {video['bvid'] for video in new_videos}
                write_bvid_cache(CACHE_FILE, new_bvids)
                logging.info(f"Processed {len(new_videos)} new videos.")
            else:
                logging.info("No new videos to process.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
