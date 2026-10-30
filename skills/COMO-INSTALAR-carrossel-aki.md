# Carrossel AKI Jardins: como instalar e usar

Guia para o André. Instalação: 5 minutos, uma vez só.

## 1. Instalar (no computador, em claude.ai)

1. Baixe o arquivo **carrossel-aki-jardins.zip**. Não descompacte.
2. Entre em **claude.ai** com a sua conta.
3. Clique no seu nome (canto de baixo, à esquerda) e abra **Configurações**.
4. Vá em **Capacidades** e ligue **Execução de código e criação de arquivos**. Sem isso a skill não consegue gerar as imagens.
5. Na mesma tela, em **Skills**, clique em **Enviar skill** (ou "Upload skill") e escolha o **carrossel-aki-jardins.zip**.
6. Confira se a skill **carrossel-aki-jardins** aparece na lista com o botão ligado.

Pronto. Ela vale também no app do celular, na mesma conta.

## 2. Pedir um carrossel

Abra uma conversa nova e escreva do seu jeito. Exemplos:

- "Faz o carrossel de sexta sobre poda: quatro perguntas antes de contratar."
- "Monta um antes e depois com essas fotos" (e anexe as fotos).
- "Um cliente me perguntou se vale a pena manutenção mensal. Transforma isso em carrossel."

O Claude manda primeiro o texto, card por card. Leia, peça o que quiser mudar e diga **ok**. Só depois ele gera as imagens.

### Com fotos de serviço

- Anexe as fotos e diga qual é o antes e qual é o depois de cada área. Ex.: "foto 1 antes, foto 2 depois do gramado da frente".
- Tire o antes e o depois **do mesmo lugar**, mesmo ângulo, e de preferência com luz parecida.
- Só use foto de cliente que **assinou o termo de autorização**. Nada de endereço, número da casa, placa de carro ou rosto de pessoas.

## 3. O que você recebe

- Um **zip** com os slides (slide-01.png, slide-02.png...) e a **legenda** pronta.
- Todos os slides saem no mesmo tamanho (formato em pé, 4:5). É isso que impede o Instagram de cortar o título.

## 4. Postar sem cortar

1. Baixe o zip no celular e abra. As imagens vão para o app Arquivos ou para a galeria.
2. No Instagram, toque em **+** e depois em **Post**.
3. Toque no ícone de **várias fotos** (os quadradinhos sobrepostos).
4. **Antes de marcar a segunda foto**, toque no ícone de **expandir** (as duas setinhas no canto de baixo, à esquerda da prévia) para a primeira aparecer **inteira, em pé**. Se a prévia estiver quadrada, o Instagram vai cortar todas.
5. Marque os slides **na ordem**: 01, 02, 03...
6. Não dê zoom nem arraste nenhuma imagem.
7. Cole a legenda que veio no arquivo **legenda.md**.

Carrossel sai na **sexta, às 19h**.

## Se der algum problema

- **"Não achei o navegador"**: peça para o Claude rodar a instalação do Playwright e tentar de novo.
- **Foto de iPhone (HEIC) não abre**: mande a foto em JPG, ou peça para o Claude instalar o leitor de HEIC.
- **Texto grande demais**: o Claude avisa "ESTOUROU". Peça para encurtar ou dividir em dois slides.
