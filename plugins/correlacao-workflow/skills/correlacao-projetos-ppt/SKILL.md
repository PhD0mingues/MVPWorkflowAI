---
name: correlacao-projetos-ppt
description: 'Agrupa uma lista de termos ou projetos em clusters por correlação semântica — incluindo relações não óbvias que não aparecem no texto literal, como uma propriedade física, química ou temática compartilhada — e gera um PPT explicando cada correlação. Aceita três formatos de entrada: uma lista de palavras colada direto no pedido, um único arquivo .pptx com uma lista de termos, ou várias pastas de projeto (cada uma com um .pptx) num repositório como SharePoint ou OneDrive. Use esta skill sempre que o usuário pedir para correlacionar, agrupar ou encontrar padrões entre termos ou projetos, perguntar o que eles têm em comum, ou invocar diretamente com /correlacao-ppt.'
---

# Correlação entre projetos ou termos

## Objetivo

Pegar uma lista de termos — de onde quer que venham — e agrupá-los em clusters por correlação semântica, indo além de categorias óbvias de dicionário. O resultado é um `.pptx` com um slide de título e um slide por cluster, cada um explicando em prosa por que aqueles termos foram agrupados.

O valor da skill está em achar conexões não óbvias: dois termos podem não ter nada em comum à primeira vista, mas compartilhar uma cor, uma função, uma origem ou um significado cultural. Trate isso como um exercício de raciocínio, não de correspondência de palavras-chave.

## Quando usar

- O usuário pede para "correlacionar", "agrupar" ou "achar padrões" entre termos, projetos ou arquivos `.pptx`.
- O usuário pergunta o que um conjunto de coisas tem em comum.
- O usuário invoca diretamente com `/correlacao-ppt`.
- O pedido é vago (“dá uma olhada nesses termos e me diz se tem algum padrão”), desde que envolva uma lista de itens a comparar.

## Visão geral do fluxo

1. Obter a lista de termos (três formas possíveis de entrada — veja abaixo).
2. Destilar o termo-chave de cada item.
3. Agrupar por correlação semântica.
4. Montar o PPT de resultado, no estilo visual da Advisia quando possível.
5. Entregar o arquivo.

## 1. Obter a lista de termos

Existem três formas de o usuário fornecer os termos. Identifique qual se aplica antes de continuar; se não estiver claro, pergunte em vez de assumir.

**a) Lista ou texto colado direto no pedido.** O usuário já escreveu os termos na mensagem (lista numerada, texto corrido, etc). Não precisa abrir nenhum arquivo — vá direto para o passo 2.

**b) Um único `.pptx` com a lista de termos.** Um deck com um termo por slide, por exemplo. Extraia o texto:
- Se o arquivo veio de um upload/anexo local ou pasta local/OneDrive: rode `scripts/extract_pptx_text.py <arquivo_ou_pasta>`.
- Se o arquivo está no SharePoint via conector Microsoft 365: chame `read_resource` na URI do arquivo — o conector já devolve o texto extraído diretamente, sem precisar rodar script nenhum.

**c) Várias pastas de projeto, cada uma com um `.pptx`.** O caso de "vários projetos numa pasta raiz, uma subpasta por projeto".
- Se o usuário indicou uma pasta específica, use essa.
- Se não indicou e o conector Microsoft 365 estiver disponível, pergunte qual pasta/site usar — não presuma automaticamente uma pasta específica como fonte de dados reais, mesmo que ela exista e pareça óbvia (ex: uma pasta de exemplo/template do repositório). Uma vez confirmada a pasta, use `sharepoint_folder_search` para localizá-la e `read_resource` para listar subpastas e ler cada `.pptx`.
- Se o conector não estiver disponível, procure uma pasta local/OneDrive com o nome indicado pelo usuário.
- Se nenhuma fonte for encontrada, pergunte — não adivinhe.

## 2. Destilar o termo-chave de cada item

Para cada item, resuma em 2-6 conceitos o que ele realmente representa. Se o texto já é curto (um termo por slide), o termo-chave é o próprio termo. Se for um deck longo, procure os conceitos que se repetem ou aparecem em destaque (títulos, primeira/última seção).

## 3. Agrupar por correlação semântica

Com todos os termos-chave em mãos:

- **Vá além da categoria óbvia.** Duas palavras da mesma categoria de dicionário são um cluster válido, mas vale checar conexões mais interessantes cruzando categorias — cor, reação química, uso comum, origem geográfica, significado cultural. Pense como um especialista no assunto conectaria os termos, não como um dicionário os classificaria.
- **Não force conexões fracas.** Um item que não se encaixa em nada pode ficar sozinho ou marcado como "sem correlação clara" — isso é uma resposta legítima.
- **Explique a correlação em 1-2 frases**, citando os termos específicos que sustentam a conexão. É essa explicação que dá valor ao slide.
- Clusters de tamanhos bem diferentes entre si são normais.

## 4. Montar o PPT de resultado

Monte um JSON com o conteúdo dos clusters (formato abaixo) e use os scripts da skill para gerar o `.pptx` no estilo visual da Advisia — barra lateral colorida, título e corpo em Georgia. **O conteúdo (nomes de cluster, itens, explicações) vem sempre do raciocínio do passo 3; os scripts só aplicam a formatação visual.**

```json
{
  "titulo": "Correlações entre Projetos",
  "subtitulo": "<contexto do pedido, se houver>",
  "rodape_data": "<fonte dos dados> — <data de hoje>",
  "clusters": [
    {"nome": "<nome do cluster>", "itens": ["<termo 1>", "<termo 2>"], "explicacao": "<parágrafo da correlação>"}
  ]
}
```

**Sobre as cores do template — sempre prefira ler ao vivo em vez de usar cor fixa:**

- **Se você tem acesso aos bytes reais de um `.pptx` de referência** (arquivo anexado na conversa, ou pasta local/OneDrive — nunca via conector M365, que só devolve texto): rode `scripts/extrair_estilo_pptx.py <referencia.pptx> > estilo.json` primeiro, depois `scripts/montar_correlacoes_pptx.py dados.json correlacoes.pptx --estilo estilo.json`. Isso lê a cor da barra lateral, do título, do corpo, do rodapé e a fonte diretamente do arquivo — nada fixo.
- **Se a única fonte disponível for texto vindo do conector Microsoft 365** (que nunca devolve bytes/tema/cor): não invente uma paleta. Rode `scripts/montar_correlacoes_pptx.py dados.json correlacoes.pptx` sem `--estilo` — cai numa última cópia conhecida das cores reais da Advisia, e avise o usuário que ela pode estar desatualizada se o template mudou, oferecendo a opção de ele anexar o arquivo real.
- Resolução de caminho dos scripts (funciona solto ou empacotado como plugin): use `$CLAUDE_PLUGIN_ROOT/skills/correlacao-projetos-ppt/scripts/<nome>.py` se a variável existir; senão, o caminho relativo ao diretório base da skill; só em último caso, `find ~/.claude/skills ~/.claude-plugin-cache -name "<nome>.py"`.
- Só use um layout limpo sem o template Advisia se o usuário pedir algo fora desse estilo, ou se os scripts falharem tecnicamente — nunca como substituto silencioso.

## 5. Entregar

Salve como `correlacoes.pptx` numa subpasta `outputs/` local, copie para a pasta de trabalho do usuário e apresente o arquivo.

Se os dados vieram do SharePoint via conector M365, lembre o usuário que o conector é somente leitura — a skill não grava o resultado de volta lá sozinha. Se ele quiser deixar disponível pro time, precisa subir manualmente.
