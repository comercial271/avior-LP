-- ============================================================
-- FASE 1A — 14 CHECK constraints + 1 trigger corretivo
-- Todas medidas com ZERO violacao em 2026-08-30. Entram VALID.
-- Nenhuma linha e alterada por esta migracao.
-- ============================================================

-- ---------- UP ----------

-- ORDEM DE DATAS (8)
ALTER TABLE public.colaboradores_rescisao_afastamentos
  ADD CONSTRAINT chk_ra_afastamento_periodo
  CHECK (afastamento_inicio IS NULL OR afastamento_fim IS NULL OR afastamento_fim >= afastamento_inicio);

ALTER TABLE public.colaboradores_ferias
  ADD CONSTRAINT chk_ferias_gozo_ordem
  CHECK (data_inicio_gozo_1 IS NULL OR data_inicio_gozo_2 IS NULL OR data_inicio_gozo_2 >= data_inicio_gozo_1);

ALTER TABLE public.colaborador_beneficio_valor
  ADD CONSTRAINT chk_cbv_vigencia_ordem
  CHECK (vigencia_fim IS NULL OR vigencia_fim >= vigencia_inicio);

ALTER TABLE public.valores_beneficios
  ADD CONSTRAINT chk_vb_vigencia_ordem
  CHECK (vigencia_inicio IS NULL OR vigencia_fim IS NULL OR vigencia_fim >= vigencia_inicio);

ALTER TABLE public.beneficio_calculo_quinzenal
  ADD CONSTRAINT chk_bcq_periodo_ordem
  CHECK (data_fim >= data_inicio);

ALTER TABLE public.beneficio_calculo_quinzenal
  ADD CONSTRAINT chk_bcq_complementar_ordem
  CHECK (data_inicio_complementar IS NULL OR data_fim_complementar IS NULL
         OR data_fim_complementar >= data_inicio_complementar);

ALTER TABLE public.efetividade_reprocess_queue
  ADD CONSTRAINT chk_erq_periodo_ordem
  CHECK (data_fim >= data_inicio);

ALTER TABLE public.ponto_importacao_log
  ADD CONSTRAINT chk_pil_periodo_ordem
  CHECK (data_fim >= data_inicio);

-- FAIXAS NUMERICAS (6)
ALTER TABLE public.ponto_registros
  ADD CONSTRAINT chk_ponto_total_horas_faixa
  CHECK (total_horas IS NULL OR (total_horas >= 0 AND total_horas <= 24));

-- espelha o CHECK que horas_atestado ja tem na MESMA tabela
ALTER TABLE public.efetividade_diaria
  ADD CONSTRAINT chk_efet_horas_trabalhadas_faixa
  CHECK (horas_trabalhadas IS NULL OR (horas_trabalhadas >= 0 AND horas_trabalhadas <= 24));

ALTER TABLE public.colaboradores_ferias
  ADD CONSTRAINT chk_ferias_dias_gozo_faixa
  CHECK (dias_gozo IS NULL OR (dias_gozo >= 0 AND dias_gozo <= 30));

ALTER TABLE public.valores_beneficios
  ADD CONSTRAINT chk_vb_valor_nonneg
  CHECK (valor IS NULL OR valor >= 0);

ALTER TABLE public.valores_beneficios
  ADD CONSTRAINT chk_vb_percentual_faixa
  CHECK (percentual IS NULL OR (percentual >= 0 AND percentual <= 100));

ALTER TABLE public.colaborador_beneficio_valor
  ADD CONSTRAINT chk_cbv_valor_nonneg
  CHECK (valor_unitario >= 0);

-- INTEGRIDADE DE IDENTIDADE (1 trigger)
-- Nao rejeita: PREENCHE a matricula a partir do colaborador_id, eliminando
-- a classe do problema em vez de so recusa-la. Hoje ha 0 divergencias.
CREATE OR REPLACE FUNCTION public.sincronizar_matricula_ponto()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $fn$
BEGIN
  SELECT c.matricula INTO NEW.matricula
  FROM public.colaboradores c WHERE c.id = NEW.colaborador_id;
  RETURN NEW;
END $fn$;

CREATE TRIGGER trg_sincronizar_matricula_ponto
  BEFORE INSERT OR UPDATE OF colaborador_id, matricula ON public.ponto_registros
  FOR EACH ROW EXECUTE FUNCTION public.sincronizar_matricula_ponto();


-- ---------- DOWN (reversao completa, nao toca em nenhuma linha) ----------
-- DROP TRIGGER IF EXISTS trg_sincronizar_matricula_ponto ON public.ponto_registros;
-- DROP FUNCTION IF EXISTS public.sincronizar_matricula_ponto();
-- ALTER TABLE public.colaborador_beneficio_valor        DROP CONSTRAINT IF EXISTS chk_cbv_valor_nonneg;
-- ALTER TABLE public.valores_beneficios                 DROP CONSTRAINT IF EXISTS chk_vb_percentual_faixa;
-- ALTER TABLE public.valores_beneficios                 DROP CONSTRAINT IF EXISTS chk_vb_valor_nonneg;
-- ALTER TABLE public.colaboradores_ferias               DROP CONSTRAINT IF EXISTS chk_ferias_dias_gozo_faixa;
-- ALTER TABLE public.efetividade_diaria                 DROP CONSTRAINT IF EXISTS chk_efet_horas_trabalhadas_faixa;
-- ALTER TABLE public.ponto_registros                    DROP CONSTRAINT IF EXISTS chk_ponto_total_horas_faixa;
-- ALTER TABLE public.ponto_importacao_log               DROP CONSTRAINT IF EXISTS chk_pil_periodo_ordem;
-- ALTER TABLE public.efetividade_reprocess_queue        DROP CONSTRAINT IF EXISTS chk_erq_periodo_ordem;
-- ALTER TABLE public.beneficio_calculo_quinzenal        DROP CONSTRAINT IF EXISTS chk_bcq_complementar_ordem;
-- ALTER TABLE public.beneficio_calculo_quinzenal        DROP CONSTRAINT IF EXISTS chk_bcq_periodo_ordem;
-- ALTER TABLE public.valores_beneficios                 DROP CONSTRAINT IF EXISTS chk_vb_vigencia_ordem;
-- ALTER TABLE public.colaborador_beneficio_valor        DROP CONSTRAINT IF EXISTS chk_cbv_vigencia_ordem;
-- ALTER TABLE public.colaboradores_ferias               DROP CONSTRAINT IF EXISTS chk_ferias_gozo_ordem;
-- ALTER TABLE public.colaboradores_rescisao_afastamentos DROP CONSTRAINT IF EXISTS chk_ra_afastamento_periodo;
