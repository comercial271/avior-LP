# Formato do spec JSON

```json
{
  "titulo": "Nome interno do carrossel (vira o nome do zip)",
  "tipo": "Utilidade | Narrativo | Prova | Venda disfarçada",
  "pedido": "Salvar",
  "slides": [ ... ],
  "legenda": "Texto da legenda, com \n entre parágrafos e hashtags no fim"
}
```

Exemplo completo: `examples/exemplo-custo-manter-jardim.json`.

## Tipos de slide (`k`)

### `capa` (sempre o slide 1)
```json
{"k": "capa", "titulo": "Gancho de 14 a 18 palavras."}
```
Com foto (capa de Prova): adicione `"foto": "fotos/depois.jpg"`. Sem o arquivo, sai o espaço tracejado.

### `texto` (cards do meio)
```json
{"k": "texto", "etiqueta": "1", "titulo": "O estado de hoje", "corpo": "Frase curta. Outra frase."}
```
- `etiqueta` é opcional (número ou palavra curta, como EXEMPLO).
- `corpo` aceita `\n` para quebrar parágrafo.
- O fundo alterna sozinho: slide par em Areia, ímpar em Capim. Para forçar, use `"fundo": "areia"`, `"capim"` ou `"capim2"`.

### `lista` (card de salvar)
Igual ao `texto`, mas cada linha do `corpo` vira um item com marcador dourado.
```json
{"k": "lista", "titulo": "Use como roteiro", "corpo": "Pergunta 1?\nPergunta 2?\nPergunta 3?"}
```

### `foto` (antes e depois)
```json
{"k": "foto", "foto": "fotos/antes.jpg", "rotulo": "ANTES", "corpo": "O que estava assim."}
```
Caminho relativo à pasta do spec, ou absoluto.

### `pedido` (sempre o último)
```json
{"k": "pedido", "titulo": "Salve este post para a hora de pedir orçamento.", "corpo": "Uma frase de apoio."}
```

## Limites de texto

| Slide | Título | Corpo |
|---|---|---|
| capa | até ~18 palavras | não tem |
| texto | até ~6 palavras | até ~45 palavras |
| lista | até ~5 palavras | até 5 itens curtos |
| foto | não tem | até ~25 palavras |
| pedido | até ~12 palavras | até ~30 palavras |

Se passar disso o renderizador avisa `ESTOUROU` (quando roda com Playwright). Sem Playwright ele não consegue medir: confira os PNGs a olho.

## Conferências automáticas

O renderizador avisa `CONFERIR:` quando acha preço (R$), menção a Selva, mentoria, imersão ou comunidade, capa fora de 10 a 20 palavras, ou capa/pedido fora do lugar. Travessão bloqueia a geração.
