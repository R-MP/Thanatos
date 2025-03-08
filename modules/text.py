# -*- coding: utf-8 -*-
import re
import random
import disnake
import aiohttp
from data import ascii as ascii_module
from disnake.ext import commands
from io import BytesIO
from PIL import Image
class Text(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if "thanatin" in message.content.lower():
            await message.channel.send(f"Olá, {message.author.mention}! Como posso ajudar?")

    @commands.command(name="ascii", help="mostra uma arte em ASCII aléatoria.")
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

    @commands.command(name="img2asc", help="Converte uma imagem em ASCII. Use uma imagem anexada ou forneça um URL.")
    async def asciiimg(self, ctx: commands.Context, url: str = None):
        if not url:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.send("Envie uma imagem ou forneça um URL.")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return await ctx.send("Não foi possível baixar a imagem.")
                    data = await response.read()
        except Exception:
            return await ctx.send("Erro ao baixar a imagem.")

        # Abre a imagem com Pillow
        try:
            img = Image.open(BytesIO(data))
        except Exception:
            return await ctx.send("Erro ao abrir a imagem.")

        # Converte a imagem para ASCII
        ascii_text = image_to_ascii(img, new_width=80)
        # Se o resultado for muito grande, envia como arquivo; caso contrário, envia em um bloco de código
        if len(ascii_text) > 1900:
            bio = BytesIO(ascii_text.encode('utf-8'))
            await ctx.send(file=disnake.File(bio, "ascii.txt"))
        else:
            await ctx.send(f"```\n{ascii_text}\n```")

def setup(bot: commands.Bot):
    bot.add_cog(Text(bot))