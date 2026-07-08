#!/usr/bin/env python3
"""
Pré-filtro determinístico de candidatos a template de proposta.

Esta skill busca as propostas aprovadas no SharePoint através do conector
de Microsoft 365 (uma ferramenta MCP chamada pelo agente, não algo que um
script Python consiga acessar sozinho). Este script NÃO se conecta ao
SharePoint — ele recebe a lista de candidatos que o agente já buscou
(título + um resumo/trecho de cada um) e faz um pré-ranqueamento leve por
sobreposição de palavras-chave, útil quando o banco de propostas crescer e
tiver dezenas de documentos.

Importante: isto é só um pré-filtro para reduzir quanto texto o agente
precisa ler quando o banco for grande. A seleção final dos 2-3 templates
mais relevantes (Passo 3 do SKILL.md) continua sendo um julgamento
semântico do agente, não deste script — não use a saída deste script como
decisão final, use como um "top N" para o agente então ler com atenção e
decidir de verdade.

Uso:
    python3 ranquear_templates.py briefing.txt candidatos.json [--top N]

Onde candidatos.json é uma lista:
    [
      {"id": "proposta-123", "titulo": "...", "resumo": "..."},
      ...
    ]

Saída (stdout): a mesma lista, reordenada, com um campo "score_preliminar".
"""

import argparse
import json
import re
import sys
from collections import Counter

STOPWORDS = {
    "a", "o", "os", "as", "de", "da", "do", "das", "dos", "e", "em", "para",
    "com", "um", "uma", "que", "no", "na", "nos", "nas", "por", "se", "ao",
    "aos", "à", "às", "é", "foi", "ser", "sua", "seu", "suas", "seus", "não",
}


def tokenize(text: str) -> Counter:
    words = re.findall(r"[a-zà-úA-ZÀ-Ú0-9]+", text.lower())
    return Counter(w for w in words if w not in STOPWORDS and len(w) > 2)


def score(briefing_tokens: Counter, candidate_tokens: Counter) -> float:
    if not briefing_tokens or not candidate_tokens:
        return 0.0
    shared = set(briefing_tokens) & set(candidate_tokens)
    if not shared:
        return 0.0
    # Sobreposição ponderada pela frequência nos dois lados (Jaccard ponderado simples)
    overlap = sum(min(briefing_tokens[w], candidate_tokens[w]) for w in shared)
    total = sum(briefing_tokens.values()) + sum(candidate_tokens.values())
    return round(2 * overlap / total, 4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("briefing_file", help="Arquivo de texto com o briefing do cliente novo")
    parser.add_argument("candidatos_json", help="JSON com a lista de candidatos já buscados no SharePoint")
    parser.add_argument("--top", type=int, default=10, help="Quantos candidatos retornar (default: 10)")
    args = parser.parse_args()

    with open(args.briefing_file, encoding="utf-8") as f:
        briefing_text = f.read()

    with open(args.candidatos_json, encoding="utf-8") as f:
        candidatos = json.load(f)

    briefing_tokens = tokenize(briefing_text)

    for c in candidatos:
        texto_candidato = f"{c.get('titulo', '')} {c.get('resumo', '')}"
        c["score_preliminar"] = score(briefing_tokens, tokenize(texto_candidato))

    candidatos.sort(key=lambda c: c["score_preliminar"], reverse=True)

    if all(c["score_preliminar"] == 0.0 for c in candidatos):
        print(
            "Aviso: nenhum candidato teve sobreposição de palavras com o briefing. "
            "Isso não significa que não há correlação semântica real (esse pré-filtro "
            "é só de palavras) — releia os candidatos com atenção antes de descartar o banco.",
            file=sys.stderr,
        )

    print(json.dumps(candidatos[: args.top], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
