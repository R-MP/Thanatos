import os
import cv2
import asyncio
import re
import shutil
from pathlib import Path
import disnake
from disnake.ext import commands

def convert_frame_to_ascii(frame, width=80):
    """
    Converte um frame (imagem) para ASCII.
    """
    # Redimensiona o frame mantendo a proporção
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(aspect_ratio * width * 0.55)  # fator de correção para fontes monoespaçadas
    resized_frame = cv2.resize(frame, (width, new_height))
    # Converte para escala de cinza
    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    # Mapeamento de níveis de cinza para caracteres ASCII (do mais escuro para o mais claro)
    ascii_chars = " .:-=+*#%@"
    ascii_str = ""
    for pixel in gray.flatten():
        ascii_str += ascii_chars[int(pixel) * len(ascii_chars) // 256]
    # Insere quebras de linha
    ascii_str = "\n".join([ascii_str[i:i+width] for i in range(0, len(ascii_str), width)])
    return ascii_str

def process_video_frames(video_path: str, output_dir: str, width: int = 60, max_frames: int = None):
    """
    Processa um vídeo e salva cada frame convertido para ASCII em arquivos de texto.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ascii_frame = convert_frame_to_ascii(frame, width=width)
        # Salva cada frame em um arquivo com nome sequencial
        filename = os.path.join(output_dir, f"frame{frame_count:04d}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(ascii_frame)
        frame_count += 1
        if max_frames and frame_count >= max_frames:
            break
    cap.release()
    return frame_count

class VideoASCIICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="apple", help="Reproduz um vídeo em ASCII no chat.")
    async def apple(self, ctx: commands.Context):
        video_path = "data/video/badapple.mp4"

        # Apaga a mensagem do comando, se desejado
        try:
            await ctx.message.delete()
        except Exception:
            pass

        width = 60

        # Define o diretório onde os frames serão salvos
        video_name = Path(video_path).stem
        output_dir = f"data/video/frames/{video_name}_w{width}"
        
        # Se não houver frames pré-processados, processa e salva
        if not os.path.exists(output_dir) or len(os.listdir(output_dir)) == 0:
            frame_count = process_video_frames(video_path, output_dir, width=width)

        # Carrega os frames já processados (arquivos .txt) e pré-carrega em memória
        frame_files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.txt')])
        if not frame_files:
            return await ctx.send("Nenhum frame encontrado para reprodução.")

        ascii_frames = []
        for frame_file in frame_files:
            try:
                with open(frame_file, "r", encoding="utf-8") as f:
                    ascii_frames.append(f.read())
            except Exception as e:
                print(f"Erro ao ler o arquivo {frame_file}: {e}")

        # Envia uma mensagem inicial que será editada com os frames
        # Alterna entre enviar nova mensagem e atualizar a mensagem
        message = None
        interval = 5  # a cada 5 frames, envia uma nova mensagem
        for i, frame in enumerate(ascii_frames):
            try:
                if i % interval == 0:
                    # Se houver uma mensagem antiga, deleta-a antes de enviar a nova
                    if message is not None:
                        try:
                            await message.delete()
                        except Exception:
                            pass
                    message = await ctx.send(f"```\n{frame}\n```")
                else:
                    await message.edit(content=f"```\n{frame}\n```")
                await asyncio.sleep(1)
            except Exception as e:
                print("Erro ao processar frame:", e)
                break

        # Após a reprodução, deleta a última mensagem
        try:
            await message.delete()
        except Exception:
            pass

        # Remove a pasta dos frames para liberar espaço
        try:
            shutil.rmtree(output_dir)
            await ctx.send("Frames deletados após a reprodução.", delete_after=5)
        except Exception as e:
            await ctx.send(f"Erro ao deletar os frames: {e}", delete_after=5)

def setup(bot: commands.Bot):
    bot.add_cog(VideoASCIICog(bot))
