---
name: perplexity
description: Pesquisa na web com a API da Perplexity (modelos Sonar), com respostas fundamentadas e lista de fontes citadas. Use quando o usuário pedir "pesquise na Perplexity", "use a Perplexity", "busca com fontes", ou quando a tarefa exigir informação atual e verificável (jurisprudência recente, normas, notícias, dados institucionais, literatura acadêmica), com filtros por período ou por domínio (ex.: stf.jus.br, cnj.jus.br, tjro.jus.br).
---

# Perplexity — pesquisa com fontes

## Como executar

```bash
python3 .claude/skills/perplexity/scripts/perplexity_search.py "PERGUNTA" [opções]
```

Opções:

| Opção | Uso |
|---|---|
| `--model` | ID do modelo; padrão `perplexity/sonar` (busca na web com fontes). `--list-models` lista os demais disponíveis na conta (inclusive modelos de terceiros) e seus preços |
| `--domains` | Domínios a priorizar (ex.: `stf.jus.br,cnj.jus.br,tjro.jus.br`); enviado como instrução, não como filtro rígido |
| `--recency` | Período a priorizar, em texto livre (ex.: `desde 2024`) |
| `--instructions` | Substitui a instrução padrão (português formal, com citações e sem invenções) |
| `--no-search` | Desativa a busca na web |
| `--max-tokens` | Limite de saída (obrigatório para modelos `anthropic/*`) |
| `--json` | Resposta bruta, com `search_results` completos |

Observação técnica: a Perplexity substituiu a antiga rota `/chat/completions` (modelos `sonar-pro` etc.) pela Agent API (`POST /v1/responses`). O script já usa a rota nova; a busca é ativada pela ferramenta `web_search` e as fontes vêm no item `search_results` da saída.

## Credencial

- Nas sessões na nuvem do Claude Code, a chave fica cadastrada como segredo de rede do host `api.perplexity.ai` e o proxy a injeta; não é preciso exportar nada.
- Em uso local, exporte `PERPLEXITY_API_KEY` antes de rodar.
- Nunca grave a chave em arquivo do repositório nem a exiba no chat.
- Se vier erro 401/403, a credencial não está cadastrada ou foi recusada: peça ao usuário que a cadastre (na nuvem, pela ferramenta de credenciais; em uso local, pela variável de ambiente).

## Diretrizes de uso

1. Formule a pergunta de forma específica, com órgão, período e tema.
2. Para temas jurídicos, prefira filtrar domínios oficiais (`stf.jus.br`, `stj.jus.br`, `cnj.jus.br`, `tjro.jus.br`, `planalto.gov.br`, `enfam.jus.br`).
3. Ao apresentar o resultado, preserve a numeração das fontes e liste os links ao final.
4. A resposta da Perplexity é ponto de partida: confira números de processos, datas e dispositivos legais na fonte primária antes de usá-los em peça ou documento oficial, e sinalize ao usuário o que não foi confirmado.
5. Não repita a mesma consulta sem necessidade: cada chamada consome créditos da conta.
