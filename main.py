import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup


intents = discord.Intents.default()
client = discord.Client(intents=intents)

TOKEN = ''
CHANNEL_ID =
TARGET = ''
URL = ''


sent_urls = set()

def crawl_pages(start, end, target, URL):
    for p in range(start, end + 1):

        gallurl = f'{URL}{p}'

        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'gall.dcinside.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        try:
            url_get = requests.get(gallurl, headers=header, allow_redirects=False)
        except:
            url_get = requests.get(gallurl, headers=header, allow_redirects=False)


        soup = BeautifulSoup(url_get.text, "html.parser")

        url_get.raise_for_status()
        if url_get.status_code == 301 or url_get.status_code == 302:
            print('페이지끝')
            break

        re = []
        try:
            for i in range(1, 53):

                target_element = soup.select_one(
                    f'#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr:nth-child({i}) > td.gall_writer.ub-writer')
                writer_td = target_element.get('data-uid')
                HorseHead_element = soup.select_one(
                    f'#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr:nth-child({i}) > td.gall_subject')

                HorseHead = HorseHead_element.get_text(strip=True)

                if writer_td == target and HorseHead != '공지':
                    target_element = soup.select_one(
                        f'#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr:nth-child({i}) > td.gall_tit.ub-word > a')
                    title = target_element.get_text(strip=True)
                    url = 'https://gall.dcinside.com' + target_element.get('href')

                    target_element = soup.select_one(
                        f'#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr:nth-child({i}) > td.gall_date')
                    date = target_element.get('title')
                    re.append((date, title, url))

        except:
            pass
    return re

@tasks.loop(seconds=60)
async def check_new_posts():
    results = crawl_pages(1, 1, TARGET, URL)

    if results:
        channel = client.get_channel(CHANNEL_ID)
        for date, title, url in results:
            if url not in sent_urls:
                embed = discord.Embed(title=title, url=url, color=discord.Color.blue())
                embed.add_field(name="Date", value=date, inline=False)
                await channel.send(embed=embed)
                sent_urls.add(url)


    if len(sent_urls) > 1000:
        sent_urls.clear()
        sent_urls.update(set(result[2] for result in results))
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    check_new_posts.start()

client.run(TOKEN)