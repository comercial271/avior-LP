-- Tabelas do agente de WhatsApp (mensagem semanal para grupo).

create table if not exists public.agente_whatsapp_config (
  id            bigint generated always as identity primary key,
  nome          text not null,                 -- apelido, ex.: "Bom dia comunidade"
  grupo_jid     text not null,                 -- ex.: 120363XXXXXXXXXX@g.us
  mensagem_fixa text,                          -- texto fixo (usado se briefing_ia estiver vazio)
  briefing_ia   text,                          -- instrucoes para a IA escrever uma mensagem nova toda semana
  ativo         boolean not null default true,
  criado_em     timestamptz not null default now()
);

create table if not exists public.agente_whatsapp_envios (
  id         bigint generated always as identity primary key,
  config_id  bigint references public.agente_whatsapp_config(id) on delete set null,
  grupo_jid  text not null,
  mensagem   text,
  origem     text not null,                    -- 'fixa' ou 'ia'
  status     text not null,                    -- 'enviado' ou 'erro'
  detalhe    text,                             -- resposta da Evolution ou mensagem de erro
  teste      boolean not null default false,   -- true quando disparado manualmente com ?teste=1
  enviado_em timestamptz not null default now()
);

-- Ninguem acessa pela API publica; so a Edge Function (service role) le e escreve.
alter table public.agente_whatsapp_config enable row level security;
alter table public.agente_whatsapp_envios enable row level security;

-- Exemplo de configuracao (edite antes de rodar ou insira depois pelo painel):
-- insert into public.agente_whatsapp_config (nome, grupo_jid, mensagem_fixa)
-- values ('Bom dia da semana', '120363XXXXXXXXXX@g.us', 'Bom dia, pessoal! Boa semana para todos.');
