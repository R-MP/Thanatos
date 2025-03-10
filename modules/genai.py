import asyncio
import disnake
from disnake.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(os.getenv("API_KEY"))

class IA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active = False          # Flag para indicar se o modo está ativo
        self.task = None             # Tarefa para desativação automática
        self.last_channel = None     # Canal onde o modo foi ativado

    @commands.command(name="genai", help="Ativa o modo IA. Todas as mensagens serão respondidas automaticamente por 30 segundos ou até desativar.")
    async def aiswitch(self, ctx: commands.Context):
        if self.active:
            await ctx.send("Modo IA desativado.")
            self.active = False

            if self.task and not self.task.done():
                self.task.cancel()

        if not self.active:
            self.active = True
            self.last_channel = ctx.channel
            self.task = self.bot.loop.create_task(self.auto_deactivate())
            await ctx.send("Modo IA ativado.")

    async def auto_deactivate(self):
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            return
        self.active = False
        if self.last_channel:
            try:
                await self.last_channel.send("Modo IA desativado.")
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Ignora mensagens de bots
        if message.author.bot:
            return
        # Se o modo IA estiver ativo, responde a todas as mensagens
        if self.active:
            ai_request = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"{message.content}"}]
            )

            ai_response = ai_request.choices[0].message

            try:
                await message.channel.send(ai_response)
            except Exception as e:
                print("Erro ao enviar resposta de IA:", e)

def setup(bot: commands.Bot):
    bot.add_cog(IA(bot))
