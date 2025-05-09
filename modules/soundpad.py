import os
import asyncio
import disnake
from disnake.ext import commands
from disnake.ui import View, Select, Button
from disnake import FFmpegPCMAudio

def load_sounds(directory: str) -> dict:
    """
    Lê os arquivos do diretório e retorna um dicionário onde
    a chave é o nome do som (nome do arquivo sem extensão)
    e o valor é o caminho completo para o arquivo.
    """
    sounds = {}
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path) and file.lower().endswith((".mp3", ".wav", ".ogg")):
            sound_name = os.path.splitext(file)[0]
            sounds[sound_name] = full_path
    return sounds

class SoundDropdown(Select):
    def __init__(self, options: list[disnake.SelectOption]):
        super().__init__(
            placeholder="Escolha um som...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # Armazena a opção escolhida na view
        self.view.selected_sound = self.values[0]
class ConfirmButton(Button):
    def __init__(self):
        super().__init__(label="Confirmar", style=disnake.ButtonStyle.success)

    async def callback(self, interaction: disnake.MessageInteraction):
        view: SoundView = self.view
        if not view.selected_sound:
            return await interaction.response.send_message(
                "Nenhum som foi selecionado.", ephemeral=True
            )
        sound_name = view.selected_sound
        sound_file = view.sounds.get(sound_name)
        if not sound_file:
            return await interaction.response.send_message(
                "Som não encontrado.", ephemeral=True
            )
        if not interaction.author.voice:
            return await interaction.response.send_message(
                "Você precisa estar em um canal de voz para tocar um som.", ephemeral=True, delete_after=5
            )
        channel = interaction.author.voice.channel
        vc = await channel.connect()
        audio_source = FFmpegPCMAudio(sound_file)

        # Callback para desconectar após a reprodução
        def after_playing(error):
            coro = vc.disconnect()
            fut = asyncio.run_coroutine_threadsafe(coro, interaction.client.loop)
            try:
                fut.result()
            except Exception as e:
                print("Erro ao desconectar:", e)

        vc.play(audio_source, after=after_playing)
        # Apaga a mensagem com o dropdown
        await interaction.message.delete()
        await interaction.response.send_message(
            f"Tocando o som: **{sound_name}**", ephemeral=True, delete_after=5
        )

class SoundView(View):
    def __init__(self, sounds: dict):
        super().__init__(timeout=60)
        self.sounds = sounds
        self.selected_sound = None
        options = []
        for name in sounds.keys():
            options.append(disnake.SelectOption(label=name, description=f"Tocar {name}"))
        self.add_item(SoundDropdown(options))
        self.add_item(ConfirmButton())

class Soundpad(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="soundpad", help="Exibe um dropdown dinâmico com os sons disponíveis na database.")
    async def playsound(self, ctx: commands.Context):
        # Deleta o comando
        await ctx.message.delete()

        # Carrega os sons do diretório (ajuste o caminho conforme necessário)
        sounds = load_sounds("data/soundpad")
        if not sounds:
            return await ctx.send("Nenhum som encontrado na pasta.")
        view = SoundView(sounds)
        await ctx.send("Escolha um som para tocar:", view=view)

    @commands.command(name="savesound", help="Adiciona um novo som. Use: savesound [nome opcional] com um arquivo anexo.")
    async def savesound(self, ctx: commands.Context, sound_name: str = None):
        # Verifica se há um arquivo anexo
        if not ctx.message.attachments:
            return await ctx.send("Envie um arquivo de som anexo.")
        
        attachment = ctx.message.attachments[0]
        # Verifica se o arquivo possui uma extensão de áudio suportada
        if not attachment.filename.lower().endswith((".mp3", ".wav", ".ogg")):
            return await ctx.send("Formato de arquivo não suportado. Use mp3, wav ou ogg.")

        # Se o nome do som não foi informado, utiliza o nome do arquivo (sem extensão)
        if not sound_name:
            sound_name = os.path.splitext(attachment.filename)[0]

        # Define o diretório onde os sons serão salvos (cria se não existir)
        directory = "data/soundpad"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Constrói o caminho do arquivo, preservando a extensão original
        _, ext = os.path.splitext(attachment.filename)
        file_path = os.path.join(directory, sound_name + ext)

        try:
            # Salva o arquivo enviado
            await attachment.save(file_path)
        except Exception as e:
            return await ctx.send(f"Erro ao salvar o som: {e}")

        await ctx.send(f"Som salvo com sucesso como `{sound_name}`.")

def setup(bot: commands.Bot):
    bot.add_cog(Soundpad(bot))
