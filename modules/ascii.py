# -*- coding: utf-8 -*-
import re
import random
import disnake
import aiohttp
from data import ascii as ascii_module
from disnake.ext import commands
from io import BytesIO
from PIL import Image

def image_to_ascii(image, new_width=80):
        width, height = image.size
        aspect_ratio = height / width
        new_height = int(aspect_ratio * new_width * 0.55)
        
        image = image.resize((new_width, new_height))
        image = image.convert("L")
        pixels = image.getdata()
        
        ascii_chars = [".", ",", ":", ";", "=", "o", "+", "*", "?", "%", "F", "S", "H", "#", "O", "@"]
        ascii_str = ""
        for i, pixel in enumerate(pixels):
            ascii_str += ascii_chars[pixel * len(ascii_chars) // 256]
            if (i + 1) % new_width == 0:
                ascii_str += "\n"
        return ascii_str

class ASCII(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if "thanatin" in message.content.lower():
            await message.channel.send(f"Olá, {message.author.mention}!")

    @commands.command(name="ASCII", aliases=["as", "asc"], help="Mostra uma arte em ASCII aleatória a partir do módulo.")
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

    @commands.command(name="ascimg", aliases=["asim", "imgasc", "asciiimage", "imageascii"], help="Converte uma imagem em ASCII. Use uma imagem anexada ou forneça um URL.")
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

        try:
            img = Image.open(BytesIO(data))
        except Exception:
            return await ctx.send("Erro ao abrir a imagem.")

        width_match = re.search(r'-w(\d+)', ctx.message.content.lower())
        new_width = int(width_match.group(1)) if width_match else 80

        ascii_text = image_to_ascii(img, new_width=new_width)
        
        if "-file" in ctx.message.content.lower() or len(ascii_text) >= 2000:
            bio = BytesIO(ascii_text.encode('utf-8'))
            await ctx.send(file=disnake.File(bio, "ascii.txt"))
        else:
            await ctx.send(f"```\n{ascii_text}\n```")
        
    @commands.command(name="saveasc", help="Salva o último ASCII exibido no chat no banco de dados. (Use: saveasc nome_da_variavel)")
    async def saveascii(self, ctx: commands.Context, var_name: str):
        if not var_name.isidentifier():
            return await ctx.send("O nome da variável deve ser um identificador Python válido.")

        ascii_text = None
        async for message in ctx.channel.history(limit=20):
            if message.author.id == self.bot.user.id and "```" in message.content:
                match = re.search(r"```(?:\w*\n)?(.*?)```", message.content, re.DOTALL)
                if match:
                    ascii_text = match.group(1).strip()
                    break

        if not ascii_text:
            return await ctx.send("Não encontrei nenhum ASCII no chat para salvar.")

        try:
            with open("data/ascii.py", "a", encoding="utf-8") as file:
                file.write("\n\n")
                file.write(f"{var_name} = '''\n{ascii_text}\n'''")
        except Exception as e:
            return await ctx.send("Erro ao salvar a variável no arquivo.")

        await ctx.send(f"ASCII salvo como variável `{var_name}` na memória.")

def setup(bot: commands.Bot):
    bot.add_cog(ASCII(bot))