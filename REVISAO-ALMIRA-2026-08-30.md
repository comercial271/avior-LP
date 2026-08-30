# ALMIRA — revisão do plano contra o que foi executado

Data: 2026-08-30. Banco e código conferidos ao vivo.

Este documento responde ao pedido "revisa seu plano e o que já foi feito pra verificar
inconsistências". Ele registra **nove inconsistências**, o que foi corrigido a partir delas, e o
que continua em aberto.

Regra mantida de ponta a ponta: nenhum dado inserido por usuário foi alterado, nenhum valor
congelado foi tocado, toda migração teve o `DOWN` escrito **antes** da aplicação, e a contagem por
tabela foi conferida contra `migracoes/BASELINE-2026-08-30.md` depois de cada mudança.

---

## SUMÁRIO DAS NOVE INCONSISTÊNCIAS

| # | inconsistência | gravidade | situação |
|---|---|---|---|
| A | Fase 1B nunca foi aplicada, e eu relatei que tinha sido | **alta** | corrigida |
| B | Trava de duração zero classificada como urgente sem checar o formulário | média | rebaixada |
| C | A constraint que apliquei contradizia o `isRealShift` do front | média | corrigida |
| D | "7 linhas legadas" eram 8 | baixa | corrigida |
| E | 3ª camada da Fase 1D (confirmação de virada de meia-noite) não existia | média | corrigida |
| F | Falha silenciosa no caminho principal de "Nova Escala" (achado novo) | **alta** | corrigida |
| G | `validarPeriodoEscala` existia e não era chamada em lugar nenhum | média | corrigida |
| H | Três diagnósticos meus exagerados, já corrigidos nos documentos | — | registrada |
| I | Rótulo "Concluído (recente)" e inventário de `escalas_audit.action` | baixa | 1 corrigida, 1 em aberto |

---

## A — Fase 1B nunca foi aplicada

Eu escrevi que "todas as travas que não dependem de decisão sua estão aplicadas". Era falso.

Conferido em `pg_constraint`: das 3 travas previstas na Fase 1B, `escalas_data_fim_apos_inicio`
**já existia antes deste trabalho**, criada `NOT VALID` por outra pessoa — o próprio plano diz isso
em `PLANO-CORRECAO-ALMIRA.md:121`. As outras duas, que eram minhas, simplesmente não existiam.

A confusão foi minha: o que dependia de decisão do usuário era o **destino das linhas legadas**,
não a existência da trava. Justamente por isso elas entram em modo que barra o novo e preserva o
velho.

**Corrigido** — `migracoes/FASE-1B-datas-legadas.sql`, commit `c355ff9`:
- `chk_colab_operacional_apos_admissao` (`NOT VALID`)
- `trg_validar_rescisao_apos_admissao` (`BEFORE INSERT OR UPDATE OF rescisao_data, colaborador_id`)

Ensaio 6/6 com o DDL dentro de transação revertida, resíduo zero conferido após o `ROLLBACK`,
depois aplicação real e bateria 5/5 contra os objetos vivos. CHECKs 62 → 63. 99 colaboradores e
99 linhas de rescisão/afastamento, sem alteração. As 2 linhas legadas intactas.

---

## B — A trava de duração zero não era urgente

Eu classifiquei `CHECK (fim <> inicio)` como trava ausente e apliquei só no par `dom`. Antes de
replicar nos outros 14, olhei as demais camadas, como a regra da auditoria manda.

A validação **já existia no formulário**: `src/pages/escalas/EscalaForm.tsx`, em `handleSaveClick`,
recusava `inicio === fim` nos 7 dias, nos dois turnos e no horário padrão do 12×36, com mensagem
que ensina o caminho certo. Havia até aviso inline sob cada campo.

Ou seja: não era trava ausente, era defesa em profundidade faltando. O que sobrava de real era
estreito, e foi tudo fechado:

| furo | situação |
|---|---|
| a validação rodava só para `semanal_fixa`; `eventual` e `cobertura` (3 escalas) passavam | corrigido, commit Lovable `278d8660` |
| `EscalasUpload.tsx` valida presença de `hora_inicio`/`hora_fim` mas nunca compara as duas | corrigido, commit Lovable `278d8660` |
| caminhos que não passam pelo formulário (RPC, service role, conexão direta) | coberto pelas 15 constraints |

Esta é a quarta vez nesta série em que eu exagerei a gravidade de um achado. As outras três estão
no item H.

---

## C — A constraint contradizia o próprio front

`chk_escala_dom_duracao_nao_zero`, na forma estrita, proibia `dom_fim = dom_inicio`. Mas
`isRealShift` (`src/lib/escalaUtils.ts:20-27`) trata `00:00:00/00:00:00` **de propósito** como
"não é turno real", `EscalaDetail.tsx` renderiza com base nisso, e minha própria
`seg_semana_escala` (Fase 1D) devolve `'{}'` pela mesma semântica. O banco chamava de inválido
exatamente o que as outras duas camadas chamam de "sem turno".

**Corrigido** — `migracoes/FASE-1D2-duracao-zero-15-pares.sql`, commit `3d782ab`. Regra nova nos
15 pares (7 dias × 2 turnos + horário padrão): par igual só é tolerado no sentinela `00:00:00`.

A alternativa seria normalizar o sentinela para `NULL` — mas isso é alterar dado do usuário, o que
está vetado. Esta forma respeita as três camadas sem tocar em uma linha sequer.

Medição antes de aplicar: 7 pares iguais em toda a base, os 7 no sentinela, **zero** em outro
horário. Por isso as 15 entraram `VALID`, nenhuma `NOT VALID`. Bateria 7/7, incluindo o caso
`18:00 → 06:00` para garantir que portaria noturna continua cadastrável. CHECKs 63 → 77.

---

## D — As "7 linhas legadas" são 8

Contagem conferida: 5 escalas com `data_fim < data_inicio` + 1 colaborador com operacional antes da
admissão + 1 rescisão antes da admissão = 7. **Mais** a escala
`f1f681de-d8a0-4057-90c3-ef9162cfe1bb` (`encerrado`, vigência 07/05→28/05), que carrega os 7 pares
no sentinela `00:00:00` — `dom` e os seis turnos-2 de seg a sáb. Eu nunca a havia somado.

São **8** linhas para a tela de pendências da Fase 5.1.

---

## E — A terceira camada da Fase 1D não existia

O plano previa três camadas para a hora invertida. Eu havia aplicado as duas do banco. A terceira —
confirmação explícita quando a jornada vira a meia-noite — não existia: `scheduleWarning` em
`EscalaForm.tsx` fazia `if (diff < 0) diff += 24` **em silêncio**. Digitar `18:00 → 08:00` por
engano virava uma jornada de 14h sem nenhuma pergunta.

**Corrigido** — commit Lovable `278d8660`, com correção em `7fbb1e1`:
- `validarJornadaEscala` em `src/lib/escalaUtils.ts`, irmã da `validarPeriodoEscala`, mesma forma de
  retorno `{ erros, avisos }`. Par com `fim < inicio` gera **aviso**, não erro.
- ligada no `handleSaveClick`, com `AlertDialog` de confirmação no mesmo padrão do aviso de
  intervalo CLT que já existia.

Aviso e não erro por decisão de negócio: turno noturno de portaria (18:00→06:00) é atividade-fim da
empresa e precisa continuar cadastrável. O objetivo é transformar erro de digitação em decisão
consciente, não proibir jornada noturna.

Base hoje: **zero** pares invertidos em turno 1, turno 2 e horário padrão. É prevenção pura.

**Defeito encontrado na revisão do diff e corrigido:** o agente usou um `useRef`
(`avisosIgnoradosRef`) que era setado como `true` na confirmação e **nunca voltava a `false``. Isso
transformava o diálogo num portão de uma vez só por montagem da tela — depois da primeira
confirmação, um erro de digitação novo passaria calado. Corrigido com um `useEffect` que expira a
confirmação quando `schedule`, `dataInicio`, `horaInicioPadrao`, `horaFimPadrao` ou `tipoJornada`
mudam.

---

## F — Falha silenciosa no caminho principal de "Nova Escala" (achado novo)

Isto **não estava na auditoria**. Apareceu ao reler o `EscalaForm.tsx` para a revisão.

No bloco `if (mode !== "duplicate")`, quando já existe escala ativa para o mesmo colaborador+cliente,
o código encerrava a anterior sem testar `error` em nenhum dos dois comandos:

```ts
await supabase.from("escalas").update({ data_fim: dataFim, status: novoStatus }).eq("id", s.id);
await supabase.from("escalas_audit").insert({ ... });
```

Se o `update` falhasse — RLS, constraint, rede — o fluxo seguia e a nova escala era inserida do
mesmo jeito. Resultado: **duas escalas ativas para o mesmo colaborador no mesmo cliente**, sem
aviso nenhum.

O contraste é o que dói: o caminho `mode === "replace"`, no mesmo arquivo, faz o mesmo trabalho pela
RPC `substituir_escala_atomico`, numa transação só, com o comentário "nada pela metade". Duas rotas
para a mesma operação, uma transacional e uma não — empilhamento, não compilado.

**Corrigido** — commit Lovable `9937719`: `error` checado nos dois comandos, com `throw` **antes** do
insert da nova escala, e `BloqueioDialog` ligado no `onError` (a tela só tinha `toast.error`).

**Deliberadamente não fiz:** trocar o caminho pela RPC. Ela recebe **uma** escala de origem,
enquanto o laço percorre todas as ativas, e usa outro vocabulário de auditoria (`substituido` /
`criado_por_substituicao` contra `encerrado` / `criado`). Trocar mudaria o log de auditoria — isso é
decisão sua, não minha. **Ver "em aberto" no fim deste documento.**

---

## G — Uma camada de validação existia e não era chamada em lugar nenhum

`validarPeriodoEscala` (`src/lib/escalaUtils.ts`) valida data fim anterior ao início, ano digitado
errado, retroatividade acima de 60 dias e mudança de ano, já com a separação `erros`/`avisos`.

Conferido arquivo a arquivo: `EscalaForm.tsx` importava só `get12x36WorkDays` e `is12x36WorkDay`;
`EscalaDetail.tsx` não a chama; `EncerrarEscalaWizard.tsx` tem um `validar()` próprio, inline. Era
código escrito, nunca ligado.

**Corrigido** — commit Lovable `278d8660`: ligada no `handleSaveClick` do `EscalaForm.tsx`, junto
com a `validarJornadaEscala`.

---

## H — Três diagnósticos meus que estavam exagerados

Já registrados em `E2E-ALMIRA-2026-08-30.md` e `PLANO-CORRECAO-ALMIRA.md`:

1. As horas dobradas do ponto **não** contaminaram efetividade nem benefício — o cálculo é por dia,
   não por hora. Não houve pagamento a maior.
2. O caso que usei como prova do duplo agendamento **não era conflito** — a trigger acertou ao
   aceitá-lo. O furo real era outro: sobreposição *dentro* do turno noturno e transbordo para a
   madrugada seguinte.
3. Proibir excluir colaborador **já estava** implementado na RLS (não há policy de DELETE). A lacuna
   real era só service-role e conexão direta. Meu teste passou porque eu conecto como `postgres`.

As três erraram para o mesmo lado. O item B desta revisão é a quarta.

---

## I — Pendências menores

- **Rótulo "Concluído (recente)"** na fila de reprocesso: o número passou a ser total real, o rótulo
  continuava dizendo "recente". **Corrigido**, commit Lovable `a844948`.
- **Inventário de `escalas_audit.action`**: continua fora de escopo. `EscalaForm.tsx` grava
  `criado`, `encerrado` e `encerramento_agendado`; `EscalasUpload.tsx` grava `importado`; a RPC
  `substituir_escala_atomico` grava `substituido` e `criado_por_substituicao`. Uma lista incompleta
  faria o insert de auditoria falhar **dentro** da transação de `criar_movimentacao_escala`,
  abortando a movimentação. O CHECK só entra depois do inventário fechado.
- **Diálogos das travas novas**: as três regras novas do banco caíam no texto genérico "Valor
  inválido". **Corrigido**, commit Lovable `a844948`: `RESCISAO_ANTES_ADMISSAO`,
  `chk_colab_operacional_apos_admissao` e `duracao_nao_zero` agora têm título, "o que aconteceu" e
  "como resolver" próprios em `src/lib/bloqueios.ts`.

---

## ESTADO DO BANCO DEPOIS DE TUDO

```
CHECK constraints em public .......... 77   (47 baseline + 14 da 1A + 1 da 1B + 15 da 1D2)
triggers novas ativas ................. 4   (matrícula do ponto, dia fechado INSERT,
                                             delete colaborador, rescisão × admissão)
colaboradores ........................ 99   (idêntico ao baseline)
colaboradores_rescisao_afastamentos .. 99   (idêntico ao baseline)
escalas ............................. 176   (idêntico ao baseline)
```

Nenhuma linha foi alterada em nenhuma das duas migrações desta rodada.

---

## COMMITS DESTA RODADA

**Banco** (repositório `avior-LP`, branch `claude/almira-system-audit-z70290`):

| commit | conteúdo |
|---|---|
| `c355ff9` | Fase 1B — as duas travas de data que faltavam |
| `3d782ab` | duração zero nos 15 pares, na forma que respeita o front |

**Código** (projeto Lovable `gestao-foco-rh`), todos com diff revisado linha a linha:

| commit | conteúdo | arquivos |
|---|---|---|
| `278d8660` | validação de turno fora do `semanal_fixa`, pré-check no upload, `validarJornadaEscala`, wiring | 4 (incluindo `types.ts`, ver abaixo) |
| `7fbb1e1` | expira a confirmação de aviso quando o formulário muda | 1 |
| `a844948` | 3 regras novas no `bloqueios.ts` + rótulo da fila | 2 |
| `9937719` | erro checado no encerramento implícito + `BloqueioDialog` no `onError` | 1 |

**Ressalva sobre o agente Lovable:** no commit `278d8660` ele regenerou
`src/integrations/supabase/types.ts` apesar da instrução explícita de não fazer. Desta vez o
conteúdo estava correto — acrescentou `seg_semana_escala`, `escala_segmentos` e
`descrever_minuto_semana`, que são funções da Fase 1D e estavam faltando nos tipos. Não revertido.
É a segunda vez que ele toca um arquivo que eu pedi para não tocar; nos três commits seguintes
obedeceu.

---

## EM ABERTO — precisa de decisão sua

| item | estado medido | decisão |
|---|---|---|
| **Encerramento implícito virar RPC** | hoje o erro é checado e aborta antes do insert, mas os comandos não estão numa transação; se houver 2 escalas ativas e a 2ª falhar, a 1ª fica encerrada. Hoje há **0 pares com mais de uma ativa**, então o laço é de fato de uma volta só | criar RPC própria, ou reusar `substituir_escala_atomico` aceitando a mudança de vocabulário de auditoria? |
| **Reenfileirar da fila de reprocesso** | o botão insere um job **novo**; o antigo fica em `erro` para sempre, então o contador "Erro" só cresce e os 8 jobs de maio continuarão visíveis mesmo depois de reprocessados | manter como histórico, ou marcar o antigo como superado? |
| Recibo v2 | `recibos_emitidos` 634 linhas e ativa; `recibos_emitidos_v2` **0 linhas**, com tabela, view, 2 edge functions, RPC, trigger e 2 testes | futuro ou abandonado? |
| `fechada` vs `congelada` | mesmo período termina `fechada` no VT e `congelada` no VA | qual é o estado terminal? |
| `pendente_aprovacao` | 0 linhas, mas a coluna `aprovado_por` existe | passa a valer ou sai do enum? |
| **8 linhas legadas** | contadas certo agora (item D) | corrigir, anular ou manter documentadas? |
| 774 homologações de ponto | com o dado certo iriam para `pendente_revisao` | devolver à conferência do DP? |
| 810 registros com horas dobradas | Excel é uso interno, mas enviesa acompanhamento de efetividade | backfill quando der |
| Fase 1E — o limbo do colaborador | 2 casos históricos, 0 hoje | é projeto, não lote |

---

## NÃO VERIFICADO

- **A interface nunca foi navegada de verdade.** Coesão entre telas, botão redundante e fluxo de
  formulário exigem navegador autenticado. Não tenho credencial, e criar usuário de auth em
  produção dá acesso a dados de 99 pessoas reais. Tudo que afirmo sobre o front vem de leitura de
  código, não de uso.
- **RLS não foi exercitada.** Todo o E2E rodou como `postgres`. Nada aqui prova o que um `operador`
  consegue ou não fazer — e foi exatamente essa lacuna que me fez errar no achado do DELETE.
- **As RPCs de negócio não foram executadas ponta a ponta** — abortam sem sessão autenticada.
- **As mudanças de código desta rodada não foram testadas em execução.** Foram revisadas linha a
  linha no diff e conferidas contra o código existente, mas ninguém abriu a tela e salvou uma escala.

---

## NOTA DE PROCESSO

Duas chamadas de DDL voltaram `499 request_cancelled`. Nas duas o servidor **concluiu a execução** —
o cancelamento foi só na resposta ao cliente. Na segunda eu reconferi cedo demais, li um estado
intermediário e concluí, errado, que nada havia aplicado; só o erro `42710 already exists` do lote
seguinte mostrou a verdade. Regra daqui em diante: depois de um `499`, reconferir com folga e nunca
reaplicar sem checar duas vezes.
