from itertools import cycle
import json
import time
from datetime import datetime
import discord
from discord.ext import commands, tasks
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .utils import scrape_campaigns, scrape_quests_for_campaign

def current_date():
    return datetime.now().strftime("%Y-%m-%d")

def current_time():
    return datetime.now().strftime("%H:%M")

def convert_date(date_str):
    date_parts = date_str.split(',')
    date_part = f"{date_parts[0].strip()} {date_parts[1].strip()}"
    date_obj = datetime.strptime(date_part, "%b %d %Y")
    return date_obj.strftime("%Y-%m-%d")

def load_channel_id(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

def save_channel_id(file_path: str, data: dict):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

def get_channel_ids(channel_id_data: dict) -> list:
    if "channel_ids" in channel_id_data:
        return [channel["channel_id"] for channel in channel_id_data["channel_ids"]]
    return []

class ChannelIdEventHandler(FileSystemEventHandler):
    def __init__(self, reload_callback):
        self.reload_callback = reload_callback

    def on_modified(self, event):
        if event.src_path.endswith('notification_channels.json'):
            print(f'File changed: {event.src_path}')
            self.reload_callback()

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.announced_campaigns = set()
        self.notif_time = "08:45"
        self.channel_id_data = load_channel_id('notification_channels.json')
        self.Notifs_Channel = get_channel_ids(self.channel_id_data)

        self.observer = Observer()
        handler = ChannelIdEventHandler(self.reload_channel_ids)
        self.observer.schedule(handler, path='.', recursive=False)
        self.observer.start()

        self.check_new_campaigns.start()
        self.bot_status_rotation.start()
        self.new_quest.start()

    def cog_unload(self):
        self.observer.stop()
        self.check_new_campaigns.cancel()
        self.bot_status_rotation.cancel()
        self.new_quest.cancel()

    def reload_channel_ids(self):
        self.channel_id_data = load_channel_id('notification_channels.json')
        self.Notifs_Channel = get_channel_ids(self.channel_id_data)
        print("Channel IDs reloaded!")

    @commands.command()
    async def add_channel(self, ctx, id: int):
        self.channel_id_data["channel_ids"].append({"channel_id": id})
        save_channel_id("notification_channels.json", self.channel_id_data)
        self.reload_channel_ids()
        await ctx.send("The channel has been added for notifications!")

    @tasks.loop(minutes=1)
    async def new_quest(self):
        unix_timestamp = int(time.time()) + 3600
        timestamp_message = f"<t:{unix_timestamp}:R>"
        
        async with aiohttp.ClientSession() as session:
            try:
                campaigns = await scrape_campaigns(session)
                for campaign in campaigns:
                    try:
                        quests = await scrape_quests_for_campaign(session, campaign['link'])
                        for quest in quests:
                            quest_date = convert_date(quest['starts'])
                            present_date = current_date()
                            present_time = current_time()
                            if quest_date == present_date and present_time == self.notif_time:
                                for c_id in self.Notifs_Channel:
                                    targeted_channel = self.bot.get_channel(c_id) or await self.bot.fetch_channel(c_id)
                                    if targeted_channel:
                                        await targeted_channel.send(f"Hey @stackies, \n{quest['name']} of {campaign['name']} campaign will start {timestamp_message}. Go check it out.\n\n Questions with answers found in the quest will be ignored. For those who like to help, please ask guiding questions instead of giving answers. This encourages learning and independence during the campaign.\n\n Ensure that you thoroughly review the screenshot you're submitting, verifying that it adheres to the correct formatting.")                        
                                        embed = discord.Embed(
                                            color=discord.Colour.random(),
                                            description=f'''{quest['rewards']}                
                                            **Status: ** {quest['status']}
                                            ‎
                                            **Starts: ** {quest['starts']}
                                            **Ends: ** {quest['ends']}
                                            ‎
                                            [Quest Link](https://earn.stackup.dev{quest['link']})''')
                                        embed.set_author(name=quest['name'], url=f"https://earn.stackup.dev{quest['link']}")
                                        embed.set_image(url=campaign['image'])
                                        await targeted_channel.send(embed=embed)
                    except Exception as e:
                        print(f"Error processing campaign quests: {e}")
            except Exception as e:
                print(f"Error processing campaigns loop: {e}")

    @new_quest.before_loop
    async def before_new_quest(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def check_new_campaigns(self):
        async with aiohttp.ClientSession() as session:
            campaigns = await scrape_campaigns(session)
            for campaign in campaigns:
                if campaign['status'] == "Upcoming" and campaign['link'] not in self.announced_campaigns:
                    for c_id in self.Notifs_Channel:
                        targeted_channel = self.bot.get_channel(c_id) or await self.bot.fetch_channel(c_id)
                        if targeted_channel:
                            await targeted_channel.send("Hey @stackies, a new campaign is out. Go check it out.")
                            await targeted_channel.send("‎")
                            embed = discord.Embed(
                                color=discord.Colour.random(),
                                description=f'''
                                    **Starts at:** {campaign['start']}
                                    **Ends at:** {campaign['end']}
                                    {'https://earn.stackup.dev' + campaign['link']}''')
                            embed.set_author(name=campaign['name'], url=f"https://earn.stackup.dev{campaign['link']}")
                            embed.set_image(url=campaign['image'])
                            await targeted_channel.send(embed=embed)
                            self.announced_campaigns.add(campaign['link'])

    @check_new_campaigns.before_loop
    async def before_check_new_campaigns(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=20)
    async def bot_status_rotation(self):
        bot_statuses = ["a!help", "stackie.ie | a!help"]
        displaying = cycle(bot_statuses)
        current_status = next(displaying)
        await self.bot.change_presence(activity=discord.Game(current_status))

async def setup(bot):
    await bot.add_cog(Notifications(bot))