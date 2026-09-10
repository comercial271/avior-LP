// Agente de WhatsApp: envia uma mensagem para um grupo toda segunda-feira.
// Roda como Supabase Edge Function, disparada pelo pg_cron (ver ../../cron.sql).
//
// Segredos necessarios (Supabase > Edge Functions > Secrets):
//   EVOLUTION_URL       ex.: https://minha-evolution.up.railway.app
//   EVOLUTION_APIKEY    a AUTHENTICATION_API_KEY configurada na Evolution
//   EVOLUTION_INSTANCE  nome da instancia criada na Evolution (ex.: avior)
//   CRON_SECRET         segredo que o pg_cron manda no header x-cron-secret
//   ANTHROPIC_API_KEY   opcional; so precisa se quiser a mensagem gerada por IA
//
// A configuracao da mensagem e do grupo fica na tabela agente_whatsapp_config,
// assim voce troca o texto sem reimplantar a funcao.

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
import Anthropic from "npm:@anthropic-ai/sdk";

type Config = {
  id: number;
  nome: string;
  grupo_jid: string;
  mensagem_fixa: string | null;
  briefing_ia: string | null;
  ativo: boolean;
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

function env(name: string): string {
  const v = Deno.env.get(name);
  if (!v) throw new Error(`Segredo ${name} nao configurado`);
  return v;
}

async function gerarMensagemIA(briefing: string): Promise<string> {
  const client = new Anthropic({ apiKey: env("ANTHROPIC_API_KEY") });
  const hoje = new Date().toLocaleDateString("pt-BR", {
    timeZone: "America/Sao_Paulo",
    weekday: "long",
    day: "2-digit",
    month: "long",
  });

  const response = await client.beta.messages.create({
    model: "claude-opus-5",
    max_tokens: 2000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system:
      "Voce escreve mensagens curtas de WhatsApp em portugues do Brasil para um grupo. " +
      "Responda APENAS com o texto final da mensagem, pronto para enviar, sem titulo, " +
      "sem aspas e sem comentarios. Use no maximo 3 emojis. Nunca invente dados, links ou promocoes.",
    messages: [
      {
        role: "user",
        content: `Hoje e ${hoje}. Escreva a mensagem desta semana seguindo este briefing:\n\n${briefing}`,
      },
    ],
  });

  if (response.stop_reason === "refusal") {
    throw new Error("A IA recusou gerar a mensagem desta semana");
  }
  const texto = response.content
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
  if (!texto) throw new Error("A IA devolveu uma mensagem vazia");
  return texto;
}

async function enviarWhatsApp(grupoJid: string, texto: string) {
  const url = `${env("EVOLUTION_URL").replace(/\/$/, "")}/message/sendText/${env("EVOLUTION_INSTANCE")}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: env("EVOLUTION_APIKEY"),
    },
    body: JSON.stringify({ number: grupoJid, text: texto }),
  });
  const body = await res.text();
  if (!res.ok) throw new Error(`Evolution respondeu ${res.status}: ${body}`);
  return body;
}

Deno.serve(async (req: Request) => {
  // Autenticacao simples por segredo compartilhado com o pg_cron.
  if (req.headers.get("x-cron-secret") !== env("CRON_SECRET")) {
    return new Response("nao autorizado", { status: 401 });
  }

  // ?teste=1 permite disparar manualmente sem esperar segunda-feira.
  const teste = new URL(req.url).searchParams.get("teste") === "1";

  const { data: configs, error } = await supabase
    .from("agente_whatsapp_config")
    .select("*")
    .eq("ativo", true);
  if (error) return new Response(error.message, { status: 500 });

  const resultados: Record<string, string>[] = [];

  for (const cfg of (configs ?? []) as Config[]) {
    let texto = "";
    let origem = "fixa";
    try {
      if (cfg.briefing_ia && Deno.env.get("ANTHROPIC_API_KEY")) {
        texto = await gerarMensagemIA(cfg.briefing_ia);
        origem = "ia";
      } else if (cfg.mensagem_fixa) {
        texto = cfg.mensagem_fixa;
      } else {
        throw new Error("Nenhuma mensagem_fixa nem briefing_ia configurado");
      }

      const resposta = await enviarWhatsApp(cfg.grupo_jid, texto);
      await supabase.from("agente_whatsapp_envios").insert({
        config_id: cfg.id,
        grupo_jid: cfg.grupo_jid,
        mensagem: texto,
        origem,
        status: "enviado",
        detalhe: resposta.slice(0, 2000),
        teste,
      });
      resultados.push({ config: cfg.nome, status: "enviado", origem });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      await supabase.from("agente_whatsapp_envios").insert({
        config_id: cfg.id,
        grupo_jid: cfg.grupo_jid,
        mensagem: texto || null,
        origem,
        status: "erro",
        detalhe: msg.slice(0, 2000),
        teste,
      });
      resultados.push({ config: cfg.nome, status: "erro", detalhe: msg });
    }
  }

  return new Response(JSON.stringify({ ok: true, resultados }, null, 2), {
    headers: { "Content-Type": "application/json" },
  });
});
