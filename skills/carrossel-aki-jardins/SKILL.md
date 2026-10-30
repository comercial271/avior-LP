---
name: carrossel-aki-jardins
description: Gera carrosséis de Instagram no padrão visual da AKI Jardins (@akijardins), do André Krieger, de Rio do Sul/SC. Fundo verde Capim, texto Areia, detalhes em Latão, logotipo AKiJardinS, slides PNG 1080x1350 prontos para postar, legenda e zip. Use SEMPRE que o André pedir carrossel, post, slides ou conteúdo para o Instagram da AKI, ou disser coisas como "faz um carrossel disso", "transforma isso em post", "quero os slides de sexta", "monta o carrossel da poda", "post de antes e depois", "preciso de conteúdo pro Instagram". Acione também quando ele mandar um áudio transcrito, uma ideia solta, uma dúvida de cliente ou fotos de serviço pedindo para virar post, mesmo sem usar a palavra carrossel.
---

# Carrossel AKI Jardins

Transforma uma ideia, dúvida de cliente ou serviço feito em um carrossel pronto para o feed de **@akijardins**: texto na voz do André + PNGs 1080x1350 na identidade da AKI + legenda + zip para baixar no celular.

O Instagram da AKI existe para uma coisa: fazer o cliente certo ver o perfil e pedir uma visita. Curtida é bônus. Conversa é o resultado.

## Fluxo

1. **Entenda a matéria-prima.** Ideia solta, áudio, pergunta que um cliente fez, foto de serviço. Se faltar o essencial (qual o assunto e qual o pedido final), pergunte tudo numa mensagem curta.
2. **Escolha o tipo** (tabela abaixo) e o pedido do último card.
3. **Escreva o texto primeiro, no chat,** card a card, mais 3 a 5 opções de gancho para a capa e a legenda. Espere o "ok" do André antes de gerar imagem. Ajustar texto é barato, refazer PNG não.
4. **Monte o spec JSON** (formato em `references/spec.md`).
5. **Rode o renderizador:**
   ```bash
   python scripts/render.py spec.json --out <pasta-de-saida>
   ```
   Ele gera `slide-01.png` em diante, `legenda.md` e um `.zip`. Leia os avisos `CONFERIR:` e `ESTOUROU:` e corrija antes de entregar.
6. **Olhe os PNGs** (pelo menos capa, um card do meio e o último) antes de entregar.
7. **Entregue:** o zip primeiro, depois os slides, e a legenda pronta para colar.

## Para quem o André fala

Público único: o cliente final de jardim. Residências, condomínios (síndico) e empresas de Rio do Sul e região.

- **Nunca** falar de Selva, mentoria, imersão, comunidade, método ou marcas de fora. Nem no slide, nem na legenda, nem nas hashtags.
- Os pedidos são sempre de cliente: salvar, compartilhar, marcar alguém, comentar, seguir, pedir orçamento ou visita técnica, chamar no WhatsApp, indicar para um vizinho.
- **Sem preço**, sem número interno, sem nome de cliente. A AKI visita primeiro e passa o preço depois.
- Foto de cliente só com autorização assinada. Sem endereço, número de casa, placa de carro ou rosto de quem não autorizou.

## A voz do André

- Primeira pessoa, de quem está no campo todo dia. "Eu olho primeiro o estado do jardim", não "especialistas recomendam".
- Frase curta, palavra simples, uma ideia por card. Se o card pede duas respirações, são dois cards.
- Honesto antes de vendedor: "serve para qualquer prestador, comigo ou com outro" gera mais confiança que propaganda.
- Cada card do meio termina com algo que o cliente pode fazer ou perguntar.
- Sem travessão (o renderizador recusa). Ponto ou vírgula resolvem.
- Só afirme sobre a prática da AKI o que o André confirmou. Exemplo inventado vai marcado como EXEMPLO. Dado que só ele sabe vai como `[A PREENCHER: ...]`, que sai destacado em dourado no slide para ele ver.

## Tipos de carrossel

| Tipo | Para que serve | Frequência | Pedido |
|---|---|---|---|
| Utilidade | Ensina algo que o cliente aplica. O que mais se salva. | 2 a cada 4 | Salvar, compartilhar |
| Narrativo | A história por trás da AKI (o nome, a família, o jeito de trabalhar). Gera confiança. | 1 a cada 4 | Comentar, marcar alguém |
| Prova | Antes e depois com a lista do que foi feito. | Só com fotos reais e autorizadas | Seguir |
| Venda disfarçada | Começa num problema real e conduz ao pedido de visita. | No máximo 1 a cada 4 | Pedir orçamento ou visita |

## O molde de 10 cards

| Card | Função | Regra |
|---|---|---|
| 1 (capa) | Gancho | Uma frase de 14 a 18 palavras. Promete uma resposta, não um assunto. |
| 2 | O problema | A situação que o cliente reconhece. |
| 3 a 7 | O raciocínio | Uma ideia por card, frases curtas, etiqueta numerada. Termina com algo que o cliente pode fazer. |
| 8 | O exemplo | Concreto. Marcado EXEMPLO quando não for caso real. |
| 9 | O card de salvar | Resumo ou lista de perguntas. É o card que a pessoa guarda (`k: lista`). |
| 10 | O pedido | Um só pedido. Sem preço. |

Narrativo pode ter 9 cards, Prova 7. O que não muda: capa com gancho, um pedido só no fim.

**Capa boa:** "Antes de perguntar quanto custa manter o jardim, descubra o que faz esse valor subir ou cair."
**Capa fraca:** "Dicas de manutenção de jardim." (é assunto, não promete resposta)

## Legenda

40 a 90 palavras. Começa pela situação do cliente, conta em 2 ou 3 parágrafos curtos o que tem nos cards, termina com o mesmo pedido do último card. 3 a 5 hashtags locais e de serviço (ex.: #jardinagem #riodosul #manutencaodejardim #akijardins).

## Identidade visual

O renderizador já implementa tudo. Não troque cores nem fontes no spec. Detalhes e o porquê em `references/identidade.md`.

- Capa e último card em verde **Capim**. Cards do meio alternam **Areia** (creme) e Capim.
- Moldura fina em **Latão** (dourado), logotipo **AKiJardinS** no topo, filete dourado embaixo do título.
- Rodapé fixo: "AKI Jardins | Rio do Sul e região", "arraste →" e a numeração. No último card, @akijardins no lugar do arraste.
- Se o André mandar a logo em PNG com fundo transparente, salve como `assets/logo.png`: o renderizador passa a usar a imagem no lugar do logotipo escrito.

## Fotos

Para carrossel de Prova ou capa com foto, use `k: foto` e o campo `foto` no spec (caminho do arquivo). Sem foto, o slide sai com um espaço tracejado escrito "FOTO DO ANTES/DEPOIS [a preencher]", para ele saber o que falta. Antes e depois sempre do mesmo ângulo. Na dúvida sobre qual foto é antes e qual é depois, pergunte: trocar os dois é o pior erro possível.

## Calendário de referência

Carrossel sai na sexta, 19h. Os pedidos de venda (orçamento, visita) ficam separados por pelo menos 3 posts. Ao ser pedido "o carrossel da semana", confira com o André qual pauta está na vez.
