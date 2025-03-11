import asyncio
import disnake
from disnake.ext import commands
from disnake import FFmpegPCMAudio

theme_path = "data/entry_theme/"
monkey_palace = 1337172437145616495

class VoiceSoundCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dicionário mapeando o ID do usuário para um dicionário contendo:
        # - channel_id: ID do canal de voz onde o som deve ser tocado
        # - sound_file: caminho para o arquivo de som
        self.user_sounds = {
            496224529472028684: { # Vitin
                "channel_id": monkey_palace,
                "sound_file": theme_path + "vitinho-entry.mp3"
            },
            311976988438953994: { # Soren
                "channel_id": monkey_palace,
                "sound_file": theme_path + "soren-entry.mp3"
            },
            393853808754556929: { # Gabs
                "channel_id": monkey_palace,
                "sound_file": theme_path + "gabs-entry.mp3"
            },
            305790558750638100: { # Yenneko
                "channel_id": monkey_palace,
                "sound_file": theme_path + "yenneko-entry.mp3"
            },
            348243086977007628: { # Rodrigo
                "channel_id": monkey_palace,
                "sound_file": theme_path + "rodrigo-entry.mp3"
            },
        }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        user_info = self.user_sounds.get(member.id)
        if not user_info:
            return  # Usuário não configurado para tocar som

        target_channel_id = user_info["channel_id"]
        sound_file = user_info["sound_file"]

        # Verifica se o usuário entrou no canal especificado
        if (before.channel is None or before.channel.id != target_channel_id) and (after.channel and after.channel.id == target_channel_id):
            channel = after.channel
            try:
                vc = await channel.connect()
            except Exception as e:
                print("Erro ao conectar no canal:", e)
                return

            audio_source = FFmpegPCMAudio(sound_file)

            def after_playing(error):
                coro = vc.disconnect()
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    print("Erro ao desconectar:", e)

            vc.play(audio_source, after=after_playing)

def setup(bot: commands.Bot):
    bot.add_cog(VoiceSoundCog(bot))
