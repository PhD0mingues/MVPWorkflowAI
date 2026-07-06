---
name: correlacao-projetos-ppt
description: 'Analisa termos ou projetos e agrupa-os por correlação semântica — inclusive relações não óbvias que não aparecem no texto literal, como uma propriedade física, química ou temática compartilhada — e gera um novo PPT de resultado com os clusters e a explicação de cada correlação. A entrada pode ser: (a) várias pastas de projeto, cada uma com um .pptx, espalhadas num repositório (SharePoint/OneDrive); (b) um único .pptx contendo uma lista de palavras/termos; ou (c) uma lista de palavras ou texto colado diretamente no pedido do usuário. Use esta skill sempre que o usuário pedir para analisar pastas, agrupar termos, encontrar correlações, perguntar o que projetos ou palavras têm em comum, comparar/organizar por tema múltiplos PPTs, colar uma lista de palavras para correlacionar, ou invocar diretamente com /correlacao-ppt. Dispare mesmo quando o pedido for vago (ex: dá uma olhada nesses termos e me diz se tem algum padrão).'
---

# Correlação entre projetos ou termos

## O que esta skill faz

Agrupa um conjunto de termos em clusters por correlação semântica e gera um `.pptx` com um slide de título e um slide por cluster, explicando por que aqueles termos foram agrupados. A lógica de agrupamento (Passos 3 e 4) é sempre a mesma, independente de onde os termos vieram — o que muda é só como eles chegam até você (Passo 0).

O valor real desta skill está em achar conexões que não são óbvias a partir do nome do arquivo ou da categoria superficial do termo — por exemplo, dois termos podem parecer não ter nada em comum à primeira vista, mas compartilhar uma propriedade (cor, função, origem, contexto histórico) que só aparece se você pensar sobre o conteúdo, não apenas categorizar por palavra-chave. Trate o agrupamento como um exercício de raciocínio, não de correspondência de texto.

## Passo 0 — Identificar o tipo de entrada

Antes de tudo, identifique qual dos três cenários se aplica ao pedido:

1. **Lista de palavras/texto colado direto no pedido do usuário** (ex: uma lista numerada de termos, ou um texto corrido com vários conceitos). Nesse caso, pule direto para o Passo 3 — não há pasta nem PPT para localizar/extrair, os "termos-chave" já estão dados ou são triviais de extrair da lista.
2. **Um único arquivo `.pptx` contendo a lista de termos** (um deck com uma lista de palavras, um termo por slide, ou similar). Extraia o texto desse arquivo (via `read_resource` se veio do SharePoint/M365, ou via `scripts/extract_pptx_text.py` se for um arquivo local) e trate cada termo/linha extraído como um item da lista — depois siga para o Passo 3.
3. **Várias pastas de projeto, cada uma com um `.pptx`** (o caso original desta skill). Siga os Passos 1 e 2 abaixo normalmente.

Se não estiver claro qual cenário se aplica (por exemplo, o usuário mencionou "esses projetos" sem colar nada e sem indicar pasta), pergunte antes de assumir.

**Importante sobre a pasta `Workflows AI` no SharePoint:** essa pasta (site `MVPWorkflowAI`, `Shared Documents/Workflows AI`) é **sempre e apenas um template/pasta-mãe de base** — um exemplo de estrutura e de formato de saída (incluindo `outputs/correlacoes_eletrodomesticos.pptx` como modelo de forma, ver Passo 5). Ela **não é**, por padrão, a fonte de dados reais para um pedido de correlação. Nunca assuma que um pedido genérico de correlação deve analisar o conteúdo dessa pasta — os dados reais vêm do que o usuário indicar (lista colada, PPT anexado, ou uma pasta de projeto que ele aponte explicitamente). Só recorra a `Workflows AI` quando o usuário pedir explicitamente para usá-la como referência/base, ou quando estiver testando/validando a própria skill.

## Passo 1 — Localizar as pastas de projeto (só se aplica ao cenário 3 do Passo 0, com dados reais indicados pelo usuário)

Resolva a fonte de dados nesta ordem:

1. **O usuário informou um caminho ou nome de pasta específico no pedido?** Use esse, mesmo que pareça incomum — isso tem prioridade sobre qualquer padrão, e é o caminho normal para um pedido real (não é `Workflows AI`, salvo se o usuário pedir isso especificamente).
2. **Se não informou uma pasta e as ferramentas do conector Microsoft 365 estiverem disponíveis** (ferramentas com nomes como `sharepoint_folder_search`, `sharepoint_search`, `read_resource`, geralmente prefixadas por um ID de conector MCP): pergunte ao usuário qual pasta/site usar antes de buscar — não presuma `Workflows AI` como padrão. Se o usuário confirmar que é para usar a pasta-mãe de template, aí sim use `sharepoint_folder_search` com o nome indicado e prefira sempre o resultado com `webUrl` contendo `/sites/MVPWorkflowAI/` (a fonte oficial compartilhada, não uma cópia pessoal em OneDrive).
3. **Se o conector Microsoft 365 não estiver disponível** (conta sem o conector conectado, ou rodando fora do Cowork), caia para o comportamento antigo: procure uma pasta local/OneDrive com o nome indicado pelo usuário. Isso é um plano B temporário — sinalize ao usuário que os resultados vêm de uma cópia local.
4. **Se nenhuma fonte for encontrada**, não adivinhe — pergunte ao usuário qual pasta contém os projetos antes de continuar.

Uma vez com a pasta raiz em mãos (via SharePoint ou local): cada subpasta (numerada ou não) deve conter um `.pptx` representando um projeto. Use `read_resource` na URI da pasta raiz para listar as subpastas, e repita para cada subpasta até chegar nos arquivos `.pptx`. Se não houver `.pptx` em subpastas diretas, procure recursivamente, mas confirme com o usuário antes de assumir uma estrutura muito diferente do padrão (uma subpasta = um projeto = um `.pptx`).

## Passo 2 — Extrair o texto de cada PPT (só se aplica aos cenários 2 e 3 do Passo 0)

**Se os arquivos vieram do SharePoint via conector Microsoft 365:** chame `read_resource` diretamente na URI de cada arquivo `.pptx` (a mesma URI retornada pela listagem da pasta ou pela busca). O conector já retorna o texto completo extraído do arquivo (títulos, corpo, notas) — não é necessário baixar o arquivo nem rodar nenhum script local. Monte a mesma estrutura de dados internamente (projeto → texto) a partir dessas respostas antes de seguir para o Passo 3.

**Se os arquivos vierem de uma pasta local/OneDrive (plano B, sem conector disponível):** use o script `scripts/extract_pptx_text.py` para extrair de forma determinística todo o texto de cada apresentação. Não tente parsear `.pptx` manualmente com XML — o script já faz isso de forma robusta com `python-pptx`.

Resolução do caminho do script (só se aplica ao plano B local): esta skill pode rodar tanto solta (copiada para dentro de um projeto) quanto empacotada como plugin. Nunca assuma que `scripts/` está relativo ao diretório de trabalho atual. Resolva o caminho assim, nesta ordem:

1. Se a variável de ambiente `CLAUDE_PLUGIN_ROOT` estiver definida (é o caso quando a skill roda como parte de um plugin instalado), o script está em `"$CLAUDE_PLUGIN_ROOT/skills/correlacao-projetos-ppt/scripts/extract_pptx_text.py"`.
2. Caso contrário, procure a partir do diretório da própria skill (o caminho que aparece no cabeçalho "Base directory for this skill" quando a skill é invocada) — o script está em `<base_directory>/scripts/extract_pptx_text.py`.
3. Só como último recurso, faça uma busca (`find ~/.claude/skills ~/.claude-plugin-cache -name "extract_pptx_text.py" 2>/dev/null | head -1`) — isso é mais lento e menos confiável, use apenas se os dois passos acima não resolverem.

```bash
SCRIPT="${CLAUDE_PLUGIN_ROOT:-<base_directory_da_skill>}/scripts/extract_pptx_text.py"
# se a variável/caminho acima não existir, caia para a busca:
[ -f "$SCRIPT" ] || SCRIPT=$(find ~/.claude/skills ~/.claude-plugin-cache -name "extract_pptx_text.py" 2>/dev/null | head -1)
python3 "$SCRIPT" "<pasta_raiz>" > /tmp/projetos.json
```

Isso gera um JSON no formato:

```json
[
  {"project": "1", "file": "Workflows AI/1/1.pptx", "text": "Cigarro"},
  {"project": "2", "file": "Workflows AI/2/2.pptx", "text": "Batata"}
]
```

Quando os PPTs tiverem bastante texto (múltiplos slides, bullets longos), o campo `text` virá extenso — é esperado. Leia o conteúdo completo antes de seguir para o próximo passo; não corte nem faça o resumo com um script, use seu próprio julgamento.

## Passo 3 — Destilar termos-chave por projeto (ou por item da lista)

**Cenários 2 e 3 (veio de PPT/pasta de projetos):** para cada projeto, releia o texto extraído e resuma em uma lista curta (2 a 6 itens) dos conceitos/termos que realmente representam do que aquele projeto trata. Em decks curtos (como um único termo no slide), o termo-chave é o próprio termo. Em decks longos, procure os conceitos que se repetem ou que aparecem em posição de destaque (títulos, primeira/última seção).

**Cenário 1 (lista/texto colado direto no pedido):** separe a lista em itens individuais (um por número/linha/vírgula, conforme o formato que o usuário usou). Se for um texto corrido em vez de lista, extraia os termos/conceitos centrais do texto da mesma forma que faria com o conteúdo de um slide. Cada item vira o equivalente a um "projeto" para efeito do Passo 4 — não precisa ter pasta, arquivo ou número associado.

## Passo 4 — Agrupar por correlação semântica

Com a lista de termos-chave de todos os projetos em mãos, procure agrupamentos. Regras práticas:

- **Vá além da categoria óbvia.** Duas palavras da mesma categoria de dicionário (ex: dois alimentos) são um cluster válido, mas também vale a pena checar se existe uma conexão mais interessante atravessando categorias diferentes — por exemplo, itens que compartilham uma cor, uma reação química, um uso comum, uma origem geográfica, ou um significado cultural. Pense em como um especialista no assunto conectaria esses termos, não apenas como um dicionário os classificaria.
- **Não force conexões fracas.** Se um projeto realmente não se encaixa em nenhum grupo, deixe-o em um cluster próprio ou marque como "sem correlação clara" — isso é uma resposta legítima e mais útil do que uma conexão forçada.
- **Escreva a explicação da correlação em uma ou duas frases**, citando os termos específicos que sustentam a conexão. A explicação é o que dá valor ao slide — evite nomes de cluster genéricos sem justificar o porquê.
- Está tudo bem ter clusters de tamanhos bem diferentes (um cluster com 4 projetos e outro com 1).

## Passo 5 — Montar o PPT de resultado

Esta skill já tem um **template visual oficial da Advisia**, definido pelo script `scripts/montar_correlacoes_pptx.py`. Ele reproduz exatamente o estilo do PPT de referência (`Shared Documents/Workflows AI/outputs/correlacoes_eletrodomesticos.pptx` no SharePoint): barra lateral navy (`#1F1F4A`) no slide de título, barra lateral dourada (`#C99A2E`) nos slides de cluster com a lista de itens em branco empilhada, título em Georgia bold navy, corpo em Georgia cinza (`#333333`), rodapé em Georgia bold dourado. Use esse script sempre que possível — é mais confiável do que tentar recriar o estilo do zero.

1. **Caminho padrão (use sempre que não houver instrução diferente):** monte um JSON com o formato abaixo e rode o script.

```json
   {
     "titulo": "Correlações entre Projetos",
     "subtitulo": "<contexto do pedido, se houver>",
     "rodape_data": "<fonte dos dados> — <data de hoje>",
     "clusters": [
       {"nome": "<nome do cluster>", "itens": ["<projeto/termo 1>", "<projeto/termo 2>"], "explicacao": "<parágrafo da correlação>"}
     ]
   }
```

```bash
   SCRIPT="${CLAUDE_PLUGIN_ROOT:-<base_directory_da_skill>}/scripts/montar_correlacoes_pptx.py"
   [ -f "$SCRIPT" ] || SCRIPT=$(find ~/.claude/skills ~/.claude-plugin-cache -name "montar_correlacoes_pptx.py" 2>/dev/null | head -1)
   python3 "$SCRIPT" dados.json correlacoes.pptx
```

   O conteúdo de `clusters` (nomes, itens, explicações) vem sempre do seu raciocínio nos Passos 3 e 4 — o script só aplica o estilo visual, nunca invente ou copie clusters do exemplo de referência.

2. **Se o usuário pedir explicitamente um template diferente** (ex: apontar um `template.pptx` próprio, ou pedir outro estilo visual), respeite o pedido dele: abra o arquivo indicado com `Presentation()` e monte os slides nele, seguindo as instruções da skill `pptx` do sistema (leia o `SKILL.md` dela).
3. **Só use um layout limpo padrão (sem o template Advisia)** se o usuário pedir algo claramente fora desse estilo, ou se o script acima falhar por algum motivo técnico.

Estrutura do PPT de resultado (title/cluster já cobertos pelo script no caminho padrão):

- **Slide 1 (título):** título do pedido (ex: "Correlações entre Projetos" ou "Correlações entre Termos") + subtítulo de contexto + rodapé com fonte/data.
- **Um slide por cluster:** nome do cluster, lista dos projetos/termos que o compõem, e o parágrafo de explicação da correlação (Passo 4).

## Passo 6 — Salvar e entregar

Salve o resultado como `correlacoes.pptx` dentro de uma subpasta `outputs/` local (crie a subpasta se não existir). Depois, copie o arquivo final para a pasta de trabalho do usuário e apresente o arquivo a ele.

**Importante quando a fonte foi o SharePoint via conector Microsoft 365:** o conector é somente leitura — ele não permite gravar o `.pptx` de volta no SharePoint automaticamente. Entregue o arquivo normalmente ao usuário (pasta local de trabalho) e avise que, se ele quiser deixar o resultado disponível para o time no repositório central, precisa fazer o upload manual para a pasta `outputs/` dentro de `Shared Documents/Workflows AI` no site `MVPWorkflowAI`.

Se o usuário pedir explicitamente um caminho de saída diferente, respeite o pedido dele.
