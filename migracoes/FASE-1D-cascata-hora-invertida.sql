-- ============================================================
-- FASE 1D — sobreposicao de escala que enxerga jornada noturna
-- Aplicado 2026-08-30. Versao anterior de check_escala_overlap:
--   md5(pg_get_functiondef) = 28ec3326f81f0fb0a15550500504615e  (6767 bytes)
--
-- PROBLEMA: check_escala_overlap comparava horarios crus
--   (n_ini_1 < o_fim_1 AND o_ini_1 < n_fim_1).
-- Com um turno que vira a meia-noite (ex.: ter 18:00 -> 08:00) a comparacao
-- falha e a sobreposicao NAO e detectada. Confirmado por teste:
--   ter 20:00-22:00 contra ter 18:00->08:00  -> era ACEITO (deveria bloquear)
--   qua 06:00-10:00 contra ter 18:00->08:00  -> era ACEITO (colide na madrugada)
--
-- NAO se resolve com CHECK (fim > inicio): isso inviabilizaria turno noturno
-- de portaria, que e atividade-fim. A correcao normaliza a travessia de
-- meia-noite numa linha do tempo semanal e compara intervalos de verdade.
--
-- SEGURANCA: dos 41 pares de escalas vigentes hoje, ZERO passa a conflitar.
-- ============================================================

-- ---------- UP ----------

CREATE OR REPLACE FUNCTION public.seg_semana_escala(dia_idx int, ini time, fim time)
RETURNS int4range[] LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE s int; f int;
BEGIN
  IF ini IS NULL OR fim IS NULL THEN RETURN '{}'::int4range[]; END IF;
  s := dia_idx*1440 + (extract(hour from ini)::int*60 + extract(minute from ini)::int);
  f := dia_idx*1440 + (extract(hour from fim)::int*60 + extract(minute from fim)::int);
  -- duracao zero = nao trabalha (mesma semantica de getHoursForDay no motor)
  IF f = s THEN RETURN '{}'::int4range[]; END IF;
  IF f < s THEN f := f + 1440; END IF;              -- vira a meia-noite
  IF f <= 10080 THEN RETURN array[int4range(s,f)];
  ELSE RETURN array[int4range(s,10080), int4range(0, f-10080)];  -- sab/dom -> seg
  END IF;
END $$;

CREATE OR REPLACE FUNCTION public.escala_segmentos(e public.escalas)
RETURNS int4range[] LANGUAGE plpgsql STABLE AS $$
DECLARE dias text[] := array['dom','seg','ter','qua','qui','sex','sab'];
        idx int; i1 time; f1 time; i2 time; f2 time; out int4range[] := '{}';
BEGIN
  IF e.tipo_jornada = '12x36' THEN
    -- janela igual em todos os dias (conservador); a paridade e tratada na trigger
    FOR idx IN 0..6 LOOP
      out := out || public.seg_semana_escala(idx, e.hora_inicio_padrao, e.hora_fim_padrao);
    END LOOP;
  ELSE
    FOR idx IN 0..6 LOOP
      EXECUTE format('select ($1).%I, ($1).%I, ($1).%I, ($1).%I',
        dias[idx+1]||'_inicio', dias[idx+1]||'_fim', dias[idx+1]||'_inicio_2', dias[idx+1]||'_fim_2')
        INTO i1,f1,i2,f2 USING e;
      out := out || public.seg_semana_escala(idx,i1,f1) || public.seg_semana_escala(idx,i2,f2);
    END LOOP;
  END IF;
  RETURN out;
END $$;

CREATE OR REPLACE FUNCTION public.descrever_minuto_semana(m int) RETURNS text
LANGUAGE sql IMMUTABLE AS $$
  SELECT (array['dom','seg','ter','qua','qui','sex','sáb'])[((m/1440) % 7)+1]||' '||
         lpad((((m%1440)/60))::text,2,'0')||':'||lpad((m%60)::text,2,'0')
$$;

CREATE OR REPLACE FUNCTION public.check_escala_overlap() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE r public.escalas%rowtype; seg_new int4range[]; seg_oth int4range[];
        cli_nome text; novo_fim date; oth_fim date; ov int4range;
BEGIN
  seg_new := public.escala_segmentos(NEW);
  IF array_length(seg_new,1) IS NULL THEN RETURN NEW; END IF;
  novo_fim := coalesce(NEW.data_fim, date '9999-12-31');

  FOR r IN SELECT e.* FROM public.escalas e
    WHERE e.colaborador_id = NEW.colaborador_id
      AND e.id <> coalesce(NEW.id,'00000000-0000-0000-0000-000000000000'::uuid)
      AND (e.status IN ('ativo','futuro')
           -- cobre "Encerrar" manual seguido de "Nova Escala" fora do fluxo atomico
           OR (e.status='encerrado' AND e.updated_at > now() - interval '5 minutes'))
  LOOP
    oth_fim := coalesce(r.data_fim, date '9999-12-31');
    IF NEW.data_inicio > oth_fim OR r.data_inicio > novo_fim THEN CONTINUE; END IF;

    -- dois 12x36 em fases opostas nunca coincidem
    IF NEW.tipo_jornada='12x36' AND r.tipo_jornada='12x36'
       AND NEW.data_base_ciclo IS NOT NULL AND r.data_base_ciclo IS NOT NULL
       AND ((NEW.data_base_ciclo - date '2000-01-01') % 2) <> ((r.data_base_ciclo - date '2000-01-01') % 2)
    THEN CONTINUE; END IF;

    seg_oth := public.escala_segmentos(r);
    SELECT x*y INTO ov FROM unnest(seg_new) x, unnest(seg_oth) y WHERE x && y LIMIT 1;
    IF ov IS NOT NULL THEN
      SELECT c.nome_abreviado INTO cli_nome FROM public.clientes c WHERE c.id = r.cliente_id;
      RAISE EXCEPTION 'Conflito de escala: o colaborador já está alocado em % neste horário (% a %). Jornada que vira a meia-noite também conta. Encerre ou ajuste a escala existente antes de criar esta.',
        coalesce(cli_nome,'outro cliente'),
        public.descrever_minuto_semana(lower(ov)), public.descrever_minuto_semana(upper(ov));
    END IF;
  END LOOP;
  RETURN NEW;
END $$;

-- Turno de duracao zero nunca tem leitura possivel. Existe 1 linha assim
-- (dom 00:00-00:00), por isso NOT VALID: barra o novo, preserva o legado.
ALTER TABLE public.escalas
  ADD CONSTRAINT chk_escala_dom_duracao_nao_zero
  CHECK (dom_inicio IS NULL OR dom_fim IS NULL OR dom_fim <> dom_inicio) NOT VALID;


-- ---------- DOWN ----------
-- A trigger continua sendo check_escala_overlap; para reverter, restaure a
-- definicao anterior (md5 28ec3326f81f0fb0a15550500504615e) e rode:
-- ALTER TABLE public.escalas DROP CONSTRAINT IF EXISTS chk_escala_dom_duracao_nao_zero;
-- DROP FUNCTION IF EXISTS public.escala_segmentos(public.escalas);
-- DROP FUNCTION IF EXISTS public.seg_semana_escala(int, time, time);
-- DROP FUNCTION IF EXISTS public.descrever_minuto_semana(int);
