import asyncio
import disnake
from disnake.ext import commands
from disnake import FFmpegPCMAudio

theme_path = "data/entry_theme/"
monkey_palace = 1337172437145616495

# ID do usuário que, se já estiver na call, dispara o som extra
SPECIFIC_USER_FOR_EXTRA_SOUND = 311976988438953994  # Substitua pela ID correta
EXTRA_SOUND_FILE = theme_path + "follow-entry.mp3"      # Substitua pelo caminho do arquivo desejado

class VoiceSoundCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dicionário mapeando o ID do usuário para suas configurações de som e canal
        self.user_sounds = {
            291336181348696081: {  # Soto
                "channel_id": monkey_palace,
                "sound_file": theme_path + "soto-entry.mp3"
            },
            496224529472028684: {  # Vitin
                "channel_id": monkey_palace,
                "sound_file": theme_path + "vitinho-entry.mp3"
            },
            311976988438953994: {  # Soren
                "channel_id": monkey_palace,
                "sound_file": theme_path + "soren-entry.mp3"
            },
            393853808754556929: {  # Gabs
                "channel_id": monkey_palace,
                "sound_file": theme_path + "gabs-entry.mp3"
            },
            305790558750638100: {  # Yenneko
                "channel_id": monkey_palace,
                "sound_file": theme_path + "yenneko-entry.mp3"
            },
            348243086977007628: {  # Rodrigo
                "channel_id": monkey_palace,
                "sound_file": theme_path + "rodrigo-entry.mp3"
            },
            331855701205057536: {  # Vitao
                "channel_id": monkey_palace,
                "sound_file": theme_path + "vitao-entry.mp3"
            },
        }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        user_info = self.user_sounds.get(member.id)
        if not user_info:
            return  # Usuário não configurado para tocar som

        target_channel_id = user_info["channel_id"]
        sound_file = user_info["sound_file"]

        # Verifica se o usuário entrou no canal especificado (considera mudança de canal ou conexão)
        if (before.channel is None or before.channel.id != target_channel_id) and (after.channel and after.channel.id == target_channel_id):
            channel = after.channel
            try:
                vc = await channel.connect()
            except Exception as e:
                print("Erro ao conectar no canal:", e)
                return

            # Toca o som principal
            vc.play(FFmpegPCMAudio(sound_file))
            # Aguarda enquanto o som está tocando
            while vc.is_playing():
                await asyncio.sleep(0.5)

            # Verifica se o usuário específico já está presente na call
            if any(m.id == SPECIFIC_USER_FOR_EXTRA_SOUND for m in channel.members):
                await asyncio.sleep(5)  # Espera 5 segundos antes de tocar o som extra
                vc.play(FFmpegPCMAudio(EXTRA_SOUND_FILE))
                # Aguarda a finalização do som extra
                while vc.is_playing():
                    await asyncio.sleep(0.5)

            await vc.disconnect()

def setup(bot: commands.Bot):
    bot.add_cog(VoiceSoundCog(bot))
