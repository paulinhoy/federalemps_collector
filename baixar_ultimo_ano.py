"""
Passo 2: para cada concessão de concessoes.json, baixa os arquivos do ÚLTIMO ANO que tenha
dados em "Percentuais de Avanço Físico dos Cronogramas de Obras e Serviços do Planejamento Anual".
ZIPs são descompactados.

Uso:
    pip install requests
    python listar_concessoes.py          # gera concessoes.json
    python baixar_ultimo_ano.py          # todas as concessões
    python baixar_ultimo_ano.py eco050 via-040   # só algumas (slugs)

Saída (ao lado do script):
    dados/<slug>/<ano>/arquivos/<arquivo>        (arquivos originais baixados)
    dados/<slug>/<ano>/extraido/<nome-do-zip>/   (conteúdo de cada ZIP)
    dados/resumo.json                            (o que foi baixado / erros por concessão)
"""
import html
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

AQUI = Path(__file__).resolve().parent
CONCESSOES = AQUI / "concessoes.json"
RAIZ = AQUI / "dados"

PASTA_OBRAS = "documentos-de-gestao/acompanhamento-de-obras"
# o nome da subpasta varia entre concessões ("...dos-cronogramas-de-obras..." / "...de-obras..."),
# então ela é descoberta na listagem de acompanhamento-de-obras
PREFIXO_SUBPASTA = "percentuais-de-avanco-fisico"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

sessao = requests.Session()
sessao.headers.update(HEADERS)


def get(url: str, **kw) -> requests.Response:
    return sessao.get(url, timeout=120, **kw)


def achar_pagina(url_concessao: str) -> str | None:
    """URL da subpasta 'percentuais de avanço físico...' da concessão (None se não existir)."""
    base = f"{url_concessao}/{PASTA_OBRAS}"
    r = get(base)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    subs = sorted(set(re.findall(r'href="' + re.escape(base) + r'/([^"/?#]+)"', r.text)))
    subs = [x for x in subs if x.startswith(PREFIXO_SUBPASTA)]
    return f"{base}/{subs[0]}" if subs else None


def anos_da_pagina(url_pagina: str) -> list[int] | None:
    """Anos disponíveis (abas da página), do mais novo para o mais antigo. None se a página não existe."""
    r = get(url_pagina)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    anos = {int(a) for a in re.findall(r'class="tab-content"\s+data-id="(\d{4})"', r.text)}
    if not anos:  # fallback: abas do cabeçalho
        anos = {int(a) for a in re.findall(r'<a href="" data-id="(\d{4})"', r.text)}
    return sorted(anos, reverse=True)


def arquivos_do_ano(url_pagina: str, ano: int) -> list[str]:
    """URLs de download (sem o sufixo /view) dos arquivos listados na pasta do ano."""
    r = get(f"{url_pagina}/{ano}")
    if r.status_code == 404:
        return []
    r.raise_for_status()
    links = re.findall(r'href="([^"]+?)/view"', html.unescape(r.text))
    base = f"{url_pagina}/{ano}/"
    return sorted({l for l in links if l.startswith(base)})


def baixar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    with get(url, stream=True) as r:
        r.raise_for_status()
        if "text/html" in r.headers.get("content-type", "").lower():
            raise RuntimeError(f"resposta HTML em vez de arquivo: {url}")
        with open(tmp, "wb") as f:
            for bloco in r.iter_content(chunk_size=1 << 20):
                f.write(bloco)
    tmp.replace(destino)


def extrair(zip_path: Path, pasta: Path) -> int:
    pasta.mkdir(parents=True, exist_ok=True)
    # prefixo \?\ evita o limite de 260 caracteres do Windows (nomes de ZIP + pastas longos)
    destino = "\\\\?\\" + str(pasta.resolve()) if sys.platform == "win32" else str(pasta)
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            # nomes sem flag UTF-8 vêm em cp437; corrige para cp850
            if info.flag_bits & 0x800 == 0:
                try:
                    info.filename = info.filename.encode("cp437").decode("cp850")
                except Exception:
                    pass
        z.extractall(destino)
        return len(z.namelist())


def processar(c: dict) -> dict:
    slug = c["slug"]
    res = {"slug": slug, "nome": c["nome"], "ano": None, "arquivos": [], "erros": [], "status": "ok"}
    url_pagina = achar_pagina(c["url"])
    if url_pagina is None:
        res["status"] = "sem_pagina"
        print(f"[{slug}] não tem a pasta de percentuais de avanço físico")
        return res

    anos = anos_da_pagina(url_pagina)
    if anos is None:
        res["status"] = "sem_pagina"
        print(f"[{slug}] página de acompanhamento não existe (404)")
        return res

    # primeiro ano (mais novo) que realmente tenha arquivos
    for ano in anos:
        urls = arquivos_do_ano(url_pagina, ano)
        if urls:
            break
    else:
        res["status"] = "sem_dados"  # pasta existe, mas vazia no site
        print(f"[{slug}] pasta vazia no site (anos: {anos or 'nenhum'})")
        return res

    res["ano"] = ano
    base = RAIZ / slug / str(ano)
    print(f"[{slug}] ano {ano}: {len(urls)} arquivo(s)")

    for url in urls:
        nome = unquote(Path(urlparse(url).path).name)
        destino = base / "arquivos" / nome
        try:
            if destino.exists() and destino.stat().st_size > 0:
                print(f"    já baixado: {nome}")
            else:
                print(f"    baixando:   {nome}")
                baixar(url, destino)
            item = {"arquivo": nome, "url": url, "tamanho": destino.stat().st_size}
            # .xlsx/.xlsm também são ZIPs por dentro: só extrai o que é .zip de fato
            if destino.suffix.lower() == ".zip" and zipfile.is_zipfile(destino):
                n = extrair(destino, base / "extraido" / destino.stem)
                item["extraidos"] = n
            res["arquivos"].append(item)
        except Exception as e:
            res["erros"].append(f"{nome}: {e}")
            print(f"    ERRO {nome}: {e}", file=sys.stderr)

    if res["erros"]:
        res["status"] = "parcial"
    return res


def main(argv: list[str]) -> int:
    if not CONCESSOES.exists():
        print("concessoes.json não encontrado. Rode primeiro: python listar_concessoes.py", file=sys.stderr)
        return 1
    todas = json.loads(CONCESSOES.read_text(encoding="utf-8"))
    if argv:
        todas = [c for c in todas if c["slug"] in argv]

    RAIZ.mkdir(exist_ok=True)
    resumo = []
    for c in todas:
        try:
            resumo.append(processar(c))
        except Exception as e:
            print(f"[{c['slug']}] ERRO: {e}", file=sys.stderr)
            resumo.append({"slug": c["slug"], "nome": c["nome"], "status": "erro", "erros": [str(e)]})

    (RAIZ / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Resumo ===")
    for r in resumo:
        print(f"  {r['slug']:40s} {r['status']:11s} ano={r.get('ano')}  arquivos={len(r.get('arquivos', []))}")
    return 1 if any(r["status"] in ("erro", "parcial") for r in resumo) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
