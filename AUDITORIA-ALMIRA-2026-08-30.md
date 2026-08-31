# AUDITORIA GERAL DO SISTEMA ALMIRA — RETRATO DO QUE EXISTE
**Data:** 2026-08-30 · **Modo:** somente leitura · **Nada foi alterado no sistema.**

---

## 0. Identificação do alvo e método

Antes de qualquer achado, o registro de **onde eu olhei**, porque a rodada anterior foi invalidada
por citar arquivos inexistentes.

**O repositório aberto nesta sessão (`/home/user/avior-LP`) NÃO é o ALMIRA.** Ele contém apenas
`index.html` + `assets/` — a landing page da AVIOR. O ALMIRA foi localizado assim:

| Passo | Resultado |
|---|---|
| `mcp__SUPABASE__list_projects` | Nenhum projeto chamado "Almira" |
| `list_projects` em 9 workspaces Lovable, query `almira` | Zero resultados por nome |
| Varredura dos 95 projetos do workspace `Juliana's Lovable` | Nenhum "Almira" no nome |
| `list_files` no projeto `gestao-foco-rh` | **`src/components/brand/AlmiraLogo.tsx`** ← confirmação |

**ALMIRA = projeto Lovable `gestao-foco-rh` ("Foco RH & DP")**
`project_id: 7ec3c535-767b-4c7c-bae3-705b8dee1492` · `https://gestao-foco-rh.lovable.app`
Banco: Supabase via Lovable Cloud — 99 objetos em `public` (77 tabelas, 22 views), 47 CHECK
constraints, 36 enums, 88 triggers, 47 edge functions.

### Sobre o formato do endereço (leia antes de cobrar `arquivo:linha`)

O código do ALMIRA vive dentro do Lovable. **Não existe espelho no GitHub** (`list_repos` retornou
9 repositórios, nenhum é o `gestao-foco-rh`), logo não há checkout local para `grep -n`.

- Para **3 arquivos grandes**, a API do Lovable gravou o conteúdo em disco preservando o arquivo
  íntegro. Nesses casos os números de linha abaixo são **reais e conferidos com `grep -n`**:
  `supabase/functions/calcular-beneficios/index.ts` (3.226 linhas),
  `src/pages/beneficios/CalculoQuinzenal.tsx` (3.582 linhas),
  `src/pages/colaboradores/ColaboradorForm.tsx` (1.847 linhas).
- Para os demais arquivos, a API devolve o texto **sem numeração**. Em vez de estimar um número de
  linha (que seria exatamente o erro da rodada anterior), o endereço é **arquivo + trecho literal de
  código**, localizável por busca exata. Onde uso essa forma, escrevo `arquivo → trecho`.

Objetos de banco são citados pelo nome exato.

---

# EIXO 1 — MAU FUNCIONAMENTO E FALHA SILENCIOSA

### [EIXO 1] [CRÍTICO] Importação de ponto duplica o par de marcações e dobra as horas do dia
**Endereço:** `supabase/functions/sincronizar-ponto/index.ts` → `if (sortedPunches.length >= 2) { entrada_2 = epochToTime(sortedPunches[1].dateIn); saida_2 = epochToTime(sortedPunches[1].dateOut); }` e a função `calcTotalHoras`. Tabela `ponto_registros`.
**O que acontece:** quando a API Solides devolve duas marcações idênticas para o mesmo dia, o código
não deduplica: joga a primeira em `entrada_1/saida_1`, a segunda (idêntica) em `entrada_2/saida_2`, e
`calcTotalHoras` soma os dois intervalos, dobrando `total_horas`.
**Como verifiquei:** leitura do arquivo + SQL no banco de produção:
```sql
select status_homologacao, count(*),
       round(avg(total_horas),2) gravada,
       round(avg(extract(epoch from (saida_1-entrada_1))/3600),2) real
from ponto_registros
where entrada_1=entrada_2 and saida_1=saida_2 and entrada_2 is not null
group by 1;
-- homologado       | 776 | 8.50 | 4.25
-- pendente_revisao |  34 | 6.23 | 3.12
```
810 registros afetados entre 2026-06-01 e 2026-08-27. Amostra: 06:55→11:00 (4h05) gravado como
8.17h; 07:57→13:16 (5h19) gravado como 10.63h. A média gravada é **exatamente o dobro** da real.
**Consequência observável:** 776 desses registros passaram pela auto-homologação (`horasNaFaixa =
totalHoras >= 4 && totalHoras <= 12` — o valor dobrado cai dentro da faixa e valida). Esses dias
entram como homologados na efetividade e na base que alimenta cálculo de benefício e relatórios de
folha, com o dobro das horas. Nenhuma tela sinaliza a duplicidade.

### [EIXO 1] [CRÍTICO] Pré-check de benefícios continua rodando após falhar a consulta principal e libera o cálculo
**Endereço:** `src/pages/beneficios/preCheckCalculo.ts` → `if (errColabs) console.error("[preCheck] err colabs", errColabs);`
**O que acontece:** o erro da consulta de colaboradores é apenas logado no console; a execução segue
com `const ativos = (colabs || []) as any[]`, cai em `if (colabIds.length === 0) return vazio()` e o
pré-check devolve `temImpeditivo: false` — ou seja, "nenhum impedimento".
**Como verifiquei:** leitura integral do arquivo. O próprio arquivo documenta a doutrina oposta
poucas linhas acima, em `fetchAllPages`: *"FAIL-SAFE: se qualquer página falhar, LANÇA com contexto e
aborta o pré-check inteiro. Nunca devolver dados parciais — parcial libera cálculo ou gera alerta
incorreto silenciosamente."* A regra existe no arquivo e não é aplicada na consulta mais importante dele.
**Consequência observável:** numa falha de rede/RLS na consulta de colaboradores, o operador vê o
pré-check passar limpo e autoriza o cálculo da quinzena sobre uma base vazia.

### [EIXO 1] [ALTO] Pré-check descarta o erro das rescisões e o da quinzena anterior
**Endereço:** `src/pages/beneficios/preCheckCalculo.ts` → `const { data: rescs } = await supabase.from("colaboradores_rescisao_afastamentos")...` e `const { data } = await supabase.from("beneficio_calculo_quinzenal").select("status")...`
**O que acontece:** nas duas consultas o `error` sequer é desestruturado.
**Como verifiquei:** leitura do arquivo.
**Consequência observável:** (a) se as rescisões não carregam, `rescMap` fica vazio, `janelaElegivel`
recebe `rescisao = null` e **colaboradores já rescindidos ganham janela cheia de benefício**; (b) se
a consulta da quinzena anterior falha, `data` é null e a trava de "quinzena anterior não fechada"
simplesmente não dispara. Nos dois casos a tela não muda de aparência.

### [EIXO 1] [ALTO] Importação de colaboradores ignora o erro de 7 dos 8 inserts e conta a linha como importada
**Endereço:** `src/pages/colaboradores/ColaboradoresUpload.tsx` → função `importRow`
**O que acontece:** só o primeiro insert é checado (`if (colabErr || !colabData) throw colabErr;`).
Os sete seguintes — `colaboradores_documentos`, `colaboradores_dados_pessoais`,
`colaboradores_dados_cadastrais`, `colaboradores_remuneracao`, `colaboradores_dados_bancarios`,
`colaboradores_lotacao`, `colaboradores_rescisao_afastamentos`, `colaboradores_ferias` — são
aguardados com `await` mas nunca têm o `error` inspecionado. Como não lançam, `imported[cat]++`
executa e a linha é contada como sucesso.
**Como verifiquei:** leitura do arquivo. Testei se o dano já se materializou:
```sql
select (select count(*) from colaboradores c where not exists
        (select 1 from colaboradores_documentos d where d.colaborador_id=c.id)) sem_documentos, ...
-- todos os contadores = 0, sobre 99 colaboradores
```
**Consequência observável:** hoje **não há órfãos** — o defeito é latente, não materializado. Mas o
caminho é real: `colaboradores_documentos` tem CHECK `cpf_valido = validate_cpf(cpf)` e
`validate_cpf('')` retorna **false**; o importador trata CPF ausente como aviso, não erro
(`warnings.push("CPF ausente (pendência)")`), então uma planilha sem CPF gera colaborador sem
documentos e o relatório final exibe "Importação Concluída" com o registro no verde.

### [EIXO 1] [ALTO] A edge de cálculo detecta que não conseguiu atualizar o cabeçalho, devolve o erro, e o front joga fora
**Endereço:** `supabase/functions/calcular-beneficios/index.ts:154-157` (grava `headerUpdateError`) e `:3196` (devolve `header_update_error` no payload); consumidor `src/pages/beneficios/CalculoQuinzenal.tsx`
**O que acontece:** a falha ao atualizar `beneficio_calculo_quinzenal` (data_inicio, data_fim,
data_corte) é capturada em `headerUpdateError` e devolvida — mas na mesma resposta com
`ok: true` e `message: "Cálculo realizado com sucesso"`.
**Como verifiquei:**
```
$ grep -n "header_update_error" calcular-beneficios.index.ts   → 3196
$ grep -n "header_update_error\|guards_bloqueados" CalculoQuinzenal.tsx   → (vazio)
```
O front lê `efetividade_incompleta`, `dias_sem_efetividade`, `colabs_sem_escala`, `pendencias`,
`descartados_por_motivo` (linhas 511-553) — mas **nunca** `header_update_error` nem
`guards_bloqueados`. Termina em `toast.success(msg)` (`CalculoQuinzenal.tsx:555`).
**Consequência observável:** o operador lê "Cálculo concluído: N linhas" enquanto o período e a data
de corte gravados no cabeçalho continuam os antigos.

### [EIXO 1] [MÉDIO] 291 importações de ponto marcadas "sucesso" escondem o detalhe do que foi descartado
**Endereço:** `src/pages/ponto/PontoImportacaoLog.tsx` → `const temErros = (log.erros ?? 0) > 0;` e `const itens = temErros ? parseDetalhes(log.detalhes_erro) : null;`
**O que acontece:** `sincronizar-ponto` grava em `detalhes_erro` também os descartes silenciosos
(`ignoradosFantasma`, `ignoradosAfastamento`, `ignoradosFerias`, `ignoradosRescisao`) mesmo quando
`erros = 0` e `status = 'sucesso'`. A tela só monta o botão de expandir quando `erros > 0`.
**Como verifiquei:**
```sql
select count(*) from ponto_importacao_log where erros = 0 and detalhes_erro is not null;  -- 291
```
**Consequência observável:** em 291 importações o operador vê a badge verde "sucesso" sem nenhuma
indicação de que marcações foram descartadas, e o detalhe existe no banco mas é inalcançável pela tela.

### [EIXO 1] [MÉDIO] Histórico do usuário descarta o erro: RLS negado aparece como "Nenhum evento registrado"
**Endereço:** `src/pages/usuarios/HistoricoUsuarioDrawer.tsx` → `.then(({ data }) => { setRows((data as LogRow[]) ?? []); setLoading(false); });`
**O que acontece:** o callback desestrutura só `data`. A policy de leitura de `audit_log` é
`Admins can view audit logs` → `has_role(auth.uid(), 'admin')`.
**Como verifiquei:** leitura do arquivo + consulta a `pg_policy` sobre `audit_log`.
**Consequência observável:** um usuário `operador` que abra o drawer recebe negação do RLS e lê
"Nenhum evento registrado." — indistinguível de um histórico legitimamente vazio.

### [EIXO 1] [MÉDIO] Importação de escalas não checa o erro ao gravar a auditoria
**Endereço:** `src/pages/escalas/EscalasUpload.tsx` → `await supabase.from("escalas_audit").insert({ escala_id: data.id, action: "importado", ... });`
**O que acontece:** insert sem `error` inspecionado, logo depois do insert da escala (esse sim
checado com `if (error) throw error`). `success++` roda de qualquer forma.
**Como verifiquei:** leitura do arquivo.
**Consequência observável:** escala importada sem rastro de auditoria, contada como sucesso.

### [EIXO 1] [BAIXO] `isPhantomRecord` usa o minuto errado e nunca compara o que pretende comparar
**Endereço:** `supabase/functions/sincronizar-ponto/index.ts` → `const diffMin = ((sh * 60 + sm) - (eh * 60 + sm));`
**O que acontece:** `e1` é desestruturado como `const [eh] = e1.split(":")` (só a hora), e `sm` vem de
`s1`. Como `sm` aparece nos dois lados da subtração, ele se cancela: `diffMin = (sh - eh) * 60`. Os
minutos da entrada nunca entram na conta.
**Como verifiquei:** leitura do arquivo.
**Consequência observável:** o segundo critério de detecção de marcação-fantasma é inerte. Efeito
prático limitado porque a condição ainda exige `totalHoras > 23`.

### [EIXO 1] [BAIXO] "CPF ausente (pendência)" é calculado e nunca chega ao usuário
**Endereço:** `src/pages/colaboradores/ColaboradoresUpload.tsx` → `const warnings: string[] = [];` dentro de `validateRow`, e `warnings.push("CPF ausente (pendência)")`
**O que acontece:** `warnings` é populado mas não é devolvido no objeto `ParsedRow` (o retorno só
carrega `errors` e `valid`). A tabela de preview não tem coluna para ele.
**Como verifiquei:** leitura do arquivo — `warnings` não aparece no `return` de `validateRow`.
**Consequência observável:** a planilha importa linhas sem CPF e o operador nunca vê o aviso.

---

# EIXO 2 — EMPILHAMENTO DE FUNCIONALIDADE

### [EIXO 2] [ALTO] A fórmula de jornada existe duas vezes — no front e na edge — e as cópias já divergiram
**Endereço:** `src/lib/beneficios/jornadaEscala.ts` (`getHoursForDay`, `getHoursForDate`, `is12x36WorkDay`) ⟷ `supabase/functions/calcular-beneficios/index.ts:770` (`is12x36WorkDay`), `:778` (`getHoursForDay`), `:803` (`getHoursForDate`)
**O que acontece:** o mesmo cálculo de horas previstas está implementado nos dois lados. O cabeçalho
do arquivo do front assume a duplicação: *"funções PURAS que replicam a semântica de `getHoursForDate`
da edge function `calcular-beneficios`"*.
**Como verifiquei:** `grep -n "function getHoursFor" ` no arquivo em disco (linhas 778 e 803) e
comparação linha a linha com o arquivo do front. **Duas divergências já existem:**

| | front `jornadaEscala.ts` | edge `index.ts:784` |
|---|---|---|
| minutos | `return h + (m \|\| 0) / 60;` | `return h + m / 60;` |
| intervalo | `const intv = Number(escala.intervalo \|\| 0);` | `const intv = escala.intervalo \|\| 0;` |

O front recebeu guardas (`m || 0`, `Number(...)`) que a edge não recebeu.
**Consequência observável:** o pré-check e o motor financeiro podem projetar números diferentes para
a mesma escala. O pré-check libera, o cálculo entrega outro valor — e nada aponta a divergência.

### [EIXO 2] [ALTO] Existe uma pilha completa de "recibo v2" construída em paralelo à v1 e sem uso nenhum
**Endereço:** tabelas `recibos_emitidos` e `recibos_emitidos_v2`; views `vw_recibo_consolidado` e `vw_recibo_consolidado_v2`; edge functions `gerar-recibo-beneficio/` e `gerar-recibo-beneficio-v2/`; `src/lib/beneficios/statusEmissaoV2.ts`; RPC `registrar_recibos_v2_lote`; trigger `trg_recibos_v2_imutavel`; testes `src/__tests__/recibo-v2-fechamento.test.ts` e `recibo-v2-legado-status.test.ts`
**O que acontece:** dois caminhos completos para emitir o mesmo recibo de benefício. O v2 tem tabela,
view, edge function, RPC de lote, trigger de imutabilidade, CHECK próprio
(`recibos_emitidos_v2_tipo_beneficio_check` aceita `vt|va`) e dois arquivos de teste.
**Como verifiquei:**
```sql
select 'recibos_emitidos', count(*), max(created_at) from recibos_emitidos      -- 634, 2026-08-28
union all select 'recibos_emitidos_v2', count(*), max(created_at) from recibos_emitidos_v2; -- 0, null
```
**Consequência observável:** a v1 é a que roda (634 recibos, último em 28/08). A v2 está com **zero
linhas**. Toda manutenção futura precisa decidir, sem critério escrito, qual das duas alterar.

### [EIXO 2] [MÉDIO] O parse de erro de edge function tem um helper robusto e uma cópia pobre inline
**Endereço:** `src/lib/beneficios/parseFunctionError.ts` (helper) ⟷ `src/pages/colaboradores/ColaboradorForm.tsx:936-953` (cópia inline)
**O que acontece:** o helper tenta **cinco** formas de extrair o corpo do erro (objeto plano,
`clone().json()`, `json()`, `text()`+parse, `body` string) e extrai `bloqueios[]`. A cópia inline em
`ColaboradorForm.tsx` tenta **duas** (`clone().json()`, depois `text()`), não extrai `bloqueios`, e
o arquivo **não importa** o helper.
**Como verifiquei:** leitura dos dois; `grep -n "parseFunctionError" ColaboradorForm.tsx` → vazio.
O comentário de topo do helper descreve exatamente a falha que a cópia inline reproduz: *"`context.clone().json()` falhar silenciosamente e o dialog exibir só a mensagem genérica"*.
**Consequência observável:** o mesmo erro de edge function aparece detalhado na tela de benefícios e
genérico ("Edge Function returned a non-2xx status code") na geração de documentos de admissão.

### [EIXO 2] [MÉDIO] A derivação do status da escala existe como RPC no banco e reimplementada no importador — com regra a menos
**Endereço:** função `public.calcular_status_escala(p_inicio date, p_fim date)` ⟷ `src/pages/escalas/EscalasUpload.tsx` → `status: first.dataInicio > new Date().toISOString().split("T")[0] ? "futuro" : "ativo",`
**O que acontece:** a RPC canônica cobre três casos:
```sql
WHEN p_inicio > CURRENT_DATE THEN 'futuro'
WHEN p_fim IS NOT NULL AND p_fim < CURRENT_DATE THEN 'encerrado'
ELSE 'ativo'
```
O importador cobre dois e **ignora `data_fim`**.
**Como verifiquei:** `pg_get_functiondef` da RPC + leitura do importador.
**Consequência observável:** uma escala importada com `data_fim` já passada entra como **`ativo`** em
vez de `encerrado`, e passa a contar como vínculo vigente nas telas e no motor de benefícios.

### [EIXO 2] [MÉDIO] Identificar "qual colaborador é este" tem duas estratégias diferentes
**Endereço:** `supabase/functions/sincronizar-ponto/index.ts` (CPF → `pin_externo` → `matricula` → nome normalizado com match por subconjunto de tokens, e grava `pin_externo` de volta) ⟷ `src/pages/escalas/EscalasUpload.tsx` (`matricula` exata → `nome_completo.toLowerCase()` exato)
**O que acontece:** dois algoritmos de resolução de identidade para a mesma entidade. O do ponto
normaliza acentos, aceita subconjunto de tokens e faz auto-aprendizado do PIN; o de escalas exige
igualdade exata do nome em minúsculas.
**Como verifiquei:** leitura dos dois arquivos.
**Consequência observável:** o mesmo nome de planilha casa no ponto e falha na escala, ou vice-versa,
sem que a diferença seja explicada em nenhuma tela.

### [EIXO 2] [MÉDIO] Quatro telas distintas se chamam "auditoria"
**Endereço:** `src/pages/auditoria/RegistrosAuditoria.tsx` (`/auditoria/registros`) · `src/pages/efetividade/EfetividadeAuditoria.tsx` (`/efetividade/auditoria`) · `src/pages/beneficios/AuditoriaIA.tsx` (`/beneficios?modulo=auditoria`) · `src/pages/beneficios/InconsistenciasLog.tsx`
**O que acontece:** quatro superfícies com o mesmo rótulo cobrindo fontes diferentes
(`beneficio_audit`+`efetividade_audit`; efetividade; `auditoria_findings`; `beneficio_inconsistencia_log`).
Na sidebar (`src/components/AppSidebar.tsx`), "Auditoria" é um subgrupo dentro de **Administração**
(`AUDITORIA_CHILDREN`, 6 itens) enquanto "Auditoria IA" fica dentro de **Benefícios**
(`BENEFICIOS_CHILDREN`).
**Como verifiquei:** leitura de `AppSidebar.tsx`, `App.tsx` (tabela de rotas) e `RegistrosAuditoria.tsx`.
**Consequência observável:** para saber "o que aconteceu com este colaborador" o operador precisa
visitar quatro telas em dois ramos diferentes do menu, sem que nenhuma indique a existência das outras.

### [EIXO 2] [BAIXO] Tabela de backup de 40 mil linhas vive no schema `public`
**Endereço:** tabela `public.recibos_emitidos_bkp_20260720`
**O que acontece:** 40.134 linhas de um backup de 20/07/2026 permanecem no schema de produção.
**Como verifiquei:** `select count(*) from recibos_emitidos_bkp_20260720;` → 40134.
**Consequência observável:** aparece na lista de tabelas ao lado das tabelas vivas; nada no nome
indica se ainda é necessária.

---

# EIXO 3 — AUSÊNCIA DE TRAVA

> **Nota de calibragem:** o achado anterior *"ausência total de CHECK constraints no schema public"*
> está **CORRIGIDO**. Hoje existem **47 CHECK constraints**. Os achados abaixo são as lacunas
> que sobraram, cada uma conferida nas cinco camadas.

### [EIXO 3] [ALTO] `rescisao_data` pode ser anterior à `data_admissao` — e já é, em um caso
**Endereço:** `colaboradores_rescisao_afastamentos.rescisao_data` × `colaboradores.data_admissao`
**O que acontece:** nada impede rescindir alguém antes de admitir.
**Como verifiquei:**
```sql
select count(*) from colaboradores_rescisao_afastamentos ra
join colaboradores c on c.id = ra.colaborador_id
where ra.rescisao_data is not null and ra.rescisao_data < c.data_admissao;   -- 1
```
**Camadas onde procurei antes de concluir ausência:**
1. **CHECK no banco** — impossível (colunas em tabelas distintas); nenhum CHECK equivalente nas 47 existentes.
2. **Trigger** — os 6 triggers de `colaboradores_rescisao_afastamentos` (`trg_audit_row`,
   `trg_encerrar_escalas_pos_rescisao`, `trg_enqueue_efetividade_from_rescisao`,
   `trg_enqueue_efetividade_from_rescisao_upd`, `trg_sync_status_from_ra`,
   `update_colaboradores_rescisao_updated_at`) foram listados via `pg_get_triggerdef`; nenhum compara as datas.
3. **RLS** — as policies da tabela controlam apenas papel, não valor.
4. **Validação de formulário** — `src/pages/colaboradores/ColaboradorForm.tsx`: as validações de
   submit estão nas linhas 556-590 (CPF, matrícula, nome, presença de `dataAdmissao`, série da CTPS,
   dados bancários, `validarCadastroNovo`, `validarExperienciaCLT`, campos de lotação). Nenhuma
   compara `rescisaoDataStr` com `dataAdmissao`. `grep -n "rescisao_data"` → só a leitura (528) e a
   escrita (740).
5. **Importador em lote** — `ColaboradoresUpload.tsx` → `if (dbStatus === "inativo" && r.data_rescisao) { rescisaoData.rescisao_data = r.data_rescisao; }`, sem comparação.
6. **Edge function / pré-check** — `preCheckCalculo.ts` apenas *consome* a data em `janelaElegivel`; não a valida.

**Consequência observável:** `janelaElegivel(periodo, admissao, rescisao)` retorna `null` quando
`inicio > fim`, então esse colaborador é **silenciosamente excluído** de toda quinzena de benefício,
sem aparecer em nenhuma lista de pendência.

### [EIXO 3] [ALTO] A trava de datas da escala existe mas nunca foi validada, e 5 linhas seguem violando
**Endereço:** constraint `escalas_data_fim_apos_inicio` na tabela `escalas`
**O que acontece:** a constraint foi criada como **`NOT VALID`**:
```
CHECK (((data_fim IS NULL) OR (data_fim >= data_inicio))) NOT VALID
```
`NOT VALID` bloqueia inserts/updates novos, mas **dispensa a verificação das linhas que já existiam**.
Elas nunca foram limpas.
**Como verifiquei:**
```sql
select id, data_inicio, data_fim, status from escalas where data_fim < data_inicio;  -- 5 linhas
-- pior caso: data_inicio 2026-04-01 → data_fim 2026-01-13 (78 dias invertidos), status 'encerrado'
```
E a auditoria mostra que **já houve uma tentativa de correção que ficou pela metade**:
```sql
select action, count(*) from escalas_audit group by 1;
-- correcao_anomalia_data_fim_menor_data_inicio | 3   (última em 2026-05-06)
```
**Camadas onde procurei:** CHECK (existe, mas `NOT VALID`); trigger `check_escala_overlap_trigger` —
li o `prosrc` completo: valida **apenas sobreposição de horários entre escalas**, nunca a ordem
data_fim/data_inicio; `calculate_escala_hours` só calcula horas; RLS não trata valor; formulário
`EscalaForm.tsx` (não lido — ver NÃO VERIFICADO); importador `EscalasUpload.tsx` não compara as datas
(a constraint é que barraria).
**Consequência observável:** 3 linhas foram corrigidas em maio, 5 continuam quebradas e são lidas
normalmente pelo motor de efetividade e pelas telas de histórico. Um
`ALTER TABLE ... VALIDATE CONSTRAINT` hoje falharia.

### [EIXO 3] [ALTO] `data_inicio_operacional` pode ser anterior à admissão — e é, com efeito direto no benefício
**Endereço:** `colaboradores.data_inicio_operacional` × `colaboradores.data_admissao`
**O que acontece:** sem nenhuma trava de ordem entre as duas.
**Como verifiquei:**
```sql
select matricula, nome_completo, data_admissao, data_inicio_operacional
from colaboradores where data_inicio_operacional < data_admissao;
-- 09490 | MARLUZA COSTA DE BRITTO | 2026-05-29 | 2026-05-18   (11 dias antes)
```
**Camadas onde procurei:** nenhum dos 47 CHECKs cobre o par; os 3 triggers de `colaboradores`
(`trg_audit_row`, `trg_normalizar_colaboradores_texto`, `update_colaboradores_updated_at`) não
comparam datas; RLS não trata valor; `ColaboradorForm.tsx:597` faz apenas
`const dataInicioOpFinal = dataInicioOperacional || dataAdmissao;` (default, não validação);
`ColaboradoresUpload.tsx` sequer preenche a coluna.
**Consequência observável:** `preCheckCalculo.ts` usa
`const admissao = c.data_inicio_operacional || c.data_admissao || null;` — a coluna operacional tem
**precedência**. Essa colaboradora recebe 11 dias de elegibilidade a benefício **antes da data de
admissão** dela.

### [EIXO 3] [MÉDIO] Hora de fim menor que hora de início é aceita e reinterpretada como turno noturno
**Endereço:** colunas `seg_inicio/seg_fim … dom_inicio/dom_fim`, `*_inicio_2/*_fim_2`, `hora_inicio_padrao/hora_fim_padrao` em `escalas`
**O que acontece:** não há CHECK para nenhum dos 30 pares. O cálculo trata inversão como virada de
meia-noite: `if (diff1 < 0) diff1 += 24;` (em `src/lib/beneficios/jornadaEscala.ts` e em
`calcular-beneficios/index.ts:786`).
**Como verifiquei:** lista completa dos 47 CHECKs via `pg_constraint` — nenhum sobre pares de hora;
`prosrc` de `calculate_escala_hours` e `check_escala_overlap` — nenhum valida ordem; leitura de
`EscalasUpload.tsx` (valida só presença: `if (!horaInicio) errors.push("Hora início obrigatória")`).
Varredura de dados:
```sql
select count(*) filter (where dom_fim <= dom_inicio) ... from escalas;  -- 1 linha (dom 00:00→00:00)
```
**Consequência observável:** um erro de digitação (18:00→08:00) não gera erro nenhum: vira uma
jornada de 14h aceita em silêncio, que entra nas horas semanais e no direito a benefício.

### [EIXO 3] [MÉDIO] `afastamento_fim` × `afastamento_inicio` sem trava
**Endereço:** `colaboradores_rescisao_afastamentos.afastamento_inicio` / `.afastamento_fim`
**O que acontece:** o par não tem CHECK, enquanto o par equivalente em `beneficio_vt_nao_optante` tem
**dois** (`beneficio_vt_nao_optante_check` e `beneficio_vt_nao_optante_periodo_valido`).
**Como verifiquei:** lista de `pg_constraint` (a assimetria é visível na própria lista); triggers da
tabela conferidos um a um; `ColaboradorForm.tsx` grava `afastamento_inicio`/`afastamento_fim`
(linhas 735-736) sem validar. Dados hoje: **0 violações**.
**Camadas onde procurei:** CHECK (ausente), trigger (5, nenhum valida), RLS (não trata valor),
formulário (não valida), importador (não preenche).
**Consequência observável:** latente. Um afastamento invertido entraria sem resistência e o motor de
efetividade o consumiria.

### [EIXO 3] [MÉDIO] Colaborador inativo sem data de rescisão
**Endereço:** `colaboradores.status = 'inativo'` × `colaboradores_rescisao_afastamentos.rescisao_data` (nullable)
**Como verifiquei:**
```sql
select count(*) from colaboradores c where c.status='inativo'
and not exists (select 1 from colaboradores_rescisao_afastamentos ra
                where ra.colaborador_id=c.id and ra.rescisao_data is not null);  -- 2
```
**Camadas onde procurei:** `rescisao_data` é `is_nullable = YES` e não há CHECK condicional; o
trigger `trg_sync_status_from_ra` sincroniza status *a partir* da rescisão, nunca o contrário; RLS
não trata valor; o formulário não exige a data ao marcar inativo; o importador só grava
`rescisao_data` `if (dbStatus === "inativo" && r.data_rescisao)` — se a planilha vier sem a data, o
colaborador é inativado sem ela.
**Consequência observável:** `sincronizar-ponto` usa `rescisaoMap` para descartar marcações
pós-rescisão; sem `rescisao_data` esses 2 colaboradores nunca acionam esse descarte.

### [EIXO 3] [MÉDIO] Vigências de valor de benefício sem CHECK, ao contrário da vigência vizinha
**Endereço:** `colaborador_beneficio_valor.vigencia_inicio/.vigencia_fim` e `valores_beneficios.vigencia_inicio/.vigencia_fim`
**O que acontece:** as duas tabelas guardam vigência e nenhuma tem CHECK de ordem;
`beneficio_vt_nao_optante`, no mesmo módulo, tem dois.
**Como verifiquei:** lista completa de `pg_constraint`; nenhum trigger dessas tabelas além de
`update_updated_at_column`. Dados hoje: 0 violações nas duas.
**Camadas onde procurei:** CHECK (ausente), trigger (só updated_at), RLS (papel), formulário
(`BeneficiosValoresEditor.tsx` / `ValorPersonalizadoTab.tsx` — **não lidos**, ver NÃO VERIFICADO),
importador (não existe para essas tabelas).
**Consequência observável:** latente. Uma vigência invertida daria valor unitário nulo para o período.

### [EIXO 3] [MÉDIO] O período da própria quinzena não tem trava de ordem
**Endereço:** `beneficio_calculo_quinzenal.data_inicio/.data_fim` e `.data_inicio_complementar/.data_fim_complementar`
**O que acontece:** a tabela tem CHECK para `quinzena IN (1,2)` e para `tipo_calculo`, mas nenhum
para a ordem das datas — nem no par regular nem no complementar.
**Como verifiquei:** os únicos CHECKs da tabela são `beneficio_calculo_quinzenal_quinzena_check` e
`chk_tipo_calculo`. Dados hoje: 0 violações.
**Camadas onde procurei:** CHECK (ausente), trigger (só `update_..._updated_at`), RLS (papel),
front (`construirPeriodoQuinzena` em `periodoQuinzena.ts` sempre gera período coerente), edge
(`calcular-beneficios/index.ts:145-146` grava `fmtDate(dataInicio)`/`fmtDate(dataFim)` sem comparar).
**Consequência observável:** latente, mas é exatamente o campo que o
`header_update_error` (EIXO 1) pode deixar desatualizado sem aviso.

### [EIXO 3] [BAIXO] `escalas_audit.action` é texto livre e já acumulou 14 convenções diferentes
**Endereço:** coluna `escalas_audit.action` (sem CHECK, sem enum)
**Como verifiquei:**
```sql
select action, count(*) from escalas_audit group by 1 order by 2 desc;
-- correção(126) · importado(90) · criado(86) · encerrado(63) · descongelado(9) · ativado(7)
-- recongelado_apos_correcao(5) · correcao_anomalia_data_fim_menor_data_inicio(3)
-- movimentacao_cancelada(3) · encerramento_agendado(3) · correcao_datas(2)
-- anulacao_anomalia(1) · reativado(1) · correcao_data_base_ciclo(1)
```
**Camadas onde procurei:** nenhum CHECK sobre a coluna (lista de 47 conferida); nenhum enum do banco
cobre esses valores (36 enums listados); os inserts são livres (`action: "importado"` em
`EscalasUpload.tsx`).
**Consequência observável:** "correção" (com acento) e "correcao_datas" convivem; filtrar ou contar
por tipo de ação exige conhecer as 14 grafias.

---

# EIXO 4 — COESÃO E COERÊNCIA ENTRE MÓDULOS

### [EIXO 4] [ALTO] Tipo de benefício é representado de cinco formas diferentes
**Endereço:**
| Representação | Objeto | Valores |
|---|---|---|
| enum `beneficio_tipo` | `beneficio_calculo_quinzenal.tipo_beneficio` | `vt \| va \| al` |
| enum `tipo_beneficio` | `valores_beneficios.tipo` | `vale_alimentacao \| auxilio_lanche \| assiduidade \| insalubridade` |
| texto + CHECK | `colaborador_beneficio_valor.tipo_beneficio` | `va \| al` |
| texto + CHECK | `recibos_emitidos_v2.tipo_beneficio` | `vt \| va` |
| texto livre | `auditoria_findings.tipo_beneficio`, `beneficio_inconsistencia_log.tipo_beneficio` | sem restrição |

**O que acontece:** dois enums com **nomes quase idênticos e invertidos** (`beneficio_tipo` ×
`tipo_beneficio`) modelam o mesmo conceito com vocabulários incompatíveis, e mais três colunas o
repetem em texto.
**Como verifiquei:** `pg_enum` (36 enums) + `pg_constraint` + `information_schema.columns`. Uso real:
```sql
-- beneficio_calculo_quinzenal: va(11), vt(11)
-- valores_beneficios: vale_alimentacao(5), auxilio_lanche(4)
-- colaborador_beneficio_valor: va(2), al(1)
```
**Consequência observável:** `va` e `vale_alimentacao` são a mesma coisa em duas tabelas que se
cruzam no cálculo; nenhum JOIN direto é possível sem tradução manual, e a tradução não está em
lugar nenhum do banco. **Este achado da rodada anterior CONTINUA VÁLIDO.**

### [EIXO 4] [ALTO] `fechada` e `congelada` são usados de forma misturada — o VT fecha de um jeito e o VA de outro
**Endereço:** enum `beneficio_calculo_status` (`em_aberto | pendente_aprovacao | fechada | congelada`), coluna `beneficio_calculo_quinzenal.status`
**Como verifiquei:**
```sql
select competencia, quinzena, tipo_beneficio, status from beneficio_calculo_quinzenal order by 1 desc,2 desc;
```
| competência | quinzena | VT | VA |
|---|---|---|---|
| 2026-07 | 1 | `fechada` | **`congelada`** |
| 2026-06 | 2 | `congelada` | `congelada` |
| 2026-06 | 1 | `fechada` | **`em_aberto`** |
| 2026-05 | 2 | `fechada` | **`congelada`** |
| 2026-05 | 1 | `fechada` | **`congelada`** |

**O que acontece:** para o mesmo período, o VT termina em `fechada` e o VA em `congelada` — dois
estados terminais usados como sinônimos. A trava de sequência do pré-check testa **um só** deles:
`src/pages/beneficios/preCheckCalculo.ts` → `if (data && data.status !== "fechada")`.
E o fechamento guiado só é idempotente contra um deles:
`src/pages/beneficios/CalculoQuinzenal.tsx:911` → `if (header?.status === "fechada") return;`
**Consequência observável:** duas falhas concretas. (a) Toda quinzena de VA marcada `congelada` é
lida como "quinzena anterior aberta" e **bloqueia permanentemente** o cálculo da quinzena seguinte de
VA. (b) `CalculoQuinzenal.tsx:912-915` sobrescreve um header `congelada` para `fechada` sem
resistência, porque a guarda de idempotência não o reconhece. Além disso, 2026-06 quinzena 1 (VA)
segue `em_aberto` enquanto 07 e 08 já fecharam — período pulado, sem alerta em tela.

### [EIXO 4] [ALTO] Três colunas de data de admissão, com regra de uso que muda por contexto
**Endereço:** `colaboradores.data_admissao` (NOT NULL) · `colaboradores.data_admissao_esocial` (nullable) · `colaboradores.data_inicio_operacional` (nullable)
**O que acontece:** cada camada escolhe uma:
- `ColaboradorForm.tsx:604-606` e `:636-638` gravam **o mesmo valor** em `data_admissao` e
  `data_admissao_esocial`, e derivam a operacional: `data_inicio_operacional: dataInicioOpFinal`.
  O comentário em `:595-596` admite a confusão: *"dataAdmissao = oficial (eSocial). data_admissao (legado) = mesmo valor."*
- `ColaboradorForm.tsx:422-423` lê ao contrário: `setDataAdmissao(colab.data_admissao_esocial || colab.data_admissao)`.
- `preCheckCalculo.ts` usa a operacional com precedência: `const admissao = c.data_inicio_operacional || c.data_admissao || null;`
- `ColaboradoresUpload.tsx` grava **só** `data_admissao`, deixando as outras duas nulas.

**Como verifiquei:** `information_schema.columns` + leitura dos 3 arquivos + dados:
```sql
select count(data_admissao), count(data_admissao_esocial), count(data_inicio_operacional),
       count(*) filter (where data_admissao_esocial <> data_admissao) from colaboradores;
-- 99 | 99 | 99 | 0
```
**Consequência observável:** `data_admissao_esocial` é hoje 100% redundante (idêntica à
`data_admissao` nas 99 linhas) mas continua sendo a que o formulário exibe;
`data_inicio_operacional` diverge em 1 linha e é **ela** que decide o direito a benefício.
Qual data vale depende da tela em que o operador está. **Achado da rodada anterior CONTINUA VÁLIDO.**

### [EIXO 4] [MÉDIO] `pendente_aprovacao` existe no enum, tem coluna de suporte e nunca foi usado
**Endereço:** valor `pendente_aprovacao` do enum `beneficio_calculo_status`; coluna `beneficio_calculo_quinzenal.aprovado_por`
**Como verifiquei:** `select status, count(*) from beneficio_calculo_quinzenal group by 1;` →
`fechada 14`, `congelada 5`, `em_aberto 3`, **`pendente_aprovacao` 0**. Em
`CalculoQuinzenal.tsx:913` o fechamento grava direto `status: "fechada", aprovado_por: user?.id` —
o estado intermediário de aprovação é pulado.
**Consequência observável:** o enum promete um passo de aprovação que nenhum caminho do sistema
percorre; quem lê o schema conclui que existe uma etapa de aprovação que não existe.

### [EIXO 4] [MÉDIO] Um mesmo módulo tem quatro nomes: sidebar, rota, arquivo e tabela não coincidem
**Endereço:** `src/components/AppSidebar.tsx` → `{ title: "Sucesso do Cliente", url: "/supervisao/risco", canEditOnly: true }` · rota em `src/App.tsx` → `<Route path="/supervisao/risco" ... <PainelRisco />` · arquivo `src/pages/supervisao/PainelRisco.tsx` · tabelas `painel_risco` e `painel_risco_cliente_mensal`
**O que acontece:** o menu diz "Sucesso do Cliente", a URL diz "risco", o componente diz
"PainelRisco" e o banco diz `painel_risco`.
**Como verifiquei:** leitura de `AppSidebar.tsx` (`MODULES` → grupo `operacao`) e da tabela de rotas
em `App.tsx`; nomes de tabela via `information_schema.tables`.
**Consequência observável:** um operador que ouve "abre o Sucesso do Cliente" não encontra o termo
na URL, e quem lê o banco não liga `painel_risco` ao módulo que o menu anuncia.

### [EIXO 4] [MÉDIO] "Folha" é dois territórios distintos com entradas distintas
**Endereço:** `src/App.tsx` → `<Route path="/folha-pagamento" ... <FolhaPagamentoPage />` (arquivo `src/pages/folha/FolhaPagamentoPage.tsx`) **e** `<Route path="/relatorios/folha" ... <FolhaHome />` com 6 sub-relatórios `R3…R10` (`src/pages/relatorios/folha/`)
**O que acontece:** dois conjuntos de tela sob o mesmo conceito. A sidebar expõe **apenas o
primeiro**, como `{ title: "Folha do Mês", url: "/folha-pagamento" }` dentro de Relatórios;
`/relatorios/folha` e seus seis relatórios não aparecem em `MODULES`.
**Como verifiquei:** tabela de rotas de `App.tsx` × array `MODULES` de `AppSidebar.tsx`; a listagem
de arquivos confirma os 6 arquivos `R*.tsx` em `src/pages/relatorios/folha/`.
**Consequência observável:** seis relatórios de folha construídos e roteados só são alcançáveis por
URL digitada — não há caminho de navegação até eles.

### [EIXO 4] [MÉDIO] O status do colaborador mistura duas dimensões no mesmo enum
**Endereço:** enum `colaborador_status` (`ativo | inativo | afastado | ativo_operacional | ativo_afastado_inss | ativo_free`)
**O que acontece:** o enum combina *vigência do vínculo* (ativo/inativo) com *situação operacional*
(afastado INSS, free) num campo só, e mantém três valores que a base nunca usa.
**Como verifiquei:**
```sql
select status, count(*) from colaboradores group by 1;
-- ativo 61 | inativo 25 | ativo_afastado_inss 9 | ativo_free 4
-- 'afastado' e 'ativo_operacional': 0 linhas
```
Mesmo sem uso, `sincronizar-ponto/index.ts` mantém `const BLOCKED_STATUSES = ["ativo_afastado_inss", "inativo", "afastado"];` e `preCheckCalculo.ts` filtra `.in("status", ["ativo", "ativo_free"])`,
enquanto `sincronizar-ponto` consulta `.in("status", ["ativo", "ativo_operacional", "ativo_free"])`.
**Consequência observável:** três listas diferentes de "quem conta como ativo" em três arquivos, cada
uma incluindo ou omitindo valores mortos do enum.

---

# EIXO 5 — RETROALIMENTAÇÃO

### [EIXO 5] [CRÍTICO] `audit_log` tem 46.873 linhas e só 2 são alcançáveis por alguma tela
**Endereço:** tabela `public.audit_log`; único leitor `src/pages/usuarios/HistoricoUsuarioDrawer.tsx` → `.from("audit_log").select(...).eq("record_id", userId)`
**O que acontece:** o trigger `fn_audit_row()` grava em `audit_log` a partir de 8+ tabelas. A única
tela que lê a tabela filtra por `record_id = <id do usuário>`, ou seja, só enxerga linhas cujo
`record_id` seja um id de `auth.users`.
**Como verifiquei:**
```sql
select table_name, count(*) from audit_log group by 1 order by 2 desc;
-- recibos_emitidos 41816 | efetividade_diaria 1859 | colaboradores_lotacao 1371
-- beneficio_vt_item_snapshot 747 | colaboradores 320 | beneficio_credito_debito 229 | ...

select count(*) from audit_log a where exists (select 1 from auth.users u where u.id = a.record_id);
-- 2
```
E a tela `Registros de Auditoria` (`RegistrosAuditoria.tsx` → `AuditoriaBeneficiosTab` +
`AuditoriaEfetividadeTab`, via `src/hooks/useAuditoria.ts`) lê **apenas** `beneficio_audit` e
`efetividade_audit` — nunca `audit_log`.
**Camadas onde procurei antes de concluir ausência:** (1) `RegistrosAuditoria.tsx` e as duas abas;
(2) `useAuditoria.ts` — as duas queries são `beneficio_audit` e `efetividade_audit`;
(3) `HistoricoUsuarioDrawer.tsx` — o único `from("audit_log")` que encontrei;
(4) `EscalaDetail.tsx` — lê `escalas_audit`, não `audit_log`;
(5) RLS — `Admins can view audit logs` permite ler, então não é restrição de acesso, é ausência de tela.
**Consequência observável:** 46.871 registros de auditoria (99,996%) — incluindo as 41.816 exclusões
de `recibos_emitidos` — não têm nenhuma superfície de leitura. **Achado da rodada anterior CONTINUA
VÁLIDO para `audit_log`** (para `beneficio_audit`, `efetividade_audit` e `escalas_audit` foi corrigido).

### [EIXO 5] [ALTO] A fila de reprocessamento tem 8 jobs em erro e a tela mostra zero
**Endereço:** `src/pages/efetividade/EfetividadeFilaReprocesso.tsx` → `.order("created_at", { ascending: false }).limit(200)` e `counts.erro = jobs?.filter(j => j.status === "erro").length`
**O que acontece:** a tela carrega os 200 jobs mais recentes e calcula os contadores **dentro dessa
janela**. Com 14.233 linhas na fila, os 200 mais recentes são todos de agosto.
**Como verifiquei:**
```sql
with ult200 as (select id,status from efetividade_reprocess_queue order by created_at desc limit 200)
select (select count(*) from ult200 where status='erro') visiveis,
       (select count(*) from efetividade_reprocess_queue where status='erro') totais,
       (select max(created_at) from efetividade_reprocess_queue where status='erro') mais_recente;
-- visiveis: 0 | totais: 8 | mais_recente: 2026-05-08
```
Corte da janela da tela: 2026-08-28. Erro mais recente: 2026-05-08.
**Camadas onde procurei:** a própria tela (único consumidor da tabela); o card "Erro" do painel de
contadores; não há filtro por status na UI, nem paginação, nem query separada de erros; RLS permite
ler (`Admin/operador can view reprocess_queue`).
**Consequência observável:** o card "Erro" exibe **0** enquanto 8 reprocessamentos de efetividade
estão travados desde maio. O botão "Reenfileirar", que só é renderizado em linhas com
`status === "erro"`, nunca aparece para eles.

### [EIXO 5] [ALTO] 91% da auditoria não registra quem fez
**Endereço:** `audit_log.user_id`, `beneficio_audit.user_id`
**Como verifiquei:**
```sql
select 'audit_log', count(*), count(*) filter (where user_id is null) from audit_log
union all select 'beneficio_audit', count(*), count(*) filter (where user_id is null) from beneficio_audit
union all select 'escalas_audit', count(*), count(*) filter (where user_id is null) from escalas_audit
union all select 'efetividade_audit', count(*), count(*) filter (where user_id is null) from efetividade_audit;
```
| tabela | linhas | sem autor | % |
|---|---|---|---|
| `audit_log` | 46.873 | **42.766** | 91,2% |
| `beneficio_audit` | 4.187 | **2.854** | 68,2% |
| `escalas_audit` | 400 | 13 | 3,3% |
| `efetividade_audit` | 2.786 | 1 | 0,04% |

**Camadas onde procurei:** o trigger `fn_audit_row()` é `AFTER INSERT OR DELETE OR UPDATE FOR EACH
ROW` e depende de `auth.uid()`, que é NULL quando a escrita vem de service-role (edge functions,
cron) ou de RPC `SECURITY DEFINER`; nenhuma coluna alternativa de autoria existe nessas tabelas.
`escalas_audit` e `efetividade_audit` escapam porque são escritas explicitamente pelo front com
`user_id: user?.id`.
**Consequência observável:** para as tabelas escritas por edge function ou cron, a auditoria registra
o quê e o quando, mas não o quem. As 41.816 exclusões de `recibos_emitidos` estão nesse grupo.

### [EIXO 5] [ALTO] `auditoria_findings` parou em 17/04 com 65 apontamentos abertos e nenhum resolvido
**Endereço:** tabela `auditoria_findings` (26 colunas, incluindo `ia_descricao`, `ia_causa_raiz`, `ia_acao_recomendada`, `ia_severidade_revisada`); tela `src/pages/beneficios/AuditoriaIA.tsx`; edge functions `auditoria-rules/` e `auditoria-ia/`
**Como verifiquei:**
```sql
select status, count(*), max(created_at) from auditoria_findings group by 1;
-- aberto | 65 | 2026-04-17 01:20:03
```
Nenhuma linha em qualquer outro status; `resolvido_em` e `resolvido_por` existem e nunca foram usados.
**Camadas onde procurei:** a tela existe (`AuditoriaIA.tsx`, rota `/beneficios?modulo=auditoria`,
mais o drawer `AuditoriaFindingDrawer.tsx`); a policy de UPDATE existe
(`Admin/operador can update auditoria_findings`); as duas edge functions de geração existem. Ou seja,
**o ciclo está construído inteiro e simplesmente parou de rodar há 4 meses.**
**Consequência observável:** o módulo de auditoria por IA exibe permanentemente os mesmos 65
apontamentos de abril, sem nenhuma indicação na tela de que a coleta está parada.

### [EIXO 5] [ALTO] 865 inconsistências de benefício abertas contra 13 resolvidas — o laço não fecha
**Endereço:** tabela `beneficio_inconsistencia_log`; telas `src/pages/beneficios/InconsistenciasLog.tsx` e `InconsistenciasReport.tsx`; produtores `calcular-beneficios/index.ts:1919` (`calculo_bloqueado_saude_dado`, severidade `critical`) e `:2886` (`cd_orfao_nao_consumido`)
**Como verifiquei:**
```sql
select status, count(*), max(created_at) from beneficio_inconsistencia_log group by 1;
-- aberto    | 865 | 2026-08-28 16:36
-- resolvido |  13 | 2026-05-28 21:42
```
**Camadas onde procurei:** as telas existem e a policy de UPDATE existe
(`Admin/operador can update inconsistencia_log`), então **não é ausência de tela** — é ausência de
fechamento. Nenhuma resolução foi registrada desde 28/05, enquanto a produção continuou até 28/08.
**Consequência observável:** o log cresce 66× mais rápido do que é tratado. Entre as abertas estão
inconsistências marcadas `critical` (cálculo bloqueado por saúde do dado) e créditos/débitos elegíveis
que o cálculo não consumiu — cada um representando dinheiro que não entrou no recibo do colaborador.

### [EIXO 5] [ALTO] As 776 marcações de ponto com horas dobradas não têm nenhuma superfície que as denuncie
**Endereço:** `ponto_registros` (ver EIXO 1, primeiro achado); telas `src/pages/ponto/PontoList.tsx` e `src/pages/ponto/PontoImportacaoLog.tsx`
**O que acontece:** a duplicação não gera linha em `beneficio_inconsistencia_log`, não gera
`auditoria_findings`, não entra em `detalhes_erro` do `ponto_importacao_log` (não é contada como
erro nem como descarte) e não altera `status_homologacao` (776 foram homologadas automaticamente).
**Como verifiquei:** leitura de `sincronizar-ponto/index.ts` — os únicos contadores registrados são
`ignoradosFantasma`, `ignoradosAfastamento`, `ignoradosFerias`, `ignoradosRescisao` e `errors`;
duplicidade de par não é nenhum deles. Consulta cruzada:
```sql
select count(*) from beneficio_inconsistencia_log where tipo ilike '%ponto%';  -- 0
```
**Camadas onde procurei:** log de importação (não registra), inconsistências de benefício (0 linhas
sobre ponto), `auditoria_findings` (parado desde abril), `saude_dado_snapshot` (checks por
colaborador/competência, não por marcação), homologação (aprovou os 776).
**Consequência observável:** o sistema calculou horas erradas em 810 dias-colaborador e **não tem
onde dizer isso**. A descoberta só aconteceu por consulta SQL direta.

### [EIXO 5] [MÉDIO] `colaboradores_remuneracao_audit` não tem leitor identificado e parou em maio
**Endereço:** tabela `colaboradores_remuneracao_audit` (123 linhas, última em 2026-05-06)
**Como verifiquei:** `select count(*), max(created_at) from colaboradores_remuneracao_audit;` → 123,
2026-05-06. Busca por leitor: `grep -n "remuneracao_audit"` em `ColaboradorForm.tsx` (1.847 linhas) e
`CalculoQuinzenal.tsx` (3.582 linhas) → **nenhuma ocorrência**; `useAuditoria.ts` lê só
`beneficio_audit` e `efetividade_audit`; `RegistrosAuditoria.tsx` tem só essas duas abas.
**Camadas onde procurei:** as 4 acima. **Não pude varrer os ~250 arquivos restantes** (ver NÃO
VERIFICADO), então registro como *leitor não identificado*, não como *inexistente*.
**Consequência observável:** o histórico de alteração salarial (a auditoria com 100% de autoria
preenchida, a melhor da base) não aparece na tela de Registros de Auditoria.

### [EIXO 5] [MÉDIO] O log de auditoria da escala mostra um pedaço de UUID no lugar do nome
**Endereço:** `src/pages/escalas/EscalaDetail.tsx` → `<TableCell className="text-xs">{l.user_id ? l.user_id.slice(0, 8) + "…" : "—"}</TableCell>`
**O que acontece:** a coluna "Usuário" do card "Log de Auditoria" renderiza os 8 primeiros caracteres
do UUID. O resolvedor de nome já existe e é usado na outra tela de auditoria:
`src/hooks/useAuditoria.ts` → `useUsuariosPorIds()` + `renderUsuario()`.
**Como verifiquei:** leitura dos dois arquivos.
**Consequência observável:** o rastro existe e é ilegível — para saber quem encerrou uma escala o
operador precisa cruzar o fragmento de UUID manualmente.

### [EIXO 5] [MÉDIO] `hub_escala_outbox` não tem tela e depende de 69 entregas sem retentativa visível
**Endereço:** tabela `hub_escala_outbox` (colunas `status`, `tentativas`, `ultimo_erro`); produtor trigger `trg_hub_escala_outbox` → `tg_hub_escala_outbox()`; consumidor `supabase/functions/enviar-escala-hub/index.ts`
**Como verifiquei:**
```sql
select status, count(*) from hub_escala_outbox group by 1;  -- enviado: 69  (nenhum pendente/erro hoje)
```
Busca por leitor de tela: a tabela não aparece em `AppSidebar.tsx` nem na tabela de rotas de
`App.tsx`; não há arquivo em `src/pages/` com nome correspondente na listagem completa de arquivos.
A RLS tem **apenas** policy de SELECT para admin (`Admin can view hub_escala_outbox`) e nenhuma de
INSERT/UPDATE para usuário — escrita é só por trigger/service-role.
**Camadas onde procurei:** sidebar, rotas, listagem de `src/pages/**`, RLS.
**Consequência observável:** a fila tem os campos para diagnóstico (`tentativas`, `ultimo_erro`) e
nenhuma superfície que os mostre. Hoje está zerada; quando um envio falhar, ninguém verá.

---

# CONTAGEM

| Eixo | Crítico | Alto | Médio | Baixo | Total |
|---|---|---|---|---|---|
| 1 — Falha silenciosa | 2 | 3 | 3 | 2 | **10** |
| 2 — Empilhamento | 0 | 2 | 4 | 1 | **7** |
| 3 — Ausência de trava | 0 | 3 | 5 | 1 | **9** |
| 4 — Coesão | 0 | 3 | 3 | 0 | **6** |
| 5 — Retroalimentação | 1 | 4 | 3 | 0 | **8** |
| **TOTAL** | **3** | **15** | **18** | **4** | **40** |

## Situação dos achados da rodada anterior

| Achado anterior | Situação hoje | Evidência |
|---|---|---|
| Tabelas de auditoria gravadas e nunca lidas | **PARCIALMENTE CORRIGIDO** | `beneficio_audit`, `efetividade_audit` (via `RegistrosAuditoria.tsx`) e `escalas_audit` (via `EscalaDetail.tsx`) ganharam tela. `audit_log` continua com 2 de 46.873 linhas alcançáveis. `colaboradores_remuneracao_audit` sem leitor identificado. |
| Detalhe de erro de importação nunca renderizado | **CORRIGIDO — com brecha nova** | `PontoImportacaoLog.tsx` agora expande e renderiza `detalhes_erro`. Mas o botão é condicionado a `erros > 0`, escondendo 291 logs com detalhe e `erros = 0`. |
| Dois enums para tipo de benefício | **CONTINUA** (e pior) | `beneficio_tipo` + `tipo_beneficio` + 3 representações em texto. |
| Três status de quinzena, dois misturados | **CONTINUA** (e pior) | 4 valores no enum, 3 em uso, `fechada`/`congelada` misturados por tipo de benefício; `pendente_aprovacao` com 0 linhas. |
| Três colunas de data de admissão | **CONTINUA** | `data_admissao`, `data_admissao_esocial`, `data_inicio_operacional` — a terceira decide o benefício. |
| Ausência total de CHECK constraints | **CORRIGIDO** | 47 CHECKs em `public`. Restam lacunas pontuais (Eixo 3). |
| Dois helpers de parse de erro com o mesmo nome | **REFORMULADO** | Existe **um** helper nomeado (`src/lib/beneficios/parseFunctionError.ts`). A duplicação hoje é uma cópia **inline** e mais fraca em `ColaboradorForm.tsx:936-953`. |
| Função de validação de período com um único call site | **NÃO VERIFICADO** | Ver abaixo. |

---

# NÃO VERIFICADO

Tudo o que ficou de fora, e por quê. Nada aqui foi inferido nem completado de memória.

1. **Grep global no código-fonte.** O ALMIRA não tem espelho no GitHub (`list_repos` → 9 repos,
   nenhum é `gestao-foco-rh`) e a API do Lovable lê **um arquivo por vez**. Li integralmente 16
   arquivos dos ~250 de `src/` + `supabase/functions/`. Consequência direta: afirmações do tipo
   "nenhuma tela lê X" foram feitas **apenas** onde consegui enumerar os candidatos plausíveis pela
   sidebar, pelas rotas de `App.tsx` e pela listagem completa de arquivos — e onde isso não bastou,
   escrevi "leitor não identificado" em vez de "não existe".

2. **O achado anterior "função de validação de período com um único call site".** Não consegui
   confirmar nem refutar: identificar call sites exige grep global (item 1). Candidatas que li mas
   não pude contar referências: `vigenciasSobrepoem` e `intervalosIntersectam` em
   `src/lib/beneficios/periodoQuinzena.ts`, `validarExperienciaCLT` em `src/lib/contratoExperiencia.ts`
   (visto em uso em `ColaboradorForm.tsx:343` e `:582` — pelo menos 2 call sites, portanto **não é
   essa**).

3. **`src/pages/escalas/EscalaForm.tsx` não foi lido.** É a camada "formulário" do achado
   [EIXO 3][ALTO] das datas de escala. As outras cinco camadas foram conferidas (CHECK `NOT VALID`,
   `prosrc` completo de `check_escala_overlap` e `calculate_escala_hours`, RLS, importador
   `EscalasUpload.tsx`, motor). O achado se sustenta pelas 5 linhas violando o dado em produção,
   mas **não afirmo que o formulário não valide**.

4. **`BeneficiosValoresEditor.tsx` e `ValorPersonalizadoTab.tsx` não foram lidos** — camada
   "formulário" do achado [EIXO 3][MÉDIO] das vigências de valor de benefício. As demais camadas
   foram conferidas.

5. **Os ~200 arquivos de migração em `supabase/migrations/`** não foram lidos. Trabalhei sobre o
   **estado vivo** do banco (`pg_constraint`, `pg_trigger`, `pg_policy`, `pg_proc`, `pg_enum`,
   `information_schema`), que é a fonte de verdade. Não consigo, portanto, datar *quando* cada
   lacuna surgiu — só constatar que existe hoje.

6. **As 47 edge functions não foram lidas integralmente.** Li 3 (`calcular-beneficios/index.ts`,
   `sincronizar-ponto/index.ts` e trechos citados). As outras 44 — incluindo
   `processar-efetividade`, `processar-fila-efetividade`, `auditoria-rules`, `auditoria-ia`,
   `gerar-recibo-beneficio` e `gerar-recibo-beneficio-v2` — não foram auditadas. Duplicações e
   falhas silenciosas dentro delas não estão neste relatório.

7. **Não executei o sistema.** Todos os achados vêm de leitura de código e de consultas `SELECT` ao
   banco de produção. Nenhuma reprodução em tela foi feita, e a coluna "Consequência observável"
   descreve o que o código determina que aconteça — não o que eu vi acontecer.

8. **Módulo Minha FOCO (PWA do colaborador)** — 13 arquivos em `src/pages/minhafoco/` — e o módulo
   de suporte (`src/pages/suporte/`, `src/components/suporte/`) não foram auditados em nenhum eixo.

9. **`src/integrations/supabase/types.ts`** (tipos gerados) não foi lido; divergências entre os tipos
   do front e o schema real não foram checadas.

10. **Não verifiquei RLS de forma exaustiva.** Consultei `pg_policy` apenas para as 11 tabelas de
    log/auditoria/fila. As policies das ~66 tabelas restantes não foram revisadas, e o eixo de
    segurança não fazia parte do escopo pedido.
