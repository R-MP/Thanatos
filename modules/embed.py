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
        
    @commands.command(
        name="masscembed",
        aliases=["membed"],
        help=(
            "Cria vários embeds de uma vez.\n"
            "Uso: !masscembed \"Título1\" \"Link1\" \"Título2\" \"Link2\" ...\n"
            "E no mesmo envio você anexa N imagens (uma para cada par)."
        )
    )
    async def masscembed(self, ctx: commands.Context, *args: str):
        # args deve ter tamanho par: título, link, título, link, …
        if len(args) < 2 or len(args) % 2 != 0:
            return await ctx.send(
                "❌ Você deve passar pares de título e link. Exemplo:\n"
                "`!masscembed \"T1\" \"L1\" \"T2\" \"L2\" \"T3\" \"L3\"`"
            )

        # transforma args em lista de tuplas (título, link)
        pares = [(args[i], args[i+1]) for i in range(0, len(args), 2)]
        attachments = ctx.message.attachments

        for idx, (titulo, link) in enumerate(pares):
            embed = disnake.Embed(
                title=titulo,
                url=link,
                colour=0x00b0f4,
                timestamp=datetime.now()
            )

            # se houver anexo correspondente, usa como imagem
            if idx < len(attachments):
                embed.set_image(url=attachments[idx].url)

            await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(EmbedCog(bot))
