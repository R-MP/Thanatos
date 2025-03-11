import asyncio
import disnake
from disnake.ext import commands
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
from disnake import FFmpegPCMAudio, PCMVolumeTransformer

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

client = openai

class IA(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active = False          # Flag para indicar se o modo está ativo
        self.task = None             # Tarefa para desativação automática
        self.last_channel = None     # Canal onde o modo foi ativado

    @commands.command(name="genai", help="Ativa o modo IA. Todas as mensagens serão respondidas automaticamente por 60 segundos ou até desativar.")
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
            await asyncio.sleep(60)
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
        
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command is not None:
            return
        # Se o modo IA estiver ativo, responde a todas as mensagens
        if self.active:
            ai_request = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"{message.content}"}]
            )

            ai_response = ai_request.choices[0].message.content

            try:
                await message.channel.send(ai_response)
            except Exception as e:
                print("Erro ao enviar resposta de IA:", e)

    @commands.command(name="tts", help="Converte texto em áudio TTS e toca no canal de voz.")
    async def tts_command(self, ctx: commands.Context, *, tts_text: str):
        # Verifica se o usuário está em um canal de voz
        if not ctx.author.voice:
            return await ctx.send("Você precisa estar em um canal de voz para usar esse comando.")
        channel = ctx.author.voice.channel

        # Conecta ao canal de voz
        try:
            vc = await channel.connect()
        except Exception as e:
            return await ctx.send("Erro ao conectar no canal de voz.")

        # Define o caminho do arquivo de áudio (pode ser fixo ou gerado dinamicamente)
        speech_file_path = Path("data/tts/speech.mp3")

        # Gera o áudio TTS usando a API do OpenAI
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice="sage",
                input=tts_text,
            )
            response.stream_to_file(speech_file_path)
        except Exception as e:
            await ctx.send("Erro ao gerar TTS.")
            await vc.disconnect()
            print(tts_text)
            print(speech_file_path)
            return

        # Cria a fonte de áudio para reprodução
        audio_source = FFmpegPCMAudio(str(speech_file_path))
        audio_source = PCMVolumeTransformer(audio_source)
        audio_source.volume = 2.0  # 200% do volume padrão

        # Função callback para desconectar e deletar o arquivo após a reprodução
        def after_playing(error):
            coro = vc.disconnect()
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print("Erro ao desconectar:", e)
            # Remove o arquivo gerado
            try:
                os.remove(speech_file_path)
            except Exception as e:
                print("Erro ao remover o arquivo:", e)

        vc.play(audio_source, after=after_playing)
        await ctx.send("Tocando TTS...", delete_after=5)


def setup(bot: commands.Bot):
    bot.add_cog(IA(bot))
