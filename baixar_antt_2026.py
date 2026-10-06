"""
Baixa e descompacta os ZIPs de 2026 (execução mensal) da Ecovias Minas Goiás (ECO050)
publicados na ANTT.

Uso:
    pip install requests
    python baixar_antt_2026.py

Saída (ao lado do script):
    dados/zips/<arquivo>.zip
    dados/extraido/<mes>/...   (conteúdo de cada ZIP)
"""
import sys
import zipfile
from pathlib import Path

import requests

BASE = (
    "https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/"
    "lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/"
    "percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/"
)

# (pasta de destino, nome do arquivo no site)
ARQUIVOS = [
    ("2026-01", "execucao_mensal___01-2026-minas-goias.zip"),
    ("2026-02", "i___execucao_mensal___02-2026-minas-goias.zip"),
    ("2026-04", "execucao_mensal___04-2026minasgoias.zip"),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

RAIZ = Path(__file__).resolve().parent / "dados"
ZIPS = RAIZ / "zips"
EXTRAIDO = RAIZ / "extraido"


def baixar(nome: str, destino: Path) -> None:
    # URL SEM o sufixo "/view" devolve o arquivo em si
    url = BASE + nome
    with requests.get(url, headers=HEADERS, stream=True, timeout=120) as r:
        r.raise_for_status()
        if "zip" not in r.headers.get("content-type", "").lower():
            raise RuntimeError(f"Resposta inesperada ({r.headers.get('content-type')}) em {url}")
        with open(destino, "wb") as f:
            for bloco in r.iter_content(chunk_size=1 << 20):
                f.write(bloco)


def main() -> int:
    ZIPS.mkdir(parents=True, exist_ok=True)
    EXTRAIDO.mkdir(parents=True, exist_ok=True)
    erros = 0

    for mes, nome in ARQUIVOS:
        zip_path = ZIPS / nome
        pasta = EXTRAIDO / mes
        try:
            if zip_path.exists() and zipfile.is_zipfile(zip_path):
                print(f"[{mes}] já baixado: {zip_path.name}")
            else:
                print(f"[{mes}] baixando {nome} ...")
                baixar(nome, zip_path)
                print(f"[{mes}] {zip_path.stat().st_size / 1e6:.1f} MB")

            pasta.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path) as z:
                # nomes antigos de ZIP costumam vir em cp437; tenta corrigir para cp850/utf-8
                for info in z.infolist():
                    if info.flag_bits & 0x800 == 0:
                        try:
                            info.filename = info.filename.encode("cp437").decode("cp850")
                        except Exception:
                            pass
                z.extractall(pasta)
                print(f"[{mes}] extraídos {len(z.namelist())} arquivo(s) em {pasta}")
        except Exception as e:
            erros += 1
            print(f"[{mes}] ERRO: {e}", file=sys.stderr)

    print("\nConteúdo extraído:")
    for p in sorted(EXTRAIDO.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(RAIZ)}  ({p.stat().st_size / 1e3:.0f} KB)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
