-- ============================================================================
-- FASE 1D (complemento) — duracao zero nos 15 pares de horario da escala
-- Projeto: ALMIRA (Lovable gestao-foco-rh, 7ec3c535-767b-4c7c-bae3-705b8dee1492)
-- Data: 2026-08-30
--
-- POR QUE ESTE ARQUIVO EXISTE
--   Na Fase 1D eu apliquei `CHECK (dom_fim <> dom_inicio)` so no par `dom`, na
--   forma estrita e NOT VALID. A revisao do plano achou dois problemas nisso:
--
--   1. A forma estrita CONTRADIZ o proprio front. `isRealShift`
--      (src/lib/escalaUtils.ts:20-27) trata `00:00:00/00:00:00` DE PROPOSITO
--      como "nao e turno real" — e o EscalaDetail.tsx renderiza com base nisso.
--      Ou seja: o banco chamava de invalido exatamente o que o front chama de
--      "sem turno". Alem disso, minha propria funcao `seg_semana_escala`
--      (FASE-1D) ja devolve `'{}'` quando fim = inicio, pela mesma semantica.
--
--   2. Os outros 14 pares ficaram sem trava nenhuma.
--
-- A REGRA ESCOLHIDA (forma "a" do plano)
--   Par igual so e tolerado quando ambos sao `00:00:00` — o sentinela legado
--   que as tres camadas ja sabem ler. Qualquer outro par igual (08:00-08:00,
--   14:30-14:30) e erro de digitacao e passa a ser recusado.
--
--   A alternativa era normalizar `00:00/00:00` para NULL, mas isso e ALTERAR
--   DADO DO USUARIO, o que esta vetado. Esta forma respeita as tres camadas
--   sem tocar em uma linha sequer.
--
-- NAO E URGENTE, E ISSO ESTA MEDIDO
--   A interface JA barra o caso comum: EscalaForm.tsx, em `handleSaveClick`,
--   recusa `inicio === fim` nos 7 dias, turno 1 e turno 2, e no horario padrao
--   do 12x36, com mensagem que ensina o caminho certo. Isto aqui e defesa em
--   profundidade para os caminhos que nao passam pelo formulario (carga em
--   lote, RPC, service role, conexao direta).
--
-- BASE MEDIDA ANTES DE APLICAR (2026-08-30) — 176 escalas, 15 pares cada
--   pares com inicio = fim ................................ 7
--   destes, no sentinela `00:00:00` ....................... 7   (tolerados)
--   destes, em outro horario .............................. 0   (violariam)
--   => TODAS as 15 constraints entram VALID. Zero risco.
--
--   Os 7 estao todos na MESMA linha: escala f1f681de-d8a0-4057-90c3-ef9162cfe1bb,
--   status `encerrado`, vigencia 07/05/2026 a 28/05/2026 — `dom` e os seis
--   turnos-2 de seg a sab. Esta linha e a 8a linha legada (o plano dizia 7).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 0. Substituir a constraint estrita do domingo pela forma coerente
-- ----------------------------------------------------------------------------
-- A antiga (`chk_escala_dom_duracao_nao_zero`, NOT VALID) proibia o sentinela.
-- Sai e entra de novo na forma "a", desta vez VALID.

ALTER TABLE public.escalas DROP CONSTRAINT IF EXISTS chk_escala_dom_duracao_nao_zero;


-- ----------------------------------------------------------------------------
-- 1. Os 15 pares
-- ----------------------------------------------------------------------------
-- Leitura de cada CHECK: e valido a menos que os dois lados existam, sejam
-- iguais, e nao sejam o sentinela `00:00:00`.

ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_seg_duracao_nao_zero
  CHECK (seg_inicio IS NULL OR seg_fim IS NULL OR seg_fim <> seg_inicio OR seg_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_ter_duracao_nao_zero
  CHECK (ter_inicio IS NULL OR ter_fim IS NULL OR ter_fim <> ter_inicio OR ter_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_qua_duracao_nao_zero
  CHECK (qua_inicio IS NULL OR qua_fim IS NULL OR qua_fim <> qua_inicio OR qua_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_qui_duracao_nao_zero
  CHECK (qui_inicio IS NULL OR qui_fim IS NULL OR qui_fim <> qui_inicio OR qui_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_sex_duracao_nao_zero
  CHECK (sex_inicio IS NULL OR sex_fim IS NULL OR sex_fim <> sex_inicio OR sex_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_sab_duracao_nao_zero
  CHECK (sab_inicio IS NULL OR sab_fim IS NULL OR sab_fim <> sab_inicio OR sab_inicio = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_dom_duracao_nao_zero
  CHECK (dom_inicio IS NULL OR dom_fim IS NULL OR dom_fim <> dom_inicio OR dom_inicio = '00:00:00'::time);

ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_seg2_duracao_nao_zero
  CHECK (seg_inicio_2 IS NULL OR seg_fim_2 IS NULL OR seg_fim_2 <> seg_inicio_2 OR seg_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_ter2_duracao_nao_zero
  CHECK (ter_inicio_2 IS NULL OR ter_fim_2 IS NULL OR ter_fim_2 <> ter_inicio_2 OR ter_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_qua2_duracao_nao_zero
  CHECK (qua_inicio_2 IS NULL OR qua_fim_2 IS NULL OR qua_fim_2 <> qua_inicio_2 OR qua_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_qui2_duracao_nao_zero
  CHECK (qui_inicio_2 IS NULL OR qui_fim_2 IS NULL OR qui_fim_2 <> qui_inicio_2 OR qui_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_sex2_duracao_nao_zero
  CHECK (sex_inicio_2 IS NULL OR sex_fim_2 IS NULL OR sex_fim_2 <> sex_inicio_2 OR sex_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_sab2_duracao_nao_zero
  CHECK (sab_inicio_2 IS NULL OR sab_fim_2 IS NULL OR sab_fim_2 <> sab_inicio_2 OR sab_inicio_2 = '00:00:00'::time);
ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_dom2_duracao_nao_zero
  CHECK (dom_inicio_2 IS NULL OR dom_fim_2 IS NULL OR dom_fim_2 <> dom_inicio_2 OR dom_inicio_2 = '00:00:00'::time);

ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_padrao_duracao_nao_zero
  CHECK (hora_inicio_padrao IS NULL OR hora_fim_padrao IS NULL
         OR hora_fim_padrao <> hora_inicio_padrao OR hora_inicio_padrao = '00:00:00'::time);


-- ============================================================================
-- DOWN — reversao completa, escrita ANTES da aplicacao
-- ============================================================================
--
-- ALTER TABLE public.escalas
--   DROP CONSTRAINT IF EXISTS chk_escala_seg_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_ter_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_qua_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_qui_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_sex_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_sab_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_dom_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_seg2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_ter2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_qua2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_qui2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_sex2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_sab2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_dom2_duracao_nao_zero,
--   DROP CONSTRAINT IF EXISTS chk_escala_padrao_duracao_nao_zero;
--
-- -- e, para voltar EXATAMENTE ao estado anterior, recriar a estrita do domingo:
-- ALTER TABLE public.escalas ADD CONSTRAINT chk_escala_dom_duracao_nao_zero
--   CHECK (dom_inicio IS NULL OR dom_fim IS NULL OR dom_fim <> dom_inicio) NOT VALID;
--
-- Nenhuma linha e alterada por este arquivo. O DOWN restitui o estado exato.
--
-- ============================================================================
-- VERIFICACAO — rodar depois de aplicar
-- ============================================================================
--
-- -- (a) as 15 existem e TODAS estao VALID
-- select conname, convalidated from pg_constraint
--  where conrelid = 'public.escalas'::regclass and conname like 'chk_escala_%_duracao_nao_zero'
--  order by conname;                                   -- 15 linhas, convalidated = true
--
-- -- (b) contagem identica ao baseline
-- select count(*) from public.escalas;                 -- 176
--
-- -- (c) a linha legada continua la, com os 7 pares no sentinela
-- select id, status from public.escalas
--  where id = 'f1f681de-d8a0-4057-90c3-ef9162cfe1bb';  -- 1 linha, `encerrado`
