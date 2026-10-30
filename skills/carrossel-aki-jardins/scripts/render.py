#!/usr/bin/env python3
"""
Renderizador do carrossel AKI Jardins (@akijardins).

Uso:
    python render.py spec.json --out pasta-de-saida

Le um spec JSON (formato em references/spec.md) e gera:
  slide-01.png ... slide-NN.png  (todos 1080x1350, formato 4:5 do feed)
  legenda.md                      (texto para colar no Instagram)
  carrossel-<nome>.zip            (tudo junto, para baixar no celular)

Monta cada slide em HTML e fotografa com Chromium headless (Playwright,
ou o Chrome direto quando o Playwright nao esta instalado).
A identidade visual mora aqui: nao reescreva cores e fontes no spec.
"""
import argparse
import base64
import glob
import html
import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unicodedata
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FONTES = os.path.join(RAIZ, "assets", "fonts")
LOGO = os.path.join(RAIZ, "assets", "logo.png")

# Todo slide sai exatamente neste tamanho. Carrossel com slides de tamanhos
# diferentes e cortado pelo Instagram no formato do primeiro: aqui isso nao acontece.
W, H = 1080, 1350

# ---------------------------------------------------------------- identidade
# Nomes do playbook de posicionamento: Capim, Areia, Oleo, Latao.
CAPIM = "#24331C"       # verde escuro, fundo principal
CAPIM2 = "#2E4124"      # verde um tom acima, alterna com Areia nos cards do meio
AREIA = "#F3EEDF"       # creme, texto no verde e fundo dos cards claros
OLEO = "#1B1A16"        # quase preto, texto no fundo Areia
LATAO = "#D0B880"       # dourado, logotipo, molduras, filetes, etiquetas
LATAO_ESC = "#7E6428"   # dourado escuro, mesmo papel do Latao sobre Areia

RODAPE = "AKI Jardins | Rio do Sul e região"
HANDLE = "@akijardins"

# Icones de linha no estilo das capas dos destaques (traco dourado, sem preenchimento).
ICONES = {
    "folha": '<path d="M12 52C12 28 28 12 52 12c0 24-16 40-40 40z"/><path d="M12 52L38 26"/>',
    "grama": '<path d="M6 54h52"/><path d="M14 54c0-12 2-20 6-28"/><path d="M22 54c0-16-4-26-10-32"/><path d="M32 54c0-18 2-30 8-40"/><path d="M42 54c0-14-3-22-8-28"/><path d="M50 54c0-10 2-18 6-24"/>',
    "tesoura": '<circle cx="16" cy="46" r="8"/><circle cx="16" cy="18" r="8"/><path d="M22 41L56 14"/><path d="M22 23L56 50"/>',
    "regador": '<path d="M14 26h28v26H14z"/><path d="M42 32l14-12"/><path d="M53 17l6 6"/><path d="M14 32c-8 0-8 14 0 14"/><path d="M20 26c0-8 16-8 16 0"/>',
    "arvore": '<path d="M32 58V34"/><path d="M32 40l-8-6"/><path d="M32 36l9-7"/><circle cx="32" cy="22" r="16"/>',
    "casa": '<path d="M8 30L32 10l24 20"/><path d="M14 26v28h36V26"/><path d="M27 54V40h10v14"/>',
    "predio": '<path d="M14 56V10h24v46"/><path d="M38 24h14v32"/><path d="M8 56h50"/><path d="M21 18h4M29 18h2M21 28h4M29 28h2M21 38h4M29 38h2M44 32h2M44 42h2"/>',
    "calendario": '<rect x="8" y="14" width="48" height="42" rx="3"/><path d="M8 26h48"/><path d="M20 8v10M44 8v10"/><path d="M18 36h6M30 36h6M42 36h4M18 46h6M30 46h6"/>',
    "checklist": '<path d="M10 16l4 4 8-8"/><path d="M30 16h24"/><path d="M10 32l4 4 8-8"/><path d="M30 32h24"/><path d="M10 48l4 4 8-8"/><path d="M30 48h24"/>',
    "pergunta": '<circle cx="32" cy="32" r="24"/><path d="M25 25c0-10 14-10 14-1 0 6-7 6-7 13"/><path d="M32 45v1"/>',
    "familia": '<circle cx="20" cy="16" r="6"/><circle cx="44" cy="16" r="6"/><circle cx="32" cy="34" r="5"/><path d="M10 56V36c0-6 4-10 10-10s10 4 10 10"/><path d="M34 36c0-6 4-10 10-10s10 4 10 10v20"/><path d="M24 56V48c0-5 3-8 8-8s8 3 8 8v8"/>',
    "visita": '<path d="M32 58S12 38 12 24a20 20 0 0140 0c0 14-20 34-20 34z"/><circle cx="32" cy="24" r="7"/>',
    "mensagem": '<path d="M8 14h48v30H26l-12 10V44H8z"/><path d="M18 26h28M18 34h18"/>',
    "estrela": '<path d="M32 8l7 15 16 2-12 11 3 16-14-8-14 8 3-16L9 25l16-2z"/>',
}


def _fonte(nome):
    p = os.path.join(FONTES, nome)
    if not os.path.exists(p):
        sys.exit(f"Fonte {nome} nao encontrada em {FONTES}.")
    return "file://" + p


def _font_faces():
    faces = [
        ("Gelasio", 400, "normal", "Gelasio-400.ttf"),
        ("Gelasio", 700, "normal", "Gelasio-700.ttf"),
        ("Gelasio", 400, "italic", "Gelasio-400-italic.ttf"),
        ("Hanken", 400, "normal", "HankenGrotesk-400.ttf"),
        ("Hanken", 600, "normal", "HankenGrotesk-600.ttf"),
    ]
    return "".join(
        f"@font-face{{font-family:'{f}';font-weight:{w};font-style:{s};src:url('{_fonte(a)}')}}"
        for f, w, s, a in faces
    )


CSS = _font_faces() + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:'Hanken',Arial,sans-serif;-webkit-font-smoothing:antialiased}}
.s{{width:{W}px;height:{H}px;padding:96px 92px 140px;position:relative;display:flex;flex-direction:column;overflow:hidden}}
.capim{{background:{CAPIM};color:{AREIA}}}
.capim2{{background:{CAPIM2};color:{AREIA}}}
.areia{{background:{AREIA};color:{OLEO}}}
.frame{{position:absolute;inset:34px;border:2px solid {LATAO};opacity:.55;pointer-events:none;z-index:3}}
.areia .frame{{border-color:{LATAO_ESC};opacity:.4}}
.top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:56px;min-height:52px;position:relative;z-index:2}}
.brand{{font-family:'Gelasio',Georgia,serif;font-size:34px;letter-spacing:3px;color:{LATAO}}}
.areia .brand{{color:{LATAO_ESC}}}
.brand img{{height:64px;display:block}}
.kick{{font-family:'Gelasio',Georgia,serif;font-size:30px;letter-spacing:4px;color:{LATAO};border:2px solid {LATAO};padding:6px 18px;background:rgba(36,51,28,.35)}}
.areia .kick{{color:{LATAO_ESC};border-color:{LATAO_ESC};background:none}}
h1,h2{{font-family:'Gelasio',Georgia,serif;font-weight:700}}
.capa h1{{font-size:84px;line-height:1.14;color:{AREIA};margin:auto 0 0}}
.capa .rule{{margin-bottom:auto}}
.rule{{width:140px;height:5px;background:{LATAO};margin:36px 0}}
.areia .rule{{background:{LATAO_ESC}}}
h2{{font-size:68px;line-height:1.15;color:{LATAO}}}
.areia h2{{color:{CAPIM}}}
.corpo{{font-size:43px;line-height:1.42}}
.corpo p{{margin-bottom:26px}}
.corpo p:last-child{{margin-bottom:0}}
.lista p{{padding-left:44px;position:relative}}
.lista p:before{{content:'';position:absolute;left:0;top:.62em;width:22px;height:4px;background:{LATAO}}}
.areia .lista p:before{{background:{LATAO_ESC}}}
.content{{margin:auto 0;position:relative;z-index:2}}
.pedido h2{{font-size:72px;color:{AREIA}}}
.icone{{width:120px;height:120px;margin-bottom:40px;fill:none;stroke:{LATAO};stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}}
.areia .icone{{stroke:{LATAO_ESC}}}
.foot{{position:absolute;left:92px;right:92px;bottom:62px;display:flex;justify-content:space-between;font-size:26px;letter-spacing:1px;opacity:.85;z-index:2}}
.arrow{{color:{LATAO}}}
.areia .arrow{{color:{LATAO_ESC}}}
.ph{{background:{LATAO};color:{CAPIM};padding:0 8px;font-style:italic;border-radius:4px}}
.areia .ph{{background:#E9D9A8}}
.slot{{border:4px dashed {LATAO};background:rgba(208,184,128,.12);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-size:34px;color:{LATAO};padding:30px}}
.photo{{background-size:cover;background-repeat:no-repeat;position:relative;overflow:hidden}}
.photo.inteira{{background-size:contain;background-color:{OLEO}}}
.label{{font-family:'Gelasio',Georgia,serif;font-size:56px;letter-spacing:8px;color:{LATAO};margin:24px 0 8px}}
/* capa com foto de fundo */
.bg{{position:absolute;inset:0;background-size:cover;z-index:0}}
.veu{{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(36,51,28,.55) 0%,rgba(36,51,28,.15) 30%,rgba(36,51,28,.55) 55%,rgba(36,51,28,.96) 82%,{CAPIM} 100%)}}
.capafoto .gancho{{margin-top:auto;position:relative;z-index:2}}
.capafoto h1{{font-size:80px;line-height:1.14;color:{AREIA};text-shadow:0 2px 18px rgba(0,0,0,.35)}}
.capafoto .rule{{position:relative;z-index:2;margin-bottom:0}}
.capafoto .sobre{{font-family:'Gelasio',Georgia,serif;font-size:30px;letter-spacing:6px;color:{LATAO};position:relative;z-index:2;margin-bottom:22px}}
/* antes e depois lado a lado */
.ad h2{{font-size:60px;margin-bottom:28px}}
.par{{display:flex;gap:20px;height:720px}}
.par .lado{{flex:1;position:relative;border:2px solid {LATAO};overflow:hidden}}
.par .lado .photo,.par .lado .slot{{position:absolute;inset:0;height:auto}}
.par .tag{{position:absolute;left:0;bottom:22px;z-index:2;font-family:'Hanken',sans-serif;font-weight:600;font-size:28px;letter-spacing:3px;padding:10px 22px}}
.tag.antes{{background:{OLEO};color:{AREIA}}}
.tag.depois{{background:{LATAO};color:{CAPIM}}}
.ad .corpo{{font-size:36px;line-height:1.4;margin-top:34px;text-align:center}}
"""


# ---------------------------------------------------------------- utilidades
def esc(t):
    """Escapa HTML e destaca [A PREENCHER: ...] como etiqueta dourada."""
    t = html.escape(t or "")
    return re.sub(r"\[([^\]]+)\]", r'<span class="ph">[\1]</span>', t)


def paras(corpo):
    return "".join(f"<p>{esc(p)}</p>" for p in (corpo or "").split("\n") if p.strip())


def foto_url(caminho, base):
    """Le a foto, gira pelo EXIF (foto de celular), reduz e embute no HTML."""
    if not caminho:
        return None
    p = caminho if os.path.isabs(caminho) else os.path.join(base, caminho)
    if not os.path.exists(p):
        print(f"Aviso: foto nao encontrada ({p}). Vai sair o espaco tracejado.")
        return None
    try:
        from PIL import Image, ImageOps
        try:
            import pillow_heif  # fotos .HEIC do iPhone
            pillow_heif.register_heif_opener()
        except ImportError:
            pass
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        im.thumbnail((2000, 2000))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=90)
        dados = buf.getvalue()
    except Exception as e:
        if p.lower().endswith((".heic", ".heif")):
            sys.exit(f"Nao consegui abrir {p} (HEIC). Rode: pip install pillow-heif, ou mande a foto em JPG.")
        print(f"Aviso: nao consegui tratar {p} ({e}). Usando o arquivo como veio.")
        with open(p, "rb") as f:
            dados = f.read()
    return "data:image/jpeg;base64," + base64.b64encode(dados).decode()


def foco(sl):
    """Ponto da foto que nunca pode sair do quadro: center, top, bottom, left, right ou '50% 30%'."""
    f = sl.get("foco", "center")
    return {"topo": "top", "baixo": "bottom", "centro": "center", "esquerda": "left", "direita": "right"}.get(f, f)


def marca():
    if os.path.exists(LOGO):
        with open(LOGO, "rb") as f:
            src = "data:image/png;base64," + base64.b64encode(f.read()).decode()
        return f'<div class="brand"><img src="{src}" alt="AKI Jardins"></div>'
    return '<div class="brand">AKiJardinS</div>'


def icone(nome):
    if not nome:
        return ""
    if nome not in ICONES:
        print(f"Aviso: icone '{nome}' nao existe. Opcoes: {', '.join(ICONES)}")
        return ""
    return f'<svg class="icone" viewBox="0 0 64 64">{ICONES[nome]}</svg>'


def caixa_foto(url, rotulo, sl, altura=None, extra_estilo=""):
    h = f"height:{altura}px;" if altura else ""
    if url:
        cls = "photo inteira" if sl.get("enquadrar") == "inteira" else "photo"
        return (f'<div class="{cls}" style="{h}{extra_estilo}background-image:url({url});'
                f'background-position:{foco(sl)}"></div>')
    return (f'<div class="slot" style="{h}{extra_estilo}">FOTO DO {html.escape(rotulo)}<br>'
            f'<span style="font-size:26px">[a preencher: foto sem pessoas ou autorizada]</span></div>')


# ---------------------------------------------------------------- slides
def slide_html(sl, i, n, base):
    k = sl.get("k", "texto")
    seta = '<span class="arrow">arraste &rarr;</span>' if i < n else f'<span class="arrow">{HANDLE}</span>'
    foot = f'<div class="foot"><span>{RODAPE}</span>{seta}<span>{i}/{n}</span></div>'
    brand = marca()

    if k == "capa" and sl.get("fundo_foto"):
        # Capa com a foto ocupando o slide inteiro e o gancho sobre um veu verde.
        url = foto_url(sl["fundo_foto"], base)
        bg = (f'<div class="bg" style="background-image:url({url});background-position:{foco(sl)}"></div>'
              if url else f'<div class="bg" style="background:{CAPIM2}"></div>')
        sobre = f'<div class="sobre">{html.escape(sl["sobre"])}</div>' if sl.get("sobre") else ""
        inner = (f'{bg}<div class="veu"></div><div class="top">{brand}<span class="kick">CAPA</span></div>'
                 f'<div class="gancho">{sobre}<h1>{esc(sl["titulo"])}</h1><div class="rule"></div></div>')
        cls = "capim capafoto"
    elif k == "capa":
        extra = ""
        if "foto" in sl:
            extra = caixa_foto(foto_url(sl.get("foto"), base), sl.get("rotulo", "DEPOIS"), sl, 560,
                               "margin-bottom:30px;")
        estilo = ' style="font-size:64px;margin:0"' if extra else ""
        inner = (f'<div class="top">{brand}<span class="kick">CAPA</span></div>{extra}'
                 f'<h1{estilo}>{esc(sl["titulo"])}</h1><div class="rule"></div>')
        cls = "capim capa"
    elif k == "antes_depois":
        lados = ""
        for lado, rot in (("antes", "ANTES"), ("depois", "DEPOIS")):
            sub = dict(sl, foco=sl.get(f"foco_{lado}", sl.get("foco", "center")))
            lados += (f'<div class="lado">{caixa_foto(foto_url(sl.get(lado), base), rot, sub)}'
                      f'<span class="tag {lado}">{rot}</span></div>')
        titulo = f'<h2>{esc(sl["titulo"])}</h2>' if sl.get("titulo") else ""
        kick = f'<span class="kick">{html.escape(str(sl["etiqueta"]))}</span>' if sl.get("etiqueta") else ""
        inner = (f'<div class="top" style="margin-bottom:40px">{brand}{kick}</div>{titulo}'
                 f'<div class="par">{lados}</div><div class="corpo">{paras(sl.get("corpo"))}</div>')
        cls = "capim ad"
    elif k == "foto":
        rot = sl.get("rotulo", "")
        inner = (f'<div class="top">{brand}</div>{caixa_foto(foto_url(sl.get("foto"), base), rot, sl, 760)}'
                 f'<div class="label">{html.escape(rot)}</div>'
                 f'<div class="corpo" style="font-size:38px">{paras(sl.get("corpo"))}</div>')
        cls = "capim"
    elif k == "pedido":
        inner = (f'<div class="top">{brand}</div><div class="content">{icone(sl.get("icone"))}'
                 f'<h2>{esc(sl["titulo"])}</h2><div class="rule"></div><div class="corpo">{paras(sl.get("corpo"))}</div></div>')
        cls = "capim pedido"
    else:  # texto ou lista
        kick = f'<span class="kick">{html.escape(str(sl["etiqueta"]))}</span>' if sl.get("etiqueta") else ""
        lista = " lista" if k == "lista" else ""
        fotinho = ""
        if sl.get("foto"):
            fotinho = caixa_foto(foto_url(sl["foto"], base), "SERVICO", sl, 470, "margin-bottom:44px;")
        inner = (f'<div class="top">{brand}{kick}</div>{fotinho}<div class="content"{" style=margin-top:0" if fotinho else ""}>'
                 f'{"" if fotinho else icone(sl.get("icone"))}<h2>{esc(sl["titulo"])}</h2>'
                 f'<div class="rule"></div><div class="corpo{lista}">{paras(sl.get("corpo"))}</div></div>')
        cls = sl.get("fundo") or ("areia" if i % 2 == 0 else "capim2")

    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div class="s {cls}"><div class="frame"></div>{inner}{foot}</div></body></html>')


# ---------------------------------------------------------------- conferencia
PROIBIDO = [
    (r"[\u2014\u2013]", "travessao"),
    (r"R\$\s?\d", "preco (o pedido e sempre sem preco)"),
    (r"\b(selva|mentoria|imers[aã]o|comunidade)\b", "assunto fora do publico (Selva, mentoria, etc.)"),
]


def conferir(spec):
    problemas = []
    textos = [("legenda", spec.get("legenda", ""))]
    for i, sl in enumerate(spec["slides"], 1):
        textos += [(f"slide {i}", sl.get("titulo", "")), (f"slide {i}", sl.get("corpo", "")),
                   (f"slide {i}", sl.get("sobre", ""))]
    for onde, t in textos:
        for padrao, nome in PROIBIDO:
            if re.search(padrao, t or "", re.I):
                problemas.append(f"{onde}: {nome}")
    capa = spec["slides"][0]
    if capa.get("k") != "capa":
        problemas.append("slide 1 precisa ser k=capa")
    else:
        nw = len(capa["titulo"].split())
        if not 10 <= nw <= 20:
            problemas.append(f"capa com {nw} palavras (o molde pede 14 a 18)")
    if spec["slides"][-1].get("k") != "pedido":
        problemas.append("ultimo slide precisa ser k=pedido")
    if len(spec["slides"]) > 10:
        problemas.append(f"{len(spec['slides'])} slides: o Instagram aceita no maximo 20, o molde da AKI pede ate 10")
    return problemas


# ---------------------------------------------------------------- render
CHROMES = [
    os.environ.get("CHROME", ""),
    *sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-*/chrome-headless-shell")),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell"))),
    "/opt/pw-browsers/chromium",
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome")),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"))),
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def achar_chrome():
    for exe in CHROMES:
        if exe and os.path.isfile(exe):
            return exe
    sys.exit("Nao achei Chromium/Chrome. Instale (pip install playwright && playwright install chromium) "
             "ou aponte a variavel CHROME para o executavel.")


def abrir_navegador(p):
    try:
        return p.chromium.launch()
    except Exception:
        return p.chromium.launch(executable_path=achar_chrome(), args=["--no-sandbox"])


def render_playwright(paginas, saidas):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = abrir_navegador(p)
        pg = nav.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        tmp = tempfile.mkdtemp(prefix="aki-")
        for i, (doc, png) in enumerate(zip(paginas, saidas), 1):
            # Abre como arquivo (e nao set_content) para o navegador poder ler as fontes locais.
            hp = os.path.join(tmp, f"s{i:02d}.html")
            with open(hp, "w", encoding="utf-8") as f:
                f.write(doc)
            pg.goto("file://" + hp, wait_until="load")
            pg.evaluate("document.fonts.ready")
            # Texto que passou do limite encosta no rodape: avisa em vez de cortar calado.
            estouro = pg.evaluate(
                "(() => { const s=document.querySelector('.s'); const f=document.querySelector('.foot');"
                " let max=0; s.querySelectorAll('h1,h2,.corpo,.label,.par').forEach(e=>{max=Math.max(max,e.getBoundingClientRect().bottom)});"
                " return max > f.getBoundingClientRect().top - 24; })()"
            )
            if estouro:
                print(f"ESTOUROU: slide {i} tem texto demais. Encurte ou divida em dois.")
            pg.screenshot(path=png)
        nav.close()
    shutil.rmtree(tmp, ignore_errors=True)


def render_chrome(paginas, saidas):
    """Sem Playwright no Python: chama o Chrome headless direto, um slide por vez."""
    chrome = achar_chrome()
    tmp = tempfile.mkdtemp(prefix="aki-")
    for i, (doc, png) in enumerate(zip(paginas, saidas), 1):
        hp = os.path.join(tmp, f"s{i:02d}.html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(doc)
        if os.path.exists(png):
            os.remove(png)
        # O Chrome headless as vezes nao fecha depois do print: espera o arquivo e encerra.
        cmd = [chrome] + ([] if chrome.endswith("headless-shell") else ["--headless=new"]) + [
            "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            f"--user-data-dir={os.path.join(tmp, 'perfil')}", f"--window-size={W},{H}", "--no-first-run",
            "--disable-background-networking", f"--screenshot={os.path.abspath(png)}", "file://" + hp]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < 60 and proc.poll() is None:
            if os.path.exists(png) and os.path.getsize(png) > 1000:
                time.sleep(0.8)
                break
            time.sleep(0.3)
        proc.kill()
        proc.wait()
        if not os.path.exists(png):
            sys.exit(f"Chrome nao gerou {png}.")
    shutil.rmtree(tmp, ignore_errors=True)
    print("Aviso: rodou sem Playwright, entao nao deu para medir estouro de texto. Confira os slides a olho.")


def garantir_tamanho(pngs):
    """Todos os slides precisam ter o mesmo tamanho, senao o Instagram corta."""
    for png in pngs:
        with open(png, "rb") as f:
            cab = f.read(24)  # largura e altura ficam no cabecalho IHDR do PNG
        w, h = struct.unpack(">II", cab[16:24])
        if (w, h) != (W, H):
            sys.exit(f"{os.path.basename(png)} saiu {w}x{h} e nao {W}x{H}. Nao poste.")
    print(f"Tamanho conferido: todos os {len(pngs)} slides em {W}x{H} (4:5).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    base = os.path.dirname(os.path.abspath(a.spec))
    os.makedirs(a.out, exist_ok=True)

    problemas = conferir(spec)
    for pr in problemas:
        print("CONFERIR:", pr)
    if any("travessao" in pr for pr in problemas):
        sys.exit("Tire os travessoes e rode de novo.")

    slides = spec["slides"]
    n = len(slides)
    paginas = [slide_html(sl, i, n, base) for i, sl in enumerate(slides, 1)]
    gerados = [os.path.join(a.out, f"slide-{i:02d}.png") for i in range(1, n + 1)]
    try:
        import playwright  # noqa: F401
        render_playwright(paginas, gerados)
    except ImportError:
        render_chrome(paginas, gerados)
    garantir_tamanho(gerados)

    leg = os.path.join(a.out, "legenda.md")
    with open(leg, "w", encoding="utf-8") as f:
        f.write(f"# Legenda: {spec.get('titulo', '')}\n\nPedido: {spec.get('pedido', '')}\n\n---\n\n"
                f"{spec.get('legenda', '').strip()}\n")

    nome = unicodedata.normalize("NFKD", spec.get("titulo", "carrossel")).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^a-z0-9]+", "-", nome.lower()).strip("-")[:50] or "carrossel"
    zp = os.path.join(a.out, f"carrossel-{nome}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for g in gerados + [leg]:
            z.write(g, os.path.basename(g))
    print(f"ok: {n} slides em {a.out}")
    print(f"zip: {zp}")


if __name__ == "__main__":
    main()
