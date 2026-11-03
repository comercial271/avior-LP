#!/usr/bin/env python3
"""
Meme AVIOR: faixa preta com a legenda em branco em cima e o clipe embaixo.

Uso:
    python3 videos/meme-tokens-quarta/montar.py clipe.mp4 [saida.mp4]

O clipe e recortado para preencher a area abaixo da faixa (1080x1920 no total).
O audio do clipe sai mudo: o som da trend entra no proprio Instagram.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FAIXA = 560
# Versões publicadas:
#   "POV: QUANDO OS TOKENS DO CLAUDE TERMINAM NA QUARTA-FEIRA E EU SÓ CONSIGO TRABALHAR NA SEMANA QUE VEM"
LEGENDA = "POV: O FUNCIONÁRIO QUE FAZIA TUDO PEDIU DEMISSÃO E NINGUÉM SABE COMO ELE FAZIA"

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "..", "..", "carrosseis", "_render", "fonts")


def faixa_png(caminho):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, FAIXA], fill=(0, 0, 0, 255))
    f = ImageFont.truetype(os.path.join(FONTS, "Poppins-Bold.ttf"), 60)
    # quebra centralizada
    linhas, cur = [], ""
    for p in LEGENDA.split():
        t = (cur + " " + p).strip()
        if d.textlength(t, font=f) > W - 140:
            linhas.append(cur)
            cur = p
        else:
            cur = t
    linhas.append(cur)
    lh = f.size * 1.32
    y = (FAIXA - len(linhas) * lh) / 2 + 10
    for l in linhas:
        d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill=(255, 255, 255, 255))
        y += lh
    img.save(caminho)


def main():
    clipe = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "meme-tokens-quarta.mp4")
    png = os.path.join(AQUI, "faixa.png")
    faixa_png(png)
    vh = H - FAIXA
    filtro = (f"[0:v]scale={W}:{vh}:force_original_aspect_ratio=increase,crop={W}:{vh},"
              f"pad={W}:{H}:0:{FAIXA}:black,setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clipe, "-i", png,
                    "-filter_complex", filtro, "-map", "[out]", "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", "30",
                    "-movflags", "+faststart", saida], check=True)
    print("ok:", saida)


if __name__ == "__main__":
    main()
