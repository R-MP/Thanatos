# -*- coding: utf-8 -*-
import re
import random
import disnake
from data import ascii as ascii_module
from disnake.ext import commands

class Text(commands.Cog):
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
        ascii_list = [
            getattr(ascii_module, attr)
            for attr in dir(ascii_module)
            if not attr.startswith("__") and isinstance(getattr(ascii_module, attr), str)
        ]
        
        if ascii_list:
            selected_value = random.choice(ascii_list)
            await ctx.send(f"```\n{selected_value}\n```")
        else:
            await ctx.send("Nenhum ASCII encontrado no módulo.")

def setup(bot: commands.Bot):
    bot.add_cog(Text(bot))