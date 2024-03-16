import asyncio
import aiohttp
import json
import itertools
import bs4

## Shinchain
# ANIME = "shinchan"
# season_numbers = [f"{num:02d}" for num in [2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15]]

## Doaremon-old
# ANIME = "doraemon"
# season_numbers = [f"{num:02d}" for num in [2, 3, 4, 5, 6]]

## Doaremon-new
ANIME = "doraemon-2005"
season_numbers = [f"{num:02d}" for num in [3, 4, 5, 6, 7, 8, 9]]

BASE_URL_FOR_SEASON_1 = "https://beta.awstream.net/watch?v={ANIME}-8211-episode-{episode_number}&lang=hin"
BASE_URL = "https://beta.awstream.net/watch?v={ANIME}-8211-season-{season_number}-8211-episode-{episode_number}&lang=hin"

# Format episode numbers with leading zeros
episode_numbers = [f"{num:02d}" for num in range(1, 55)]

# Create combinations
combinations = list(itertools.product(season_numbers, episode_numbers))

def create_url(season_number, episode_number):
    return BASE_URL.format(ANIME=ANIME, season_number=season_number, episode_number=episode_number)

async def check_if_episode_exists(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()  
            soup = bs4.BeautifulSoup(text, "html.parser")
            return soup.find("title").text.strip() != "Warning"

async def main():
    tasks = []
    
    # season 1
    for ep_num in episode_numbers:
        url = BASE_URL_FOR_SEASON_1.format(ANIME=ANIME, episode_number=ep_num)
        tasks.append(check_if_episode_exists(url))
    
    with open("awsstream_urls.jsonl", "w") as file:
        with open("awsstream_urls_errors.jsonl", "w") as error_file:
            results = await asyncio.gather(*tasks)
            for ep_num, result in zip(episode_numbers, results):
                data = {
                    "season_number": "01",
                    "episode_number": ep_num,
                    "url": BASE_URL_FOR_SEASON_1.format(ANIME=ANIME, episode_number=ep_num)
                }
                if result:
                    file.write(json.dumps(data) + "\n")
                else: 
                    error_file.write(json.dumps(data) + "\n")
    
    tasks = []
    
    # for season 2 onwards
    for s_num, ep_num in combinations:
        url = create_url(s_num, ep_num)
        tasks.append(check_if_episode_exists(url))
    results = await asyncio.gather(*tasks)
    
    with open("awsstream_urls.jsonl", "a") as file:
        with open("awsstream_urls_errors.jsonl", "a") as error_file:
            for url, result in zip(combinations, results):
                data = {
                    "season_number": url[0],
                    "episode_number": url[1],
                    "url": create_url(*url)
                }
                if result:
                    file.write(json.dumps(data) + "\n")
                else:
                    error_file.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    asyncio.run(main())
