import asyncio
import disnake
from disnake.ext import commands
from disnake import FFmpegPCMAudio

class UserTheme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Substitua pelos IDs do usuário e do canal desejado
        self.target_user_id = 496224529472028684  # ID do usuário específico
        self.target_channel_id = 1337172437145616495  # ID do canal de voz específico
        self.sound_file = "data/entry_theme/vitinho-entry.mp3"  # Caminho para o arquivo de som

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        # Verifica se é o usuário desejado
        if member.id != self.target_user_id:
            return

        # Verifica se ele entrou no canal de voz específico
        if (before.channel is None or before.channel.id != self.target_channel_id) and (after.channel and after.channel.id == self.target_channel_id):
            channel = after.channel
            try:
                # Conecta ao canal de voz
                vc = await channel.connect()
            except Exception as e:
                print("Erro ao conectar no canal:", e)
                return

            # Toca o som usando FFmpeg (certifique-se de ter o FFmpeg instalado)
            audio_source = FFmpegPCMAudio(self.sound_file)
            vc.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(vc.disconnect(), self.bot.loop))
            
def setup(bot: commands.Bot):
    bot.add_cog(UserTheme(bot))
