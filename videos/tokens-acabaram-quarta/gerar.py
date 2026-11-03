#!/usr/bin/env python3
"""
Reel AVIOR: "Quando os tokens do Claude acabam na quarta-feira".

Uso:
    python3 videos/tokens-acabaram-quarta/gerar.py [saida.mp4]

Gera um MP4 1080x1920, 30 fps, so tipografia (sem fotos), nas cores da
AVIOR. Os quadros sao desenhados com Pillow e enviados direto ao ffmpeg.
O audio sai mudo de proposito: o som da trend entra no proprio Instagram.
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
M = 96                          # margem lateral
MAXW = W - 2 * M

PRETO = (14, 13, 12)
CHAMP = (214, 188, 142)
BRONZE = (150, 112, 52)
CLARO = (239, 236, 231)
BRANCO = (244, 242, 238)
TEXTO = (38, 37, 35)
CINZA_P = (190, 186, 180)       # texto de apoio sobre preto
MARROM = (60, 50, 36)           # texto de apoio sobre champanhe

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "..", "..", "carrosseis", "_render", "fonts")


def anton(sz):
    return ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), sz)


def pop(sz, peso="Regular"):
    return ImageFont.truetype(os.path.join(FONTS, f"Poppins-{peso}.ttf"), sz)


# ------------------------------------------------------------------ easing
def clamp(x):
    return max(0.0, min(1.0, x))


def out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def out_back(x, s=1.7):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


# ------------------------------------------------------------------ texto
_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def tokens(texto):
    """'a {b c} d' vira palavras com marca de acento."""
    out, ac = [], False
    for wd in texto.split(" "):
        if not wd:
            continue
        if wd.startswith("{"):
            ac = True
        out.append((wd.strip("{}"), ac))
        if wd.endswith("}"):
            ac = False
    return out


def linhas(texto, font, maxw=MAXW):
    """Quebra respeitando \\n manual e a largura maxima."""
    res = []
    for par in texto.split("\n"):
        cur = []
        for wd, ac in tokens(par):
            teste = " ".join(w for w, _ in cur + [(wd, ac)])
            if cur and _tmp.textlength(teste, font=font) > maxw:
                res.append(cur)
                cur = []
            cur.append((wd, ac))
        res.append(cur)
    return res


def camada(linha, font, cor, cor_ac):
    """Uma linha de texto em RGBA transparente, pronta para animar."""
    esp = _tmp.textlength(" ", font=font)
    larg = int(sum(_tmp.textlength(w, font=font) for w, _ in linha) + esp * max(len(linha) - 1, 0)) + 8
    alt = int(font.size * 1.35)
    im = Image.new("RGBA", (max(larg, 1), alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 0
    for w, ac in linha:
        d.text((x, 0), w, font=font, fill=cor_ac if ac else cor)
        x += _tmp.textlength(w, font=font) + esp
    return im


def cola(base, im, x, y, alpha=1.0, escala=1.0):
    if alpha <= 0:
        return
    if escala != 1.0:
        nw, nh = max(1, int(im.width * escala)), max(1, int(im.height * escala))
        im = im.resize((nw, nh), Image.LANCZOS)
        x -= (nw - im.width / escala) / 2 if False else 0
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    base.alpha_composite(im, (int(x), int(y)))


class Bloco:
    """Texto que entra linha a linha subindo e aparecendo."""

    def __init__(self, texto, font, cor, cor_ac, y, t0, stagger=0.10, dur=0.38, lh=1.08, maxw=MAXW):
        self.cam = [camada(l, font, cor, cor_ac) for l in linhas(texto, font, maxw)]
        self.y, self.t0, self.stg, self.dur = y, t0, stagger, dur
        self.passo = font.size * lh
        self.fim = y + len(self.cam) * self.passo

    def desenha(self, base, t):
        for i, im in enumerate(self.cam):
            p = out_cubic((t - self.t0 - i * self.stg) / self.dur)
            cola(base, im, M, self.y + i * self.passo + (1 - p) * 70, alpha=p)


# ------------------------------------------------------------------ pecas
def rotulo(base, texto, cor, t, t0):
    p = out_cubic((t - t0) / 0.3)
    if p <= 0:
        return
    d = ImageDraw.Draw(base)
    f = pop(32, "SemiBold")
    x = M
    for c in texto.upper():
        d.text((x, 250), c, font=f, fill=cor + (int(255 * p),))
        x += d.textlength(c, font=f) + 7
    d.rectangle([M, 312, M + int(80 * p), 316], fill=cor)


def aviso(base, t, t0, y_final):
    """Cartao de aviso generico que desce do topo com um quique."""
    p = out_back((t - t0) / 0.55, 1.4)
    if t < t0:
        return
    cw, ch = MAXW, 230
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=36, fill=(34, 33, 31, 255), outline=(78, 73, 66, 255), width=3)
    d.ellipse([44, 52, 100, 108], outline=CHAMP, width=5)
    d.rectangle([69, 64, 75, 84], fill=CHAMP)
    d.rectangle([69, 90, 75, 96], fill=CHAMP)
    f = pop(38, "Medium")
    d.text((134, 46), "Você atingiu seu limite de uso.", font=f, fill=BRANCO)
    d.text((134, 112), "Seu acesso volta segunda, às 9h.", font=pop(34), fill=CINZA_P)
    y = -ch + (y_final + ch) * p
    cola(base, card, M, y, alpha=clamp((t - t0) / 0.15))


def batida(base, texto, font, cor, x, y, t, t0):
    """Palavra que bate na tela: entra grande e assenta, com tremidinha."""
    if t < t0:
        return 0, 0
    im = camada([(texto, False)], font, cor, cor)
    p = out_cubic((t - t0) / 0.22)
    esc = 1.9 - 0.9 * p
    nw, nh = int(im.width * esc), int(im.height * esc)
    big = im.resize((nw, nh), Image.LANCZOS)
    cola(base, big, x - (nw - im.width) / 2, y - (nh - im.height) / 2, alpha=p)
    # tremor logo depois do impacto
    dt = t - t0 - 0.22
    if 0 < dt < 0.25:
        amp = 14 * (1 - dt / 0.25)
        return int(amp * math.sin(dt * 90)), int(amp * math.cos(dt * 70))
    return 0, 0


def recarrega(base, cor, t, t0, x, y):
    """Setinha de atualizar girando e contador ate 7."""
    if t < t0:
        return
    d = ImageDraw.Draw(base)
    r = 58
    ang = (t - t0) * 720
    d.arc([x, y, x + 2 * r, y + 2 * r], start=ang, end=ang + 290, fill=cor, width=12)
    a = math.radians(ang)
    cx, cy = x + r + r * math.cos(a), y + r + r * math.sin(a)
    tang = a - math.pi / 2
    pts = [(cx + 24 * math.cos(tang), cy + 24 * math.sin(tang)),
           (cx + 22 * math.cos(a), cy + 22 * math.sin(a)),
           (cx - 22 * math.cos(a), cy - 22 * math.sin(a))]
    d.polygon(pts, fill=cor)
    n = min(7, 1 + int((t - t0) / 0.28))
    d.text((x + 2 * r + 44, y + 4), f"× {n}", font=anton(110), fill=cor)


def documento(base, t, t0, y):
    """Folha em branco com cursor piscando."""
    p = out_cubic((t - t0) / 0.4)
    if p <= 0:
        return
    d = ImageDraw.Draw(base)
    h = 430
    top = y + (1 - p) * 60
    d.rounded_rectangle([M, top, W - M, top + h], radius=22, fill=(252, 251, 248), outline=(205, 199, 189), width=3)
    for i in range(3):
        d.ellipse([M + 30 + i * 34, top + 26, M + 50 + i * 34, top + 46], fill=(205, 199, 189))
    if int((t - t0) * 2.2) % 2 == 0:
        d.rectangle([M + 60, top + 100, M + 66, top + 170], fill=TEXTO)


def checklist(base, itens, t, t0, y, cor, cor_ok):
    d = ImageDraw.Draw(base)
    f = pop(50, "Medium")
    for i, txt in enumerate(itens):
        p = out_back((t - t0 - i * 0.35) / 0.35)
        if t < t0 + i * 0.35:
            continue
        yy = y + i * 96
        cx, cy = M + 30, yy + 32
        rr = 28 * clamp(p)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=cor_ok)
        if p > 0.6:
            d.line([(cx - 13, cy + 1), (cx - 3, cy + 12), (cx + 15, cy - 11)], fill=CHAMP, width=7)
        d.text((M + 84, yy), txt, font=f, fill=cor)


# ------------------------------------------------------------------ roteiro
F_GRANDE = anton(150)
F_MEDIO = anton(124)
F_APOIO = pop(52)
LH_APOIO = 1.45
GAP = 90                        # respiro entre blocos


def apoio(texto, cor, cor_ac, y, t0, stagger=0.3):
    return Bloco(texto, F_APOIO, cor, cor_ac, y, t0, stagger, lh=LH_APOIO)


CENAS = []


def cena(ini, fim, fundo):
    def deco(fn):
        CENAS.append((ini, fim, fundo, fn))
        return fn
    return deco


@cena(0.0, 3.0, CLARO)
def c_capa(b, t):
    d = ImageDraw.Draw(b)
    p = out_cubic(t / 0.4)
    d.rectangle([M, 480, M + int(110 * p), 490], fill=BRONZE)
    tit = Bloco("QUANDO OS TOKENS DO CLAUDE ACABAM {NA QUARTA-FEIRA}", F_GRANDE, PRETO, BRONZE, 560, 0.15, 0.12)
    tit.desenha(b, t)
    apoio("e só voltam na segunda.", TEXTO, BRONZE, tit.fim + 60, 1.4).desenha(b, t)


@cena(3.0, 6.4, PRETO)
def c_aviso(b, t):
    rotulo(b, "Quarta, 14h32", CHAMP, t, 0.1)
    aviso(b, t, 0.35, 560)
    return batida(b, "TÁ.", anton(330), BRANCO, M, 930, t, 1.7)


@cena(6.4, 9.6, CHAMP)
def c_negacao(b, t):
    rotulo(b, "14h33", PRETO, t, 0.1)
    tit = Bloco("FASE 1:\n{NEGAÇÃO.}", F_GRANDE, PRETO, BRANCO, 520, 0.15)
    tit.desenha(b, t)
    recarrega(b, PRETO, t, 0.9, M, tit.fim + GAP)
    apoio("Atualizo a página sete vezes.\nVai que.", MARROM, BRANCO, tit.fim + GAP + 220, 1.3).desenha(b, t)


@cena(9.6, 13.2, PRETO)
def c_barganha(b, t):
    rotulo(b, "14h41", CHAMP, t, 0.1)
    tit = Bloco("FASE 2:\n{BARGANHA.}", F_GRANDE, BRANCO, CHAMP, 520, 0.15)
    tit.desenha(b, t)
    apoio("Prometo usar menos.\nPrometo não pedir 14 versões da legenda.\nNinguém responde.",
          CINZA_P, CHAMP, tit.fim + GAP, 0.9, 0.5).desenha(b, t)


@cena(13.2, 17.0, CLARO)
def c_antes(b, t):
    rotulo(b, "15h10", BRONZE, t, 0.1)
    tit = Bloco("FASE 3:\nLEMBRAR {COMO SE FAZIA ANTES.}", F_MEDIO, PRETO, BRONZE, 470, 0.15)
    tit.desenha(b, t)
    documento(b, t, 1.0, tit.fim + GAP)
    apoio("Olho pro cursor.\nO cursor olha pra mim.", TEXTO, BRONZE, tit.fim + GAP + 430 + 70, 1.6, 0.5).desenha(b, t)


@cena(17.0, 21.0, CHAMP)
def c_aceitacao(b, t):
    rotulo(b, "Quinta, 10h", PRETO, t, 0.1)
    tit = Bloco("FASE 4:\n{ACEITAÇÃO.}", F_GRANDE, PRETO, BRANCO, 520, 0.15)
    tit.desenha(b, t)
    checklist(b, ["Processo tá escrito.", "O time sabe o que fazer.", "A empresa continua rodando."],
              t, 1.0, tit.fim + GAP, PRETO, PRETO)
    Bloco("Ufa.", anton(120), PRETO, BRANCO, tit.fim + GAP + 3 * 96 + 70, 2.4).desenha(b, t)


@cena(21.0, 25.0, PRETO)
def c_virada(b, t):
    tit = Bloco("SE A SUA EMPRESA PARA QUANDO {UMA FERRAMENTA PARA,}", F_MEDIO, BRANCO, CHAMP, 420, 0.15, 0.14)
    tit.desenha(b, t)
    Bloco("o problema nunca foi a ferramenta.", anton(96), CHAMP, CHAMP, tit.fim + GAP, 1.6, 0.2).desenha(b, t)


@cena(25.0, 29.0, CLARO)
def c_cta(b, t):
    tit = Bloco("E AÍ, EM QUE {FASE} VOCÊ TÁ?", F_GRANDE, PRETO, BRONZE, 560, 0.15, 0.12)
    tit.desenha(b, t)
    sub = apoio("Comenta o número.\nA gente também já atualizou a página sete vezes.", TEXTO, BRONZE, tit.fim + GAP, 0.9)
    sub.desenha(b, t)
    p = out_cubic((t - 1.6) / 0.4)
    if p > 0:
        d = ImageDraw.Draw(b)
        d.text((M, sub.fim + 80), "@sejaavior", font=pop(48, "SemiBold"), fill=BRONZE)


DURACAO = CENAS[-1][1]


def quadro(t):
    for i, (ini, fim, fundo, fn) in enumerate(CENAS):
        if ini <= t < fim or i == len(CENAS) - 1:
            break
    base = Image.new("RGBA", (W, H), fundo + (255,))
    desloc = fn(base, t - ini) or (0, 0)
    # cortina: a cor da cena anterior sobe e revela a nova
    if i > 0:
        p = out_cubic((t - ini) / 0.32)
        if p < 1:
            ante = CENAS[i - 1][2]
            d = ImageDraw.Draw(base)
            d.rectangle([0, 0, W, int(H * (1 - p))], fill=ante + (255,))
    img = base.convert("RGB")
    if desloc != (0, 0):
        sh = Image.new("RGB", (W, H), fundo)
        sh.paste(img, desloc)
        img = sh
    return img


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "reel-tokens-acabaram.mp4")
    n = int(DURACAO * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", saida]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        proc.stdin.write(quadro(k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"ok: {saida} ({DURACAO:.0f}s, {n} quadros)")


if __name__ == "__main__":
    main()
