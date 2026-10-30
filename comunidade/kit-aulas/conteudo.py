"""Conteúdo do Kit das Aulas AVIOR (Comunidade de Tecnologia e Negócios).

Fonte única: o PDF e as mensagens de WhatsApp são gerados a partir daqui por
gerar.py. Base: gravações, transcrições e anotações das aulas de segunda
(14/09, 21/09, 28/09, 05/10 e 19/10 de 2026) e o roteiro da área de membros.
Para trocar um texto ou um prompt, edite aqui e rode `python3 gerar.py && node pdf.js`.
"""

TITULO = "Kit das Aulas"
TITULO_DESTAQUE = "IA no Negócio"
SUBTITULO = "O resumo das 5 aulas ao vivo da comunidade, com o prompt de cada aula pronto para copiar e a tarefa para aplicar na sua empresa."
COMUNIDADE = "Comunidade de Tecnologia e Negócios"
ASSINATURA = "AVIOR"
HANDLE = "@sejaavior"

INTRO = (
    "Cada aula vira duas páginas: o resumo, com o que levar e a tarefa da semana, "
    "e o prompt da aula, pronto para copiar. Não precisa seguir a ordem. "
    "Comece pela aula que resolve o que mais trava a sua empresa hoje."
)

PILARES = [
    ("Cultura", "O que o time faz quando você não está olhando. Sem um time que abrace a mudança, a ferramenta não pega."),
    ("Processos", "Tirar da sua cabeça o que hoje só funciona com você presente. Um processo por vez."),
    ("Inteligência", "IA e sistemas em cima de um processo que já funciona. Não o contrário."),
]

REGRAS = [
    "<b>Comece pela tarefa, não pela ferramenta.</b> Saiba o resultado que você quer antes de abrir a IA.",
    "<b>Dê contexto como daria a um funcionário novo.</b> Quem é a empresa, o cliente, o diferencial e o que não pode prometer. Até o óbvio precisa ser dito.",
    "<b>Diga o papel.</b> \"Atue como especialista sênior em...\" rende mais que um pedido solto.",
    "<b>Um objetivo por vez.</b> Pedido demais na mesma conversa faz a IA se perder. Conversa muito longa: abra um chat novo.",
    "<b>Coloque limites.</b> A IA tende a agradar quem usa. Peça para separar fato de hipótese e para não inventar número, preço ou promessa.",
]

CONFERENCIA = [
    ("Fonte", "Ela mostrou de onde tirou a informação? Abra o link."),
    ("Fato", "Tem número ou regra que precisa ser confirmado por você?"),
    ("Privacidade", "Troque nomes de clientes por fictícios antes de colar dados."),
    ("Decisão", "Uma pessoa responsável aprova antes de usar."),
]

AULAS = [
    {
        "n": 1,
        "data": "14/09",
        "modulo": "Processo antes da IA",
        "titulo": "Tire o processo da sua cabeça e coloque a IA para trabalhar",
        "ideia": "Sua empresa funciona sem você? Se a resposta é não, o primeiro uso de IA não é automatizar: é escrever o processo que só você sabe fazer.",
        "resumo": (
            "A Foco vivia da oralidade: tudo passava pela dona e o processo morava na cabeça dela. "
            "A virada veio colocando cultura, processo e IA nessa ordem, e o back-office foi de 14 para 5 pessoas sem desmontar a operação. "
            "Na aula, um processo real de jardinagem virou procedimento e checklist com um único prompt."
        ),
        "aprendizados": [
            "Comece pelo processo que só você sabe fazer. Ele é o seu maior gargalo e o primeiro a ser escrito.",
            "Ataque um processo por vez. Vários projetos ao mesmo tempo atrasam o resultado de todos.",
            "Antes de automatizar: questione por que o processo é assim, elimine o que não agrega, simplifique e acelere. A automação vem por último.",
            "A IA responde conforme o contexto que recebe. \"Como se faz um ovo?\" tem dez respostas certas até você dizer qual ovo quer.",
            "Antes de criar um agente, avalie quatro coisas: complexidade, valor que gera, se a IA já faz bem e o risco de errar, como um atendente de WhatsApp que informa um preço errado.",
        ],
        "frase": ("Quando as coisas estão só na nossa cabeça, ninguém sabe. E até o óbvio precisa ser dito.", "Juliana Anhaia"),
        "tarefa": "Escolha um processo que hoje só você sabe fazer, rode o prompt da aula até chegar ao procedimento e ao checklist de uma página, e entregue para alguém do time testar e dizer o que não ficou claro.",
        "prompt_nome": "Mapeamento de processo",
        "ferramenta": "ChatGPT ou Claude",
        "como_usar": [
            "Escolha um processo só. O que mais depende de você.",
            "Responda as perguntas da IA no seu jeito de falar. Pode ser por áudio.",
            "Revise o checklist com quem executa a tarefa.",
        ],
        "prompt": (
            "Você vai me ajudar a tirar um processo da minha empresa da cabeça e colocar no papel.\n\n"
            "Contexto: sou dono(a) de uma empresa de [ramo do negócio]. O processo que vamos mapear é [nome do processo]. "
            "Hoje ele está só na minha cabeça, gera ruído e retrabalho, e dá problema quando eu me afasto.\n\n"
            "Seu papel: aja como um funcionário novo, curioso e inteligente, que vai assumir esse processo e executá-lo sem mim ao lado. "
            "Seu objetivo é perguntar o necessário para conseguir rodar o processo sem a minha presença.\n\n"
            "Como perguntar: faça uma pergunta por vez e espere a minha resposta antes da próxima. Investigue como eu faço na prática, "
            "o que eu evito, o que eu decido e com base em quê, o que eu nunca deixo passar e o que é errado quando alguém faz por mim.\n\n"
            "Resultado: quando entender o processo inteiro, me avise e escreva:\n"
            "1. O procedimento em passos numerados, com as minhas regras.\n"
            "2. Um checklist de uma página para quem entrou ontem.\n"
            "3. Os três pontos onde alguém novo vai errar e o que fazer em cada caso.\n\n"
            "Regras: use a minha forma de falar e as minhas palavras. Não invente etapas nem coisas que eu não disse. "
            "Se eu for vago, pergunte de novo.\n\n"
            "Pode começar pela primeira pergunta."
        ),
        "extras": [
            ("Metaprompt: quando não souber como pedir",
             "\"Escreva um prompt para [o que você quer]. Tire suas dúvidas comigo antes e depois responda.\" E para conferir qualquer resposta: \"O que você assumiu que eu não disse? Onde essa resposta pode estar errada?\""),
        ],
    },
    {
        "n": 2,
        "data": "28/09",
        "modulo": "Processo antes da IA",
        "titulo": "Qual IA usar em cada tarefa e como fazer uma pesquisa de mercado",
        "ideia": "Quando a IA decepciona, quase sempre o problema é a escolha, não a ferramenta. É como colocar a pessoa mais comunicativa do time para analisar planilha o dia inteiro.",
        "resumo": (
            "Modelo é a tecnologia que gera a resposta (GPT, Gemini, Claude). Ferramenta é onde você usa (o chat, o NotebookLM). "
            "Tarefa é o trabalho que você quer resolver. Ao vivo, o mesmo pedido de pesquisa de mercado rodou no Claude e no ChatGPT "
            "para uma empresa de limpeza pós-obra, e a maior descoberta não foi um número."
        ),
        "aprendizados": [
            "Identifique a tarefa, escolha a ferramenta pela função (criar, pesquisar, estudar uma fonte, analisar dados, construir) e confira o resultado.",
            "Qual testar primeiro? Todas. Faça a mesma tarefa em duas ou três e fique com a que chega mais perto do resultado certo.",
            "Seu concorrente não é só quem vende igual: tem o direto, o indireto (resolve a mesma necessidade com outro produto) e o substituto.",
            "Peça para a IA separar fato de hipótese e não inventar números. Confira as fontes antes de usar.",
            "A pesquisa mostrou para a participante um diferencial que ela já entregava e não usava na venda: voltar sem custo se sobrasse poeira fina.",
        ],
        "frase": ("Não adianta ter uma Ferrari nas mãos e colocar qualquer um ao volante.", "Juliana Anhaia"),
        "tarefa": "Escolha uma tarefa que se repete toda semana, anote quanto tempo ela leva, teste em duas IAs diferentes e conte na comunidade qual entregou melhor: menos tempo, mais clareza ou menos retrabalho.",
        "prompt_nome": "Pesquisa de mercado",
        "ferramenta": "ChatGPT, Claude ou Gemini",
        "como_usar": [
            "Antes de abrir a IA, anote: o que vende, para quem, onde, 3 concorrentes e o que o cliente compraria no lugar.",
            "Se puder, ative a pesquisa na internet.",
            "Rode em duas IAs e compare as respostas.",
        ],
        "prompt": (
            "Quero que você atue como analista de mercado e me ajude a entender o mercado do meu negócio antes de qualquer decisão.\n\n"
            "Meu negócio: [o que a empresa faz]\nO que eu vendo: [produtos ou serviços]\nPara quem vendo hoje: [público]\nOnde atuo: [cidade, região ou online]\n\n"
            "Organize a pesquisa assim:\n"
            "1. Um panorama do mercado em que estou: como ele funciona e quem são os principais tipos de cliente.\n"
            "2. Qual problema o meu negócio resolve e quanto esse problema pesa para o cliente (tempo, dinheiro, risco ou incômodo).\n"
            "3. Tamanho do mercado: quem tem esse problema na minha região e se esse público está crescendo ou diminuindo.\n"
            "4. Tendências que podem afetar esse mercado nos próximos anos.\n"
            "5. Concorrentes diretos: quem vende algo parecido para o mesmo público.\n"
            "6. Concorrentes indiretos: quem atende a mesma necessidade com outro produto ou serviço.\n"
            "7. Substitutos: o que faz o cliente desistir de comprar uma solução como a minha.\n"
            "8. Como esses concorrentes se posicionam e o que prometem.\n"
            "9. Os produtos e serviços mais comuns nesse mercado e o que quase todo mundo oferece igual.\n"
            "10. Necessidades do cliente que parecem mal atendidas.\n"
            "11. Oportunidades que a minha empresa poderia explorar.\n\n"
            "Regras:\n- Separe o que é fato encontrado do que é hipótese.\n"
            "- Se não encontrar informação suficiente, diga isso claramente. Não invente números nem dados.\n"
            "- Use linguagem simples, sem termos técnicos.\n\n"
            "No final, monte uma tabela com as colunas: Concorrente | Tipo (direto, indireto ou substituto) | Público | Oferta principal | Como se posiciona | Diferencial | Oportunidade para mim"
        ),
        "extras": [
            ("Depois da pesquisa, leia com olhar de dono",
             "O que me surpreendeu? Que concorrentes eu não estava considerando? Onde o mercado parece saturado? Onde parece existir espaço? Qual oportunidade merece ser investigada?"),
        ],
    },
    {
        "n": 3,
        "data": "19/10",
        "modulo": "Vendas com IA",
        "titulo": "Como usar IA para prospectar clientes",
        "ideia": "Antes de buscar mais clientes, descubra onde a sua venda vaza. Lista nova só resolve um dos quatro problemas.",
        "resumo": (
            "As vendas vazam em quatro pontos: pouca gente chegando, gente que some no acompanhamento, perda no preço ou cliente que não volta. "
            "Quando o problema é falta de cliente novo, a IA localiza empresas com o seu perfil, cita as fontes, prioriza e escreve a primeira mensagem. "
            "Ao vivo, o prompt mestre achou cinco leads para uma empresa de jardinagem de Cachoeirinha."
        ),
        "aprendizados": [
            "Se o funil já está cheio de oportunidades paradas, mais lista só aumenta o caos. O problema está na abordagem, na proposta ou no acompanhamento.",
            "Uma boa lista começa com quatro definições: cliente ideal, território, um sinal público que justifique investigar a empresa e o canal onde está o decisor.",
            "Posicionamento também é dizer não. Diga para a IA quem excluir.",
            "No WhatsApp, não mande bloco de texto nem PDF solto. Puxe conversa com algo em comum: seja interessante, não interesseiro.",
            "A IA pode errar: confira a fonte, se a empresa ainda existe e se ela combina de fato com quem você quer atender.",
        ],
        "frase": ("Prospecção é sobre rotina. Rotina vira o jogo.", "Juliana Anhaia"),
        "tarefa": "Escreva no papel o que vende, para quem, onde, que sinal a IA deve observar e quem excluir. Rode o prompt mestre, confira os resultados, faça os primeiros contatos e conte no grupo como foi.",
        "prompt_nome": "Prompt mestre de prospecção",
        "ferramenta": "ChatGPT ou Claude, com pesquisa na web",
        "como_usar": [
            "Um segmento e uma região por vez.",
            "Fixe a conversa no ChatGPT para manter o contexto da prospecção.",
            "Registre cada lead: fonte, critério, data do contato e responsável.",
        ],
        "prompt": (
            "Atue como especialista em inteligência comercial, pesquisa local e prospecção de clientes. Ajude-me a encontrar potenciais clientes com critério, não apenas reunir nomes.\n\n"
            "Meu negócio: [o que você vende]\nPerfil de cliente: [ex.: empresas e condomínios]\nRegião: [cidade, bairro ou raio de atendimento]\n"
            "Sinal que justifica investigar: [ex.: condomínio com mais de 20 unidades, área verde]\nQuem excluir: [ex.: pessoa física, empresa em recuperação judicial]\n\n"
            "Se faltar alguma informação essencial, pergunte antes de pesquisar.\n\n"
            "Faça um diagnóstico rápido: o principal gargalo parece estar na falta de clientes novos, no acompanhamento dos interessados, na oferta ou na experiência e recompra? Explique como hipótese, não como certeza. Se o gargalo não for falta de clientes novos, avise que aumentar a lista talvez não resolva.\n\n"
            "Pesquise até 5 empresas que correspondam ao perfil e à região. Para cada uma, traga em tabela: nome; segmento; cidade; site, perfil público ou contato comercial; link da fonte; sinal de aderência ao perfil; motivo para investigar; confiança da informação (alta, média ou baixa). Depois, ordene por aderência e explique a prioridade de cada uma. Se não encontrar um dado, escreva \"não encontrado\".\n\n"
            "Regras:\n- Não invente empresas, contatos, necessidades ou informações.\n- Separe o que a fonte confirma do que é inferência.\n"
            "- Use só informação pública de empresas e cite a fonte de cada resultado.\n- Se encontrar poucos resultados, explique e peça autorização antes de ampliar a região ou o perfil.\n\n"
            "Depois da lista, peça que eu escolha um lead. Só então crie uma primeira mensagem breve, personalizada com informação verificada e terminando com uma pergunta simples."
        ),
        "extras": [
            ("Os 4 critérios para escolher quem abordar primeiro",
             "**Aderência:** é o tipo de cliente que você definiu? **Região:** está na sua área? **Sinal:** há algo público que justifique? **Canal:** dá para chegar no decisor?"),
        ],
    },
    {
        "n": 4,
        "data": "21/09",
        "modulo": "Vendas com IA",
        "titulo": "Crie seu assistente de IA para responder objeções",
        "ideia": "Quando a IA não converte o cliente, quase sempre o problema é o contexto que demos a ela, não a ferramenta.",
        "resumo": (
            "Um assistente de IA é como um funcionário novo: precisa de onboarding. Na aula, um assistente foi montado ao vivo no ChatGPT (em GPTs, Criar) "
            "com as instruções da empresa e uma base de arquivos, e testado com a objeção mais comum de todas: \"está caro\". "
            "Bem configurado, ele pergunta antes de responder e não inventa desconto."
        ),
        "aprendizados": [
            "Não adianta colocar IA num processo bagunçado. Ela só acelera a bagunça. Primeiro organize, depois decida onde a IA ajuda.",
            "O assistente precisa de objetivo, contexto, formato e regras. Na base de conhecimento: apresentação comercial, portfólio, cases e manual da empresa.",
            "O cliente não compra o \"como\" do seu método. Ele compra o resultado e a saída para o problema que não aguenta mais.",
            "A IA sofre da síndrome de agradar. Coloque limites claros e não confie de olhos fechados.",
            "Boa resposta a objeção primeiro acolhe e entende, depois esclarece o valor. \"Meu preço é justo, se quer barato procure outro\" fecha a conversa.",
        ],
        "frase": ("Todo cliente nunca vai comprar o como. Ele vai comprar o resultado.", "Juliana Anhaia"),
        "tarefa": "Reserve um tempo para detalhar a fundo o seu negócio, crie o seu assistente de objeções no ChatGPT com essas informações e teste com uma objeção real que você já recebeu.",
        "prompt_nome": "Instruções do assistente de objeções",
        "ferramenta": "ChatGPT (GPTs, Criar) ou Projetos do Claude",
        "como_usar": [
            "No ChatGPT: + > GPTs > Criar. Dê nome e descrição.",
            "Cole este texto em Instruções e suba seus arquivos. PDF pesado? Peça a uma IA para converter em .md.",
            "Quando a objeção chegar, cole a mensagem ou o print da conversa.",
        ],
        "prompt": (
            "Você é o assistente de objeções comerciais da [nome da empresa] e atua como especialista sênior em vendas consultivas de [produto ou serviço].\n\n"
            "Segmento: [segmento]\nCliente ideal (quem compra hoje): [descrição]\nO que vendemos: [oferta]\n"
            "Problema que o cliente não aguenta mais: [dor principal]\nDiferenciais (o resultado que entregamos, não o \"como\"): [diferenciais]\n"
            "Provas: [resultados, cases, depoimentos]\nLimites: [o que não fazemos e o que não podemos prometer]\n\n"
            "Quando eu trouxer uma objeção, siga esta ordem:\n"
            "1. Se faltar contexto, pergunte antes de responder: o valor e o que está incluso, quem é o cliente, o que ele relatou antes e as palavras exatas que usou.\n"
            "2. Identifique a objeção real por trás da frase (orçamento, entendimento do que está incluso, comparação com outra opção, confiança ou momento).\n"
            "3. Sugira a melhor pergunta para fazer ao cliente.\n"
            "4. Escreva uma resposta consultiva que primeiro acolhe e depois esclarece o valor.\n"
            "5. Proponha o próximo passo e diga o que evitar.\n\n"
            "Regras: não invente informações, não ofereça desconto e não prometa nada que não esteja nos limites acima. Use os arquivos da base de conhecimento como fonte."
        ),
        "extras": [
            ("Treine antes da conversa real",
             "Abra o assistente e peça: \"Você será o cliente. Apresente uma objeção realista para [oferta]. Eu respondo como vendedor e, no fim, você me dá um feedback.\""),
        ],
    },
    {
        "n": 5,
        "data": "05/10",
        "modulo": "Vendas com IA",
        "titulo": "Objeções, CRM e dashboard com IA",
        "ideia": "Todo cliente deixa uma pista. \"Está caro\" quase sempre esconde outra coisa.",
        "resumo": (
            "O \"está caro\" pode ser orçamento que não cabe, cliente que não entendeu o que está incluso ou comparação com outra opção. "
            "Na aula, dados de negociações exportados do CRM, com nomes trocados por fictícios, foram para o Claude com um prompt em quatro etapas: "
            "limpar, cruzar, achar padrões de venda ganha e perdida e desenhar um dashboard."
        ),
        "aprendizados": [
            "Separe fato de hipótese. O que o cliente disse é fato. O que você supõe sobre o bolso dele é hipótese que se testa com pergunta.",
            "Teste rápido: tire o preço da sua proposta. Se não sobrar nada que convença, o problema é posicionamento, não o valor.",
            "Antes de mandar dados para a IA, limpe a planilha e troque nomes de clientes por fictícios. Dado ruim gera resposta ruim, e a LGPD vale.",
            "Cruzar dados mostra o que as vendas fechadas têm em comum: origem do lead, visita feita, proposta com valor e próximo passo combinado.",
            "Não peça retorno, combine o próximo passo: \"Posso te ligar amanhã às 10h ou às 15h para falarmos da proposta?\"",
        ],
        "frase": ("É entender onde eu estou acertando e onde preciso apertar o parafuso para alavancar o resultado.", "Juliana Anhaia"),
        "tarefa": "Exporte as negociações do seu CRM ou planilha sem dados pessoais, rode o prompt da aula e saia com pelo menos um padrão mapeado. Coloque no atendimento as 2 ou 3 perguntas sugeridas para testar as hipóteses.",
        "prompt_nome": "Análise de vendas e dashboard",
        "ferramenta": "Claude ou ChatGPT, com a planilha anexada",
        "como_usar": [
            "Exporte as negociações: origem, etapa, valor, objeção, motivo de perda, ganho ou perdido.",
            "Troque nomes de clientes por fictícios.",
            "Anexe a planilha e cole o prompt.",
        ],
        "prompt": (
            "Você é especialista em análise de dados e inteligência comercial. Analise a planilha de negociações anexada para identificar padrões de venda e desenhar um dashboard. Trabalhe em etapas.\n\n"
            "Etapa 1. Visão geral e limpeza: apresente as colunas, as variáveis e o volume de registros, e indique quais são relevantes. Aponte dados faltantes, duplicados e inconsistências e trate-os antes de seguir.\n\n"
            "Etapa 2. Análise: olhe cada coluna separadamente e depois cruze as informações. O que acontece nas vendas ganhas que não acontece nas perdidas?\n\n"
            "Etapa 3. Padrões:\n"
            "a) De sucesso: origem dos leads ganhos e etapas que se repetem nas vendas fechadas.\n"
            "b) Objeções mais frequentes, motivos de perda e taxa de conversão.\n"
            "c) De perda: em que etapa a negociação parou ou esfriou (antes da reunião, depois da proposta, no follow-up).\n"
            "Separe FATOS (o que o cliente disse e está registrado) de HIPÓTESES (interpretações).\n\n"
            "Desenhe a estrutura de um dashboard em três painéis: Performance e volume; Gargalos e objeções; Oportunidades e sinais de compra. Para cada indicador, diga o tipo de gráfico e a decisão prática que ele permite tomar.\n\n"
            "Etapa 4. Auditoria: diga o que estes dados ainda não permitem concluir, que colunas eu devo começar a registrar e sugira 2 ou 3 perguntas para o atendimento testar as hipóteses."
        ),
        "extras": [
            ("A conta do funil, de trás para frente",
             "Meta de R$ 100 mil no mês com ticket médio de R$ 3 mil: cerca de 34 vendas. Se você fecha 3 a cada 8 conversas (37%), precisa iniciar uns 90 contatos no mês. Conversão boa e pouca venda? O problema é atração. Conversão baixa? É o processo comercial."),
        ],
    },
]

FERRAMENTAS = [
    ("ChatGPT", "chatgpt.com", "Rascunhos, planejamento, fluxos visuais, prospecção com pesquisa e assistentes (GPTs)."),
    ("Claude", "claude.ai", "Textos longos, revisão, mapeamento de processos e análise de planilhas. Costuma inventar menos."),
    ("Gemini", "gemini.google.com", "Imagens e quando o trabalho já está no Google (Drive, Docs, Planilhas)."),
    ("NotebookLM", "notebooklm.google.com", "Resposta a partir dos seus materiais: PDFs, links e vídeos viram resumo, mapa mental e slides."),
    ("Manus", "manus.im", "Tarefas de várias etapas, forte em dados, números e painéis."),
    ("Lovable", "lovable.dev", "Site ou sistema a partir de instruções em português."),
    ("Google Meu Negócio", "business.google.com", "Ser encontrado: peça avaliação a cada cliente e mantenha fotos e dados em dia."),
]

FRASE_FINAL = "A IA sempre vai dar suporte. Mas quem inicia a ação, quem dá o contexto e quem avalia a resposta <b>somos nós</b>."
CONVITE = (
    "<b>Aula ao vivo toda segunda, às 20h</b>, aqui na comunidade. Traga uma tarefa real do seu negócio: é com ela que a gente testa. "
    "Quer ajuda além das aulas? Comece pelo diagnóstico em <b>avior.ia.br</b>."
)

ABERTURA = """Boa noite, pessoal da *Comunidade de Tecnologia e Negócios*! 👋

Nas últimas semanas a gente fez 5 aulas ao vivo aqui. Muita gente não conseguiu assistir todas, e quem assistiu me pediu os prompts.

Então a partir de amanhã, por 5 dias, eu mando aqui *o resumo de uma aula por dia*, com o *prompt da aula pronto para copiar* e a tarefa para aplicar na sua empresa:

1️⃣ Tire o processo da sua cabeça
2️⃣ Qual IA usar e pesquisa de mercado
3️⃣ IA para prospectar clientes
4️⃣ Assistente de objeções
5️⃣ CRM e dashboard com IA

No último dia vai o *Kit das Aulas* completo em PDF, para salvar e passar para o time. 🎁

Responde com um 🙋 quem vai aplicar junto."""

ENCERRAMENTO = """🎁 E como prometido, segue o *Kit das Aulas* completo em PDF: as 5 aulas resumidas, os 5 prompts e a lista das ferramentas.

Salva e passa para o seu time.

Me conta aqui: *qual tarefa você já colocou em prática?* E segunda tem aula nova, às 20h. 👇"""
