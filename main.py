import json
import subprocess
import os
import threading

COMMAND = 'ffmpeg -i "{URL}" -c:v copy -c:a copy -preset ultrafast -f mp4 "{OUTPUT}"'
MAX_THREADS = 50
LOCK = threading.Lock()
OUTPUT_LOC = 'output-2'

def run_command(command, season_number, episode_number):
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with LOCK:
            print(f'Finished downloading Season {season_number} Episode {episode_number}')
    except subprocess.CalledProcessError as e:
        with LOCK:
            print(f'Error downloading Season {season_number} Episode {episode_number}: {e}')

def download_video(url_info):
    season_number = url_info['season_number']
    episode_number = url_info['episode_number']
    url = url_info['url']
    output_file = f'{OUTPUT_LOC}/S{season_number}/S{season_number}E{episode_number}.mp4'
    
    if os.path.exists(output_file):
        print(f'Season {season_number} Episode {episode_number} already downloaded.')
        return
    
    command = COMMAND.format(URL=url, OUTPUT=output_file)
    run_command(command, season_number, episode_number)

if __name__ == "__main__":
    with open('awsstream_m3u8_urls.jsonl', 'r') as file:
        urls = [json.loads(line) for line in file]

    for url in urls:
        season_dir = f'{OUTPUT_LOC}/S{url["season_number"]}'
        if not os.path.exists(season_dir):
            try:
                os.makedirs(season_dir, exist_ok=True)
                print(f'Created directory for Season {url["season_number"]}')
            except OSError as e:
                print(f'Error creating directory for Season {url["season_number"]}: {e}')
                continue
                
        while threading.active_count() >= MAX_THREADS:
            pass  # Wait until the number of active threads decreases
        
        threading.Thread(target=download_video, args=(url,)).start()
