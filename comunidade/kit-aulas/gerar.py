"""Gera kit.html e MENSAGENS-WHATSAPP.md a partir de conteudo.py.

Uso:
    python3 gerar.py
    node pdf.js        # converte kit.html em Kit-das-Aulas-AVIOR.pdf
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
ITALICO = "../../assets/59a3b0de-19ca-49f6-a5c7-adfe27bc0df3.woff2"


def esc(t):
    return html.escape(t, quote=False)


def prompt_html(t):
    """Escapa, destaca [campos] e mantém quebras de linha."""
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]", r'<span class="campo">[\1]</span>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --navy: #14162B; --champ: #BAB196; --champ-esc: #8C7A4E;
  --creme: #F5F1E8; --cinza: #4B5266; --cinza-cl: #98A0AE; --linha: #E2DCCC;
}
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Poppins', sans-serif; font-weight: 300; color: var(--navy); background: #fff; }
.pagina { width: 210mm; height: 297mm; padding: 18mm 18mm 16mm; position: relative; overflow: hidden; page-break-after: always; }
.pagina:last-child { page-break-after: auto; }
.rodape { position: absolute; left: 18mm; right: 18mm; bottom: 9mm; display: flex; justify-content: space-between;
  font-size: 7.5pt; letter-spacing: .12em; text-transform: uppercase; color: var(--cinza-cl); }
.escura { background: var(--navy); color: #fff; }
.selo { font-size: 8pt; letter-spacing: .28em; text-transform: uppercase; color: var(--champ-esc); font-weight: 400; }
.escura .selo { color: var(--champ); }
.filete { width: 34mm; height: 1.2px; background: var(--champ); margin: 7mm 0; }
h2 { font-weight: 300; font-size: 24pt; line-height: 1.15; margin-top: 3mm; }
h2 b { font-weight: 500; }
h3 { font-size: 8.5pt; letter-spacing: .2em; text-transform: uppercase; font-weight: 500; color: var(--champ-esc); margin: 7mm 0 3mm; }
.lead { font-size: 10.5pt; line-height: 1.6; color: var(--cinza); margin-top: 4mm; }
.campo { color: var(--champ-esc); font-weight: 500; }

/* capa */
.capa { display: flex; flex-direction: column; justify-content: space-between; padding: 24mm 20mm 20mm; }
.capa h1 { font-weight: 200; font-size: 46pt; line-height: 1.04; margin-top: 4mm; }
.capa h1 b { font-weight: 500; color: var(--champ); display: block; }
.capa .sub { font-size: 12.5pt; line-height: 1.55; color: #D5D8E2; max-width: 140mm; margin-top: 8mm; }
.capa .sumario { margin-top: 12mm; border-top: 1px solid #343957; }
.capa .item { display: flex; gap: 6mm; align-items: baseline; padding: 3.6mm 0; border-bottom: 1px solid #343957; }
.capa .item .n { font-size: 15pt; font-weight: 200; color: var(--champ); min-width: 10mm; }
.capa .item .t { font-size: 10.5pt; flex: 1; }
.capa .item .d { font-size: 7.5pt; letter-spacing: .14em; color: #8A90A8; text-transform: uppercase; }
.capa .marca { display: flex; justify-content: space-between; align-items: flex-end; }
.capa .marca .logo { font-size: 20pt; font-weight: 500; letter-spacing: .32em; }
.capa .marca .com { font-size: 8.5pt; color: #A3A8BA; text-align: right; line-height: 1.6; }

/* método */
.pilares { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm; margin-top: 2mm; }
.pilar { background: var(--creme); border-radius: 2mm; padding: 5mm 4.5mm; }
.pilar .k { font-size: 18pt; font-weight: 200; color: var(--champ-esc); line-height: 1; }
.pilar .t { font-weight: 500; font-size: 11pt; margin: 2.5mm 0 1.5mm; }
.pilar .d { font-size: 8.8pt; color: var(--cinza); line-height: 1.5; }
.regras { list-style: none; counter-reset: r; }
.regras li { counter-increment: r; display: flex; gap: 5mm; padding: 3.2mm 0; border-bottom: 1px solid var(--linha); font-size: 9.6pt; line-height: 1.55; }
.regras li::before { content: counter(r, decimal-leading-zero); font-weight: 200; font-size: 14pt; color: var(--champ); line-height: 1.1; min-width: 9mm; }
.regras b { font-weight: 500; }
.conferencia { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2.5mm; }
.conferencia div { border: 1px solid var(--linha); border-radius: 2mm; padding: 3.5mm; font-size: 8.4pt; line-height: 1.45; color: var(--cinza); }
.conferencia b { display: block; color: var(--navy); font-weight: 500; font-size: 9.4pt; margin-bottom: 1mm; }

/* aula: página de resumo */
.topo-aula { display: flex; align-items: flex-end; border-bottom: 1px solid var(--linha); padding-bottom: 5mm; }
.topo-aula .grande { font-size: 56pt; font-weight: 200; line-height: .85; color: var(--champ); }
.topo-aula .info { flex: 1; margin-left: 6mm; }
.topo-aula h2 { font-size: 19pt; margin-top: 1.5mm; }
.ideia { font-size: 12.5pt; font-style: italic; line-height: 1.5; margin-top: 6mm; }
.resumo { font-size: 9.8pt; line-height: 1.65; color: var(--cinza); margin-top: 3.5mm; }
.aprendizados { list-style: none; counter-reset: a; }
.aprendizados li { counter-increment: a; display: flex; gap: 4mm; padding: 2.8mm 0; border-bottom: 1px solid var(--linha); font-size: 9.5pt; line-height: 1.55; }
.aprendizados li::before { content: counter(a); font-weight: 500; font-size: 8.5pt; color: #fff; background: var(--champ-esc);
  border-radius: 50%; min-width: 5.4mm; height: 5.4mm; display: flex; align-items: center; justify-content: center; margin-top: .4mm; }
.frase { margin-top: 6mm; border-left: 2px solid var(--champ); padding: 1mm 0 1mm 5mm; font-size: 12pt; font-weight: 200; line-height: 1.5; }
.frase span { display: block; font-size: 7.5pt; letter-spacing: .18em; text-transform: uppercase; color: var(--champ-esc); font-weight: 400; margin-top: 2mm; }
.tarefa { margin-top: 6mm; background: var(--navy); color: #fff; border-radius: 2mm; padding: 5mm 6mm; font-size: 9.6pt; line-height: 1.6; }
.tarefa .selo { display: block; margin-bottom: 1.5mm; }

/* aula: página do prompt */
.passos { display: flex; gap: 2.5mm; margin-top: 4mm; }
.passos div { flex: 1; border: 1px solid var(--linha); border-radius: 2mm; padding: 3mm 3.5mm; font-size: 8.4pt; line-height: 1.45; color: var(--cinza); }
.passos b { display: block; color: var(--champ-esc); font-weight: 500; font-size: 7.5pt; letter-spacing: .14em; margin-bottom: .8mm; }
.prompt { margin-top: 5mm; background: var(--creme); border-radius: 2mm; padding: 5mm 6mm; }
.prompt .cab { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3mm; }
.prompt .nome { font-size: 11pt; font-weight: 500; }
.prompt .copie { font-size: 7pt; letter-spacing: .18em; text-transform: uppercase; color: var(--champ-esc); font-weight: 500; }
.prompt .txt { font-size: 8.9pt; line-height: 1.55; color: #2A2E45; }
.extra { margin-top: 4mm; border: 1px solid var(--linha); border-radius: 2mm; padding: 4mm 5mm; font-size: 8.9pt; line-height: 1.55; color: var(--cinza); }
.extra b { color: var(--navy); font-weight: 500; }
.extra .t { font-size: 7.5pt; letter-spacing: .18em; text-transform: uppercase; color: var(--champ-esc); font-weight: 500; margin-bottom: 1.5mm; }

/* fechamento */
.tabela { width: 100%; border-collapse: collapse; margin-top: 2mm; }
.tabela td { padding: 3mm 0; border-bottom: 1px solid var(--linha); font-size: 9.3pt; vertical-align: top; }
.tabela td:first-child { font-weight: 500; width: 32mm; }
.tabela td:nth-child(2) { color: var(--champ-esc); width: 50mm; font-size: 8.8pt; }
.tabela td:last-child { color: var(--cinza); }
.fim { margin-top: 8mm; background: var(--navy); color: #fff; border-radius: 2mm; padding: 8mm 9mm; }
.fim .citacao { font-size: 14pt; font-weight: 200; line-height: 1.45; }
.fim .citacao b { color: var(--champ); font-weight: 400; }
.fim p { font-size: 9.4pt; color: #C9CCD8; line-height: 1.6; margin-top: 4mm; }
.fim p b { color: #fff; font-weight: 500; }
"""


def fontes_css():
    css = "".join(
        f"@font-face{{font-family:'Poppins';font-weight:{p};src:url('{u}') format('woff2');}}"
        for p, u in FONTES.items()
    )
    return css + f"@font-face{{font-family:'Poppins';font-style:italic;font-weight:300;src:url('{ITALICO}') format('woff2');}}"


class Paginas:
    def __init__(self):
        self.lista = []

    def add(self, corpo, classe="", rodape=True):
        n = len(self.lista) + 1
        pe = f'<div class="rodape"><span>{c.TITULO} · {c.ASSINATURA}</span><span>{n:02d}</span></div>' if rodape else ""
        self.lista.append(f'<section class="pagina {classe}">{corpo}{pe}</section>')


def capa(p):
    itens = "".join(
        f'<div class="item"><span class="n">{a["n"]:02d}</span><span class="t">{esc(a["titulo"])}</span>'
        f'<span class="d">{a["data"]}</span></div>'
        for a in c.AULAS
    )
    p.add(f"""
  <div>
    <div class="selo">{c.COMUNIDADE}</div>
    <div class="filete"></div>
    <h1>Kit das Aulas<b>{c.TITULO_DESTAQUE}</b></h1>
    <p class="sub">{esc(c.SUBTITULO)}</p>
    <div class="sumario">{itens}</div>
  </div>
  <div class="marca">
    <div class="logo">{c.ASSINATURA}</div>
    <div class="com">Material exclusivo para membros<br>{c.HANDLE}</div>
  </div>""", "escura capa", rodape=False)


def metodo(p):
    pilares = "".join(
        f'<div class="pilar"><div class="k">{i:02d}</div><div class="t">{t}</div><div class="d">{esc(d)}</div></div>'
        for i, (t, d) in enumerate(c.PILARES, 1)
    )
    regras = "".join(f"<li><span>{r}</span></li>" for r in c.REGRAS)
    conf = "".join(f"<div><b>{k}</b>{esc(d)}</div>" for k, d in c.CONFERENCIA)
    p.add(f"""
  <div class="selo">Antes de começar</div>
  <h2>Como usar <b>este kit</b></h2>
  <p class="lead">{esc(c.INTRO)}</p>
  <h3>O método que atravessa todas as aulas</h3>
  <div class="pilares">{pilares}</div>
  <h3>5 regras para a IA trabalhar bem</h3>
  <ol class="regras">{regras}</ol>
  <h3>Antes de usar qualquer resposta, confira</h3>
  <div class="conferencia">{conf}</div>""")


def aula(p, a):
    aprend = "".join(f"<li><span>{esc(x)}</span></li>" for x in a["aprendizados"])
    p.add(f"""
  <div class="topo-aula">
    <div class="grande">{a["n"]:02d}</div>
    <div class="info">
      <div class="selo">Aula {a["n"]} · {a["modulo"]} · {a["data"]}</div>
      <h2>{esc(a["titulo"])}</h2>
    </div>
  </div>
  <p class="ideia">{esc(a["ideia"])}</p>
  <p class="resumo">{esc(a["resumo"])}</p>
  <h3>O que levar desta aula</h3>
  <ol class="aprendizados">{aprend}</ol>
  <div class="frase">“{esc(a["frase"][0])}”<span>{a["frase"][1]}</span></div>
  <div class="tarefa"><span class="selo">Tarefa da semana</span>{esc(a["tarefa"])}</div>""")

    passos = "".join(f"<div><b>{i:02d}</b>{esc(t)}</div>" for i, t in enumerate(a["como_usar"], 1))
    extras = "".join(
        f'<div class="extra"><div class="t">{esc(t)}</div>{prompt_html(x)}</div>' for t, x in a.get("extras", [])
    )
    p.add(f"""
  <div class="selo">Aula {a["n"]} · O prompt da aula</div>
  <h2>{esc(a["prompt_nome"])}</h2>
  <div class="passos">{passos}</div>
  <div class="prompt"><div class="cab"><span class="nome">Copie, preencha e cole</span><span class="copie">Use em {esc(a["ferramenta"])}</span></div>
  <div class="txt">{prompt_html(a["prompt"])}</div></div>
  {extras}""")


def fechamento(p):
    linhas = "".join(f"<tr><td>{n}</td><td>{u}</td><td>{esc(d)}</td></tr>" for n, u, d in c.FERRAMENTAS)
    p.add(f"""
  <div class="selo">Para salvar</div>
  <h2>As ferramentas <b>das aulas</b></h2>
  <p class="lead">Comece pela tarefa, não pela marca. Faça a mesma tarefa em duas ou três e fique com a que chega mais perto do resultado certo.</p>
  <table class="tabela">{linhas}</table>
  <div class="fim">
    <div class="citacao">{c.FRASE_FINAL}</div>
    <p>{c.CONVITE}</p>
  </div>""")


def gerar_html():
    p = Paginas()
    capa(p)
    metodo(p)
    for a in c.AULAS:
        aula(p, a)
    fechamento(p)
    doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Kit das Aulas AVIOR</title>
<style>{fontes_css()}{CSS}</style></head>
<body>{''.join(p.lista)}</body></html>"""
    (AQUI / "kit.html").write_text(doc, encoding="utf-8")


def mensagem(a, total):
    prox = next((x for x in c.AULAS if x["n"] == a["n"] + 1), None)
    pontos = "\n".join(f"▪️ {x}" for x in a["aprendizados"][:3])
    fim = (
        f"Amanhã: *Aula {prox['n']} · {prox['titulo']}* 👀"
        if prox else c.ENCERRAMENTO
    )
    return f"""*📚 KIT DAS AULAS · DIA {a['n']}/{total}*
*{a['titulo']}*
_Aula de {a['data']}_

{a['ideia']}

*O que levar dessa aula:*
{pontos}

*👇 O prompt da aula ({a['prompt_nome']})*
Copia, troca o que está entre [colchetes] e cola no {a['ferramenta']}:

{a['prompt']}

✅ *Tarefa:* {a['tarefa']}

{fim}"""


def gerar_mensagens():
    total = len(c.AULAS)
    partes = [
        "# Mensagens de WhatsApp: Kit das Aulas AVIOR",
        "",
        "Para a **Comunidade de Tecnologia e Negócios**. Copie o conteúdo de cada bloco e cole no grupo.",
        "A formatação já está no padrão do WhatsApp (`*negrito*`, `_itálico_`).",
        "",
        f"**Cronograma sugerido:** véspera = abertura · Dias 1 a {total} = uma aula por dia, sempre no mesmo horário.",
        f"No **Dia {total}**, envie a mensagem e, logo depois, o arquivo `Kit-das-Aulas-AVIOR.pdf`.",
        "Se o prompt ficar longo demais numa mensagem só, mande o texto até o prompt e o prompt numa segunda mensagem.",
        "",
        "> **Antes de enviar:** o prompt da aula 2 é o texto do resumo oficial. Os das aulas 1, 3, 4 e 5 foram remontados a partir das",
        "> gravações (nas aulas 1, 4 e 5 o texto completo não foi lido em voz alta). Se a Ju ou a Carol tiverem o texto original do slide,",
        "> troque em `conteudo.py` e rode `python3 gerar.py && node pdf.js`.",
        "",
        "---",
        "",
        "## Véspera: abertura",
        "",
        "```",
        c.ABERTURA,
        "```",
    ]
    for a in c.AULAS:
        partes += ["", "---", "", f"## Dia {a['n']}: {a['titulo']}", "", "```", mensagem(a, total), "```"]
    partes.append("")
    (AQUI / "MENSAGENS-WHATSAPP.md").write_text("\n".join(partes), encoding="utf-8")


if __name__ == "__main__":
    gerar_html()
    gerar_mensagens()
    print("kit.html e MENSAGENS-WHATSAPP.md gerados.")
