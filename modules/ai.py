# -*- coding: utf-8 -*-
import aiofiles
import disnake

from disnake.ext import commands
from utils.client import BotCore
from utils.others import CustomContext

class AI(commands.Cog):

    emoji = "🤖"
    name = "IA Generativa"
    desc_prefix = f"[{emoji} {name}] | "

    def __init__(self, bot: BotCore):
        self.bot = bot

    about_cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.member)

    @commands.command(name="mentecapto", aliases=["test", "tes", "tesao"], description="maracutaia.", cooldown=about_cd)      
    async def tes(self, ctx: CustomContext):
        await self.about.callback(self=self, interaction=ctx)
        print(f"🎉 - Bota na calcinha preta")

    @commands.slash_command(
        description=f"{desc_prefix} abubuie",
        extras={"allow_private": True}
    )

    @commands.Cog.listener()
    async def tescog(self):
        print(f"escomungado")

        try:
            channel = guild.system_channel if guild.system_channel.permissions_for(guild.me).send_messages else None
        except AttributeError:
            channel = None

        try:
            await channel.send(f"Confira o meu pau demonstrando essa funcionalidade.")
        except:
            print(f"Falha ao enviar mensagem de novo servidor no canal: {channel}\n"
                f"ID do canal: {channel.id}\n"
                f"Tipo de canal: {type(channel)}\n")


def setup(bot: BotCore):
    bot.add_cog(AI(bot))
