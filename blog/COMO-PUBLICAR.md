# Como publicar um artigo novo no blog

1. Copie uma pasta de artigo existente (por exemplo `blog/ia-em-cima-de-bagunca/`)
   e renomeie com o endereço do novo artigo, só com letras minúsculas e hífens.
   Ex.: `blog/como-reduzir-turnover/`.
2. No `index.html` da pasta nova, troque:
   - o `<title>`, a `description`, o `canonical`, o `og:` e o bloco `application/ld+json`
     (título, descrição, data e endereço);
   - o `<h1>`, a linha de categoria/data/tempo de leitura;
   - o texto dentro de `<div class="body">` (use `<p>`, `<h2>`, `<ul>`, `<strong>`, `<blockquote>`).
3. Em `blog/index.html`, adicione um card novo copiando um `<a class="post">`.
   O primeiro card (`post featured`) é o destaque do topo: coloque nele o artigo mais recente.
4. Se quiser, atualize o "Continue lendo" no fim dos outros artigos.

A chamada no fim de cada artigo leva para `/diagnostico/` (LP do diagnóstico gratuito).
