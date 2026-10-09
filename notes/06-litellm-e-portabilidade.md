# LiteLLM e portabilidade de provedor

Meta-fichamento, mesmo padrão do [05](05-construindo-o-mcp-toy-server.md): aplicar na prática, documentar no caminho. Motivação: o `mcp-toy-server` nunca chamou nenhum modelo — a pergunta que ficou em aberto foi "se um dia ele chamar, isso prende a empresa a um provedor só?". Este fichamento testa a resposta (não, se a chamada for feita por trás de uma camada como o LiteLLM) sem depender de chave de provedor nenhuma: tudo aqui é simulado de propósito, e cada seção deixa explícito o que é real e o que é simulação.

## Passo 1 — Setup

**Feito:** `uv add litellm` no `mcp-toy-server` (resolveu `litellm==1.104.2`, trazendo `openai` como dependência interna — o SDK da OpenAI é usado por baixo pra falar o formato comum, mesmo quando o provedor de destino não é a OpenAI).

**Correção de rota, antes mesmo de começar:** o plano original pedia confirmar chave de pelo menos 2 provedores. Não tem nenhuma chave configurada neste ambiente — e, mais importante, não precisa: o que este estudo prova é a **forma da chamada** (o mesmo código funciona trocando só a string do modelo), não a qualidade de resposta de provedor nenhum. Virou simulação de propósito, não workaround de falta de credencial.

## Passo 2 — Conectar o LiteLLM às tools do MCP

**Feito:** `litellm_bridge.py`, com `mcp_tool_to_litellm_tool()` — converte uma `Tool` do MCP (`name`, `description`, `input_schema`) pro formato que o litellm espera.

**Descoberta, confirmada no código-fonte, não suposta:** o litellm usa o mesmo formato de tool-calling da OpenAI — `{"type": "function", "function": {"name", "description", "parameters"}}` (`ChatCompletionToolParamFunctionChunk` em `litellm/types/llms/openai.py`). Como o `input_schema` de uma tool MCP já É JSON Schema, a conversão é literalmente copiar os três campos pro formato de fora — nenhuma transformação de tipo, só reempacotamento.

**Validação, sem chave e sem rede:** rodei `litellm.completion(model="gpt-3.5-turbo", tools=<tools convertidas>, mock_response="...")`. O `mock_response` evita a chamada de rede de verdade, mas o `tools` passa pela validação interna do litellm normalmente — confirma que o schema convertido é aceito pela biblioteca, não só que "parece certo" visualmente.

**Limite do `mock_response`, que vai importar no próximo passo:** ele só simula **texto** (`resp.choices[0].message.content`), não `tool_calls` estruturado — testei isso antes de assumir que resolvia o passo 3. Pra simular "o modelo decidiu chamar uma tool", vou precisar montar a resposta à mão, não usar esse parâmetro.

## Passo 3 — Chamada simulada com tool_call

**Feito:** `decide(model, messages, tools)` em `litellm_bridge.py` — a assinatura imita exatamente `litellm.completion(model=..., messages=..., tools=...)`. Por dentro, em vez de chamar a rede, monta à mão um `litellm.ModelResponse` com um `tool_calls` (via `ChatCompletionMessageToolCall`/`Function`/`Message`, as classes reais do litellm) simulando a decisão de chamar `search_notes`.

**O que é simulado e o que não é, sem ambiguidade:** simulado = a decisão de qual tool chamar (não existe modelo nenhum pensando nisso). Real = a conversão de schema do passo 2, o parsing da decisão, e a chamada de `search_notes` no servidor MCP de verdade — que respondeu com conteúdo real dos fichamentos.

**Validação:** rodei o fluxo completo e o resultado da tool bateu com uma busca real por "ACI" — a mesma que já tínhamos validado no [05](05-construindo-o-mcp-toy-server.md).

## Passo 4 — Trocar "provedor" só na config

**Feito:** chamei `run_with_model()` duas vezes, mudando só a string de `model` — `claude-opus-5` e `deepseek/deepseek-chat` (um modelo chinês, de propósito, já que foi exatamente esse cenário que motivou o estudo). Nenhuma outra linha mudou entre as duas chamadas.

**Resultado:** as duas rodaram idêntico — mesma conversão de tool, mesmo parsing, mesma chamada real ao servidor MCP, 16 linhas de resultado nas duas. A única coisa diferente no código inteiro foi o valor de uma string.

**O limite honesto disto:** isso prova portabilidade de **forma de chamada** — o `model=` muda, o resto do código não. Não prova que os dois modelos dariam a mesma resposta de verdade (aqui a decisão é simulada igual nos dois casos). Numa migração real, o código de integração não muda; o que precisaria de trabalho é validar se o modelo novo decide bem — isso é avaliação de qualidade, não arquitetura, e fica fora do escopo deste fichamento.

## Passo 5 — Escrita final

**Feito:** esta página revisada de ponta a ponta, mais os READMEs atualizados (raiz e `mcp-toy-server/`) pra listar este fichamento e o `litellm_bridge.py`.

**O que isso prova, resumido:** a preocupação original — "o servidor que construí tá preso à Anthropic?" — tinha duas partes, e cada uma se resolveu de um jeito diferente. A primeira (o próprio MCP) já não era um problema antes mesmo de eu testar qualquer coisa: o protocolo foi doado pra Agentic AI Foundation em dez/2025, é padrão multi-vendor hoje. A segunda (a camada que decide qual tool chamar) era, de fato, um ponto real de acoplamento — e esse fichamento mostrou, rodando código, que uma função com a assinatura de `litellm.completion(model=...)` isola esse acoplamento numa única string, sem tocar em schema, parsing ou execução de tool.

**Conexão com [01](01-building-effective-agents.md):** o texto que abriu toda essa série já recomendava integrar tools "via Model Context Protocol" dentro do augmented LLM — mas não falava de como o próprio *provedor* do LLM podia ser trocado. Esse fichamento preenche essa lacuna: MCP resolve portabilidade de tool/dado; LiteLLM (ou equivalente) resolve portabilidade de modelo. São duas camadas diferentes do mesmo problema de não ficar preso a um fornecedor só.

## Passo 6 — Lista de provedores em YAML

**Feito:** `providers.yaml`, listando OpenAI, Anthropic, Vertex AI, Azure OpenAI, Bedrock, Ollama (local) e DeepSeek — cada um com o `model` no formato do litellm e os `env_vars` que ele exige. O loop de execução passou a ler esse arquivo em vez de uma lista fixa no código.

**Nada aqui foi chutado:** tanto os prefixos de provedor (`vertex_ai/`, `azure/`, `bedrock/`, `ollama/`) quanto os nomes exatos de env var vieram de `litellm.provider_list` e `litellm.validate_environment(model)`, rodados de verdade contra a biblioteca instalada — não da documentação nem da memória.

**Validação:** rodei o bridge lendo o YAML — os 7 provedores passaram pelo mesmo `decide()` → tool real → resultado, sem nenhuma linha de código nova por provedor. Adicionar um oitavo é só adicionar uma entrada no YAML.

**É aqui que a analogia com Terraform fecha de verdade:** um provider novo no Terraform é um bloco de config; aqui, idem — o código que orquestra (`run_with_model`) não sabe nem precisa saber quantos provedores existem.