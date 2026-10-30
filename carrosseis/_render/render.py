#!/usr/bin/env python3
"""
Renderizador do carrossel AVIOR.

Uso:
    python render.py spec.json --out /mnt/user-data/outputs/carrossel-avior

Le um spec JSON com a lista de slides e gera PNGs 1080x1350 + um .zip.
Ver references/spec.md para o formato completo do JSON.
"""
import argparse
import json
import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- identidade
W, H = 1080, 1350
BG = (10, 10, 10)
CHAMP = (214, 188, 142)        # champanhe: frase-chave, acento
CHAMP_DIM = (150, 132, 100)    # champanhe apagado: filete, rodape
WHITE = (242, 240, 236)        # off-white: titulo
GREY = (140, 138, 134)         # cinza: apoio
FAINT = (70, 68, 64)           # quase invisivel: numeracao
BORDER = (52, 50, 46)

MARGIN = 96
MAXW = W - 2 * MARGIN
SCALE = 1.14                   # calibrado para leitura no feed do celular

CORES = {"branco": WHITE, "champanhe": CHAMP, "cinza": GREY, "fraco": FAINT}

FONT_DIRS = [
    os.environ.get("AVIOR_FONTS", ""),
    "/usr/share/fonts/truetype/google-fonts/",
    os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"),
]


def _font_path(nome):
    for d in FONT_DIRS:
        p = os.path.join(d, nome)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        f"Fonte {nome} nao encontrada. Instale Lora e Poppins ou coloque os .ttf em assets/fonts/."
    )


def lora(sz, italic=False):
    sz = int(sz * SCALE)
    return ImageFont.truetype(
        _font_path("Lora-Italic-Variable.ttf" if italic else "Lora-Variable.ttf"), sz
    )


def pop(sz, peso="Light"):
    sz = int(sz * SCALE)
    return ImageFont.truetype(_font_path(f"Poppins-{peso}.ttf"), sz)


# ------------------------------------------------------------------ tipografia
# Papeis tipograficos. Serif (Lora) carrega a frase que a pessoa vai lembrar.
# Sans light (Poppins) carrega o apoio. Nunca o contrario.
PAPEIS = {
    "titulo":   dict(fn=lambda: lora(64), cor=WHITE, lh=1.32, gap=52),
    "manchete": dict(fn=lambda: lora(78), cor=CHAMP, lh=1.28, gap=56),
    "impacto":  dict(fn=lambda: lora(96), cor=WHITE, lh=1.20, gap=60),
    "citacao":  dict(fn=lambda: lora(46, italic=True), cor=CHAMP, lh=1.40, gap=44),
    "apoio":    dict(fn=lambda: pop(34), cor=GREY, lh=1.55, gap=44),
    "destaque": dict(fn=lambda: pop(38, "Medium"), cor=CHAMP, lh=1.50, gap=44),
    "lista":    dict(fn=lambda: pop(32), cor=GREY, lh=1.70, gap=44),
}


def bloco_fmt(b):
    base = dict(PAPEIS[b.get("papel", "apoio")])
    f = base["fn"]()
    if "tamanho" in b:
        nome = b.get("papel", "apoio")
        if nome in ("titulo", "manchete", "impacto", "citacao"):
            f = lora(b["tamanho"], italic=(nome == "citacao"))
        else:
            f = pop(b["tamanho"], "Medium" if nome == "destaque" else "Light")
    cor = CORES.get(b.get("cor"), base["cor"])
    return dict(text=b["texto"], font=f, color=cor, lh=b.get("lh", base["lh"]), gap=b.get("gap", base["gap"]))


def wrap(d, text, font, maxw):
    linhas = []
    for para in text.split("\n"):
        if not para.strip():
            linhas.append("")
            continue
        cur = ""
        for wd in para.split(" "):
            t = (cur + " " + wd).strip()
            if d.textlength(t, font=font) <= maxw:
                cur = t
            else:
                if cur:
                    linhas.append(cur)
                cur = wd
        linhas.append(cur)
    return linhas


def altura(d, blocos):
    tot = 0
    for b in blocos:
        for l in wrap(d, b["text"], b["font"], MAXW):
            tot += b["font"].size * b["lh"] if l else b["font"].size * 0.6
        tot += b["gap"]
    return tot - (blocos[-1]["gap"] if blocos else 0)


def desenha(d, blocos, y):
    for b in blocos:
        for l in wrap(d, b["text"], b["font"], MAXW):
            if not l:
                y += b["font"].size * 0.6
                continue
            d.text((MARGIN, y), l, font=b["font"], fill=b["color"])
            y += b["font"].size * b["lh"]
        y += b["gap"]
    return y


def canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # filete lateral: assinatura que amarra o carrossel inteiro
    d.rectangle([0, 0, 6, H], fill=(30, 26, 20))
    d.rectangle([0, 0, 6, 260], fill=CHAMP_DIM)
    return img, d


def rodape(d, handle, num):
    f = pop(24)
    d.text((MARGIN, H - 132), handle, font=f, fill=CHAMP_DIM)
    if num:
        d.text((W - MARGIN - d.textlength(num, font=f), H - 132), num, font=f, fill=FAINT)


def arredonda(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0], im.size[1]], radius=r, fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0))
    out.putalpha(m)
    return out


# --------------------------------------------------------------- tipos de slide
def slide_texto(s, handle, num):
    img, d = canvas()
    blocos = [bloco_fmt(b) for b in s["blocos"]]
    desenha(d, blocos, (H - altura(d, blocos)) / 2 - 20)
    if s.get("filete"):
        d.rectangle([MARGIN, H - 250, MARGIN + 70, H - 248], fill=CHAMP_DIM)
    rodape(d, handle, num)
    return img


def slide_print(s, handle, num):
    """Print de rede social emoldurado. Prova documental, nao colagem."""
    img, d = canvas()
    topo = [bloco_fmt(b) for b in s.get("acima", [])]
    y = desenha(d, topo, 210) if topo else 210

    card = Image.open(s["imagem"])
    if s.get("recorte"):
        card = card.crop(tuple(s["recorte"]))
    cw = MAXW
    ch = int(card.size[1] * cw / card.size[0])
    card = arredonda(card.resize((cw, ch), Image.LANCZOS), 24)

    cy = int(y + 30)
    d.rounded_rectangle([MARGIN - 3, cy - 3, MARGIN + cw + 3, cy + ch + 3],
                        radius=27, outline=(60, 52, 40), width=3)
    img.paste(card, (MARGIN, cy), card)

    abaixo = [bloco_fmt(b) for b in s.get("abaixo", [])]
    if abaixo:
        desenha(d, abaixo, cy + ch + 70)
    rodape(d, handle, num)
    return img


def slide_foto(s, handle, num):
    """Foto sangrada com veu preto e gradiente. Texto sempre na base."""
    ph = Image.open(s["imagem"]).convert("RGB")
    ar_t, ar_p = W / H, ph.size[0] / ph.size[1]
    if ar_p > ar_t:
        nh, nw = H, int(H * ar_p)
    else:
        nw, nh = W, int(W / ar_p)
    ph = ph.resize((nw, nh), Image.LANCZOS).crop(((nw - W) // 2, 0, (nw - W) // 2 + W, H))

    img = Image.blend(ph, Image.new("RGB", (W, H), (8, 8, 8)), s.get("veu", 0.32))
    grad = Image.new("L", (1, H), 0)
    for i in range(H):
        t = max(0.0, (i - H * 0.42) / (H * 0.58))
        grad.putpixel((0, i), int(245 * (t ** 1.5)))
    img = Image.composite(Image.new("RGB", (W, H), (6, 6, 6)), img, grad.resize((W, H)))

    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 6, H], fill=(30, 26, 20))
    d.rectangle([0, 0, 6, 260], fill=CHAMP_DIM)
    blocos = [bloco_fmt(b) for b in s["blocos"]]
    desenha(d, blocos, H - 300 - altura(d, blocos))
    rodape(d, handle, num)
    return img


def slide_chips(s, handle, num):
    """Lista de itens em chips. Item aceso em champanhe = o que a narrativa escolhe."""
    img, d = canvas()
    y = 300
    if s.get("titulo"):
        f = lora(76)
        d.text((MARGIN, y), s["titulo"], font=f, fill=WHITE)
        y += f.size * 1.5

    CH, GAPY = int(108 * SCALE), 26
    fn_nome, fn_num = pop(44), pop(22)
    for i, it in enumerate(s["itens"]):
        nome = it["nome"] if isinstance(it, dict) else it
        aceso = isinstance(it, dict) and it.get("aceso")
        top = y + i * (CH + GAPY)
        cor = CHAMP if aceso else GREY
        d.rounded_rectangle([MARGIN, top, W - MARGIN, top + CH], radius=14,
                            outline=CHAMP_DIM if aceso else BORDER, width=2)
        cx, cy = MARGIN + 52, top + CH / 2
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=cor if aceso else FAINT)
        d.text((MARGIN + 96, top + CH / 2 - fn_nome.size * 0.68), nome, font=fn_nome, fill=cor)
        d.text((W - MARGIN - 60, top + CH / 2 - fn_num.size * 0.6), "%02d" % (i + 1),
               font=fn_num, fill=FAINT)

    y2 = y + len(s["itens"]) * (CH + GAPY) + 40
    if s.get("abaixo"):
        desenha(d, [bloco_fmt(b) for b in s["abaixo"]], y2)
    rodape(d, handle, num)
    return img


def slide_numero(s, handle, num):
    """Item de lista numerada. Numero gigante vazado atras do titulo,
    filete separando a ideia do apoio, sintese em champanhe no fim."""
    img, d = canvas()
    fn = lora(560)
    n = s["numero"]
    nx = W - d.textlength(n, font=fn) + int(fn.size * 0.12)
    d.text((nx, 40), n, font=fn, fill=BG, stroke_width=3, stroke_fill=(92, 80, 60))

    f_rot = pop(24, "Medium")
    d.text((MARGIN, 230), s.get("rotulo", n), font=f_rot, fill=CHAMP_DIM)
    topo = [bloco_fmt(dict({"papel": "titulo"}, **b)) for b in s["titulo"]]
    y = desenha(d, topo, 290)

    y = max(y + 30, 660)
    d.rectangle([MARGIN, y, MARGIN + 70, y + 2], fill=CHAMP_DIM)
    blocos = [bloco_fmt(b) for b in s["blocos"]]
    desenha(d, blocos, y + 70)
    rodape(d, handle, num)
    return img


TIPOS = {"numero": slide_numero, "texto": slide_texto, "print": slide_print, "foto": slide_foto, "chips": slide_chips}


# ------------------------------------------------------------------- verificacao
def verifica(img, idx, tipo, avisos):
    """Checa o que da errado de verdade: texto colado no rodape ou estourando."""
    import numpy as np
    a = np.array(img.convert("L"))[:1180, 40:]
    linhas = a.max(axis=1)
    nz = [j for j, v in enumerate(linhas) if v > 90]
    if not nz:
        return
    if 1180 - nz[-1] < 40:
        avisos.append(f"slide {idx}: conteudo a menos de 40px do rodape, reduza texto")
    if nz[0] < 60 and tipo != "foto":  # foto e sangrada de proposito
        avisos.append(f"slide {idx}: conteudo colado no topo")


def travessao(spec, avisos):
    """A Juliana nao usa travessao. Nunca. Pega antes de virar PNG."""
    bruto = json.dumps(spec, ensure_ascii=False)
    for ch in ("\u2014", "\u2013"):
        if ch in bruto:
            avisos.append(f"ERRO: travessao '{ch}' no texto. Reescreva com ponto ou virgula.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", default="/mnt/user-data/outputs/carrossel-avior")
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    handle = spec.get("handle", "@sejaavior")
    slides = spec["slides"]
    total = len(slides)

    avisos = []
    travessao(spec, avisos)
    if any(v.startswith("ERRO") for v in avisos):
        print("\n".join(avisos))
        sys.exit(1)

    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.out):
        if f.endswith(".png"):
            os.remove(os.path.join(a.out, f))

    caminhos = []
    for i, s in enumerate(slides, 1):
        tipo = s.get("tipo", "texto")
        img = TIPOS[tipo](s, handle, f"{i}/{total}")
        verifica(img, i, tipo, avisos)
        p = os.path.join(a.out, "slide_%02d.png" % i)
        img.save(p, quality=95)
        caminhos.append(p)

    z = os.path.join(os.path.dirname(a.out.rstrip("/")), os.path.basename(a.out.rstrip("/")) + ".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in caminhos:
            zf.write(p, os.path.basename(p))

    print("gerados: %d slides" % total)
    print("zip: %s" % z)
    for v in avisos:
        print("aviso:", v)


if __name__ == "__main__":
    main()
