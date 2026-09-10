# Agente de WhatsApp: mensagem toda segunda-feira para um grupo

Manda uma mensagem automaticamente para um grupo do WhatsApp toda segunda-feira.
A mensagem pode ser fixa ou escrita por IA a cada semana a partir de um briefing seu.

Sem n8n. Tres pecas:

| Peca | Para que serve | Custo |
|---|---|---|
| Evolution API (Railway) | Conecta o numero do WhatsApp e envia a mensagem | ~R$ 25 a 40/mes (servidor) |
| Supabase Edge Function | O "agente": decide o texto e chama a Evolution | Gratis |
| Supabase pg_cron | O relogio: dispara a funcao toda segunda 09:00 | Gratis |

Estrutura desta pasta:

```
whatsapp-agent/
  README.md                                   <- este guia
  supabase/functions/enviar-segunda/index.ts  <- a funcao (o agente)
  supabase/migrations/..._agente_whatsapp.sql <- tabelas de configuracao e log
  supabase/cron.sql                           <- agendamento de segunda-feira
```

---

## Passo 1: subir a Evolution API no Railway (voce faz, ~10 min)

1. Crie uma conta em https://railway.app (pode entrar com GitHub).
2. Abra o template oficial: https://railway.com/template/evolution-api  
   Se o link mudar, procure "Evolution API" em https://railway.com/templates.
3. Clique em **Deploy Now**. O template ja sobe a Evolution, o Postgres e o Redis.
4. Nas variaveis do servico da Evolution, confira ou defina:
   - `AUTHENTICATION_API_KEY`: invente uma senha longa. **Guarde, e a sua chave da API.**
   - `SERVER_URL`: a URL publica que o Railway gerou (Settings > Networking > Generate Domain).
5. Abra `https://SUA-URL/manager`, entre com a chave e clique em **+ Instance**.
   - Name: `avior` (ou outro nome; esse nome e o `EVOLUTION_INSTANCE`).
   - Channel: Baileys.
6. Clique na instancia e escaneie o **QR Code** com o WhatsApp do numero que vai mandar as mensagens
   (Configuracoes > Aparelhos conectados > Conectar aparelho).

Dica: use um chip dedicado, nao o seu numero principal. Uma mensagem por semana e volume baixo,
mas e API nao oficial, e o WhatsApp pode bloquear numeros que ele considere automatizados.

## Passo 2: descobrir o ID do grupo

Com a instancia conectada, no manager clique em **Groups** (ou chame a API):

```
GET https://SUA-URL/group/fetchAllGroups/avior?getParticipants=false
Header: apikey: SUA_CHAVE
```

Procure o grupo pelo nome e copie o campo `id`. Ele tem este formato:

```
120363XXXXXXXXXX@g.us
```

Esse e o `grupo_jid`.

## Passo 3: criar as tabelas no Supabase

No painel do Supabase > **SQL Editor**, cole e rode o arquivo
`supabase/migrations/20260910000000_agente_whatsapp.sql`.

Depois insira a configuracao do envio. Escolha UMA das duas formas:

**Mensagem fixa (sempre a mesma):**

```sql
insert into public.agente_whatsapp_config (nome, grupo_jid, mensagem_fixa)
values (
  'Bom dia da semana',
  '120363XXXXXXXXXX@g.us',
  'Bom dia, pessoal! Boa semana para todos.'
);
```

**Mensagem escrita por IA toda semana (precisa do Passo 5):**

```sql
insert into public.agente_whatsapp_config (nome, grupo_jid, briefing_ia)
values (
  'Bom dia da semana',
  '120363XXXXXXXXXX@g.us',
  'Mensagem de bom dia de segunda-feira para um grupo de empreendedores de servicos.
   Tom acolhedor e direto, no maximo 4 linhas. Traga uma reflexao curta sobre gestao,
   processos ou rotina. Assine como Juliana.'
);
```

Se preencher os dois campos, a IA tem prioridade. Para pausar sem apagar, marque `ativo = false`.

## Passo 4: publicar a Edge Function

Opcao A, sem instalar nada: mande o Claude publicar (ele tem acesso ao seu Supabase),
dizendo qual projeto usar.

Opcao B, pela linha de comando:

```bash
npm i -g supabase
supabase login
cd whatsapp-agent
supabase functions deploy enviar-segunda --project-ref SEU_PROJECT_REF --no-verify-jwt
```

`--no-verify-jwt` e proposital: a funcao se protege com o segredo `x-cron-secret`, nao com JWT.

## Passo 5: cadastrar os segredos

Painel do Supabase > **Edge Functions > Secrets** (ou `supabase secrets set ...`):

| Segredo | Valor |
|---|---|
| `EVOLUTION_URL` | URL publica da Evolution no Railway (sem barra no final) |
| `EVOLUTION_APIKEY` | a `AUTHENTICATION_API_KEY` do Passo 1 |
| `EVOLUTION_INSTANCE` | `avior` (o nome da instancia) |
| `CRON_SECRET` | invente uma senha longa; vai ser usada tambem no Passo 7 |
| `ANTHROPIC_API_KEY` | so se for usar a mensagem por IA. Crie em https://console.anthropic.com |

`SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` ja existem automaticamente dentro da funcao.

## Passo 6: testar agora, sem esperar segunda

```bash
curl -X POST "https://SEU_PROJECT_REF.supabase.co/functions/v1/enviar-segunda?teste=1" \
  -H "x-cron-secret: SEU_CRON_SECRET"
```

A mensagem deve chegar no grupo. Se der erro, o motivo fica em:

```sql
select * from public.agente_whatsapp_envios order by enviado_em desc limit 5;
```

## Passo 7: ligar o relogio de segunda-feira

No **SQL Editor**, abra `supabase/cron.sql`, troque `SEU_PROJECT_REF` e `SEU_CRON_SECRET`
pelos valores reais e rode. Pronto: toda segunda as 09:00 (Brasilia) a funcao dispara.

Para mudar o horario, edite a expressao cron. Lembre que ela e em UTC (Brasilia + 3h):

| Horario em Brasilia | Expressao |
|---|---|
| 07:00 | `0 10 * * 1` |
| 08:00 | `0 11 * * 1` |
| 09:00 | `0 12 * * 1` |
| 18:00 | `0 21 * * 1` |

---

## Manutencao

- **Trocar o texto ou o briefing:** edite a linha em `agente_whatsapp_config`. Nao precisa republicar nada.
- **Mais de um grupo:** insira mais linhas na tabela. A funcao envia para todas as ativas.
- **Historico:** tabela `agente_whatsapp_envios` guarda toda mensagem enviada e todo erro.
- **WhatsApp desconectou:** abra o manager da Evolution e escaneie o QR Code de novo.
- **Pausar:** `update agente_whatsapp_config set ativo = false;`

## Como a IA funciona (se ativar)

A funcao usa o modelo `claude-opus-5` com um sistema de fallback automatico: se o modelo
recusar algum pedido por politica, a API reenvia sozinha para um modelo alternativo na mesma
chamada. Custo por mensagem semanal: centavos.
