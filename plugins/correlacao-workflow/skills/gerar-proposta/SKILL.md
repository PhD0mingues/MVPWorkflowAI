---
name: gerar-proposta
description: 'Gera o rascunho de uma proposta comercial de projeto de consultoria em .pptx, a partir de um briefing de cliente novo, buscando as propostas aprovadas mais parecidas (incluindo o PPT-modelo oficial da Advisia) num banco compartilhado no SharePoint e combinando o melhor delas com o contexto específico do cliente. Use esta skill sempre que o usuário pedir para montar/gerar/rascunhar uma proposta comercial, elaborar uma proposta de projeto para um cliente, ou colar um briefing de cliente pedindo uma proposta. Preços, escopo e cláusulas contratuais NUNCA são inventados pelo modelo — vêm sempre de uma tabela de referência determinística. O documento final é sempre depositado no SharePoint/CRM antes do fluxo terminar, para servir de trilha de auditoria.'
---

# Gerar proposta comercial

## O que esta skill faz

A partir de um briefing de cliente novo, produz um rascunho de proposta comercial em `.pptx` combinando: (1) a estrutura e os argumentos de propostas passadas aprovadas que sejam semanticamente parecidas com o briefing (incluindo o PPT-modelo oficial de propostas da Advisia, que vive no mesmo banco do SharePoint), e (2) o contexto específico deste cliente. O objetivo não é gerar uma proposta do zero a cada vez, mas reaproveitar o que já funcionou, adaptado ao caso novo.

**Princípio central: separe o que pode ser gerado livremente do que não pode.** Uma proposta comercial tem duas naturezas de conteúdo bem diferentes, e tratá-las do mesmo jeito é a fonte mais comum de erro:

- **Conteúdo criativo/argumentativo** (proposta de valor, diagnóstico do problema do cliente, argumento comercial): aqui você tem liberdade — use o contexto rico do briefing, não se prenda a fórmulas fixas, e escreva como um consultor sênior escreveria para aquele cliente específico.
- **Conteúdo determinístico** (preço, escopo contratado, cláusulas, prazos, condições de pagamento): aqui você **não tem liberdade nenhuma**. Esses valores vêm de uma tabela de referência (ver Passo 5) e são copiados, nunca gerados ou estimados por você. Um preço "razoável" inventado pelo modelo é um erro grave, não uma aproximação aceitável.

## Estado atual do banco de propostas (leia antes de começar)

Este é um MVP em fase inicial: o banco de propostas aprovadas no SharePoint pode estar vazio ou ter poucos documentos ainda, porque a organização está construindo esse acervo aos poucos. Antes de tratar isso como erro, siga esta lógica:

- **Banco vazio ou sem casos parecidos:** avise o usuário que não há precedente direto, gere a proposta apoiando-se só no briefing e em boas práticas gerais de proposta de consultoria (caindo no estilo visual padrão — ver Passo 4), e sinalize claramente no rascunho (e para o usuário) que esta proposta é uma boa candidata a virar o primeiro template de sua categoria no banco, uma vez aprovada.
- **Banco com poucos ou nenhum resultado realmente parecido:** não force uma correlação fraca só para preencher a cota de "2 a 3 templates" pedida no Passo 2 — é preferível usar 1 template parcialmente relevante (ou nenhum) do que forçar um encaixe ruim que vai contaminar o tom ou o escopo da proposta nova.
- **O PPT-modelo oficial de propostas** (o arquivo `.pptx` de referência visual da Advisia) é só mais um documento dentro desse mesmo banco do SharePoint — não é buscado por um caminho especial nem tratado como padrão automático; ele entra na disputa do Passo 3 por correlação semântica como qualquer outro, mas na prática costuma ser o mais indicado quando não há um template de escopo mais específico parecido.

## Passo 1 — Receber o briefing

O briefing pode chegar de duas formas: colado diretamente na conversa pelo consultor, ou como um arquivo (`.docx`, `.txt`, `.md`, e-mail exportado) dentro da pasta do projeto atual. Se não estiver claro onde está o briefing, pergunte — não assuma que o primeiro arquivo da pasta é o briefing certo.

Extraia do briefing, no mínimo: nome do cliente, setor/mercado, o problema ou necessidade descrita, e qualquer menção a escopo, prazo ou orçamento já discutido informalmente. Isso alimenta tanto a busca de templates (Passo 2) quanto a redação das seções criativas (Passo 5).

## Passo 2 — Buscar templates no banco de propostas (SharePoint)

O banco de propostas aprovadas — incluindo o PPT-modelo oficial de propostas da Advisia — vive num SharePoint compartilhado da organização, acessado através do **conector oficial de Microsoft 365 para Claude** (não é uma pasta local, e não é um servidor MCP customizado desta skill — é o conector padrão que dá acesso a SharePoint/OneDrive com a permissão delegada do próprio consultor).

1. Confirme que o conector M365 está disponível nesta sessão. Se não estiver, avise o usuário claramente: essa etapa depende de um admin da organização ter habilitado o conector antes — não tente contornar isso lendo arquivos locais que só por acaso tenham nome parecido.
2. Localize a pasta/site do banco de propostas. Se o usuário não informou o caminho neste pedido, use o último caminho que ele confirmou em conversas anteriores, ou pergunte.
3. Liste os documentos disponíveis e leia o suficiente de cada um (título, resumo, seção de escopo) para entender do que trata — não é preciso ler a proposta inteira de cada candidato nesta fase.

## Passo 3 — Selecionar os templates mais relevantes por correlação semântica

Aplique o mesmo raciocínio da skill `correlacao-projetos-ppt`: não escolha templates só por palavra-chave batendo no nome do arquivo ou no setor declarado. Pense em como um consultor experiente reconheceria uma proposta parecida — pode ser pelo tipo de problema de negócio (não pelo setor do cliente), pela estrutura de entregáveis, ou pelo porte do projeto. O PPT-modelo oficial entra nessa mesma disputa, sem prioridade automática.

Selecione 2 a 3 templates (menos, se o banco não tiver bons candidatos — releia a seção "Estado atual do banco de propostas" acima). Para cada um escolhido, anote em uma frase por que ele foi selecionado — essa justificativa entra no rascunho como nota interna para quem for revisar, não no corpo da proposta final.

## Passo 4 — Recriar ou copiar o template selecionado para a pasta do projeto (e capturar o estilo visual)

Depois de escolher o(s) template(s) mais relevante(s) no Passo 3, traga uma cópia de trabalho do melhor candidato para dentro da pasta do projeto atual (a pasta do Cowork onde você está montando esta proposta) — isso dá um ponto de partida real (estrutura e, quando possível, formatação), em vez de só notas de texto soltas.

Como isso é feito depende de que tipo de acesso você tem ao arquivo original:

- **Se o arquivo veio de uma pasta local ou OneDrive sincronizado (bytes reais disponíveis):** copie o arquivo diretamente para a pasta do projeto — cópia idêntica, com toda formatação, imagens e estilo preservados. Além disso, rode `$CLAUDE_PLUGIN_ROOT/skills/correlacao-projetos-ppt/scripts/extrair_estilo_pptx.py <arquivo.pptx> > estilo.json` (o mesmo script já usado pela skill `correlacao-projetos-ppt`, compartilhado dentro deste plugin) para extrair as cores e a fonte reais desse template — isso alimenta o `--estilo` do Passo 7.
- **Se o arquivo só está acessível via conector Microsoft 365 sem sincronização local (caso mais comum neste MVP):** o conector não expõe os bytes do arquivo, só o texto extraído (títulos, corpo, notas) — então não é possível fazer uma cópia bit-a-bit nem extrair cor real. Nesse caso, **recrie** o arquivo: use o texto completo já extraído no Passo 2/3 para remontar um novo `.pptx` com a mesma estrutura de seções (mesma ordem, mesmos títulos), usando a skill `pptx` do sistema. Nomeie o arquivo recriado de forma clara, por exemplo `template_base_<nome-original>.pptx`, e **avise o usuário explicitamente**: isto é uma recriação a partir do texto extraído, não uma cópia idêntica — formatação visual detalhada, imagens e elementos gráficos do arquivo original não são preservados, só a estrutura textual. Nesse caso não há `--estilo` real disponível; o Passo 7 cai no estilo padrão conhecido da Advisia.

Esse arquivo recriado/copiado (e o `estilo.json`, quando existir) servem de referência para o Passo 7 (montagem do documento final) — não são o entregável final em si, e não substituem os Passos 5 e 6 (geração do conteúdo e QA).

## Passo 5 — Gerar o rascunho: pipeline bifurcado

Monte o rascunho em duas frentes com regras de geração diferentes:

**Frente criativa** (proposta de valor, diagnóstico, argumento comercial, tom de abertura):
- Escreva com o contexto completo do briefing e das seções equivalentes dos templates selecionados como inspiração de estrutura e tom — não copie frases prontas, adapte o raciocínio ao cliente novo.
- Não force uma estrutura rígida de exemplo; deixe o argumento seguir a lógica do problema real do cliente.

**Frente determinística** (preço, escopo contratado, cláusulas, prazos, condições de pagamento):
- Esses valores vêm de uma tabela de referência da organização (ex: `tabela_precos.json` ou planilha equivalente no mesmo SharePoint). **Esta tabela ainda não existe neste MVP** — enquanto ela não for criada, deixe esses campos marcados explicitamente como `[PENDENTE — preencher com tabela oficial]` no rascunho, em vez de estimar um valor. Nunca gere um preço, prazo ou cláusula "plausível" no lugar de um valor real.
- Assim que a tabela existir, use o script `scripts/montar_proposta_pptx.py` (Passo 7) para injetar esses campos programaticamente — nunca via geração livre do modelo.

## Passo 6 — QA via subagente

Antes de considerar o rascunho pronto, rode uma verificação usando um subagente dedicado (não confie na sua própria revisão do texto que você acabou de escrever — use um agente novo, sem o viés de quem gerou o conteúdo). O checklist mínimo:

- Todos os campos obrigatórios da proposta estão presentes (nome do cliente, escopo, contato, data)?
- Não há nenhuma menção, nome ou dado de outro cliente vazando de algum template usado como referência?
- O escopo descrito no texto criativo é consistente com o escopo determinístico da tabela (ou com o marcador `[PENDENTE]`, se a tabela ainda não existe)?
- Os campos determinísticos (preço/prazo/cláusulas) foram copiados da tabela ou marcados como pendentes — nenhum deles foi gerado livremente pelo modelo?

Se o subagente encontrar qualquer falha, corrija antes de prosseguir para o Passo 7. Não entregue um rascunho que falhou no QA.

## Passo 7 — Montar o documento final (.pptx)

Antes de gerar o documento, crie o arquivo marcador `.proposta_rascunho_em_andamento` na raiz do projeto atual (`touch .proposta_rascunho_em_andamento`, conteúdo irrelevante). Esse marcador é o que ativa a checagem do hook de auditoria do plugin (Passo 8) — sem ele, o hook não sabe que uma proposta foi gerada nesta sessão e não vai cobrar o depósito.

Monte um JSON com os dados da proposta (formato no cabeçalho do script) e use `scripts/montar_proposta_pptx.py dados_proposta.json proposta.pptx [--estilo estilo.json]` para montar o `.pptx` final de forma determinística — o script recebe o texto das seções criativas (já revisadas no Passo 6) e os valores da tabela de referência (ou os marcadores `[PENDENTE]`, destacados em vermelho), e monta o documento a partir de um estilo visual (Advisia). **A formatação em si não deve ser decidida pelo modelo a cada vez.**

- Se você extraiu um `estilo.json` real no Passo 4, passe `--estilo estilo.json` — a proposta sai com a cor/fonte reais do template escolhido.
- Se não (caso conector-somente, sem bytes), rode sem `--estilo` — o script cai na última cor conhecida da Advisia e avisa isso no console; repasse esse aviso ao usuário.
- Se o usuário pedir explicitamente uma proposta em `.docx` em vez de `.pptx`, use `scripts/gerar_proposta.py` (mesmo formato de JSON, sem o campo de estilo visual) e siga também a skill `docx` do sistema.

## Passo 8 — Depósito obrigatório no SharePoint/CRM (auditoria)

Esta skill não considera o fluxo encerrado até o documento final ser depositado na pasta de propostas do SharePoint (ou no CRM, conforme configurado). Isso não é opcional nem uma sugestão de boas práticas — é a trilha de auditoria do processo, já que o Cowork não mantém log técnico completo por conta própria.

Depois de salvar o `.pptx` (ou `.docx`) final localmente:

1. Faça o upload para o SharePoint/CRM através do conector M365.
2. Confirme que o upload foi bem-sucedido (releia o item criado, não confie apenas na ausência de erro).
3. Só então crie o arquivo marcador `.proposta_deposito_confirmado` na raiz do projeto atual — é esse marcador que o hook `hooks/checar_deposito_proposta.sh` do plugin verifica antes de deixar o turno terminar. Sem ele, o hook bloqueia o encerramento e devolve um aviso pedindo o depósito.

Se o upload falhar por qualquer motivo, avise o usuário explicitamente e não crie o marcador — é intencional que o hook continue bloqueando o fim do turno até o depósito de fato acontecer.
