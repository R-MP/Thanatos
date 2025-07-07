# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands
from datetime import datetime

class EmbedCog(commands.Cog):
    """
    Cog para criar mensagens embed personalizadas.
    Comando: !embed "Título" "URL"
    Anexe uma imagem à mensagem para incluí-la no embed.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="embed", aliases=["Embed"], help="Cria um embed com título, URL e imagem (anexada). Uso: !embed \"Título\" \"URL\"")
    async def embed(self, ctx: commands.Context, title: str, url: str):
        # Captura a primeira imagem anexada, se houver
        image_url = None
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url

        # Cria o embed
        embed = disnake.Embed(
            title=title,
            url=url,
            colour=0x00b0f4,
            timestamp=datetime.utcnow()
        )

        # Adiciona a imagem ao embed, se disponível
        if image_url:
            embed.set_image(url=image_url)

        # Envia o embed no canal
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(EmbedCog(bot))
