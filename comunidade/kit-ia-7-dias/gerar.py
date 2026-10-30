"""Gera kit.html e MENSAGENS-WHATSAPP.md a partir de conteudo.py.

Uso:
    python3 gerar.py
    node pdf.js        # converte kit.html em Kit-IA-no-Negocio.pdf
"""
import html
import re
from pathlib import Path

import conteudo as c

AQUI = Path(__file__).parent
FONTES = {
    200: "../../assets/5018da12-84ed-4aa5-8a4d-fa39c1026628.woff2",
    300: "../../assets/36cda6f1-8369-4cad-9a72-c7608396a3d8.woff2",
    400: "../../assets/fddb5b02-0303-47f7-9c79-9bfbb5ac4be4.woff2",
    500: "../../assets/1f7e1e0a-dce3-4bac-beda-2017e0ce499c.woff2",
}


def esc(t):
    return html.escape(t, quote=False)


def prompt_html(t):
    """Escapa, destaca [campos] e mantém quebras de linha."""
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]", r'<span class="campo">[\1]</span>', t)
    return t.replace("\n", "<br>")


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --navy: #14162B; --navy2: #1E2140; --champ: #BAB196; --champ-esc: #8C7A4E;
  --creme: #F5F1E8; --cinza: #4B5266; --cinza-cl: #98A0AE; --linha: #E2DccC;
}
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Poppins', sans-serif; font-weight: 300; color: var(--navy); background: #fff; }
.pagina { width: 210mm; height: 297mm; padding: 18mm 18mm 16mm; position: relative; overflow: hidden; page-break-after: always; }
.pagina:last-child { page-break-after: auto; }
.rodape { position: absolute; left: 18mm; right: 18mm; bottom: 9mm; display: flex; justify-content: space-between;
  font-size: 7.5pt; letter-spacing: .12em; text-transform: uppercase; color: var(--cinza-cl); }
.escura { background: var(--navy); color: #fff; }
.escura .rodape { color: #6E7489; }
.selo { font-size: 8pt; letter-spacing: .28em; text-transform: uppercase; color: var(--champ); font-weight: 400; }
.filete { width: 34mm; height: 1.2px; background: var(--champ); margin: 7mm 0; }

/* capa */
.capa { display: flex; flex-direction: column; justify-content: space-between; padding: 24mm 20mm 20mm; }
.capa h1 { font-weight: 200; font-size: 50pt; line-height: 1.02; letter-spacing: -.01em; margin-top: 4mm; }
.capa h1 b { font-weight: 500; color: var(--champ); display: block; }
.capa .sub { font-size: 13pt; line-height: 1.5; color: #D5D8E2; max-width: 135mm; }
.capa .dias { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2.5mm; margin-top: 12mm; }
.capa .dia { border: 1px solid #3A3F5E; border-radius: 2mm; padding: 4mm 2mm 3.5mm; text-align: center; }
.capa .dia .num { font-size: 18pt; font-weight: 200; color: var(--champ); line-height: 1; }
.capa .dia .nome { font-size: 6.6pt; letter-spacing: .08em; text-transform: uppercase; margin-top: 2mm; color: #C9CCD8; }
.capa .marca { display: flex; justify-content: space-between; align-items: flex-end; }
.capa .marca .logo { font-size: 20pt; font-weight: 500; letter-spacing: .32em; }
.capa .marca .com { font-size: 8.5pt; color: #A3A8BA; text-align: right; line-height: 1.6; }

/* textos gerais */
h2 { font-weight: 300; font-size: 25pt; line-height: 1.12; margin-top: 3mm; }
h2 b { font-weight: 500; }
.lead { font-size: 10.5pt; line-height: 1.6; color: var(--cinza); margin-top: 4mm; max-width: 150mm; }
h3 { font-size: 8.5pt; letter-spacing: .2em; text-transform: uppercase; font-weight: 500; color: var(--champ-esc); margin: 9mm 0 4mm; }

.regras { list-style: none; counter-reset: r; }
.regras li { counter-increment: r; display: flex; gap: 5mm; padding: 3.6mm 0; border-bottom: 1px solid var(--linha); font-size: 10pt; line-height: 1.55; }
.regras li::before { content: counter(r, decimal-leading-zero); font-weight: 200; font-size: 15pt; color: var(--champ); line-height: 1.1; min-width: 9mm; }

.formula { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; }
.formula .bloco { background: var(--creme); border-radius: 2mm; padding: 5mm 4mm; }
.formula .bloco .k { font-weight: 500; font-size: 11pt; }
.formula .bloco .d { font-size: 8.2pt; color: var(--cinza); margin: 1.5mm 0 3mm; line-height: 1.45; }
.formula .bloco .e { font-size: 8.4pt; font-style: italic; line-height: 1.45; border-top: 1px solid var(--linha); padding-top: 2.5mm; }
.exemplo { margin-top: 5mm; background: var(--navy); color: #fff; border-radius: 2mm; padding: 5mm 6mm; font-size: 9.6pt; line-height: 1.6; }
.exemplo .selo { display: block; margin-bottom: 2mm; }

/* páginas de dia */
.topo-dia { display: flex; align-items: flex-end; justify-content: space-between; border-bottom: 1px solid var(--linha); padding-bottom: 5mm; }
.topo-dia .grande { font-size: 54pt; font-weight: 200; line-height: .85; color: var(--champ); }
.topo-dia .info { flex: 1; margin-left: 6mm; }
.topo-dia h2 { font-size: 19pt; margin-top: 1.5mm; }
.gancho { font-size: 12pt; font-style: italic; font-weight: 300; margin-top: 5mm; line-height: 1.5; }
.meta { display: flex; gap: 6mm; margin-top: 3mm; font-size: 9.4pt; color: var(--cinza); line-height: 1.5; }
.meta .intro { flex: 1; }
.meta .ferr { min-width: 48mm; max-width: 52mm; border-left: 2px solid var(--champ); padding-left: 3.5mm; }
.meta .ferr b { display: block; font-size: 7pt; letter-spacing: .18em; text-transform: uppercase; color: var(--champ-esc); font-weight: 500; }
.prompts { margin-top: 5mm; display: flex; flex-direction: column; gap: 2.6mm; }
.prompt { background: var(--creme); border-radius: 2mm; padding: 3.5mm 5mm 3.7mm; break-inside: avoid; }
.prompt .cab { display: flex; gap: 3mm; align-items: baseline; margin-bottom: 1.4mm; }
.prompt .id { font-size: 7.5pt; font-weight: 500; color: var(--champ-esc); letter-spacing: .06em; }
.prompt .nome { font-size: 10.5pt; font-weight: 500; }
.prompt .txt { font-size: 9.1pt; line-height: 1.5; color: #2A2E45; }
.campo { color: var(--champ-esc); font-weight: 500; }
.dica { margin-top: 3.2mm; display: flex; gap: 3mm; font-size: 8.6pt; line-height: 1.5; background: var(--navy); color: #fff; border-radius: 2mm; padding: 3.4mm 4.5mm; }
.dica b { color: var(--champ); font-weight: 500; letter-spacing: .14em; font-size: 7pt; text-transform: uppercase; white-space: nowrap; padding-top: .6mm; }

/* ferramentas e fim */
.tabela { width: 100%; border-collapse: collapse; margin-top: 2mm; }
.tabela td { padding: 3.6mm 0; border-bottom: 1px solid var(--linha); font-size: 9.6pt; vertical-align: top; }
.tabela td:first-child { font-weight: 500; width: 34mm; }
.tabela td:nth-child(2) { color: var(--champ-esc); width: 52mm; font-size: 9pt; }
.tabela td:last-child { color: var(--cinza); }
.fim { margin-top: 12mm; background: var(--navy); color: #fff; border-radius: 2mm; padding: 9mm 9mm; }
.fim .citacao { font-size: 15pt; font-weight: 200; line-height: 1.4; }
.fim .citacao b { color: var(--champ); font-weight: 400; }
.fim p { font-size: 9.5pt; color: #C9CCD8; line-height: 1.6; margin-top: 5mm; }
"""


def fontes_css():
    return "".join(
        f"@font-face{{font-family:'Poppins';font-weight:{p};src:url('{u}') format('woff2');}}"
        for p, u in FONTES.items()
    ) + "@font-face{font-family:'Poppins';font-style:italic;font-weight:300;" \
        "src:url('../../assets/59a3b0de-19ca-49f6-a5c7-adfe27bc0df3.woff2') format('woff2');}"


def rodape(pagina, escura=False):
    return f'<div class="rodape"><span>{c.TITULO} · {c.ASSINATURA}</span><span>{pagina:02d}</span></div>'


def capa():
    dias = "".join(
        f'<div class="dia"><div class="num">{d["n"]}</div><div class="nome">{d["area"]}</div></div>'
        for d in c.DIAS
    )
    return f"""
<section class="pagina escura capa">
  <div>
    <div class="selo">{c.COMUNIDADE}</div>
    <div class="filete"></div>
    <h1>Kit IA<b>no Negócio</b></h1>
    <p class="sub" style="margin-top:8mm">{esc(c.SUBTITULO)}</p>
    <div class="dias">{dias}</div>
  </div>
  <div class="marca">
    <div class="logo">{c.ASSINATURA}</div>
    <div class="com">Material exclusivo para membros<br>{c.HANDLE}</div>
  </div>
</section>"""


def como_usar():
    regras = "".join(f"<li><span>{esc(r)}</span></li>" for r in c.COMO_USAR)
    blocos = "".join(
        f'<div class="bloco"><div class="k">{k}</div><div class="d">{esc(d)}</div><div class="e">“{esc(e)}”</div></div>'
        for k, d, e in c.FORMULA
    )
    exemplo = " ".join(e for _, _, e in c.FORMULA)
    return f"""
<section class="pagina">
  <div class="selo" style="color:var(--champ-esc)">Antes de começar</div>
  <h2>Como usar <b>este kit</b></h2>
  <p class="lead">São 7 áreas da empresa, uma por dia, com 5 prompts cada. Escolha o que dói mais hoje e comece por ele. Não precisa seguir a ordem, mas precisa usar.</p>
  <h3>4 regras</h3>
  <ol class="regras">{regras}</ol>
  <h3>A fórmula de um bom prompt</h3>
  <div class="formula">{blocos}</div>
  <div class="exemplo"><span class="selo">Juntando tudo</span>“{esc(exemplo)}”</div>
  {rodape(2)}
</section>"""


def pagina_dia(d, num_pagina):
    prompts = "".join(
        f'<div class="prompt"><div class="cab"><span class="id">{d["n"]}.{i}</span>'
        f'<span class="nome">{esc(nome)}</span></div><div class="txt">{prompt_html(txt)}</div></div>'
        for i, (nome, txt) in enumerate(d["prompts"], 1)
    )
    return f"""
<section class="pagina">
  <div class="topo-dia">
    <div class="grande">{d["n"]:02d}</div>
    <div class="info">
      <div class="selo" style="color:var(--champ-esc)">Dia {d["n"]} · {d["area"]}</div>
      <h2>{esc(d["titulo"])}</h2>
    </div>
  </div>
  <p class="gancho">{esc(d["gancho"])}</p>
  <div class="meta">
    <div class="intro">{esc(d["intro"])}</div>
    <div class="ferr"><b>Use em</b>{esc(d["ferramenta"])}</div>
  </div>
  <div class="prompts">{prompts}</div>
  <div class="dica"><b>Dica</b><span>{esc(d["dica"])}</span></div>
  {rodape(num_pagina)}
</section>"""


def ferramentas(num_pagina):
    linhas = "".join(
        f"<tr><td>{n}</td><td>{u}</td><td>{esc(d)}</td></tr>" for n, u, d in c.FERRAMENTAS
    )
    return f"""
<section class="pagina">
  <div class="selo" style="color:var(--champ-esc)">Para salvar</div>
  <h2>As ferramentas <b>do kit</b></h2>
  <p class="lead">Todas têm versão gratuita para testar. Comece com uma só. Domine, depois avance.</p>
  <table class="tabela">{linhas}</table>
  <div class="fim">
    <div class="citacao">Ferramenta sem processo vira <b>brinquedo caro</b>. A IA multiplica o que já existe na sua empresa: se for bagunça, multiplica a bagunça.</div>
    <p>Use um prompt por dia. Em uma semana, sua empresa já trabalha diferente. Conta na comunidade o que você colocou em prática: a troca entre a gente é o que faz isso valer.</p>
  </div>
  {rodape(num_pagina)}
</section>"""


def gerar_html():
    paginas = [capa(), como_usar()]
    for i, d in enumerate(c.DIAS):
        paginas.append(pagina_dia(d, 3 + i))
    paginas.append(ferramentas(3 + len(c.DIAS)))
    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>{c.TITULO}</title>
<style>{fontes_css()}{CSS}</style></head>
<body>{''.join(paginas)}</body></html>"""
    (AQUI / "kit.html").write_text(doc, encoding="utf-8")


PROXIMO = {d["n"]: d for d in c.DIAS}


def mensagem_dia(d):
    nome, prompt = d["prompts"][0]
    prox = PROXIMO.get(d["n"] + 1)
    teaser = (
        f"Amanhã, *Dia {prox['n']}: {prox['area']}*. {prox['titulo']}. 👀"
        if prox else c.ENCERRAMENTO_EXTRA
    )
    return f"""*🤖 DESAFIO 7 DIAS DE IA · DIA {d['n']}/7 · {d['area'].upper()}*

_{d['gancho']}_

{d['intro']}

*Prompt de hoje: {nome}*
Funciona no ChatGPT, Claude ou Gemini. Copia, troca o que está entre [colchetes] e cola 👇

{prompt}

💡 *Dica:* {d['dica']}

{teaser}"""


def gerar_mensagens():
    partes = [
        "# Mensagens de WhatsApp: Desafio 7 Dias de IA no Negócio",
        "",
        "Para a **Comunidade de Tecnologia e Negócios**. Copie o conteúdo de cada bloco e cole no grupo.",
        "A formatação já está no padrão do WhatsApp (`*negrito*`, `_itálico_`).",
        "",
        "**Cronograma sugerido:** véspera = abertura · Dias 1 a 7 = uma mensagem por dia, sempre no mesmo horário (ex.: 8h).",
        "No **Dia 7**, envie a mensagem e, logo depois, o arquivo `Kit-IA-no-Negocio.pdf`.",
        "",
        "---",
        "",
        "## Véspera: abertura do desafio",
        "",
        "```",
        c.ABERTURA,
        "```",
    ]
    for d in c.DIAS:
        partes += ["", "---", "", f"## Dia {d['n']}: {d['area']}", "", "```", mensagem_dia(d), "```"]
    partes.append("")
    (AQUI / "MENSAGENS-WHATSAPP.md").write_text("\n".join(partes), encoding="utf-8")


if __name__ == "__main__":
    gerar_html()
    gerar_mensagens()
    print("kit.html e MENSAGENS-WHATSAPP.md gerados.")
