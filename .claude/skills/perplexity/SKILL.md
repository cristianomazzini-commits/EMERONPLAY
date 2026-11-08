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

| Opção | Valores | Uso |
|---|---|---|
| `--model` | `sonar`, `sonar-pro` (padrão), `sonar-reasoning-pro`, `sonar-deep-research` | `sonar` para consultas rápidas; `sonar-pro` para o uso geral; `sonar-reasoning-pro` para análise comparativa; `sonar-deep-research` para levantamentos extensos (lento e mais caro) |
| `--recency` | `hour`, `day`, `week`, `month`, `year` | Restringe as fontes ao período |
| `--domains` | `stf.jus.br,cnj.jus.br` ou `-wikipedia.org` | Inclui (ou exclui, com `-`) domínios; até 20 |
| `--context` | `low`, `medium` (padrão), `high` | Volume de contexto de busca |
| `--system` | texto | Substitui a instrução padrão (português formal, com citações) |
| `--json` | — | Resposta bruta, inclusive `search_results` |

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
