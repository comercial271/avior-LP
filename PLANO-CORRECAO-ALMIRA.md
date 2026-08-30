# PLANO DE CORREÇÃO — SISTEMA ALMIRA
**Base:** auditoria de 2026-08-30 + teste E2E em transações reversíveis
**Alvo:** projeto Lovable `gestao-foco-rh` · banco Supabase (Lovable Cloud), produção

---

## PRINCÍPIOS INEGOCIÁVEIS

Traduzidos em regra operacional, não em intenção:

| Princípio | Como é garantido na prática |
|---|---|
| Não comprometer o banco | Toda trava é medida contra o dado existente ANTES de aplicar. Nenhuma constraint entra sem eu saber quantas linhas ela recusaria. |
| Não alterar valores congelados | Nada toca `beneficio_calculo_quinzenal` com status `fechada`/`congelada`, linhas com `validado_em`, dias em `efetividade_dia_fechamento`, nem `recibos_emitidos`. As travas novas são todas de INSERT/UPDATE futuro. |
| Não mexer em dado inserido por usuário | Onde houver linha legada em desacordo, a trava entra `NOT VALID` (barra o novo, preserva o velho) e a linha vai para uma **tela de pendência**, para uma pessoa decidir. Correção automática de dado histórico: nunca. |
| Segurança dos dados | Fase 4 dedicada. Inclui a rota de dev exposta a qualquer usuário logado. |
| Compilado, não empilhamento | Fase 2 elimina duplicatas em vez de somar mais uma camada. Toda consolidação escolhe UMA fonte de verdade e remove as outras. |
| Botão inútil sai | Fase 3, com método de varredura, não só os que já achei. |
| Travas são urgentes | Fase 1 é a primeira e a maior, e 15 das 18 travas podem entrar hoje sem risco nenhum. |

---

## O DADO QUE DEFINE O PLANO

Medi quantas linhas de produção violariam cada trava proposta. Resultado:

**15 travas têm ZERO violação hoje.** Entram como `VALID`, imediatamente, sem recusar um único
registro existente:

```
afastamento_fim < inicio ............... 0     valores_beneficios: valor < 0 ......... 0
ferias: gozo_2 < gozo_1 ................ 0     valores_beneficios: vigência .......... 0
ferias: dias_gozo fora de 0..30 ........ 0     valores_beneficios: percentual ........ 0
cbv: vigencia_fim < inicio ............. 0     quinzena: data_fim < data_inicio ...... 0
cbv: valor_unitario < 0 ................ 0     quinzena: complementar invertido ...... 0
ponto: total_horas fora de 0..24 ....... 0     fila reprocesso: data_fim < inicio .... 0
efetividade: horas fora de 0..24 ....... 0     import log: data_fim < inicio ......... 0
ponto: matricula diverge ............... 0
```

**Apenas 3 têm dado legado em desacordo:**

| trava | linhas em desacordo |
|---|---|
| `escalas`: `data_fim >= data_inicio` (constraint existe, mas `NOT VALID`) | **5** |
| `colaboradores`: `data_inicio_operacional >= data_admissao` | **1** (matrícula 09490) |
| `rescisao_data >= data_admissao` (cruza tabelas → trigger) | **1** |

Ou seja: **83% do trabalho de trava é risco zero.** Isso muda a ordem de execução — não há motivo
para adiar.

---

# FASE 0 — REDE DE SEGURANÇA (antes de qualquer DDL)

Nada abaixo altera dado. É o que permite desfazer.

**0.1** Registrar o estado atual: contagem por tabela, lista das constraints e triggers existentes,
e o conjunto exato das 7 linhas legadas em desacordo (5 escalas + 2 colaboradores), com todas as
colunas, salvo como evidência fora do banco.

**0.2** Verificar o backup automático do projeto (PITR / snapshot diário) e anotar o ponto de
restauração antes da primeira migração.

**0.3** Escrever cada migração com o `DOWN` correspondente no mesmo arquivo. Toda constraint criada
nesta fase é `ALTER TABLE ... ADD CONSTRAINT`, cujo desfazer é um `DROP CONSTRAINT` — reversível em
segundos, sem tocar em linha nenhuma.

**Critério de aceite:** existe um comando escrito, testado em transação revertida, que desfaz cada
item da Fase 1.

---

# FASE 1 — TRAVAS (urgente)

## 1A — As 15 travas de risco zero

Entram como `VALID`. Nenhuma recusa dado existente (medido acima).

**Ordem de datas**
```
colaboradores_rescisao_afastamentos: afastamento_fim >= afastamento_inicio
colaboradores_ferias:                data_inicio_gozo_2 >= data_inicio_gozo_1
colaborador_beneficio_valor:         vigencia_fim >= vigencia_inicio
valores_beneficios:                  vigencia_fim >= vigencia_inicio
beneficio_calculo_quinzenal:         data_fim >= data_inicio
beneficio_calculo_quinzenal:         data_fim_complementar >= data_inicio_complementar
efetividade_reprocess_queue:         data_fim >= data_inicio
ponto_importacao_log:                data_fim >= data_inicio
```
Todas na forma `(x IS NULL OR y IS NULL OR x >= y)`, para não exigir preenchimento de campo opcional.

**Faixas numéricas**
```
ponto_registros.total_horas          between 0 and 24
efetividade_diaria.horas_trabalhadas between 0 and 24   ← espelha o CHECK que horas_atestado já tem
colaboradores_ferias.dias_gozo       between 0 and 30
valores_beneficios.valor             >= 0
valores_beneficios.percentual        between 0 and 100
colaborador_beneficio_valor.valor_unitario >= 0
```

A assimetria de `efetividade_diaria` é o argumento mais forte da fase: `horas_atestado` **já tem**
`CHECK (>= 0 AND <= 24)`. `horas_trabalhadas`, na mesma tabela, aceita 99. Não é decisão de projeto,
é lacuna.

**Integridade de identidade**
```
ponto_registros.matricula deve bater com colaboradores.matricula
```
Zero divergências hoje. Trigger `BEFORE INSERT OR UPDATE` que **preenche** a matrícula a partir do
`colaborador_id` em vez de confiar no que veio — elimina a classe inteira do problema em vez de
apenas recusá-la.

**Critério de aceite:** as 15 aplicadas; `SELECT` de contagem em cada tabela idêntico ao da Fase 0;
nenhuma linha alterada.

## 1B — As 3 travas com dado legado

Aqui mora a regra "não mexer em dado do usuário".

**`escalas.data_fim >= data_inicio`** — a constraint já existe, criada `NOT VALID`. Ela **já barra
inserção nova** (confirmei no E2E: bloqueou). O que falta é o `VALIDATE`, que hoje falharia por causa
de 5 linhas antigas.
→ **Não rodar `VALIDATE` agora.** Deixar `NOT VALID` e mandar as 5 linhas para a tela de pendências
da Fase 5. `VALIDATE` só depois que uma pessoa decidir o que fazer com cada uma. As 5 estão todas com
status `encerrado`; uma tem inversão de 78 dias (início 2026-04-01, fim 2026-01-13).

**`colaboradores.data_inicio_operacional >= data_admissao`** — 1 linha (matrícula 09490, operacional
11 dias antes da admissão).
→ Entra `NOT VALID`. A linha vai para a tela de pendências. Enquanto não for resolvida, essa
colaboradora continua recebendo elegibilidade a benefício 11 dias antes de ter sido admitida — o
`preCheckCalculo` usa `data_inicio_operacional || data_admissao`, com a operacional tendo precedência.

**`rescisao_data >= data_admissao`** — cruza duas tabelas, então CHECK não resolve; precisa de
trigger `BEFORE INSERT OR UPDATE` em `colaboradores_rescisao_afastamentos`.
→ A trigger nasce ativa para dado novo e **não revalida o existente**. A 1 linha em desacordo vai
para pendências.

**Critério de aceite:** as 3 aplicadas em modo que barra o novo e preserva o velho; as 7 linhas
legadas listadas numa tela, nenhuma alterada por mim.

## 1C — Travas de estado que hoje não existem

**Dia fechado não bloqueia INSERT.** Existem `trg_protect_closed_day_upd` e `_del`. Não existe de
INSERT — confirmei no E2E: com o dia `2026-06-05` fechado, um `INSERT` novo de efetividade foi
aceito.
→ Criar `trg_protect_closed_day_ins BEFORE INSERT`.
→ **Cuidado obrigatório:** o motor de reprocessamento materializa efetividade e pode legitimamente
inserir em dia fechado. O projeto já tem a função `is_engine_reprocess()` exatamente para distinguir
esse caso. A trigger nova precisa isentar o motor e barrar apenas o lançamento manual. Sem essa
isenção, esta trava quebra o reprocessamento.

**DELETE de colaborador não é proibido.** A especificação do projeto diz "PROIBIDO excluir
colaborador, apenas inativar com histórico". No E2E, um colaborador sem dependências foi excluído sem
resistência — o único bloqueio que apareceu antes foi acidental (FK da fila de reprocessamento).
→ Trigger `BEFORE DELETE` em `colaboradores` que sempre levanta exceção, com mensagem que ensina o
caminho certo ("inative o colaborador em Cadastro → Colaboradores").

**`escalas_audit.action` aceita qualquer texto.** Hoje tem 14 grafias diferentes, incluindo "correção"
com acento ao lado de "correcao_datas".
→ CHECK com a lista dos 14 valores existentes (nenhum é recusado) e padronização das grafias novas
daqui para frente. Não renomear as antigas — é dado de auditoria.

## 1D — A cascata da hora invertida (a mais importante da fase)

**O problema, confirmado por teste:** o sistema aceita `seg_inicio = 18:00, seg_fim = 08:00`; calcula
e grava isso como jornada de 13h (`horas_semanais = 17.00`); e essa escala fica **invisível** para a
trigger de sobreposição, porque `check_escala_overlap` compara horários crus e `09:00 < 08:00` é
falso. Resultado: a mesma pessoa pode ser alocada duas vezes no mesmo horário e cliente, sem aviso.

**Por que a solução óbvia está errada.** Um `CHECK (fim > inicio)` parece o caminho, mas
**inviabilizaria turno noturno de portaria** (18:00→06:00), que é atividade-fim da empresa. Medi a
base: hoje há **zero** pares invertidos, em escala e em ponto, e zero 12x36 com hora invertida.
Ou seja, a trava passaria hoje — e quebraria no dia em que o primeiro porteiro noturno fosse
cadastrado. Isso é armadilha, não trava.

**Desenho proposto, em três camadas:**

1. **Bloquear o que é sempre inválido:** `CHECK (fim <> inicio)` para cada par. Um turno de duração
   zero não tem leitura possível. Há 1 linha assim hoje (domingo 00:00–00:00) → entra `NOT VALID`,
   linha vai para pendências.

2. **Fechar o buraco de verdade — corrigir a trigger, não proibir o dado.** Reescrever
   `check_escala_overlap` para normalizar intervalo invertido como travessia de meia-noite
   (somar 24h ao fim) antes de comparar. Assim a sobreposição é detectada **independentemente** de a
   jornada ser diurna ou noturna. Isto elimina o duplo agendamento sem tirar do sistema a capacidade
   de registrar turno noturno.

3. **Transformar digitação errada em decisão consciente:** no formulário de escala, quando um par
   inverter, exigir confirmação explícita ("Esta jornada vira a meia-noite: 18:00 de um dia até 08:00
   do seguinte, 13h. Confirma?"). Erro de digitação morre no diálogo; turno noturno real passa.

**Urgência, com honestidade:** hoje **não há nenhuma escala invertida em produção**, então o duplo
agendamento é risco latente, não dano em curso. É prevenção urgente, não correção de emergência.

**Critério de aceite da Fase 1:** repetir a bateria E2E completa em transação revertida. As 18 travas
ausentes devem passar a bloquear; as 11 que já funcionavam devem continuar funcionando; o
reprocessamento de efetividade deve continuar inserindo em dia fechado.

---

# FASE 2 — DE EMPILHAMENTO PARA COMPILADO

Cada item escolhe **uma** fonte de verdade e remove a outra. Nenhum item adiciona camada.

## 2.1 Recibos: existem duas pilhas completas, uma sem uso
`recibos_emitidos` tem 634 linhas e é a que roda (última gravação 28/08). `recibos_emitidos_v2` tem
**zero**, e ainda assim existe com tabela, view `vw_recibo_consolidado_v2`, edge function
`gerar-recibo-beneficio-v2/` (4 arquivos), RPC `registrar_recibos_v2_lote`, trigger de imutabilidade,
CHECK próprio, `src/lib/beneficios/statusEmissaoV2.ts` e 2 arquivos de teste.

→ **Decisão necessária (sua):** a v2 é o futuro ou foi abandonada?
- Se é o futuro: migrar de fato e aposentar a v1 num prazo definido.
- Se foi abandonada: remover a pilha inteira.
- **Enquanto não decidir, ninguém sabe qual alterar** — e essa é exatamente a definição do problema.

Remoção, se for o caso, é segura: zero linhas, nada a preservar.

## 2.2 Tabela de backup de 40 mil linhas no schema de produção
`recibos_emitidos_bkp_20260720` (40.134 linhas) convive com as tabelas vivas.
→ Exportar e remover do schema `public`, ou mover para um schema `arquivo`. Não é dado de usuário em
uso; é cópia datada.

## 2.3 Tipo de benefício tem cinco representações
| representação | objeto | valores |
|---|---|---|
| enum `beneficio_tipo` | `beneficio_calculo_quinzenal.tipo_beneficio` | `vt \| va \| al` |
| enum `tipo_beneficio` | `valores_beneficios.tipo` | `vale_alimentacao \| auxilio_lanche \| assiduidade \| insalubridade` |
| texto + CHECK | `colaborador_beneficio_valor.tipo_beneficio` | `va \| al` |
| texto + CHECK | `recibos_emitidos_v2.tipo_beneficio` | `vt \| va` |
| texto livre | `auditoria_findings`, `beneficio_inconsistencia_log` | sem restrição |

Dois enums com nomes quase idênticos e invertidos, vocabulários incompatíveis, sem tradução em lugar
nenhum do banco.
→ Eleger `beneficio_tipo` (`vt|va|al`) como canônico. Migrar as colunas de texto para ele.
`valores_beneficios.tipo` mistura benefício com adicional (`insalubridade`, `assiduidade` não são
`vt|va|al`) — precisa ser separado em dois conceitos antes de unificar.
→ **Alto impacto, requer migração de dados.** Vai para a Fase 2 tardia, com plano próprio, e nunca
sobre competência congelada.

## 2.4 Três colunas de data de admissão
`data_admissao` (NOT NULL), `data_admissao_esocial` (nullable), `data_inicio_operacional` (nullable).
Medido: `data_admissao_esocial` é **idêntica** a `data_admissao` nas 99 linhas — o formulário grava o
mesmo valor nas duas (`ColaboradorForm.tsx:604-606`). `data_inicio_operacional` diverge em 1 linha —
e é **ela** que decide elegibilidade a benefício.
→ Aposentar `data_admissao_esocial` (100% redundante). Manter `data_admissao` (legal) e
`data_inicio_operacional` (operacional), **documentando em um único lugar** qual vale para quê, e
alinhar as três camadas que hoje escolhem de forma diferente (formulário, pré-check, importador).

## 2.5 A fórmula de jornada existe duas vezes e já divergiu
`src/lib/beneficios/jornadaEscala.ts` (front) e `calcular-beneficios/index.ts:770-816` (edge). O
próprio cabeçalho do arquivo do front admite: "funções PURAS que replicam a semântica de
`getHoursForDate` da edge function". Divergências já existentes: o front tem `(m || 0)` e
`Number(escala.intervalo || 0)`; a edge não tem nenhum dos dois.
→ Fonte única. Como edge (Deno) e front (Vite) não compartilham build, a saída limpa é mover a
fórmula para uma **função no banco**, chamada pelos dois lados. Alternativa mais barata: manter a
duplicata mas com um **teste que compara as duas implementações** em uma bateria de casos, quebrando
o build quando divergirem.

## 2.6 Derivação do status da escala duplicada e divergente
RPC `calcular_status_escala(p_inicio, p_fim)` cobre `futuro`/`encerrado`/`ativo`. O importador
(`EscalasUpload.tsx`) reimplementa inline e **ignora `data_fim`** — uma escala importada com fim já
passado entra como `ativo` em vez de `encerrado`.
→ Importador passa a chamar a RPC. Remove-se a versão inline.

## 2.7 Duas estratégias de identificar o mesmo colaborador
`sincronizar-ponto` faz CPF → `pin_externo` → matrícula → nome normalizado com match por subconjunto
de tokens (e grava `pin_externo` de volta). `EscalasUpload` exige matrícula exata ou nome exato em
minúsculas.
→ Extrair um resolvedor único de identidade, usado pelos dois importadores.

## 2.8 Quatro telas chamadas "Auditoria"
`/auditoria/registros`, `/efetividade/auditoria`, `/beneficios?modulo=auditoria` (Auditoria IA) e
`InconsistenciasLog`. Na sidebar, "Auditoria" é subgrupo de **Administração**, enquanto "Auditoria IA"
mora em **Benefícios**.
→ Um único ponto de entrada "Auditoria" com abas, ou nomes distintos que digam o que cada uma faz
("Registros de alteração", "Conferência de efetividade", "Achados da IA", "Inconsistências de
benefício"). Hoje o operador precisa visitar quatro telas em dois ramos do menu sem que nenhuma
mencione a existência das outras.

## 2.9 `fechada` e `congelada` usados como sinônimos
Para o mesmo período, VT termina em `fechada` e VA em `congelada`. `preCheckCalculo` testa só
`status !== 'fechada'` → **toda quinzena de VA marcada `congelada` bloqueia permanentemente o cálculo
da seguinte**. E `CalculoQuinzenal.tsx:911` só é idempotente contra `fechada`, então sobrescreve um
header `congelada` sem resistência.
→ Definir o significado de cada um por escrito, corrigir os dois pontos de código, e tratar
`pendente_aprovacao` (que existe no enum e tem **zero** linhas, apesar de a coluna `aprovado_por`
existir): ou passa a ser usado, ou sai do enum.
→ **Não reclassificar competência congelada.** Só o código muda.

## 2.10 Cadastro de cliente pede o nome três vezes
`clientes` exige, todos NOT NULL: `codigo`, `nome`, `razao_social`, `nome_abreviado` — e ainda
`competencia` (competência de folha, obrigatória para cadastrar um cliente, resquício do padrão de
"tabela versionada" aplicado a uma entidade que não é tabela de parâmetro). Além disso há dois campos
de situação: `ativo` (boolean) e `status_contrato` (texto).
→ Manter `razao_social` (legal) e `nome_abreviado` (exibição). Aposentar `nome`. Tornar `competencia`
opcional ou removê-la do cadastro. Eleger um único campo de situação.

---

# FASE 3 — LIMPEZA DE INTERFACE

## 3.1 Confirmados (verificados no código)

**Dois cards que não levam a lugar nenhum** — `RelatoriosHome.tsx`, array `cards`:
```
{ to: "#", title: "Indicadores por Cliente",     status: "Em breve" }
{ to: "#", title: "Indicadores por Colaborador", status: "Em breve" }
```
Renderizados permanentemente como "Em breve", clicáveis para `#`. Ocupam espaço no painel principal
de relatórios e não fazem nada.
→ Remover. Funcionalidade futura entra quando existir, não como placeholder.

**Rota de desenvolvimento exposta em produção** — `/dev/solides` (`SolidesDev.tsx`), protegida apenas
por `<ProtectedRoute>`, ou seja, **qualquer usuário autenticado** — incluindo `visualizador` — pode
acessar digitando a URL. A tela dispara um health-check das credenciais da Tangerino/Sólides e
despeja o resultado cru com `JSON.stringify(result, null, 2)`.
→ Remover da produção, ou no mínimo mover para `<AdminRoute>` e parar de exibir o JSON bruto.
(Também é item de segurança — repetido na Fase 4.)

## 3.2 Correção de algo que eu havia afirmado

Na auditoria eu registrei que `/relatorios/folha` e os 6 relatórios `R3…R10` seriam inalcançáveis por
navegação. **Está errado.** Eles são linkados por `RelatoriosHome.tsx` (`{ to: "/relatorios/folha",
title: "Relatórios da Folha" }`). Não estão na sidebar, mas têm caminho. Não é item de limpeza.

## 3.3 Método para o resto (não vou afirmar sem verificar)

Não varri as ~250 telas. O que fica planejado, com método:
1. Extrair todas as rotas de `App.tsx`.
2. Extrair todos os `to=`/`navigate(` do projeto.
3. Rotas sem nenhuma origem = órfãs; links para `#` ou `to` vazio = botões mortos; botões com
   `disabled` permanente = promessa não cumprida.
4. Cada candidato é confirmado lendo a tela antes de remover.

---

# FASE 4 — SEGURANÇA DOS DADOS

**4.1 `/dev/solides` acessível a qualquer usuário logado** (detalhado em 3.1). Ferramenta de
diagnóstico de credencial de integração externa não deve estar ao alcance de um `visualizador`.

**4.2 91% da auditoria não registra autor.** `audit_log`: 42.766 de 46.873 linhas sem `user_id`;
`beneficio_audit`: 2.854 de 4.187. A causa é `fn_audit_row()` depender de `auth.uid()`, que é NULL
quando a escrita vem de service-role (edge function, cron) ou RPC `SECURITY DEFINER`.
→ Passar o autor explicitamente nos caminhos de service-role, e marcar como `sistema:<nome-do-job>`
o que for legitimamente automático. Hoje não é possível responder "quem apagou estes recibos?" — e
41.816 das linhas de `audit_log` são exclusões de `recibos_emitidos`.

**4.3 Revisão de RLS não foi feita.** Todo o E2E rodou como `postgres`, fora da RLS. As políticas das
~66 tabelas restantes não foram revisadas. Uma varredura de RLS por papel (`admin`, `operador`,
`visualizador`, `suporte`) é trabalho próprio, ainda não executado.

**4.4 Token de service-role dentro do comando do cron.** Os jobs de `cron.job` carregam o
`Authorization: Bearer <service-role>` embutido no texto do comando, legível por quem consultar
`cron.job`. Avaliar uso de Vault/`current_setting` para não versionar segredo em texto.

---

# FASE 5 — RETROALIMENTAÇÃO (o sistema devolvendo o que registra)

**5.1 Tela de pendências de integridade** — destino das 7 linhas legadas da Fase 1B/1D e de qualquer
violação futura. Sem essa tela, "entrou `NOT VALID`" vira "foi esquecido".

**5.2 `audit_log`: 46.873 linhas, 2 alcançáveis.** O único leitor é `HistoricoUsuarioDrawer`, filtrado
por `record_id = <id de usuário>`. Precisa de tela de consulta com filtro por tabela, registro,
período e autor.

**5.3 Fila de reprocesso esconde item travado.** A tela carrega os 200 mais recentes e conta os erros
dentro dessa janela: o card "Erro" mostra **0** enquanto há **8** jobs travados desde 08/05.
→ Contar por consulta agregada, não pela página carregada, e permitir filtrar por status.

**5.4 865 inconsistências abertas contra 13 resolvidas**, sem resolução nenhuma desde 28/05, enquanto
a produção seguiu até 28/08. A tela existe e a permissão de update existe — falta fechamento de ciclo.

**5.5 `auditoria_findings` parado desde 17/04** com 65 achados abertos e nenhum resolvido. O módulo
inteiro está construído (2 edge functions, tela, drawer) e simplesmente não roda. Decidir: religar ou
aposentar.

**5.6 As 774 homologações indevidas de ponto** (dedup já corrigido em 30/08). Com o dado correto,
774 dos 775 registros hoje homologados iriam para `pendente_revisao`. Decisão sua, ainda pendente:
corrigir `total_horas` e devolver esses dias à conferência, ou deixar como está.

---

# ORDEM DE EXECUÇÃO

| # | Bloco | Risco | Depende de decisão sua? |
|---|---|---|---|
| 1 | Fase 0 — rede de segurança | nenhum | não |
| 2 | Fase 1A — 15 travas de risco zero | nenhum (0 violações) | não |
| 3 | Fase 1C — dia fechado (INSERT), DELETE de colaborador, `escalas_audit.action` | baixo — exige isentar o motor via `is_engine_reprocess()` | não |
| 4 | Fase 1D — corrigir `check_escala_overlap` + confirmação de virada | baixo | não |
| 5 | Fase 1B — 3 travas `NOT VALID` + tela de pendências (5.1) | baixo | não |
| 6 | Fase 3 — cards mortos e `/dev/solides` | baixo | não |
| 7 | Fase 4.2 e 4.4 — autoria e segredo do cron | médio | não |
| 8 | Fase 5.2/5.3 — leitura de auditoria e fila | baixo | não |
| 9 | Fase 2.6/2.7/2.5 — consolidar status, identidade, jornada | médio | não |
| 10 | Fase 2.1/2.2 — recibos v2 e backup | baixo | **sim** |
| 11 | Fase 2.9 — `fechada` vs `congelada` | médio | **sim** |
| 12 | Fase 2.3/2.4/2.10 — enums, datas de admissão, cliente | alto (migra dado) | **sim** |
| 13 | Fase 5.6 — 774 homologações | alto | **sim** |

Os itens 1 a 9 não dependem de nenhuma decisão e cobrem todas as travas urgentes.

---

# DECISÕES QUE SÓ VOCÊ PODE TOMAR

1. **Recibo v2** — futuro ou abandonado? Enquanto não decidir, ninguém sabe qual pilha manter.
2. **`fechada` vs `congelada`** — qual é o estado terminal? Hoje VT usa um e VA usa outro para o
   mesmo período, e isso bloqueia o cálculo seguinte do VA.
3. **`pendente_aprovacao`** — existe no enum com zero uso e a coluna `aprovado_por` existe. Passa a
   valer ou sai?
4. **As 7 linhas legadas** (5 escalas invertidas + 1 admissão operacional + 1 rescisão) — corrigir,
   anular ou manter documentadas?
5. **As 774 homologações de ponto** — devolver à conferência do DP (gera trabalho real) ou deixar?
6. **`auditoria_findings`** — religar o módulo ou aposentar?

---

# O QUE ESTE PLANO NÃO COBRE

- **A interface não foi testada de verdade.** Coesão entre telas, fluxo de formulário e botão
  redundante exigem dirigir o navegador autenticado. Não tenho credencial, e criar usuário de auth em
  produção dá acesso a dados de 99 pessoas reais. A Fase 3.3 é método, não resultado.
- **RLS não foi exercitada** (Fase 4.3). Nada aqui prova o que um `operador` consegue ou não fazer.
- **As RPCs de negócio não foram executadas end-to-end** — abortam sem sessão autenticada. Suas 105
  validações internas foram lidas, não testadas.
- **O motor `calcular-beneficios` não foi executado.** Rodá-lo grava em competência real.

---
---

# FASE 1E — O DESTINO DA PESSOA (inserir ANTES da 1B)

Adicionada em 2026-08-30 após investigação do problema operacional relatado: colaborador some ou
cliente pede a troca; a operação precisa encerrar a escala para cobrir o posto; a pessoa não está
desligada; ela fica sem escala e sem status de desligamento.

## Por que esta fase vem antes da 1B

Todas as outras travas impedem **valor inválido** entrar. Esta impede **estado inválido** ser criado.
É a única do plano que fecha uma porta de produção de dado ruim, em vez de barrar dado ruim na porta.

## Diagnóstico em uma frase

**O sistema pergunta o que acontece com a VAGA e nunca o que acontece com a PESSOA.**

`criar_movimentacao_escala` recebe `p_destino_vaga` (`sem_reposicao | abrir_contratacao |
remanejamento`). `movimentacoes_escala` tem coluna `destino_vaga` e **não tem `destino_colaborador`**.
O `EncerrarEscalaWizard` faz quatro perguntas — último dia, motivo, tipo, destino da vaga — e a quinta,
condicional, é "quem assume o posto", com a lista filtrada para *excluir* quem sai. O limbo não é
bug: é a resposta que nunca foi pedida, sem lugar no modelo para ser guardada.

## Evidência de que já acontece

| fato | medição |
|---|---|
| Matrícula 05738 (PAMELA M. RODRIGUES) | escala encerrou 2026-04-13, rescisão 2026-05-07 → **24 dias em limbo** |
| Matrícula 07382 (VALERIA LEMOS REIS) | `inativo` **sem `rescisao_data`**, escala encerrou 2026-08-26 |
| Movimentações no ramo que não gera nada | **8 de 15** são `alteracao_operacional` + `sem_reposicao`; **2 delas com motivo literal `PEDIDO DO CLIENTE`** |
| Desligamentos efetivados sem o fato correspondente | **4 de 4** com `rescisao_data` NULL; **1 dessas pessoas ainda está `ativo`** |
| Escalas encerradas fora da RPC | **70** escalas `encerrado` sem nenhuma linha em `movimentacoes_escala` |
| Motivo "abandono" | **não existe** nas 11 opções de `motivos_alteracao`; o mais honesto é `OUTROS` |

O caminho "certo" também falha: quando o operador marca `desligamento`, a RPC cria uma
`tarefas_areas` com um **texto** ("Gerar documento rescisório — Fulano"). Ela não escreve
`rescisao_data`, e só essa coluna dispara `auto_status_on_rescisao` para virar `inativo`. Se ninguém
executar a tarefa à mão, a pessoa permanece `ativo` para sempre.

## Decisões já tomadas

1. **Bloquear** o encerramento da última escala ativa até o destino da pessoa ser declarado.
2. **Vínculo continua `ativo`**; o estado vive em `colaboradores_sem_escala_justificativa`.
3. **Prazo de 30 dias** antes de virar decisão obrigatória.

## Por que NÃO reusar o status `afastado`

Levantado e descartado com base em evidência:
- `afastado` tem **0 linhas** e só é alcançável automaticamente por `afastamento_tipo IN
  ('sal_maternidade','servico_militar')` — tipos que **nunca foram cadastrados** na história da base.
- `status_pre_afastamento` é **circuito fechado**: 4 funções escrevem e leem entre si, **zero**
  consumidores externos, **0 linhas** preenchidas. A condição de captura exige status
  `ativo_free`/`ativo_operacional`, e `ativo_operacional` tem 0 linhas porque o `ColaboradorForm`
  converte silenciosamente para `ativo` ao carregar.
- Marcar alguém `afastado` não é um estado tratado: é apenas *ausência* das listas de inclusão do
  cálculo e do alerta. Não há motivo, período obrigatório nem trilha.

Reusar essa peça seria empilhar sobre um mecanismo morto. O estado fica na tabela de justificativa.

## 1E.1 — A trava (mecanismo)

**Não pode ser trigger comum, e não pode ser só no wizard.** São quatro rotas que encerram escala:
o wizard (via RPC), o `EscalaForm` fora do modo replace (que encerra **em silêncio**, sem passar pela
RPC — origem provável das 70 órfãs), `substituir_escala_atomico`, e edição direta.

**Mecanismo correto:** `CREATE CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` em `escalas`,
avaliando no `COMMIT`. Razões:
- Cobre **todas** as rotas, porque vive no banco e não na tela.
- Não dá falso positivo em `substituir_escala_atomico`, que encerra a antiga e cria a nova na mesma
  transação — no instante intermediário o colaborador tem zero escalas ativas, e um trigger comum
  bloquearia uma substituição legítima.

**Atenção:** o banco **não tem hoje nenhum trigger postergado** (verificado: zero linhas com
`tgdeferrable` ou `tgconstraint <> 0`). É padrão novo no projeto e precisa de teste dedicado nas
quatro rotas, em transação revertida, antes de ir para produção.

**Regra:** ao `COMMIT`, se um colaborador com status operacional ficou sem nenhuma escala
`ativo`/`futuro` e não possui justificativa vigente nem rescisão registrada, a transação é recusada
com mensagem que ensina o caminho.

## 1E.2 — O modelo (onde a resposta é guardada)

- **`movimentacoes_escala` ganha `destino_colaborador`** — a coluna que falta. Valores propostos:
  `desaparecido | aguardando_realocacao | desligamento | afastamento | ferias`.
- **`motivos_alteracao` ganha `ABANDONO`** (e provavelmente `TROCA A PEDIDO DO CLIENTE`). É tabela de
  cadastro, não código — inclusão barata.
- **`colaboradores_sem_escala_justificativa.motivo` ganha um enum companheiro.** Enum para a máquina
  decidir prazo e alerta; o texto livre continua para a pessoa explicar. Resolve de passagem o achado
  "campo de texto livre onde existe enum disponível".
- **Roteamento, não duplicação:** `desligamento`, `afastamento` e `ferias` **não** criam justificativa
  — encaminham para os fluxos que já existem. Só `desaparecido` e `aguardando_realocacao` produzem
  estado novo. Uma pergunta, cinco destinos, zero tabelas novas.

## 1E.3 — A porta (sem isto, a trava vira parede)

A peça reaproveitada **existe e é inoperável hoje**:

- O **único `INSERT`** da tabela em todo o sistema está em `src/components/AlertasDirecionados.tsx`,
  um modal global que **aparece sozinho**. Não há rota, menu ou botão em lugar nenhum.
- Ele só aparece para **3 UUIDs cravados no código** da edge function
  (`const DESTINATARIOS = [...] // Dargiele, Glaucia, Vera`). Quem não está na lista **nunca**
  consegue justificar, mesmo sendo admin.
- Políticas de `UPDATE` e `DELETE` existem na migração e **nenhuma linha de código as chama**. Não há
  listagem, edição, renovação nem histórico. Há um registro `"teste teste"` em produção que nenhuma
  tela consegue exibir ou remover. Não há `UNIQUE`: a matrícula 07161 tem duas justificativas para a
  mesma competência.
- `valido_ate_competencia` nasce com default no dia 1º do **mês corrente** — a justificativa morre na
  virada do mês. Para quem some dia 28, são dois dias. **Não é o prazo de 30 dias decidido.**
- **Ninguém avisa que venceu.** Não há renovação, só re-justificação: no mês seguinte o operador
  digita o motivo inteiro de novo, e a linha antiga fica órfã.
- O **motivo nunca é exibido** no pré-cálculo (a consulta traz só `colaborador_id, id`). Quem calcula
  vê "justificado" e nunca sabe por quê.

**Entregável:** tela real de justificativa — registrar, listar, editar, renovar, encerrar, com
histórico — alcançável **a partir do ponto onde o operador está travado** (hoje, no
`PreCheckCalculoDialog`, o botão de calcular não é desabilitado: ele **não existe no DOM**, e o texto
de orientação manda "cadastrar escalas faltantes" sem nunca mencionar justificar).

## 1E.4 — O alinhamento (senão a trava cria casos insolúveis)

Existem **dois detectores de "sem escala" que não concordam**:

| | `alertar-sem-escala` (cria o alerta) | `preCheckCalculo` (trava o cálculo) |
|---|---|---|
| status | `ativo, ativo_operacional, ativo_free` | `ativo, ativo_free` |
| escalas | `ativo, futuro` — sem janela de data | `ativo, futuro, encerrado` — com interseção da quinzena |
| competência de referência | mês de hoje | competência sendo calculada |

Consequência: **quem o pré-check acusa e o alerta não acusa não tem como ser justificado por interface
nenhuma** — trava permanente, por construção. Unificar os dois critérios numa única função é
pré-requisito da trava, não melhoria opcional.

## 1E.5 — Bugs vizinhos que aparecem de brinde

- **`substituir_escala_atomico` esquece quem sai.** A última linha usa
  `PERFORM recalcular_lotacao_colaborador(COALESCE(v_nova.colaborador_id, v_e.colaborador_id))`, que
  resolve para o colaborador **novo**. Quando a pessoa muda, quem saiu nunca tem a lotação recalculada
  e fica com as horas da escala antiga penduradas em `colaboradores_lotacao`. Compare com
  `criar_movimentacao_escala`, que chama para os dois lados.
- **A tarefa do DP não cria o fato.** Ver evidência acima: 4 de 4 desligamentos efetivados sem
  `rescisao_data`.
- **Duas telas brigando no `ColaboradorForm`.** O Select de status escreve `colaboradores.status`
  direto; a aba "Rescisão/Afastamentos" faz upsert que dispara `trg_sync_status_from_ra`, que
  **sobrescreve** o que o Select escreveu. Ambos no mesmo submit.
- **`ativo_operacional` é rebaixado em silêncio:**
  `setStatus(colab.status === "ativo_operacional" ? "ativo" : ...)`. Abrir e salvar converte. A edge
  function e a `ColaboradoresList` ainda esperam esse status.
- **`afastamento_tipo = 'desligado'`** tem 22 linhas, **todas com `rescisao_data`**. O operador usa o
  campo de *tipo de afastamento* para dizer "isto é uma rescisão" — o mesmo conceito escrito em quatro
  camadas. Nenhuma função do banco lê esse valor. Candidato a remoção na Fase 2.
- **Código morto em produção:** o ramo `revisao_escalas_colaborador` de `AlertasDirecionados.tsx` tem
  datas de julho/2026 cravadas e um botão "Encerrar selecionadas em 14/07/2026". Nenhum código cria
  esse tipo de alerta. Entra na Fase 3.

## 1E.6 — Os casos existentes

As duas pessoas hoje em desacordo (05738 e 07382) e as 70 escalas encerradas sem movimentação **não
são corrigidas automaticamente**. Vão para a tela de pendências (item 5.1), com o estado descrito, e
uma pessoa decide. Respeita o princípio de não mexer em dado inserido pelo usuário.

## Critério de aceite da Fase 1E

1. Bateria E2E em transação revertida cobrindo as **quatro** rotas de encerramento: nenhuma consegue
   deixar colaborador sem escala e sem destino declarado.
2. `substituir_escala_atomico` continua funcionando (a trava postergada não pode dar falso positivo).
3. O operador travado no pré-cálculo consegue resolver **sem** depender de pop-up e sem estar numa
   lista cravada em código.
4. Os dois detectores de "sem escala" passam a usar a mesma função.
5. Nenhuma linha histórica alterada.

## Decisões pendentes desta fase

- **Os 3 UUIDs cravados na edge function** — substituir por papel (`admin`/`operador`) ou por tabela
  de destinatários configurável? Recomendo papel: é o mecanismo que o projeto já usa em todo o RLS.
- **Os valores de `destino_colaborador`** — a lista proposta cobre a operação de vocês ou falta caso?
- **O registro `"teste teste"` e a justificativa duplicada da 07161** — remover ou manter como
  histórico?
