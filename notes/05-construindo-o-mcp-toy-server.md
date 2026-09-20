# Construindo o MCP toy server

Meta-fichamento: não é sobre um texto externo, é sobre aplicar os quatro anteriores na prática. Cada passo do [roadmap combinado](../mcp-toy-server/README.md) vira uma seção aqui, documentada depois de feita, não planejada de antemão.

**O que este servidor faz** (decisão tomada ao escolher o tema): expõe os próprios fichamentos deste repo (`notes/*.md`) como Resources, e uma tool de busca por cima deles — em vez de repetir o exemplo de clima do quickstart oficial, que [04](04-build-mcp-server.md) já registrou como focado só em Tools. A escolha cobre deliberadamente a metade do protocolo (Resources) que o exemplo oficial deixa de lado.

## Passo 1 — Setup do projeto

**Feito:**
- `uv init --no-readme --name mcp-toy-server` dentro de `mcp-toy-server/` (o `--no-readme` pra não sobrescrever o README que já existia).
- `uv add "mcp[cli]"` — resolveu pra `mcp==2.2.0` (o quickstart pede `>=2.0.0`, ok).
- uv criou o ambiente com Python 3.11.14 (baixado por ele mesmo), mesmo o sistema tendo 3.10.13 como padrão — ambos atendem o mínimo de 3.10 do guia, sem conflito.
- Sanity check: `uv run python -c "from mcp.server import MCPServer"` importa sem erro.

**Detalhe que vale registrar:** todo `uv run` neste projeto imprime um aviso —
```
warning: `VIRTUAL_ENV=...` does not match the project environment path `.venv`
```
Isso é só uma variável de ambiente `VIRTUAL_ENV` de outro projeto (pyenv) vazando pro shell — inofensivo, o uv ignora e usa o `.venv` correto de qualquer forma. Não precisa de correção, mas ficaria comentando "erro" se eu não tivesse checado a causa.

**Arquivos gerados:** `pyproject.toml`, `.python-version` (3.11), `main.py` (placeholder "Hello from mcp-toy-server!", ainda não é o servidor — isso é o passo 2), `.venv/` (ignorado pelo `.gitignore` da raiz do repo).

## Passo 2 — Primeiro Resource

**Feito:** um resource estático em `main.py`, expondo só o fichamento de `01-building-effective-agents.md`.

**A API real não é a do quickstart** — e essa foi a descoberta do passo. O guia oficial ([04](04-build-mcp-server.md)) só mostra `@mcp.tool()`; pra achar como registrar um *resource* foi preciso ler o código-fonte instalado (`mcp/server/mcpserver/server.py`), não a doc. O padrão:

```python
@mcp.resource(
    "notes://building-effective-agents",
    name="building-effective-agents",
    title="Fichamento: Building Effective Agents",
    description="Reading note on workflow vs. agent, augmented LLM, and ACI.",
    mime_type="text/markdown",
)
def get_building_effective_agents() -> str:
    return FIRST_NOTE.read_text(encoding="utf-8")
```

Duas regras da assinatura que valem registrar, porque não são óbvias de fora:
- A URI decide se o resource é **estático** ou **template**: sem `{variável}` na URI, é estático e a função não pode ter parâmetro nenhum (só decidi isso depois de ler o código — o texto do quickstart não fala de template resource). Passo 3 (listar todos os fichamentos) provavelmente vira um resource *template*, com `{arquivo}` na URI.
- `description` e `title` no resource cumprem o mesmo papel de ACI que a docstring cumpre numa tool ([01](01-building-effective-agents.md)/[04](04-build-mcp-server.md)) — é o que um client enxerga antes de decidir ler o resource.

**Validação:** sem subir um client real ainda, chamei os métodos assíncronos públicos do próprio `MCPServer` (`list_resources()` e `read_resource(uri)`) direto em processo, via `uv run python -c "..."`. Confirmou o resource registrado com o `mime_type` certo e o conteúdo batendo com o arquivo. Conectar com um client de verdade (Claude Desktop/Inspector) fica pro passo 5, não antes.

## Passo 3 — Resources dinâmicos

_(ainda não feito)_
