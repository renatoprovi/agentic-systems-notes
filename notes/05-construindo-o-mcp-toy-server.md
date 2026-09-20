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

**Feito:** `main.py` agora varre `notes/*.md` e registra um resource por arquivo — nenhum nome de arquivo hardcoded.

**Correção da minha própria hipótese do passo 2:** eu tinha registrado ali que isso "provavelmente vira um resource *template*, com `{arquivo}` na URI". Ao ler a base de resources (`mcp/server/mcpserver/resources/types.py`), isso se mostrou a escolha errada: template resource serve pra quando o servidor **não sabe** o conjunto de URIs válidas de antemão (o client é quem monta a URI). Aqui o servidor sabe exatamente quais fichamentos existem no boot — então o certo é registrar um resource concreto por arquivo, pra cada um aparecer nomeado em `list_resources()`. Com template, o client não veria a lista de fichamentos disponíveis, só o padrão de URI.

**Segunda descoberta, que simplificou o código:** existe uma classe `FileResource` pronta (mesmo módulo), que já sabe ler de um `Path` com a codificação certa — não precisei envelopar `read_text()` numa função e registrar via `FunctionResource` como cheguei a cogitar. Isso também deixou o resource do Passo 2 redundante como estava: refatorei pra ele nascer do mesmo loop, em vez de manter dois jeitos diferentes de expor a mesma coisa (arquivo → resource).

```python
for note_path in sorted(NOTES_DIR.glob("*.md")):
    slug = note_path.stem
    mcp.add_resource(
        FileResource(
            uri=f"notes://{slug}",
            name=slug,
            title=note_path.name,
            description=f"Fichamento: {note_path.name}",
            mime_type="text/markdown",
            path=note_path,
        )
    )
```

**Detalhe não planejado:** o glob `notes/*.md` também pega o `README.md` da pasta (não é fichamento, é o índice). Decidi manter — vira `notes://README`, e um client de fora se beneficia de ter o índice como mais um resource disponível, não só os fichamentos individuais.

**Validação:** `list_resources()` retornou os 7 arquivos (`00` a `05` + `README`), cada um com URI, título e mime type corretos; leitura de `notes://02-agent-skills` bateu com o conteúdo real do arquivo.

## Passo 4 — Tool de busca

**Feito:** `search_notes(term)`, uma tool que varre `notes/*.md` (mesma fonte dos resources do passo 3) e devolve linhas que batem com o termo, no formato `arquivo:linha: texto` — como um `grep` simples.

**A descoberta de ACI do passo, batendo direto com [01](01-building-effective-agents.md)/[04](04-build-mcp-server.md):** minha primeira versão documentava o parâmetro `term` só na seção "Args:" da docstring, do jeito Google-style que o guia oficial usa no exemplo de clima. Testei o schema gerado (`mcp.list_tools()`) e o texto do "Args:" **não vira `description` do parâmetro** — só fica dentro do texto bruto da tool inteira. O client vê `term` sem explicação nenhuma, exceto se parsear a docstring inteira sozinho. Troquei pra `Annotated[str, Field(description=...)]`:

```python
@mcp.tool()
def search_notes(
    term: Annotated[str, Field(description="Word or phrase to search for (case-insensitive).")],
) -> str:
    """Search this repo's reading notes for a term and return matching lines."""
```

Depois disso, `input_schema` passou a ter `term.description` preenchido de verdade. Ou seja: nesta versão do SDK, "Args:" na docstring é só texto pra humano/modelo ler junto da descrição geral — quem vira *schema* estruturado (o que a ACI realmente usa pra não errar o tipo/uso do parâmetro) é a anotação via `Field`. Isso é uma nuance que só apareceu testando o schema gerado, não lendo a doc.

**Validação:** schema confirmado com `description` por parâmetro; busca por "progressive disclosure" retornou as duas linhas certas de `02-agent-skills.md`; busca por um termo inexistente devolveu a mensagem de "sem match" em vez de lista vazia silenciosa.

## Passo 5 — Conectar com um client de verdade

_(ainda não feito)_
