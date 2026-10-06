"""
Passo 1: lista todas as concessões rodoviárias da ANTT e grava em concessoes.json.

Uso:
    pip install requests
    python listar_concessoes.py

Saída:
    concessoes.json  -> [{"slug": "eco050", "nome": "ECO050", "url": "..."}, ...]
"""
import html
import json
import re
import sys
from pathlib import Path

import requests

LISTA = "https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
SAIDA = Path(__file__).resolve().parent / "concessoes.json"

# <a href=".../lista-de-concessoes/<slug>" ...>Nome</a>
LINK = re.compile(
    r'<a[^>]+href="' + re.escape(LISTA) + r'/([^"/?#]+)/?"[^>]*>(.*?)</a>',
    re.S | re.I,
)


def main() -> int:
    r = requests.get(LISTA, headers=HEADERS, timeout=60)
    r.raise_for_status()

    nomes: dict[str, str] = {}
    for slug, texto in LINK.findall(r.text):
        texto = html.unescape(re.sub(r"<[^>]+>", " ", texto))
        texto = re.sub(r"\s+", " ", texto).strip()
        # o link traz "Nome Área de atuação: UF Extensão: N km"; fica só o nome
        texto = re.split(r"\s+(?:Área de atuação|Extensão)", texto, maxsplit=1)[0].strip()
        # mantém o primeiro texto não vazio de cada slug
        if slug not in nomes or (not nomes[slug] and texto):
            nomes[slug] = texto

    concessoes = [
        {"slug": s, "nome": n or s, "url": f"{LISTA}/{s}"}
        for s, n in sorted(nomes.items(), key=lambda kv: kv[0].lower())
    ]
    SAIDA.write_text(json.dumps(concessoes, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(concessoes)} concessões gravadas em {SAIDA.name}")
    for c in concessoes:
        print(f"  {c['slug']:40s} {c['nome']}")
    return 0 if concessoes else 1


if __name__ == "__main__":
    sys.exit(main())
