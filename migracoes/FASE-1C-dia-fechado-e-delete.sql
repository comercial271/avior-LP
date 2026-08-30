-- ============================================================
-- FASE 1C — travas de estado · aplicado 2026-08-30
-- ============================================================
-- 1) protect_closed_day cobria UPDATE e DELETE, nunca INSERT. Um dia ja fechado
--    e conferido aceitava lancamento NOVO. Confirmado por teste no E2E.
--    O motor de reprocessamento e ISENTO: engine_reprocessa_periodo ja monta
--    _fechado_global para excluir dias fechados, e seta app.engine_reprocess.
--    A trava mira o lancamento manual.
-- 2) DELETE de colaborador. A RLS ja impede o usuario da aplicacao (nao existe
--    policy de DELETE em colaboradores — so insert/select/update). Esta trigger
--    fecha tambem service-role e conexao direta, tornando a regra declarada do
--    projeto real na camada mais baixa.
--
-- NAO INCLUIDO nesta fase: CHECK em escalas_audit.action. A coluna e escrita por
-- 4 funcoes do banco (cancelar_movimentacao_escala, criar_movimentacao_escala,
-- substituir_escala_atomico, tg_hub_escala_outbox), 1 cron (ativar-escalas-futuras)
-- e varios caminhos do front. Um CHECK com lista incompleta faria o insert de
-- auditoria falhar DENTRO da transacao da RPC, abortando a movimentacao inteira.
-- Exige inventario completo dos literais antes.

-- ---------- UP ----------
CREATE OR REPLACE FUNCTION public.protect_closed_day_ins() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_locked boolean;
BEGIN
  IF public.is_engine_reprocess() THEN RETURN NEW; END IF;
  SELECT EXISTS (
    SELECT 1 FROM public.efetividade_dia_fechamento
    WHERE data_referencia = NEW.data_referencia AND reaberto_em IS NULL
  ) INTO v_locked;
  IF v_locked THEN
    RAISE EXCEPTION 'Dia % está fechado — não é possível incluir lançamento novo. Reabra o dia em Efetividade → Auditoria de Efetividade (perfil admin) antes de lançar.', NEW.data_referencia;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_protect_closed_day_ins
  BEFORE INSERT ON public.efetividade_diaria
  FOR EACH ROW EXECUTE FUNCTION public.protect_closed_day_ins();

CREATE OR REPLACE FUNCTION public.bloquear_delete_colaborador() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'Colaborador não pode ser excluído — o histórico precisa ser preservado. Inative o cadastro (status "Inativo") registrando data e causa da rescisão.';
END $$;

CREATE TRIGGER trg_bloquear_delete_colaborador
  BEFORE DELETE ON public.colaboradores
  FOR EACH ROW EXECUTE FUNCTION public.bloquear_delete_colaborador();

-- ---------- DOWN ----------
-- DROP TRIGGER IF EXISTS trg_bloquear_delete_colaborador ON public.colaboradores;
-- DROP FUNCTION IF EXISTS public.bloquear_delete_colaborador();
-- DROP TRIGGER IF EXISTS trg_protect_closed_day_ins ON public.efetividade_diaria;
-- DROP FUNCTION IF EXISTS public.protect_closed_day_ins();

-- ---------- VERIFICACAO (6/6 em transacao revertida) ----------
-- INSERT manual em dia fechado ............... bloqueou
-- INSERT em dia aberto ....................... aceitou
-- UPDATE em dia fechado (regressao) .......... bloqueou
-- INSERT do MOTOR (GUC ligado) em dia fechado. aceitou  <- reprocessamento preservado
-- DELETE de colaborador ...................... bloqueou
-- UPDATE de colaborador (regressao) .......... aceitou
