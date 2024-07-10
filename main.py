import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
import re

intents = discord.Intents.default()
client = discord.Client(intents=intents)



TOKEN = ''
CHANNEL_ID =
TARGET = ''
URL = ''




old_number = 99999999
ref_time = 60


sent_urls = set()

def crawl_pages(start, end, target, URL):
    re_list = []
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
                    re_list.append((date, title, url))
                    print((date, title, url))
                if i == 10:
                    global ref_time
                    global old_number
                    try:
                        clarify_element = soup.select_one(
                            f'#container > section.left_content > article:nth-child(3) > div.gall_listwrap.list > table > tbody > tr:nth-child({i}) > td.gall_tit.ub-word > a')

                        new_url = clarify_element.get('href')


                        pattern = r'/mini/board/view/\?id=supbangsong&no=(\d+)&page=1'  # 패턴 수정
                        match = re.search(pattern, new_url)

                        new_number = int(match.group(1))

                        if ref_time == 60:
                            if (new_number- old_number) >= 30:
                                change_re = 15
                            else:
                                change_re = 60
                        else:
                            if (new_number- old_number) >= 8:
                                change_re = 15
                            else:
                                change_re = 60

                        if ref_time!=change_re:
                            print(f'ref_time: {change_re}')

                        ref_time = change_re
                        old_number = new_number

                    except Exception as e:
                        print(f"Error in processing: {e}")



        except:
            pass
    return re_list

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


    if len(sent_urls) > 10:
        sent_urls.clear()
        sent_urls.update(set(result[2] for result in results))

    check_new_posts.change_interval(seconds=ref_time)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    check_new_posts.start()

client.run(TOKEN)