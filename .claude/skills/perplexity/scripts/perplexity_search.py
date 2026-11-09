#!/usr/bin/env python3
"""Consulta a Agent API da Perplexity (POST /v1/responses) com busca na web e
imprime a resposta seguida das fontes consultadas.

Uso:
    python3 perplexity_search.py "pergunta" [--model perplexity/sonar]
        [--domains stf.jus.br,cnj.jus.br] [--recency "últimos 12 meses"]
        [--instructions "..."] [--no-search] [--max-tokens 2000] [--json]
    python3 perplexity_search.py --list-models

A chave é lida de PERPLEXITY_API_KEY. Nas sessões na nuvem do Claude Code, o
proxy de rede injeta a credencial cadastrada para api.perplexity.ai; nesse caso,
o valor fictício padrão basta.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.perplexity.ai/v1"
DEFAULT_MODEL = "perplexity/sonar"
DEFAULT_INSTRUCTIONS = (
    "Responda em português brasileiro formal, com precisão e objetividade. "
    "Fundamente cada afirmação relevante em fontes verificáveis e indique-as "
    "pela numeração [1], [2] etc. Distinga o que está confirmado do que é inferido. "
    "Não invente dados, julgados, normas, títulos de obras ou vínculos institucionais; "
    "se não encontrar a informação, diga expressamente."
)


def call(method, path, body=None, timeout=300):
    key = os.environ.get("PERPLEXITY_API_KEY", "proxy-injected")
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description="Pesquisa na web via Agent API da Perplexity.")
    p.add_argument("query", nargs="?", help="Pergunta ou tema a pesquisar.")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help="ID do modelo (padrão: perplexity/sonar; ver --list-models).")
    p.add_argument("--domains", help="Domínios a priorizar, separados por vírgula.")
    p.add_argument("--recency", help="Período a priorizar, em texto livre (ex.: 'desde 2024').")
    p.add_argument("--instructions", default=DEFAULT_INSTRUCTIONS, help="Instrução de sistema.")
    p.add_argument("--no-search", action="store_true", help="Desativa a ferramenta de busca na web.")
    p.add_argument("--max-tokens", type=int, default=None,
                   help="Limite de saída (obrigatório para modelos anthropic/*; padrão 4000 nesses casos).")
    p.add_argument("--json", action="store_true", help="Imprime a resposta bruta em JSON.")
    p.add_argument("--list-models", action="store_true", help="Lista os modelos disponíveis.")
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()

    try:
        if a.list_models:
            data = call("GET", "/models", timeout=a.timeout)
            for m in data.get("data", []):
                pr = m.get("pricing") or {}
                print(f"{m['id']}\t(entrada {pr.get('input', '?')} / saída {pr.get('output', '?')} USD por 1M tokens)")
            return 0
        if not a.query:
            p.error("informe a pergunta ou use --list-models")

        instructions = a.instructions
        if a.domains:
            instructions += " Priorize fontes dos domínios: " + a.domains + "."
        if a.recency:
            instructions += " Priorize fontes do período: " + a.recency + "."

        body = {"model": a.model, "instructions": instructions, "input": a.query}
        if not a.no_search:
            body["tools"] = [{"type": "web_search"}]
        if a.max_tokens or a.model.startswith("anthropic/"):
            body["max_output_tokens"] = a.max_tokens or 4000

        data = call("POST", "/responses", body, timeout=a.timeout)
    except urllib.error.HTTPError as e:
        print(f"Erro HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:2000]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Falha de conexão: {e.reason}", file=sys.stderr)
        return 1

    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if data.get("error"):
        print(f"Erro da API: {data['error']}", file=sys.stderr)
        return 1

    texts, sources = [], []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("text"):
                    texts.append(c["text"].strip())
        elif item.get("type") == "search_results":
            sources.extend(item.get("results", []))

    print("\n\n".join(texts) if texts else "(sem texto na resposta)")
    if sources:
        print("\nFontes consultadas:")
        seen = set()
        for r in sources:
            url = r.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            extra = " — ".join(x for x in (r.get("title"), r.get("date")) if x)
            print(f"[{r.get('id', len(seen))}] {url}" + (f" ({extra})" if extra else ""))
    usage = data.get("usage") or {}
    cost = (usage.get("cost") or {}).get("total_cost")
    print(f"\n(modelo: {data.get('model', a.model)}; tokens: {usage.get('total_tokens', '?')}"
          + (f"; custo: US$ {cost}" if cost is not None else "") + ")", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
