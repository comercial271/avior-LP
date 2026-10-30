"""Conteúdo do Kit IA no Negócio (7 dias).

Este arquivo é a fonte única: o PDF e as mensagens de WhatsApp são gerados
a partir daqui por gerar.py. Para trocar um prompt, edite aqui e rode de novo.
"""

TITULO = "Kit IA no Negócio"
SUBTITULO = "7 dias, 35 prompts prontos para colocar a inteligência artificial para trabalhar na sua empresa."
COMUNIDADE = "Comunidade de Tecnologia e Negócios"
ASSINATURA = "AVIOR"
HANDLE = "@sejaavior"

COMO_USAR = [
    "Funciona no ChatGPT, no Claude ou no Gemini. A versão gratuita de qualquer um já resolve.",
    "Tudo que está entre [colchetes] você troca pela informação do seu negócio. Quanto mais detalhe, melhor a resposta.",
    "A primeira resposta é um rascunho. Peça ajustes: \"mais curto\", \"mais direto\", \"no tom de quem fala com dono de empresa\".",
    "Nunca cole senha, dado bancário ou documento pessoal de cliente e funcionário. Troque nomes por iniciais.",
]

FORMULA = [
    ("Papel", "Quem a IA deve ser.", "Aja como um consultor financeiro de pequenas empresas."),
    ("Contexto", "Seu negócio, seu cliente, sua situação.", "Tenho uma empresa de limpeza com 40 funcionários em Porto Alegre."),
    ("Tarefa", "O que exatamente você quer.", "Monte uma tabela de preço por posto de trabalho."),
    ("Formato", "Como a resposta deve vir.", "Em tabela, com uma linha de explicação por item."),
]

DIAS = [
    {
        "n": 1,
        "area": "Processos",
        "titulo": "Tire a operação da sua cabeça",
        "gancho": "O processo que só existe na sua cabeça não é um processo. É um risco.",
        "ferramenta": "ChatGPT ou Claude",
        "intro": "O primeiro uso sério de IA numa empresa não é glamouroso: é documentar como as coisas são feitas. Você fala do seu jeito, a IA organiza.",
        "prompts": [
            ("Do áudio ao passo a passo",
             "Vou colar abaixo a transcrição de um áudio em que explico como fazer [nome da tarefa] na minha empresa. Transforme em um passo a passo numerado, com linguagem simples, para alguém que nunca fez essa tarefa. No final, liste os erros mais comuns e como evitar cada um.\n\n[cole a transcrição]"),
            ("Checklist de rotina",
             "Crie um checklist diário para a função de [cargo] em uma empresa de [segmento]. Divida em abertura, durante o dia e fechamento. Cada item deve ser uma ação verificável, que dê para marcar como feito ou não feito."),
            ("Mapa de quem faz o quê",
             "Minha empresa tem estas pessoas e funções: [liste nomes ou cargos e o que cada um faz]. Monte uma matriz de responsabilidades com as principais atividades da empresa, indicando quem executa, quem aprova e quem só precisa ser informado. Aponte atividades sem dono e funções sobrecarregadas."),
            ("Onde está o retrabalho",
             "Vou descrever como funciona hoje o processo de [ex.: venda até a entrega]. Identifique etapas repetidas, gargalos e pontos onde a informação se perde. Sugira uma versão mais enxuta, sem precisar contratar ninguém.\n\n[descreva o processo]"),
            ("Manual de boas-vindas",
             "Escreva um manual de boas-vindas de uma página para um novo funcionário da [nome da empresa], que atua com [segmento]. Inclua: quem somos, como nos comunicamos, horários, o que esperamos nos primeiros 30 dias e a quem recorrer em caso de dúvida. Tom acolhedor e direto."),
        ],
        "dica": "Grave os áudios no celular enquanto faz a tarefa. Em uma tarde você documenta o que estava preso há anos.",
    },
    {
        "n": 2,
        "area": "Vendas",
        "titulo": "Proposta no mesmo dia, cliente ainda quente",
        "gancho": "Quantos clientes você perdeu no intervalo entre a conversa e a proposta?",
        "ferramenta": "ChatGPT ou Claude + Gamma para o visual",
        "intro": "Venda esfria rápido. A IA encurta o tempo entre o \"gostei\" do cliente e a proposta na mão dele, e ajuda você a responder objeção sem improviso.",
        "prompts": [
            ("Proposta comercial",
             "Monte uma proposta comercial para [nome do cliente], que precisa de [serviço/produto]. Contexto da conversa: [o que o cliente disse, dores, prazos]. Valor: [preço e condições]. Estruture em: entendimento da necessidade, solução proposta, o que está incluso, investimento, próximos passos. Tom profissional, sem exagero."),
            ("Respostas para objeções",
             "Vendo [produto/serviço] para [tipo de cliente]. As objeções que mais escuto são: [ex.: está caro, vou pensar, já tenho fornecedor]. Para cada uma, escreva duas respostas curtas que eu possa falar ou mandar por WhatsApp: uma que faz pergunta e outra que traz argumento. Nada de pressão."),
            ("Follow-up que não incomoda",
             "Mandei uma proposta para [cliente] há [X dias] e ele não respondeu. Escreva 3 mensagens de follow-up para WhatsApp, para enviar com alguns dias de intervalo. Cada uma deve trazer um motivo novo para responder, não só \"e aí, conseguiu ver?\". Máximo 4 linhas cada."),
            ("Script de primeira ligação",
             "Crie um roteiro de 5 minutos para a primeira ligação com um potencial cliente de [segmento]. Objetivo: entender a necessidade e marcar uma visita ou reunião. Inclua abertura, 5 perguntas de diagnóstico e o fechamento com o convite. Linguagem natural, como conversa."),
            ("Quem é o meu cliente ideal",
             "Estes são meus 5 melhores clientes e por que eles são bons: [descreva]. A partir disso, descreva meu cliente ideal: tipo de empresa, porte, momento, dores e onde encontrar mais clientes parecidos. Termine com 3 perguntas para eu filtrar se um lead vale meu tempo."),
        ],
        "dica": "Cole o texto da proposta no Gamma (gamma.app) e ele monta a apresentação com cara de agência em minutos.",
    },
    {
        "n": 3,
        "area": "Marketing",
        "titulo": "Um mês de conteúdo em uma tarde",
        "gancho": "Você não precisa postar mais. Precisa postar com intenção.",
        "ferramenta": "ChatGPT ou Claude + Canva",
        "intro": "O problema raramente é falta de tempo. É sentar na frente da tela sem saber o que falar. A IA resolve a página em branco; a sua experiência dá o sabor.",
        "prompts": [
            ("Calendário de 30 dias",
             "Minha empresa é [descrição] e atende [público]. Crie um calendário de conteúdo para Instagram com 12 posts em 30 dias. Misture: posts que educam, que mostram bastidores, que trazem prova (cliente, resultado) e que convidam para comprar. Para cada post: tema, formato (carrossel, reels ou foto) e a primeira frase."),
            ("Legenda com gancho",
             "Escreva 3 versões de legenda para um post sobre [tema]. A primeira linha precisa fazer a pessoa parar de rolar a tela. Depois, uma história curta ou exemplo real, uma lição e um convite para comentar ou salvar. Sem emoji em excesso e sem frases de coach."),
            ("Perguntas que viram conteúdo",
             "Liste as 20 perguntas que um cliente de [segmento] costuma fazer antes de comprar [produto/serviço]. Agrupe por etapa: curiosidade, comparação e decisão. Cada pergunta pode virar um post ou um vídeo curto."),
            ("Roteiro de vídeo curto",
             "Crie um roteiro de reels de 40 segundos sobre [tema], para eu gravar falando para a câmera. Estrutura: gancho nos 3 primeiros segundos, um erro comum, o jeito certo e uma chamada para ação. Escreva frase por frase, como teleprompter."),
            ("Reaproveitar um conteúdo",
             "Abaixo está um texto que já escrevi. Transforme em: 1 carrossel de 7 slides (texto de cada slide), 1 mensagem para lista de transmissão do WhatsApp e 1 post para LinkedIn. Mantenha minhas ideias e meu jeito de falar.\n\n[cole o texto]"),
        ],
        "dica": "Antes de pedir conteúdo, cole 3 textos seus e peça: \"analise meu tom de voz e escreva sempre assim\". A diferença é enorme.",
    },
    {
        "n": 4,
        "area": "Atendimento",
        "titulo": "Responda rápido sem responder no automático",
        "gancho": "Cliente bem atendido no WhatsApp volta. Cliente que espera, pesquisa o concorrente.",
        "ferramenta": "ChatGPT ou Claude",
        "intro": "Atendimento bom é rápido e humano ao mesmo tempo. A IA prepara as respostas-base para a equipe e ajuda nas conversas difíceis.",
        "prompts": [
            ("Banco de respostas",
             "Crie um banco de mensagens prontas para o WhatsApp da [nome da empresa], que vende [produto/serviço]. Situações: primeiro contato, pedido de orçamento, informação de prazo, cobrança amigável, pós-venda e pedido de avaliação. Tom cordial e próximo, sem parecer robô. Deixe campos como [nome] para personalizar."),
            ("Cliente irritado",
             "Recebi esta reclamação de um cliente: [cole a mensagem]. O que aconteceu de fato foi: [sua versão]. Escreva uma resposta que reconheça o problema sem culpar ninguém, explique o que vamos fazer e em quanto tempo. Curta, firme e respeitosa."),
            ("FAQ da empresa",
             "Com base nas informações abaixo, monte um FAQ com as 15 dúvidas mais prováveis dos clientes, com respostas de no máximo 3 linhas. Pode ir para o site, para a mensagem automática ou para treinar a equipe.\n\n[horários, formas de pagamento, prazos, regiões atendidas, políticas]"),
            ("Pesquisa de satisfação",
             "Crie uma pesquisa de satisfação com no máximo 5 perguntas, para mandar por WhatsApp depois de [serviço/compra]. Uma pergunta de nota de 0 a 10, uma aberta e as outras rápidas de responder. Inclua a mensagem de convite, curta e simpática."),
            ("Ler as reclamações",
             "Abaixo estão reclamações e comentários de clientes dos últimos meses. Agrupe por tema, diga quais aparecem mais e quais têm maior impacto no negócio. Para os 3 principais, sugira uma ação prática para eliminar a causa.\n\n[cole os comentários]"),
        ],
        "dica": "Salve as respostas-base como \"respostas rápidas\" no WhatsApp Business. Digita / e a mensagem aparece.",
    },
    {
        "n": 5,
        "area": "Finanças",
        "titulo": "Decida olhando número, não sensação",
        "gancho": "Você precifica olhando pro seu custo. Seu cliente compara olhando pro mercado.",
        "ferramenta": "Claude ou ChatGPT (aceitam planilha) + Perplexity para pesquisa",
        "intro": "Todo dono tem planilha. Quase nenhum tem tempo de ler. A IA lê com você, faz as contas e aponta o que merece atenção.",
        "prompts": [
            ("Raio-x do mês",
             "Vou anexar a planilha de entradas e saídas da minha empresa dos últimos [X] meses. Analise: para onde está indo o dinheiro, quais despesas cresceram, quais podem ser cortadas e se existe algum padrão de mês fraco. Responda em linguagem de dono, não de contador."),
            ("Preço pelo custo real",
             "Me ajude a calcular o preço de [produto/serviço]. Meus custos: [matéria-prima, mão de obra, horas, impostos, custos fixos do mês] e vendo em média [quantidade] por mês. Quero margem de [X]%. Mostre a conta passo a passo e diga qual o preço mínimo abaixo do qual eu pago para trabalhar."),
            ("Fluxo de caixa de 90 dias",
             "Monte uma projeção de fluxo de caixa para os próximos 90 dias com estes dados: [recebimentos previstos, contas fixas, contas variáveis, parcelas]. Destaque as semanas em que o caixa fica negativo e sugira o que antecipar ou renegociar."),
            ("Pesquisa de preço do mercado",
             "Pesquise faixas de preço praticadas para [produto/serviço] em [cidade ou região] e liste as fontes. Compare com o meu preço de [valor] e me diga se estou abaixo, na média ou acima, e que argumento usar em cada caso."),
            ("Cliente que dá prejuízo",
             "Esta tabela tem meus clientes, quanto cada um paga e quanto tempo ou custo cada um consome: [cole]. Calcule a margem por cliente, ordene do mais para o menos lucrativo e aponte quem merece reajuste ou revisão de contrato."),
        ],
        "dica": "Use o Perplexity (perplexity.ai) para pesquisas de mercado: ele mostra a fonte de cada informação, então dá para conferir.",
    },
    {
        "n": 6,
        "area": "Pessoas",
        "titulo": "Contrate, treine e dê feedback melhor",
        "gancho": "Sua equipe não pergunta demais. Sua empresa é que responde de menos.",
        "ferramenta": "ChatGPT ou Claude + NotebookLM para treinamento",
        "intro": "Gestão de pessoas consome o dono. A IA não substitui a conversa, mas prepara você para ela: vaga clara, entrevista estruturada e feedback que constrói.",
        "prompts": [
            ("Anúncio de vaga que atrai",
             "Escreva um anúncio de vaga para [cargo] na [empresa], em [cidade]. Rotina: [atividades]. Requisitos: [lista]. Oferecemos: [salário, benefícios, horário]. Comece pelo que a pessoa ganha trabalhando aqui, não pela lista de exigências. Versão longa para site e curta para WhatsApp."),
            ("Roteiro de entrevista",
             "Crie um roteiro de entrevista de 30 minutos para [cargo]. Inclua 8 perguntas comportamentais (\"me conte uma vez em que...\"), o que observar em cada resposta e sinais de alerta. Foco em [ex.: pontualidade, cuidado com o cliente, trabalho em equipe]."),
            ("Feedback difícil",
             "Preciso dar um feedback para um colaborador que [descreva o comportamento, com fatos]. Ele é [contexto: tempo de casa, pontos fortes]. Monte um roteiro de conversa: como abrir, como descrever o fato sem julgar, como ouvir e como fechar com um combinado claro e prazo."),
            ("Plano dos primeiros 30 dias",
             "Monte um plano de integração de 30 dias para um novo [cargo]. Divida por semana: o que aprender, com quem, o que entregar e como saber se está indo bem. No fim, 5 perguntas para a conversa de avaliação do primeiro mês."),
            ("Treinamento em perguntas",
             "Com base no manual abaixo, crie 10 perguntas de múltipla escolha para testar se a equipe entendeu o procedimento. Inclua o gabarito e uma explicação curta para cada resposta.\n\n[cole o manual ou procedimento]"),
        ],
        "dica": "No NotebookLM (notebooklm.google.com) você sobe seus manuais e a equipe pergunta em linguagem normal. Ele responde citando o seu material.",
    },
    {
        "n": 7,
        "area": "Estratégia",
        "titulo": "Seu conselheiro disponível às 23h",
        "gancho": "A IA mais útil não é a que executa tarefa. É a que pensa o negócio com você.",
        "ferramenta": "Claude ou ChatGPT",
        "intro": "Dono de empresa decide sozinho com frequência demais. Use a IA como um sócio que faz as perguntas incômodas, sem ego e sem pressa.",
        "prompts": [
            ("Diagnóstico honesto",
             "Aja como um consultor experiente de pequenas e médias empresas. Vou descrever meu negócio: [segmento, faturamento aproximado, equipe, principais clientes, maiores problemas hoje]. Faça um diagnóstico honesto: forças, fraquezas, riscos e oportunidades. Não seja educado demais; quero clareza."),
            ("Plano de 90 dias",
             "Meu objetivo para os próximos 90 dias é [meta concreta, com número]. Hoje estou em [situação atual]. Monte um plano com no máximo 3 frentes, ações semanais para cada uma, quem é responsável e como vou medir se está funcionando."),
            ("O advogado do diabo",
             "Estou pensando em [decisão: abrir filial, contratar, lançar serviço, aumentar preço]. Meus motivos são: [liste]. Faça o papel de advogado do diabo: quais os riscos que não estou vendo, o que pode dar errado e quais perguntas preciso responder antes de decidir."),
            ("Pauta da reunião com a equipe",
             "Monte a pauta de uma reunião mensal de 45 minutos com minha equipe de [tamanho] pessoas. Quero revisar resultados, ouvir problemas e definir prioridades do mês. Inclua o tempo de cada bloco e perguntas que estimulem quem fala pouco."),
            ("Onde a IA entra no meu negócio",
             "Minha empresa faz [descrição] e as tarefas que mais consomem tempo da equipe são: [liste]. Sugira 5 usos práticos de inteligência artificial para economizar tempo, do mais simples ao mais avançado, com ferramenta sugerida, custo aproximado e por onde começar amanhã."),
        ],
        "dica": "Ferramenta sem processo vira brinquedo caro. A IA rende mais quando cultura e processo já existem. Comece pelo Dia 1.",
    },
]

FERRAMENTAS = [
    ("ChatGPT", "chatgpt.com", "Texto, ideias, planilhas e organização do dia a dia."),
    ("Claude", "claude.ai", "Textos longos, análise de documentos e planilhas, raciocínio."),
    ("Gemini", "gemini.google.com", "Integrado ao Gmail, Docs e Planilhas do Google."),
    ("Perplexity", "perplexity.ai", "Pesquisa na internet com as fontes citadas."),
    ("NotebookLM", "notebooklm.google.com", "Base de conhecimento da empresa a partir dos seus documentos."),
    ("Gamma", "gamma.app", "Apresentações e propostas visuais a partir de texto."),
    ("Canva", "canva.com", "Artes para redes sociais, com recursos de IA."),
    ("Tactiq", "tactiq.io", "Transcrição e resumo de reuniões online."),
]

# Mensagens de WhatsApp: abertura, um texto por dia e encerramento.
# Formatação do WhatsApp: *negrito*, _itálico_, ```monoespaçado```.
ABERTURA = """Bom dia, pessoal da *Comunidade de Tecnologia e Negócios*! ☀️

A partir de amanhã começa aqui o *Desafio 7 Dias de IA no Negócio*.

Todo dia eu mando *1 prompt pronto* para vocês colarem no ChatGPT, Claude ou Gemini e resolverem uma tarefa real da empresa:

1️⃣ Processos
2️⃣ Vendas
3️⃣ Marketing
4️⃣ Atendimento
5️⃣ Finanças
6️⃣ Pessoas
7️⃣ Estratégia

Não precisa saber nada de tecnologia. É copiar, trocar o que está entre [colchetes] e usar.

E quem acompanhar até o fim recebe no dia 7 o *Kit IA no Negócio* completo em PDF, com *35 prompts* organizados por área. 🎁

Bora? Responde com um 🙋 quem vai participar."""

ENCERRAMENTO_EXTRA = """🎁 *Prometido é cumprido:* segue o *Kit IA no Negócio* completo, com os *35 prompts* dos 7 dias, a fórmula para escrever qualquer prompt e a lista das ferramentas.

Salva, imprime, manda para o seu time.

E me conta aqui: *qual prompt mais te ajudou essa semana?* Quero saber o que vocês colocaram em prática. 👇"""
