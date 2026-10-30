#!/usr/bin/env python3
"""
Renderizador do carrossel AKI Jardins (@akijardins).

Uso:
    python render.py spec.json --out pasta-de-saida

Le um spec JSON (formato em references/spec.md) e gera:
  slide-01.png ... slide-NN.png  (1080x1350, prontos para o feed)
  legenda.md                      (texto para colar no Instagram)
  carrossel-<nome>.zip            (tudo junto, para baixar no celular)

Monta cada slide em HTML e fotografa com Chromium headless (Playwright).
A identidade visual mora aqui: nao reescreva cores e fontes no spec.
"""
import argparse
import base64
import glob
import html
import json
import os
import re
import shutil
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
.s{{width:{W}px;height:{H}px;padding:96px 92px 140px;position:relative;display:flex;flex-direction:column}}
.capim{{background:{CAPIM};color:{AREIA}}}
.capim2{{background:{CAPIM2};color:{AREIA}}}
.areia{{background:{AREIA};color:{OLEO}}}
.frame{{position:absolute;inset:34px;border:2px solid {LATAO};opacity:.55;pointer-events:none}}
.areia .frame{{border-color:{LATAO_ESC};opacity:.4}}
.top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:56px;min-height:52px}}
.brand{{font-family:'Gelasio',Georgia,serif;font-size:34px;letter-spacing:3px;color:{LATAO}}}
.areia .brand{{color:{LATAO_ESC}}}
.brand img{{height:64px;display:block}}
.kick{{font-family:'Gelasio',Georgia,serif;font-size:30px;letter-spacing:4px;color:{LATAO};border:2px solid {LATAO};padding:6px 18px}}
.areia .kick{{color:{LATAO_ESC};border-color:{LATAO_ESC}}}
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
.content{{margin:auto 0}}
.pedido h2{{font-size:72px;color:{AREIA}}}
.foot{{position:absolute;left:92px;right:92px;bottom:62px;display:flex;justify-content:space-between;font-size:26px;letter-spacing:1px;opacity:.85}}
.arrow{{color:{LATAO}}}
.areia .arrow{{color:{LATAO_ESC}}}
.ph{{background:{LATAO};color:{CAPIM};padding:0 8px;font-style:italic;border-radius:4px}}
.areia .ph{{background:#E9D9A8}}
.slot{{border:4px dashed {LATAO};background:rgba(208,184,128,.12);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-size:36px;color:{LATAO};padding:30px}}
.photo{{background-size:cover;background-position:center}}
.label{{font-family:'Gelasio',Georgia,serif;font-size:56px;letter-spacing:8px;color:{LATAO};margin:24px 0 8px}}
"""


# ---------------------------------------------------------------- utilidades
def esc(t):
    """Escapa HTML e destaca [A PREENCHER: ...] como etiqueta dourada."""
    t = html.escape(t or "")
    return re.sub(r"\[([^\]]+)\]", r'<span class="ph">[\1]</span>', t)


def paras(corpo):
    return "".join(f"<p>{esc(p)}</p>" for p in (corpo or "").split("\n") if p.strip())


def foto_url(caminho, base):
    if not caminho:
        return None
    p = caminho if os.path.isabs(caminho) else os.path.join(base, caminho)
    if not os.path.exists(p):
        print(f"Aviso: foto nao encontrada ({p}). Vai sair o espaco tracejado.")
        return None
    ext = os.path.splitext(p)[1].lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(p, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def marca():
    if os.path.exists(LOGO):
        with open(LOGO, "rb") as f:
            src = "data:image/png;base64," + base64.b64encode(f.read()).decode()
        return f'<div class="brand"><img src="{src}" alt="AKI Jardins"></div>'
    return '<div class="brand">AKiJardinS</div>'


def caixa_foto(url, altura, rotulo):
    if url:
        return f'<div class="photo" style="height:{altura}px;background-image:url({url})"></div>'
    return (f'<div class="slot" style="height:{altura}px">FOTO DO {html.escape(rotulo)}<br>'
            f'<span style="font-size:28px">[a preencher: foto sem pessoas ou autorizada]</span></div>')


# ---------------------------------------------------------------- slides
def slide_html(sl, i, n, base):
    k = sl.get("k", "texto")
    seta = '<span class="arrow">arraste &rarr;</span>' if i < n else f'<span class="arrow">{HANDLE}</span>'
    foot = f'<div class="foot"><span>{RODAPE}</span>{seta}<span>{i}/{n}</span></div>'
    brand = marca()

    if k == "capa":
        extra = ""
        if "foto" in sl:
            extra = caixa_foto(foto_url(sl.get("foto"), base), 560, sl.get("rotulo", "DEPOIS"))
            extra = extra.replace('style="', 'style="margin-bottom:30px;', 1)
        estilo = ' style="font-size:64px;margin:0"' if extra else ""
        inner = (f'<div class="top">{brand}<span class="kick">CAPA</span></div>{extra}'
                 f'<h1{estilo}>{esc(sl["titulo"])}</h1><div class="rule"></div>')
        cls = "capim capa"
    elif k == "foto":
        rot = sl.get("rotulo", "")
        inner = (f'<div class="top">{brand}</div>{caixa_foto(foto_url(sl.get("foto"), base), 760, rot)}'
                 f'<div class="label">{html.escape(rot)}</div>'
                 f'<div class="corpo" style="font-size:38px">{paras(sl.get("corpo"))}</div>')
        cls = "capim"
    elif k == "pedido":
        inner = (f'<div class="top">{brand}</div><div class="content"><h2>{esc(sl["titulo"])}</h2>'
                 f'<div class="rule"></div><div class="corpo">{paras(sl.get("corpo"))}</div></div>')
        cls = "capim pedido"
    else:  # texto ou lista
        kick = f'<span class="kick">{html.escape(str(sl["etiqueta"]))}</span>' if sl.get("etiqueta") else ""
        lista = " lista" if k == "lista" else ""
        inner = (f'<div class="top">{brand}{kick}</div><div class="content"><h2>{esc(sl["titulo"])}</h2>'
                 f'<div class="rule"></div><div class="corpo{lista}">{paras(sl.get("corpo"))}</div></div>')
        cls = sl.get("fundo") or ("areia" if i % 2 == 0 else "capim2")

    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div class="s {cls}"><div class="frame"></div>{inner}{foot}</div></body></html>')


# ---------------------------------------------------------------- conferencia
PROIBIDO = [
    (r"[—–]", "travessao"),
    (r"R\$\s?\d", "preco (o pedido e sempre sem preco)"),
    (r"\b(selva|mentoria|imers[aã]o|comunidade)\b", "assunto fora do publico (Selva, mentoria, etc.)"),
]


def conferir(spec):
    problemas = []
    textos = [("legenda", spec.get("legenda", ""))]
    for i, sl in enumerate(spec["slides"], 1):
        textos += [(f"slide {i}", sl.get("titulo", "")), (f"slide {i}", sl.get("corpo", ""))]
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
                " let max=0; s.querySelectorAll('h1,h2,.corpo,.label').forEach(e=>{max=Math.max(max,e.getBoundingClientRect().bottom)});"
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
        proc = subprocess.Popen([chrome] + ([] if chrome.endswith("headless-shell") else ["--headless=new"]) + ["--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                                 "--force-device-scale-factor=1", f"--user-data-dir={os.path.join(tmp, 'perfil')}",
                                 f"--window-size={W},{H}", "--no-first-run", "--disable-background-networking",
                                 f"--screenshot={os.path.abspath(png)}", "file://" + hp],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
