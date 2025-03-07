# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands

class IA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        # Exemplo: se a mensagem contiver "oi bot", o bot responderá
        if "oi bot" in message.content.lower():
            await message.channel.send(f"Olá, {message.author.mention}! Como posso ajudar?")

    @commands.command(name="bora", help="Responde com 'bill!' para testar a conexão.")
    async def ping(self, ctx: commands.Context):
        await ctx.send("BIIILLL!")

def setup(bot: commands.Bot):
    bot.add_cog(IA(bot))