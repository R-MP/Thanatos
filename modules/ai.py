# -*- coding: utf-8 -*-
import re
import random
import disnake
from disnake.ext import commands

class IA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if "thanatin" in message.content.lower():
            await message.channel.send(f"Olá, {message.author.mention}! Como posso ajudar?")

    @commands.command(name="ASCII", help="mostra uma arte em ASCII aléatoria.")
    async def ascii(self, ctx: commands.Context):
        try:
            with open("../data/ascii.txt", "r", encoding="utf-8") as file:
                content = file.read()

            pattern = re.compile(r'^\s*(\w+)\s*=\s*([\'"])(.*?)\2\s*$', re.MULTILINE)
            matches = pattern.findall(content)

            if matches:
                values = [match[2] for match in matches]
                selected_value = random.choice(values)
                await ctx.send(selected_value)
            else:
                await ctx.send("Nenhum ascii cadastrado.")
        except FileNotFoundError:
            await ctx.send("Arquivo do banco de dados ASCII não disponível.")

def setup(bot: commands.Bot):
    bot.add_cog(IA(bot))