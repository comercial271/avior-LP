#!/usr/bin/env python3
"""
Renderizador AVIOR, modelo "faixas" (lista numerada em duas metades).

Uso:
    AVIOR_FONTS=<pasta com Anton e Poppins> python render_faixas.py spec.json --out <pasta>

Cada slide tem uma faixa de cima (preta ou champanhe) com titulo condensado
em caixa alta, e uma metade de baixo clara com o texto de apoio e a frase de
fechamento em negrito. Trecho entre {chaves} sai no tom de acento.
"""
import argparse
import json
import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
FAIXA = 640                    # altura da faixa de cima
MARGIN = 90
MAXW = W - 2 * MARGIN

PRETO = (14, 13, 12)
CHAMP = (214, 188, 142)        # acento sobre preto
BRONZE = (150, 112, 52)        # acento sobre claro (champanhe nao tem contraste no claro)
CLARO = (239, 236, 231)
TEXTO = (38, 37, 35)
CINZA = (120, 117, 112)
BRANCO = (244, 242, 238)

FONT_DIRS = [
    os.environ.get("AVIOR_FONTS", ""),
    "/usr/share/fonts/truetype/google-fonts/",
    os.path.join(os.path.dirname(__file__), "fonts"),
]


def fonte(nome, sz):
    for d in FONT_DIRS:
        p = os.path.join(d, nome)
        if d and os.path.exists(p):
            return ImageFont.truetype(p, sz)
    raise FileNotFoundError(f"Fonte {nome} nao encontrada. Defina AVIOR_FONTS.")


def anton(sz):
    return fonte("Anton-Regular.ttf", sz)


def pop(sz, peso="Regular"):
    return fonte(f"Poppins-{peso}.ttf", sz)


# ------------------------------------------------------------------ texto rico
def tokens(texto):
    """'a {b c} d' -> [('a', False), ('b', True), ('c', True), ('d', False)]"""
    out, acento = [], False
    for linha in texto.split("\n"):
        for wd in linha.split(" "):
            if not wd:
                continue
            ini = wd.startswith("{")
            fim = wd.endswith("}")
            limpa = wd.strip("{}")
            if ini:
                acento = True
            out.append((limpa, acento))
            if fim:
                acento = False
        out.append(("\n", False))
    return out[:-1]


def quebra(d, texto, font, maxw):
    linhas, cur = [], []
    for wd, ac in tokens(texto):
        if wd == "\n":
            linhas.append(cur)
            cur = []
            continue
        teste = " ".join(w for w, _ in cur + [(wd, ac)])
        if cur and d.textlength(teste, font=font) > maxw:
            linhas.append(cur)
            cur = []
        cur.append((wd, ac))
    linhas.append(cur)
    return linhas


def escreve(d, texto, font, x, y, cor, cor_acento, lh, maxw=MAXW):
    esp = d.textlength(" ", font=font)
    for linha in quebra(d, texto, font, maxw):
        cx = x
        for wd, ac in linha:
            d.text((cx, y), wd, font=font, fill=cor_acento if ac else cor)
            cx += d.textlength(wd, font=font) + esp
        y += font.size * lh
    return y


def assinatura(img, d, spec):
    """Avatar redondo + nome espacado, como selo de autoria no rodape."""
    a = spec.get("assinatura")
    if not a:
        return
    R = 128
    x, y = 70, H - 70 - R
    if a.get("foto"):
        ph = Image.open(a["foto"]).convert("RGB")
        s = min(ph.size)
        cx = ph.size[0] // 2
        top = int(ph.size[1] * a.get("foto_topo", 0.08))
        ph = ph.crop((cx - s // 2, top, cx + s // 2, top + s)).resize((R, R), Image.LANCZOS)
        m = Image.new("L", (R, R), 0)
        ImageDraw.Draw(m).ellipse([0, 0, R, R], fill=255)
        d.ellipse([x - 4, y - 4, x + R + 4, y + R + 4], fill=CHAMP)
        img.paste(ph, (x, y), m)
    fn, ft = pop(30, "SemiBold"), pop(19, "Medium")
    tx = x + R + 28

    def espacado(t, f, yy, cor, sp):
        cx = tx
        for ch in t:
            d.text((cx, yy), ch, font=f, fill=cor)
            cx += d.textlength(ch, font=f) + sp

    espacado(a["nome"].upper(), fn, y + R / 2 - 40, TEXTO, 5)
    espacado(a.get("cargo", "").upper(), ft, y + R / 2 + 6, CINZA, 6)


# --------------------------------------------------------------- tipos de slide
def slide_capa(s, spec):
    img = Image.new("RGB", (W, H), CLARO)
    d = ImageDraw.Draw(img)
    f = anton(s.get("tamanho", 124))
    linhas = quebra(d, s["titulo"], f, MAXW)
    alt = len(linhas) * f.size * 1.08
    y = (H - alt) / 2 - 40
    d.rectangle([MARGIN, y - 60, MARGIN + 90, y - 52], fill=BRONZE)
    y = escreve(d, s["titulo"], f, MARGIN, y, PRETO, BRONZE, 1.08)
    if s.get("apoio"):
        y = escreve(d, s["apoio"], pop(32), MARGIN, y + 36, CINZA, BRONZE, 1.5)
    # seta
    ya = y + 70
    d.rectangle([MARGIN, ya, MARGIN + 84, ya + 6], fill=BRONZE)
    d.polygon([(MARGIN + 104, ya + 3), (MARGIN + 76, ya - 16), (MARGIN + 76, ya + 22)], fill=BRONZE)
    assinatura(img, d, spec)
    return img


def metade_baixo(d, s, y0):
    y = escreve(d, s["texto"], pop(34), MARGIN, y0 + 74, TEXTO, BRONZE, 1.55)
    if s.get("sintese"):
        escreve(d, s["sintese"], pop(36, "Bold"), MARGIN, y + 34, PRETO, BRONZE, 1.45)


def recorta(caminho, w, h, topo=0.06, foco_x=0.5):
    """Recorte tipo 'cover' de um retrato, ancorado perto do rosto."""
    ph = Image.open(caminho).convert("RGB")
    esc = max(w / ph.size[0], h / ph.size[1])
    ph = ph.resize((int(ph.size[0] * esc) + 1, int(ph.size[1] * esc) + 1), Image.LANCZOS)
    x = int(min(max(ph.size[0] * foco_x - w / 2, 0), ph.size[0] - w))
    y = int(min(ph.size[1] * topo, ph.size[1] - h))
    return ph.crop((x, y, x + w, y + h))


def esmaece(ph, cor, largura):
    """Funde a borda esquerda da foto na cor da faixa."""
    w, h = ph.size
    grad = Image.new("L", (w, 1))
    for i in range(w):
        grad.putpixel((i, 0), int(255 * max(0.0, 1 - i / largura) ** 1.4))
    return Image.composite(Image.new("RGB", ph.size, cor), ph, grad.resize(ph.size))


def etiqueta(d, texto, x_dir, y, cor):
    f = pop(19, "SemiBold")
    sp = 5
    larg = sum(d.textlength(c, font=f) + sp for c in texto) - sp
    cx = x_dir - larg
    for c in texto:
        d.text((cx, y), c, font=f, fill=cor)
        cx += d.textlength(c, font=f) + sp


def vazado(base, xy, texto, fn, cor, espessura=3):
    """Desenha so o contorno do texto (o PIL preenche quando nao ha fill)."""
    borda = Image.new("L", base.size, 0)
    miolo = Image.new("L", base.size, 0)
    ImageDraw.Draw(borda).text(xy, texto, font=fn, fill=255, stroke_width=espessura, stroke_fill=255)
    ImageDraw.Draw(miolo).text(xy, texto, font=fn, fill=255)
    from PIL import ImageChops
    base.paste(Image.new("RGB", base.size, cor), (0, 0), ImageChops.subtract(borda, miolo))


def slide_item(s, spec):
    img = Image.new("RGB", (W, H), CLARO)
    d = ImageDraw.Draw(img)
    escura = s.get("faixa", "preta") == "preta"
    fundo, cor_tit, cor_ac, traco = (
        (PRETO, BRANCO, CHAMP, CHAMP) if escura else (CHAMP, PRETO, PRETO, PRETO)
    )

    faixa = Image.new("RGB", (W, FAIXA), fundo)
    fd = ImageDraw.Draw(faixa)
    n = s["numero"]
    pessoa = s.get("pessoa")
    if pessoa:
        # retrato do time na direita, fundido na faixa; numero vazado por cima
        PW = 600
        ph = recorta(pessoa["foto"], PW, FAIXA, pessoa.get("topo", 0.06), pessoa.get("foco_x", 0.5))
        if escura:
            ph = Image.blend(ph, Image.new("RGB", ph.size, PRETO), 0.12)
        faixa.paste(esmaece(ph, fundo, 380), (W - PW, 0))
        rodape_foto = Image.new("L", (1, 120))
        for i in range(120):
            rodape_foto.putpixel((0, i), int(200 * (i / 120) ** 1.3))
        faixa.paste(Image.new("RGB", (PW, 120), PRETO), (W - PW, FAIXA - 120),
                    rodape_foto.resize((PW, 120)))
        etiqueta(fd, pessoa["nome"].upper(), W - 50, FAIXA - 82, BRANCO)
        etiqueta(fd, pessoa["cargo"].upper(), W - 50, FAIXA - 50, CHAMP)
        largura = s.get("largura", 520)
        ft = anton(s.get("tamanho", 92))
        y_fim = escreve(fd, s["titulo"], ft, MARGIN, 110, cor_tit, cor_ac, 1.08, maxw=largura)
        # numero vazado embaixo do titulo, cortado pela borda da faixa
        vazado(faixa, (MARGIN - 12, max(y_fim - 40, 330)), n, anton(400), traco)
        img.paste(faixa, (0, 0))
        metade_baixo(d, s, FAIXA)
        assinatura(img, d, spec)
        return img
    else:
        fn = anton(700)
        nx = W - fd.textlength(n, font=fn) + 120
        fd.text((nx, 40), n, font=fn, fill=fundo, stroke_width=3, stroke_fill=traco)
        largura = s.get("largura", MAXW)
    ft = anton(s.get("tamanho", 108 if not pessoa else 92))
    escreve(fd, s["titulo"], ft, MARGIN, 110, cor_tit, cor_ac, 1.08, maxw=largura)
    img.paste(faixa, (0, 0))

    metade_baixo(d, s, FAIXA)
    assinatura(img, d, spec)
    return img


def slide_foto(s, spec):
    img = Image.new("RGB", (W, H), CLARO)
    d = ImageDraw.Draw(img)
    if s.get("time"):
        # mosaico do time: uma faixa vertical por pessoa
        n = len(s["time"])
        larg = W // n
        ph = Image.new("RGB", (W, FAIXA), PRETO)
        for i, p in enumerate(s["time"]):
            w = larg if i < n - 1 else W - larg * (n - 1)
            ph.paste(recorta(p["foto"], w, FAIXA, p.get("topo", 0.04), p.get("foco_x", 0.5)), (i * larg, 0))
        grad = Image.new("L", (1, FAIXA))
        for i in range(FAIXA):
            grad.putpixel((0, i), int(245 * max(0.0, (i - FAIXA * 0.38) / (FAIXA * 0.62)) ** 1.2))
        ph = Image.composite(Image.new("RGB", ph.size, PRETO), ph, grad.resize(ph.size))
        img.paste(ph, (0, 0))
        ft = anton(s.get("tamanho", 100))
        alt = len(quebra(d, s["titulo"], ft, MAXW)) * ft.size * 1.08
        escreve(d, s["titulo"], ft, MARGIN, FAIXA - 50 - alt, BRANCO, CHAMP, 1.08)
        metade_baixo(d, s, FAIXA)
        assinatura(img, d, spec)
        return img
    else:
        ph = Image.open(s["imagem"]).convert("RGB")
        esc = W / ph.size[0]
        ph = ph.resize((W, int(ph.size[1] * esc)), Image.LANCZOS)
        top = int(ph.size[1] * s.get("foto_topo", 0.0))
        ph = ph.crop((0, top, W, top + FAIXA))
        # gradiente escuro na esquerda para o titulo respirar
        grad = Image.new("L", (W, 1))
        for i in range(W):
            grad.putpixel((i, 0), int(235 * max(0.0, 1 - i / (W * 0.75)) ** 1.2))
        ph = Image.composite(Image.new("RGB", ph.size, PRETO), ph, grad.resize(ph.size))
        img.paste(ph, (0, 0))
        largura = s.get("largura", 560)
    ft = anton(s.get("tamanho", 108))
    escreve(d, s["titulo"], ft, MARGIN, 90, BRANCO, CHAMP, 1.08, maxw=largura)
    metade_baixo(d, s, FAIXA)
    assinatura(img, d, spec)
    return img


TIPOS = {"capa": slide_capa, "item": slide_item, "foto": slide_foto}


def verifica(img, idx, avisos):
    """Texto da metade de baixo nao pode invadir a assinatura."""
    import numpy as np
    a = np.array(img.convert("L"))[FAIXA:H - 240, 60:]
    linhas = [j for j, v in enumerate(a.min(axis=1)) if v < 120]
    if linhas and FAIXA + linhas[-1] > H - 270:
        avisos.append(f"slide {idx}: texto encostando na assinatura, reduza")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    bruto = json.dumps(spec, ensure_ascii=False)
    if "—" in bruto or "–" in bruto:
        print("ERRO: travessao no texto. Reescreva com ponto ou virgula.")
        sys.exit(1)

    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.out):
        if f.endswith(".png"):
            os.remove(os.path.join(a.out, f))

    avisos, caminhos = [], []
    for i, s in enumerate(spec["slides"], 1):
        img = TIPOS[s["tipo"]](s, spec)
        verifica(img, i, avisos)
        p = os.path.join(a.out, "slide_%02d.png" % i)
        img.save(p)
        caminhos.append(p)

    z = a.out.rstrip("/") + ".zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in caminhos:
            zf.write(p, os.path.basename(p))
    print("gerados: %d slides\nzip: %s" % (len(caminhos), z))
    for v in avisos:
        print("aviso:", v)


if __name__ == "__main__":
    main()
