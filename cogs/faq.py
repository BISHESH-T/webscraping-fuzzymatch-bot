import asyncio
import json
import discord
from discord.ext import commands
from difflib import get_close_matches

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

class FAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.knowledge_base = load_knowledge_base('./sample_knowledge_bases/stackup_query.json')

    @commands.command(name='ask')
    async def ask(self, ctx, *, user_input: str):
        best_match = find_best_match(user_input, [q["question"] for q in self.knowledge_base["questions"]])
        if best_match:
            answer = get_answer_for_question(best_match, self.knowledge_base)
            await ctx.send(f'{answer}')
        else:
            await ctx.send("No solutions have been found yet. If you've solved it then please enlighten me. (You can also reply a!skip if you dont have the solution either.)   ```[NOTE: Do not enter anything weird as the bot learns from the user's response]```")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                new_answer = msg.content

                if new_answer.lower() != "a!skip":
                    self.knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                    save_knowledge_base("knowledge_base.json", self.knowledge_base)
                    await ctx.send("Thank you for the response!")
                else:
                    await ctx.send("Okay, maybe next time!")
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please Try again.")

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title="Here's more info related to Stackie bot",
            description="Hi there! I'm ``Stackie``:smile:, a multi-purpose bot crafted entirely in Python :snake:. I was brough in this digital realm in :two::zero::two::four: by the one and only ``Sakuta ``:sparkles:. Stackie is here to serve, assist, and entertain in the virtual worlds that he calls home:house_with_garden:. Try out ``a!ask <query>`` to get help regarding the current quest. Check ``a!help`` for more of my commands.  Happy hacking!! :blush:"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Stackie's commands",
            description="Here are the commands for Stackie. My prefix is **a!**, ``a!<command>`` ",
            color=discord.Colour.random()
        )
        embed.add_field(name=":blush:Checkout the Ongoing and Upcoming Campaigns", value="``ongoing``, ``upcoming``", inline=False)
        embed.add_field(name=":smirk_cat: Check out the Quests within the Campaigns", value="``quest``", inline=False)
        embed.add_field(name=":sunglasses: Get Quest Help from AI", value="``ask <query>``", inline=False)
        embed.add_field(name=":heart_eyes:More About Stackie", value="``info``", inline=False)
        embed.add_field(name=":smile:More features of Stackie", value="Stackie has the feature of notifying the stackies with the new campaigns and quests on quest days Automatically. Make sure to set up a notification channel by using the command ``a!add_channel <channel_id>``.", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FAQ(bot))