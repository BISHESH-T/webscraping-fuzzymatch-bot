import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

client = commands.Bot(command_prefix='a!', intents=discord.Intents.all())
client.remove_command('help')

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

async def main():
    async with client:
        await client.load_extension('cogs.campaigns')
        await client.load_extension('cogs.faq')
        await client.load_extension('cogs.notifications')
        await client.start(BOT_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())