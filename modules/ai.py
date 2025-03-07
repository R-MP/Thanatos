# -*- coding: utf-8 -*-
import aiofiles
import disnake

from disnake.ext import commands
from utils.client import BotCore


class AI(commands.Cog):

    emoji = "🤖"
    name = "IA Generativa"
    desc_prefix = f"[{emoji} {name}] | "

    def __init__(self, bot: BotCore):
        self.bot = bot

    @commands.command(name="mentecapto", aliases=["test", "tes", "tesao"], description="maracutaia.")
    async def tes():
        print(f"🎉 - Bota na calcinha preta")

    @commands.slash_command(
        description=f"{desc_prefix} abubuie",
        extras={"allow_private": True}
    )

    @commands.Cog.listener()
    async def tescog(self):
        print(f"escomungado")



def setup(bot: BotCore):
    bot.add_cog(AI(bot))
