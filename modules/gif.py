import os
import cv2
import asyncio
import re
import shutil
from pathlib import Path
import disnake
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont

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

def process_video_frames(video_path: str, output_dir: str, width: int = 80, max_frames: int = None):
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

def ascii_to_image(ascii_text, font_path=None, font_size=16, bg_color="white", text_color="black", scale_factor=2):
    """
    Converte um frame ASCII em uma imagem.
    Usa uma fonte monoespaçada para manter o alinhamento.
    O parâmetro scale_factor aumenta o tamanho final da imagem.
    """
    # Garante que o ascii_text não esteja vazio
    if not ascii_text.strip():
        ascii_text = " "
    
    lines = ascii_text.splitlines()
    if not lines:
        lines = [" "]
        
    # Usa uma fonte monoespaçada padrão se nenhuma for especificada
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)
    
    # Cria uma imagem dummy para medir o tamanho do texto
    dummy_img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(dummy_img)
    max_width = 420
    total_height = 420
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_width = max(max_width, w)
        total_height += h
    
    # Define dimensões mínimas, se necessário
    if max_width == 0 or total_height == 0:
        max_width, total_height = 10, 10

    # Cria a imagem final com o tamanho calculado
    img = Image.new("RGB", (max_width, total_height), color=bg_color)
    draw = ImageDraw.Draw(img)
    y = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((0, y), line, fill=text_color, font=font)
        y += h

    # Redimensiona a imagem para um tamanho maior, se desejado
    if scale_factor != 1:
        new_size = (img.width * scale_factor, img.height * scale_factor)
        img = img.resize(new_size, Image.NEAREST)
    return img

class GIF(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="apple", help="Reproduz um vídeo em ASCII no chat, gerando um GIF animado.")
    async def apple(self, ctx: commands.Context):
        video_path = "data/video/badapple.mp4"

        # Apaga a mensagem do comando, se desejar
        try:
            await ctx.message.delete()
        except Exception:
            pass

        width = 80
        fps = 10
        delay = 1.0 / fps  # duração de cada frame (em segundos)

        # Define o diretório onde os frames serão salvos
        video_name = Path(video_path).stem
        output_dir = f"data/video/frames/{video_name}_w{width}"
        
        # Processa os frames se não houver pré-processados
        if not os.path.exists(output_dir) or len(os.listdir(output_dir)) == 0:
            loading_msg = await ctx.send("Processando frames do vídeo, por favor aguarde...")
            frame_count = process_video_frames(video_path, output_dir, width=width)
            await loading_msg.edit(content=f"Processamento concluído. {frame_count} frames gerados.")
        else:
            await ctx.send("Frames pré-processados encontrados. Iniciando reprodução...")

        # Carrega os frames já processados e pré-carrega os conteúdos em memória
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

        # Converte cada frame ASCII em uma imagem
        images = []
        for ascii_frame in ascii_frames:
            img = ascii_to_image(ascii_frame, font_size=10)
            images.append(img)

        # Gera o GIF animado
        gif_path = f"data/video/{video_name}_ascii.gif"
        try:
            # O parâmetro duration espera milissegundos
            images[0].save(gif_path, save_all=True, append_images=images[1:], duration=int(delay*1000), loop=0)
        except Exception as e:
            return await ctx.send(f"Erro ao gerar GIF: {e}")

        # Envia o GIF no chat
        try:
            await ctx.send(file=disnake.File(gif_path))
        except Exception as e:
            await ctx.send(f"Erro ao enviar GIF: {e}")

        # Limpa: deleta a pasta dos frames e o arquivo GIF
        try:
            shutil.rmtree(output_dir)
        except Exception as e:
            print(f"Erro ao deletar frames: {e}")
        try:
            os.remove(gif_path)
        except Exception as e:
            print(f"Erro ao deletar o GIF: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(GIF(bot))
