#!/usr/bin/env python3
"""Consulta a API da Perplexity (Sonar) e imprime a resposta com as fontes citadas.

Uso:
    python3 perplexity_search.py "pergunta" [--model sonar-pro] [--recency month]
        [--domains stf.jus.br,cnj.jus.br] [--context high] [--system "..."] [--json]

A chave é lida de PERPLEXITY_API_KEY. Em sessões na nuvem do Claude Code, o proxy
de rede injeta a credencial cadastrada para api.perplexity.ai; nesse caso, um valor
fictício basta (o padrão abaixo).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.perplexity.ai/chat/completions"
MODELS = ["sonar", "sonar-pro", "sonar-reasoning-pro", "sonar-deep-research"]
DEFAULT_SYSTEM = (
    "Responda em português brasileiro formal, com precisão e objetividade. "
    "Fundamente cada afirmação relevante em fontes verificáveis e indique-as "
    "pela numeração [1], [2] etc. Não invente dados, julgados ou normas."
)


def main() -> int:
    p = argparse.ArgumentParser(description="Pesquisa na web via API da Perplexity.")
    p.add_argument("query", help="Pergunta ou tema a pesquisar.")
    p.add_argument("--model", default="sonar-pro", choices=MODELS)
    p.add_argument("--recency", choices=["hour", "day", "week", "month", "year"],
                   help="Restringe as fontes ao período indicado.")
    p.add_argument("--domains", help="Domínios separados por vírgula; prefixe com '-' para excluir.")
    p.add_argument("--context", choices=["low", "medium", "high"], default="medium",
                   help="Volume de contexto de busca.")
    p.add_argument("--system", default=DEFAULT_SYSTEM, help="Instrução de sistema.")
    p.add_argument("--json", action="store_true", help="Imprime a resposta bruta em JSON.")
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()

    body = {
        "model": a.model,
        "messages": [
            {"role": "system", "content": a.system},
            {"role": "user", "content": a.query},
        ],
        "web_search_options": {"search_context_size": a.context},
    }
    if a.recency:
        body["search_recency_filter"] = a.recency
    if a.domains:
        body["search_domain_filter"] = [d.strip() for d in a.domains.split(",") if d.strip()][:20]

    key = os.environ.get("PERPLEXITY_API_KEY", "pplx-placeholder")
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Erro HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:2000]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Falha de conexão: {e.reason}", file=sys.stderr)
        return 1

    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(data["choices"][0]["message"]["content"].strip())
    results = data.get("search_results") or []
    citations = data.get("citations") or [r.get("url") for r in results]
    if citations:
        print("\nFontes:")
        by_url = {r.get("url"): r for r in results}
        for i, url in enumerate(citations, 1):
            r = by_url.get(url, {})
            title = r.get("title") or ""
            date = r.get("date") or ""
            extra = " — ".join(x for x in (title, date) if x)
            print(f"[{i}] {url}" + (f" ({extra})" if extra else ""))
    usage = data.get("usage") or {}
    if usage:
        print(f"\n(modelo: {data.get('model', a.model)}; tokens: {usage.get('total_tokens', '?')})",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
