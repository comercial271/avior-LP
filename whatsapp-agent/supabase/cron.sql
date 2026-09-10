-- Agendamento: chama a Edge Function toda segunda-feira as 09:00 (horario de Brasilia).
-- O pg_cron roda em UTC. Brasilia = UTC-3, entao 09:00 BRT = 12:00 UTC -> '0 12 * * 1'.
--
-- Antes de rodar, troque:
--   SEU_PROJECT_REF  -> ref do projeto Supabase (aparece na URL do painel)
--   SEU_CRON_SECRET  -> o mesmo valor salvo no segredo CRON_SECRET da Edge Function

create extension if not exists pg_cron with schema pg_catalog;
create extension if not exists pg_net with schema extensions;

-- Guarda o segredo no Vault para nao ficar em texto puro no job.
select vault.create_secret('SEU_CRON_SECRET', 'agente_whatsapp_cron_secret');

select cron.schedule(
  'agente-whatsapp-segunda',
  '0 12 * * 1',
  $$
  select net.http_post(
    url     := 'https://SEU_PROJECT_REF.supabase.co/functions/v1/enviar-segunda',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'x-cron-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'agente_whatsapp_cron_secret')
    ),
    body    := '{}'::jsonb
  );
  $$
);

-- Para conferir:   select * from cron.job;
-- Para ver execucoes: select * from cron.job_run_details order by start_time desc limit 10;
-- Para desligar:   select cron.unschedule('agente-whatsapp-segunda');
