import asyncio
import discord
from discord.ext import commands
import aiohttp
from .utils import scrape_campaigns, scrape_quests_for_campaign

class Campaigns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ongoing(self, ctx):
        found_ongoing = False
        await ctx.send("**THE CURRENTLY ONGOING CAMPAIGNS ARE:**")
        async with aiohttp.ClientSession() as session:
            campaigns = await scrape_campaigns(session)
            if not campaigns:
                await ctx.send("Failed to retrieve campaigns.")
                return

            for campaign in campaigns:
                if campaign['status'] == "Ongoing":
                    found_ongoing = True
                    embed = discord.Embed(
                        color=discord.Colour.random(),
                        description=f'''
                            **Starts at:** {campaign['start']}
                            **Ends at:** {campaign['end']}
                            {'https://earn.stackup.dev' + campaign['link']}
                        '''
                    )
                    embed.set_author(name=campaign['name'], url=f"https://earn.stackup.dev{campaign['link']}")
                    embed.set_image(url=campaign['image'])
                    await ctx.send(embed=embed)
                    await ctx.send("‎")

            if not found_ongoing:
                await ctx.send("``NO ONGOING CAMPAIGNS FOUND. CHECK BACK LATER.``")

    @commands.command()
    async def upcoming(self, ctx):
        found_upcoming = False
        await ctx.send("**THE UPCOMING CAMPAIGN IS:**")
        async with aiohttp.ClientSession() as session:
            campaigns = await scrape_campaigns(session)
            if not campaigns:
                await ctx.send("Failed to retrieve campaigns.")
                return

            for campaign in campaigns:
                if campaign['status'] == "Upcoming":
                    found_upcoming = True
                    embed = discord.Embed(
                        color=discord.Colour.random(),
                        description=f'''
                            **Starts at:** {campaign['start']}
                            **Ends at:** {campaign['end']}
                            {'https://earn.stackup.dev' + campaign['link']}
                        '''
                    )
                    embed.set_author(name=campaign['name'], url=f"https://earn.stackup.dev{campaign['link']}")
                    embed.set_image(url=campaign['image'])
                    await ctx.send(embed=embed)
                    await ctx.send("‎")
                    
            if not found_upcoming:
                await ctx.send("**No Upcoming Campaigns**")

    @commands.command(name='quest')
    async def quest(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("**Which Campaign's Quests would you like to check?**")
        await ctx.send("‎")

        async with aiohttp.ClientSession() as session:
            campaigns = await scrape_campaigns(session)

            if not campaigns:
                await ctx.send("Failed to retrieve campaigns.")
                return

            available_campaigns = []
            
            for i, campaign in enumerate(campaigns, start=1):
                if campaign['status'] in ("Ongoing", "Upcoming"):
                    available_campaigns.append((i, campaign))
                    embed = discord.Embed(
                        color=discord.Colour.random(),
                        description=f'''
                            **Starts at:** {campaign['start']}
                            **Ends at:** {campaign['end']}
                            [Campaign Link](https://earn.stackup.dev{campaign['link']})
                        ''')
                    embed.set_author(name=f"{i}. {campaign['name']}", url=f"https://earn.stackup.dev{campaign['link']}")
                    embed.set_image(url=campaign['image'])
                    await ctx.send(embed=embed)
                
            if not available_campaigns:
                await ctx.send("No ongoing or upcoming campaigns found.")
            else:
                await ctx.send("```Reply with the number of the Campaign:```")

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                    index_campaign = int(msg.content)
                    if not (1 <= index_campaign <= len(available_campaigns)):
                        await ctx.send("Invalid number. Please try again.")
                        return
                except (ValueError, asyncio.TimeoutError):
                    await ctx.send("Invalid input or timeout. Please try again.")
                    return

                specific_campaign = available_campaigns[index_campaign - 1][1]
                
                embed = discord.Embed(color=discord.Colour.random())
                embed.set_author(name=specific_campaign['name'], url=f"https://earn.stackup.dev{specific_campaign['link']}")
                embed.set_image(url=specific_campaign['image'])
                await ctx.send(embed=embed)

                quests = await scrape_quests_for_campaign(session, specific_campaign['link'])

                for quest in quests:
                    embed = discord.Embed(
                        color=discord.Colour.random(),
                        description=f'''{quest['rewards']}
                            **Status: ** {quest['status']}
                            ‎
                            **Starts: ** {quest['starts']}
                            **Ends: ** {quest['ends']}
                            ‎
                            https://earn.stackup.dev{quest['link']}
                        '''
                    )
                    embed.set_author(name=quest['name'], url=f"https://earn.stackup.dev{quest['link']}")
                    await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Campaigns(bot))