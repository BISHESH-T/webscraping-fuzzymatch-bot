import aiohttp
from bs4 import BeautifulSoup

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Request error: {e}")
        return None

async def scrape_campaigns(session):
    html_text = await fetch(session, 'https://earn.stackup.dev/campaigns')
    if html_text is None:
        return []
    
    soup = BeautifulSoup(html_text, 'lxml')
    campaign_elements = soup.find_all('li', class_='w-full sm:max-w-[276px] md:max-w-[296px] lg:max-w-[424px] xl:max-w-[368px] lg:w-1/2 xl:w-1/3 grayscale-11 rounded-3xl overflow-hidden border-l border-r border-b border-grayscale-8')
    
    campaigns = []
    for c in campaign_elements:
        try:
            box_date_div = c.find('div', class_="flex space-x-8 flex-row")
            box_date = box_date_div.find_all('span')
            campaigns.append({
                'element': c,
                'image': c.find('img', class_="object-fill aspect-[2/1]")['src'],
                'name': c.find('h3').text,
                'link': c.find('a')['href'],
                'start': box_date[0].text,
                'end': box_date[1].text,
                'status': c.find('span').text
            })
        except Exception as e:
            print(f"Error parsing campaign element: {e}")
            
    return campaigns

async def scrape_quests_for_campaign(session, campaign_link):
    html_quest = await fetch(session, f'https://earn.stackup.dev{campaign_link}')
    if html_quest is None:
        return []

    soup = BeautifulSoup(html_quest, 'lxml')
    quest_elements = soup.find_all('li', class_='group relative bg-white rounded-xl border border-grayscale-8')
    
    quests = []
    for q in quest_elements:
        try:
            box_rewards = q.find_all('div', class_="flex space-x-3 items-center")
            quest_link = q.find('a', class_="p-5 flex flex-col space-y-5 md:p-8")['href']
            
            html_subquest = await fetch(session, f'https://earn.stackup.dev{quest_link}')
            if html_subquest is None:
                continue

            soup_sub = BeautifulSoup(html_subquest, 'lxml')
            box_date = soup_sub.find_all('time')
            quest_dates = [t.text for t in box_date]

            quests.append({
                'name': q.find('h2').text,
                'status': q.find('span').text,
                'rewards': box_rewards[1].text,
                'link': quest_link,
                'starts': quest_dates[0],
                'ends': quest_dates[1]
            })
        except Exception as e:
            print(f"Error parsing quest element: {e}")

    return quests