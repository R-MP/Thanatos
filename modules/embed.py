# modules/embed.py
# -*- coding: utf-8 -*-
from datetime import datetime
import disnake
from disnake.ext import commands

class EmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="customembed",
        aliases=["cembed"],
        help="Cria um embed. Uso: !customembed \"Título\" \"URL do link\""
    )
    async def customembed(self, ctx: commands.Context, title: str, link: str):
        # Cria o embed
        embed = disnake.Embed(
            title=title,
            url=link,
            colour=0xf4ee00,
        )
        # Se houver uma imagem anexada na mesma mensagem, usa-a
        if ctx.message.attachments:
            embed.set_image(url=ctx.message.attachments[0].url)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(EmbedCog(bot))
