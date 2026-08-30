-- ============================================================================
-- FASE 1B — as duas travas de data que faltaram
-- Projeto: ALMIRA (Lovable gestao-foco-rh, 7ec3c535-767b-4c7c-bae3-705b8dee1492)
-- Data: 2026-08-30
--
-- CONTEXTO
--   A Fase 1B do PLANO-CORRECAO-ALMIRA.md previa 3 travas. Uma delas
--   (escalas_data_fim_apos_inicio) JA EXISTIA antes deste trabalho, criada
--   NOT VALID por outra pessoa — conferido em pg_constraint. As outras duas
--   nunca foram aplicadas. Este arquivo aplica as duas que faltavam.
--
-- PRINCIPIO
--   Barrar o dado novo, preservar o dado velho. Nada aqui altera linha
--   existente. As 2 linhas legadas em desacordo continuam exatamente como
--   estao e vao para a tela de pendencias (Fase 5.1).
--
-- BASE MEDIDA ANTES DE APLICAR (2026-08-30)
--   colaboradores ............................................ 99 linhas
--     com data_inicio_operacional < data_admissao ............... 1 linha
--   colaboradores_rescisao_afastamentos ...................... 99 linhas
--     com rescisao_data < colaboradores.data_admissao ........... 1 linha
--     com afastamento_inicio < data_admissao .................... 0 linhas
--     com afastamento_fim < afastamento_inicio .................. 0 linhas
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. data_inicio_operacional nao pode ser anterior a data_admissao
-- ----------------------------------------------------------------------------
-- POR QUE IMPORTA: preCheckCalculo usa `data_inicio_operacional || data_admissao`,
-- com a operacional tendo precedencia. Uma operacional anterior a admissao faz o
-- colaborador ficar elegivel a beneficio antes de ter sido admitido.
--
-- NOT VALID: a regra passa a valer para INSERT e UPDATE, mas o Postgres nao
-- revalida as 99 linhas existentes. A 1 linha legada sobrevive intacta.

ALTER TABLE public.colaboradores
  ADD CONSTRAINT chk_colab_operacional_apos_admissao
  CHECK (
    data_inicio_operacional IS NULL
    OR data_admissao IS NULL
    OR data_inicio_operacional >= data_admissao
  ) NOT VALID;

COMMENT ON CONSTRAINT chk_colab_operacional_apos_admissao ON public.colaboradores IS
  'Fase 1B: inicio operacional nunca antes da admissao. NOT VALID por causa de 1 linha legada (ver migracoes/BASELINE-2026-08-30.md).';


-- ----------------------------------------------------------------------------
-- 2. rescisao_data nao pode ser anterior a data_admissao
-- ----------------------------------------------------------------------------
-- POR QUE E TRIGGER E NAO CHECK: a regra cruza duas tabelas
-- (colaboradores_rescisao_afastamentos x colaboradores). CHECK nao enxerga
-- outra tabela.
--
-- ESCOPO DELIBERADO: BEFORE INSERT OR UPDATE OF rescisao_data, colaborador_id.
-- Nao dispara em UPDATE de outras colunas, entao a linha legada pode continuar
-- sendo editada (faltas, aviso previo) sem esbarrar na trava.
--
-- CONVIVENCIA: esta tabela ja tem 5 triggers. Esta entra como BEFORE, antes de
-- todas as AFTER (trg_encerrar_escalas_pos_rescisao, trg_sync_status_from_ra,
-- trg_enqueue_efetividade_from_rescisao), de forma que um valor recusado nao
-- chega a disparar nenhum efeito colateral.

CREATE OR REPLACE FUNCTION public.validar_rescisao_apos_admissao()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_admissao date;
  v_nome     text;
BEGIN
  IF NEW.rescisao_data IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT c.data_admissao, c.nome_completo
    INTO v_admissao, v_nome
    FROM public.colaboradores c
   WHERE c.id = NEW.colaborador_id;

  IF v_admissao IS NULL THEN
    RETURN NEW;  -- sem admissao registrada nao ha o que comparar
  END IF;

  IF NEW.rescisao_data < v_admissao THEN
    RAISE EXCEPTION
      'RESCISAO_ANTES_ADMISSAO: a data de rescisao (%) e anterior a data de admissao (%) de %. Corrija a data de rescisao, ou a data de admissao na ficha do colaborador.',
      to_char(NEW.rescisao_data, 'DD/MM/YYYY'),
      to_char(v_admissao,        'DD/MM/YYYY'),
      coalesce(v_nome, 'colaborador');
  END IF;

  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.validar_rescisao_apos_admissao() IS
  'Fase 1B: impede rescisao anterior a admissao. Nasce valendo para dado novo; nao revalida o existente.';

DROP TRIGGER IF EXISTS trg_validar_rescisao_apos_admissao
  ON public.colaboradores_rescisao_afastamentos;

CREATE TRIGGER trg_validar_rescisao_apos_admissao
  BEFORE INSERT OR UPDATE OF rescisao_data, colaborador_id
  ON public.colaboradores_rescisao_afastamentos
  FOR EACH ROW
  EXECUTE FUNCTION public.validar_rescisao_apos_admissao();


-- ============================================================================
-- DOWN — reversao completa, escrita ANTES da aplicacao
-- ============================================================================
--
-- DROP TRIGGER IF EXISTS trg_validar_rescisao_apos_admissao
--   ON public.colaboradores_rescisao_afastamentos;
--
-- DROP FUNCTION IF EXISTS public.validar_rescisao_apos_admissao();
--
-- ALTER TABLE public.colaboradores
--   DROP CONSTRAINT IF EXISTS chk_colab_operacional_apos_admissao;
--
-- Nenhuma linha e alterada por este arquivo, entao o DOWN restitui o estado
-- exato anterior: 99 colaboradores, 99 linhas de rescisao/afastamento.
--
-- ============================================================================
-- VERIFICACAO — rodar depois de aplicar
-- ============================================================================
--
-- -- (a) as duas travas existem e a CHECK esta NOT VALID
-- select conname, convalidated, pg_get_constraintdef(oid)
--   from pg_constraint
--  where conname = 'chk_colab_operacional_apos_admissao';
--
-- select tgname, pg_get_triggerdef(oid)
--   from pg_trigger
--  where tgname = 'trg_validar_rescisao_apos_admissao';
--
-- -- (b) contagem identica ao baseline
-- select (select count(*) from public.colaboradores) as colab,          -- 99
--        (select count(*) from public.colaboradores_rescisao_afastamentos) as ra;  -- 99
--
-- -- (c) as 2 linhas legadas continuam la, intactas
-- select count(*) from public.colaboradores
--  where data_inicio_operacional < data_admissao;                       -- 1
-- select count(*) from public.colaboradores_rescisao_afastamentos ra
--   join public.colaboradores c on c.id = ra.colaborador_id
--  where ra.rescisao_data < c.data_admissao;                            -- 1
