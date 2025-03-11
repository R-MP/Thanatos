import cv2
import asyncio
import disnake
from disnake.ext import commands

def convert_frame_to_ascii(frame, width=80):
    """
    Converte um frame (imagem) para ASCII.
    Este é um exemplo simples. Você precisará ajustar a lógica para obter um resultado bom.
    """
    # Redimensiona o frame mantendo a proporção
    height, original_width = frame.shape[:2]
    aspect_ratio = height / original_width
    new_height = int(aspect_ratio * width * 0.55)  # 0.55 é um fator de correção para fontes monoespaçadas
    resized_frame = cv2.resize(frame, (width, new_height))
    # Converte para escala de cinza
    gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    
    # Mapeamento de níveis de cinza para caracteres ASCII
    ascii_chars = " .:-=+*#%@"
    ascii_frame = ""
    for pixel in gray.flatten():
        ascii_frame += ascii_chars[int(pixel) * len(ascii_chars) // 256]
    # Adiciona quebras de linha
    ascii_frame = "\n".join([ascii_frame[i:i+width] for i in range(0, len(ascii_frame), width)])
    return ascii_frame

class VideoASCIICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def video_to_ascii_frames(self, video_path: str, width: int = 80, max_frames: int = None):
        """
        Lê um vídeo e converte cada frame para ASCII.
        max_frames: se definido, limita a quantidade de frames processados.
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ascii_frame = convert_frame_to_ascii(frame, width=width)
            frames.append(ascii_frame)
            count += 1
            if max_frames and count >= max_frames:
                break
        cap.release()
        return frames

    @commands.command(name="apple", help="Reproduz um vídeo em ASCII no chat.")
    async def apple(self, ctx: commands.Context):
        video_path = "data/video/badapple.mp4"

        # Exclui a mensagem do comando, se desejado
        try:
            await ctx.message.delete()
        except Exception:
            pass

        width = 50
        fps = 16
        delay = 1.0 / fps

        # Converte o vídeo em frames ASCII
        frames = self.video_to_ascii_frames(video_path, width=width, max_frames=200)  # Limite de frames para não demorar demais
        if not frames:
            return await ctx.send("Não foi possível processar o vídeo.")

        # Envia uma mensagem inicial que será editada
        message = await ctx.send("```\nCarregando vídeo...\n```")

        # Atualiza a mensagem com cada frame
        for frame in frames:
            try:
                await message.edit(content=f"```\n{frame}\n```")
                await asyncio.sleep(delay)
            except Exception as e:
                print("Erro ao editar mensagem:", e)
                break

        # Após terminar, deleta a mensagem ou envia uma mensagem final
        try:
            await message.delete()
        except Exception:
            pass

def setup(bot: commands.Bot):
    bot.add_cog(VideoASCIICog(bot))
