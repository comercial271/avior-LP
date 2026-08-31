# ALMIRA — escalas: trava de duplicidade + alertas para a operação

Data: 2026-08-31. Banco e código conferidos ao vivo.

## O que motivou

A operação usava um truque: criar **duas escalas para o mesmo colaborador no mesmo cliente**, para
dar conta de jornadas com horários diferentes em dias diferentes (ex.: seg/qua/sex 08:00–17:00 com
1h de intervalo, ter/qui 08:00–14:15 com 15 min). Investigando isso, apareceram três coisas.

---

## 1. O truque não era necessário — e o campo `intervalo` engana

`calculate_escala_hours()` já resolve o caso numa escala só. Provado por simulação em transação
revertida, com a jornada exata do exemplo:

| como cadastrar | horas/semana | horas/mês |
|---|---|---|
| uma escala, intervalo digitado **0,25** | **36,00** | **180,00** ✓ |
| uma escala, intervalo digitado **0** | **36,00** | **180,00** ✓ |
| uma escala, intervalo digitado **1,00** | 34,50 | 172,50 ✗ |
| duas escalas (o truque) | 24 + 12 = 36 | 120 + 60 = 180 ✓ |

**A causa:** `intervalo` não é o intervalo, é um **piso mínimo**. A função aplica o desconto pelo
tamanho de cada dia:

| duração do dia | intervalo aplicado |
|---|---|
| até 4h | nenhum |
| mais de 4h até 7h | no mínimo **15 min** |
| mais de 7h | no mínimo **1h** |

Digitar `1,00` — o valor intuitivo, já que os dias longos realmente têm 1h — força uma hora também
nos dias de 6h15, que só deveriam perder 15 min. O texto de ajuda do formulário
("Ex: 0.25 = 15min, 0.5 = 30min, 1 = 1h") induz exatamente ao erro.

### O caso vivo

**JUCELE PADILHA FERNANDES (07323), MACADAR, escala futura a partir de 08/09/2026.**
Mesma jornada, hora por hora, da **SORAIA DA SILVA PEREIRA (7072)**, ativa desde 08/06:

| | SORAIA | JUCELE |
|---|---|---|
| seg, qua, sex, sáb | 10:00–19:00 | 10:00–19:00 |
| ter, qui | 12:45–19:00 | 12:45–19:00 |
| intervalo digitado | **0,25** | **1,00** |
| horas/semana | **44,00** | **42,50** |
| horas/mês | **220,00** | **212,50** |

Única escala vigente ou futura nessa condição na base inteira. `MACADAR.intervalo_remunerado =
false`, então o desconto é devido — 44h é o número certo, e é exatamente o teto da CLT.

A escala foi criada em 27/08 pela conta **"Usuário Teste"** (`teste@focoserv.com.br`, papel admin).

---

## 2. Seis clientes com mais gente escalada do que posto contratado

`clientes.qtd_postos` existe no cadastro e **nada no sistema confere contra ele**. Testando
sobreposição real de horário com a função `escala_segmentos` (Fase 1D):

| cliente | postos | quem está escalado | horários |
|---|---|---|---|
| **H MECH** | 1 | CAMILA (11/08) + ANA BEATRIZ (18/08) | idênticos |
| **PAJUCARA** | 1 | CAMILA (12/08) + ANA BEATRIZ (14/08) | idênticos |
| **COND. FELIPE CAMARÃO** | 1 | ROSANE (24/04) + ROSANGELA (14/08) | idênticos |
| **COND. WEINSTEIN** | 1 | ROSANE (01/04) + DAIANA (15/08) | idênticos |
| **LIV UP** | 1 | TANARA (18/08) + TATIANE (29/08) | idênticos |
| **MACADAR** | 1 | SORAIA + JUCELE (futura 08/09) | idênticos |

Nos seis os horários são **exatamente iguais** — não é gente dividindo o posto em turnos, é
substituição sem encerramento.

**Fora da lista, de propósito:**
- **ALTERVISION** — 2 escalas para 1 posto, mas os horários **não** se sobrepõem. Uso legítimo.
- **BISTEK SAPIRANGA** — 4 escalas para 2 postos, com uma dupla 12×36. `escala_segmentos` não
  modela a alternância do ciclo 12×36, então **nada é afirmado sobre o BISTEK**. Precisa de olhada
  humana.

### Por que o encerramento automático não pegou

O auto-encerramento do `EscalaForm.tsx` só procurava escalas do **mesmo colaborador no mesmo
cliente**. Os seis casos são **colaboradores diferentes no mesmo cliente** — ele nem olhava.

---

## 3. Um colaborador em limbo

**CAMILA CAVALHEIRO (07188):** status `inativo`, **sem data de rescisão**, com **duas escalas
ativas** (H MECH e PAJUCARA). A Ana Beatriz assumiu os dois postos e as da Camila nunca foram
encerradas.

**Correção a um registro meu anterior:** eu havia escrito que a Fase 1E tinha "2 casos históricos,
0 hoje". Medindo com a definição certa (colaborador não-`ativo` com escala vigente), há **1 caso
vivo**. Vale a medição de agora.

| status | pessoas | com rescisão | com escala vigente |
|---|---|---|---|
| ativo | 61 | 0 | 61 |
| inativo | 25 | 23 | **1** ← Camila |
| ativo_afastado_inss | 9 | 0 | 0 |
| ativo_free | 4 | 0 | 4 |

---

## O QUE FOI FEITO

### Código (projeto Lovable `gestao-foco-rh`), diff revisado linha a linha

| commit | conteúdo |
|---|---|
| `9cc1bf4` | `AlertasDirecionados.tsx` destravado + 3 tipos novos de alerta |
| `f34708a` | `EscalaForm.tsx`: para de encerrar sozinho, passa a perguntar |
| `f564a67` | 3 correções na revisão do diff acima |

**`9cc1bf4` — o componente de alerta era de uso único.** Tinha `DATA_ENCERRAMENTO = "2026-07-14"`,
o motivo e o `data_inicio` do reprocessamento chumbados no código, escritos para um evento de julho.
Qualquer alerta novo encerraria escalas em 14/07/2026 — data errada e no passado. Os três passaram a
vir do `payload`, com os valores de julho como padrão para os alertas antigos. De quebra, o agente
trocou `new Date().toISOString().slice(0,10)` por `hojeSaoPauloYMD()`, corrigindo um bug de fuso que
fazia "hoje" virar o dia seguinte entre 21h e meia-noite de Brasília.

**`f34708a` — a tela de escala.** A verificação saiu de dentro do `mutationFn` e foi para o
`handleSaveClick`, antes de gravar qualquer coisa. Passou a fazer duas perguntas em vez de uma:
mesma pessoa neste cliente, e posto já ocupado por outra pessoa (contra `qtd_postos`). Diálogo com
três saídas: encerrar a anterior, manter as duas, cancelar. O encerramento só roda com escolha
explícita.

**`f564a67` — três achados da revisão do diff:**
1. O diálogo avisava sobre escala `futuro`, mas o encerramento só pegava `ativo`. O operador
   clicaria em "encerrar a anterior" e a futura ficaria lá. O sistema prometia uma coisa e fazia
   outra.
2. A consulta que lista as escalas a encerrar descartava o `error` — mesma classe de falha
   silenciosa corrigida em `9937719` nos dois comandos seguintes.
3. Datas apareciam como `2026-04-24` em vez de `24/04/2026`.

### Dados: 6 alertas para a operação

Criados em `alertas_direcionados`, apontando para **Dargiele Brandão**
(`operacional@focoserv.com.br`, papel `operador`). Ela vê ao entrar no sistema, e o botão
**"Decidir depois"** traz de volta no próximo acesso.

| grupo_chave | tipo | assunto |
|---|---|---|
| `colab_inativo_07188` | `colaborador_inativo_com_escala` | Camila inativa ocupando dois postos |
| `posto_dup_C008` | `escala_posto_duplicado` | COND. FELIPE CAMARÃO |
| `posto_dup_C018` | `escala_posto_duplicado` | COND. WEINSTEIN |
| `posto_dup_C042` | `escala_posto_duplicado` | LIV UP |
| `posto_dup_C021` | `escala_posto_duplicado` | MACADAR |
| `carga_escala_jucele_macadar` | `escala_carga_horaria_suspeita` | jornada da Jucele |

**Nenhum alerta altera nada sozinho.** Quem altera é a Dargiele, clicando. Fica registrado em
`escalas_audit` quem decidiu, quando e por quê, e o reprocessamento da efetividade é enfileirado.

Decisão de desenho: as escalas da Camila apareceriam tanto no alerta dela quanto nos de H MECH e
PAJUCARA. Isso deixaria alerta órfão depois de resolvido, então **são 6 alertas, não 8** — o da
Camila cobre os dois clientes dela.

---

## VERIFICAÇÃO

Contagens depois de tudo, contra `migracoes/BASELINE-2026-08-30.md`:

```
colaboradores ......... 99    (inalterado)
escalas .............. 176    (inalterado)
clientes .............. 69    (inalterado)
CHECK constraints ..... 77    (inalterado)
alertas_direcionados ... 17    (11 antes + 6 novos, todos pendentes)
```

Nenhuma linha de escala, colaborador ou cliente foi alterada.

### Consultas para rodar de novo e ver o número cair

**Postos excedidos com sobreposição real de horário:**
```sql
select cl.codigo, cl.nome_abreviado, cl.qtd_postos,
       ca.nome_completo as pessoa_a, cb.nome_completo as pessoa_b
from public.escalas a
join public.escalas b on b.cliente_id=a.cliente_id and b.id>a.id and b.status in ('ativo','futuro')
join public.clientes cl on cl.id=a.cliente_id
join public.colaboradores ca on ca.id=a.colaborador_id
join public.colaboradores cb on cb.id=b.colaborador_id
where a.status in ('ativo','futuro')
  and exists (select 1 from unnest(public.escala_segmentos(a)) x,
                           unnest(public.escala_segmentos(b)) y where x && y)
  and (select count(*) from public.escalas e
        where e.cliente_id=cl.id and e.status in ('ativo','futuro')) > coalesce(cl.qtd_postos,999);
```

**Colaborador em limbo (não-ativo com escala vigente):**
```sql
select c.matricula, c.nome_completo, c.status, ra.rescisao_data, count(e.id) as escalas_vigentes
from public.colaboradores c
join public.escalas e on e.colaborador_id=c.id and e.status in ('ativo','futuro')
left join public.colaboradores_rescisao_afastamentos ra on ra.colaborador_id=c.id
where c.status <> 'ativo' and c.status <> 'ativo_free'
group by 1,2,3,4;
```

---

## NÃO VERIFICADO

- **Nada foi testado em tela.** Os três commits foram revisados linha a linha no diff, mas ninguém
  abriu o formulário e salvou uma escala. Não tenho credencial, e criar usuário de auth em produção
  dá acesso a dados de 99 pessoas reais.
- **Não confirmei que o deploy dos commits chegou à produção** antes de inserir os alertas. Se a
  Dargiele entrar antes do deploy, ela verá o título e a mensagem dos alertas novos, mas sem corpo
  nem botões de ação — só "Decidir depois". Não é destrutivo, mas convém conferir o deploy antes de
  avisar ela.
- **`qtd_postos` pode não estar sendo mantido atualizado.** Se não estiver, o aviso de posto ocupado
  dispara à toa. Por isso ele **avisa** em vez de bloquear.
- **A alternância do ciclo 12×36** não é modelada por `escala_segmentos` — por isso o BISTEK ficou
  fora das conclusões.
- **Caso de borda não testado:** encerrar uma escala `futuro` cuja `data_inicio` é posterior ao
  início da escala nova produziria `data_fim < data_inicio`, que a constraint
  `escalas_data_fim_apos_inicio` recusa. A trava faz o certo, mas a mensagem que aparece é o
  genérico "Valor inválido" do código 23514. Merece uma regra própria em `bloqueios.ts`.

## Fora deste lote

- **COND. VINTAGE (C060)** é o único cliente com `intervalo_remunerado = true`, e as 3 escalas
  vigentes descontam intervalo assim mesmo, porque `calculate_escala_hours` não olha o cliente.
  É mudança de regra de cálculo.
- **Rótulo do campo `intervalo`** e o cálculo por dia no `ConfirmEscalaDialog` — planejados, ainda
  não feitos.
