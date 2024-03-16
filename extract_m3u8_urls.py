import asyncio
import aiohttp
import json
import bs4

# ANIME = "shinchan"
# ANIME = "doraemon"
ANIME = "doraemon-2005"

BASE_URL = "https://beta.awstream.net/m3u8/{m3u8_id}/master.txt?s=1&lang=hin&cache=1"

with open("awsstream_urls.jsonl", "r") as file:
    urls = [json.loads(line) for line in file]

async def fetch_m3u8_and_check(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            soup = bs4.BeautifulSoup(text, "html.parser")
            script_tag = soup.find('script', string=lambda text: text and f'sniff("{ANIME}-8211' in text)
            m3u8_id = script_tag.contents[0].split('"')[3]
            m3u8_url = BASE_URL.format(m3u8_id=m3u8_id)
            async with session.get(m3u8_url) as m3u8_response:
                if m3u8_response.status == 200:
                    return m3u8_url
                else:
                    return False

async def main():
    tasks = [fetch_m3u8_and_check(url['url']) for url in urls]
    results = await asyncio.gather(*tasks)
    
    with open("awsstream_m3u8_urls.jsonl", "w") as file:
        with open("awsstream_m3u8_urls_errors.jsonl", "w") as error_file:
            for url, result in zip(urls, results):
                data = {
                    "season_number": url["season_number"],
                    "episode_number": url["episode_number"],
                    "url": result
                }
                if result:
                    file.write(json.dumps(data) + "\n")
                else:
                    error_file.write(json.dumps(data) + "\n")
                    
if __name__ == "__main__":
    asyncio.run(main())