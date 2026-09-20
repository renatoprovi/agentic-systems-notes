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

_(ainda não feito)_
