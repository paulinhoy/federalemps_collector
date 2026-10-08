"""
Acesso ao portal da ANTT e caminhos/configuração comuns do acompanhamento de obras.

Página de cada concessão:
    <url_antt>/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-.../<ano>/<arquivo>/view
O download é o mesmo link sem o "/view".
"""
import hashlib
import html
import json
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests

PROJETO = Path(__file__).resolve().parent.parent
EMPREENDIMENTOS = PROJETO / "empreendimentos.json"
DADOS = PROJETO / "dados" / "acompanhamento_obras"
BRUTOS = DADOS / "brutos"          # brutos/<slug>/<ano>/arquivos | extraido
CONSOLIDADO = DADOS / "consolidado"

PASTA_OBRAS = "documentos-de-gestao/acompanhamento-de-obras"
# o nome da subpasta varia entre concessões ("...dos-cronogramas-de-obras..." / "...de-obras..."),
# então ela é descoberta na listagem de acompanhamento-de-obras
PREFIXO_SUBPASTA = "percentuais-de-avanco-fisico"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

sessao = requests.Session()
sessao.headers.update(HEADERS)


def empreendimentos() -> list[dict]:
    return json.loads(EMPREENDIMENTOS.read_text(encoding="utf-8"))


def get(url: str, tentativas: int = 3, **kw) -> requests.Response:
    for i in range(tentativas):
        try:
            return sessao.get(url, timeout=120, **kw)
        except requests.RequestException:
            if i == tentativas - 1:
                raise
            time.sleep(5 * (i + 1))


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


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(longo(p), "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def longo(p: Path) -> str:
    # prefixo \\?\ evita o limite de 260 caracteres do Windows (ZIPs da Rio Minas passam disso)
    return "\\\\?\\" + str(p.resolve()) if sys.platform == "win32" else str(p)


def sincronizar(url: str, destino: Path) -> str:
    """Baixa só se for novo ou mudou. Devolve 'novo', 'atualizado' ou 'inalterado'.

    O servidor da ANTT não informa Last-Modified nem ETag, só o tamanho (Content-Length).
    Tamanho igual => considera inalterado; tamanho diferente (ou ausente) => baixa e compara hash.
    A versão anterior de um arquivo atualizado é guardada em arquivos/_versoes/.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    existe = destino.exists() and destino.stat().st_size > 0
    tmp = destino.with_suffix(destino.suffix + ".part")
    for i in range(3):  # downloads grandes às vezes caem no meio (IncompleteRead)
        try:
            with get(url, stream=True) as r:
                r.raise_for_status()
                if "text/html" in r.headers.get("content-type", "").lower():
                    raise RuntimeError(f"resposta HTML em vez de arquivo: {url}")
                remoto = int(r.headers.get("content-length") or -1)
                if existe and remoto == destino.stat().st_size:
                    return "inalterado"
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(chunk_size=1 << 20):
                        f.write(bloco)
            break
        except (requests.RequestException, OSError):
            if i == 2:
                raise
            time.sleep(5 * (i + 1))
    if existe:
        if sha256(tmp) == sha256(destino):  # sem Content-Length: conteúdo igual
            tmp.unlink()
            return "inalterado"
        versoes = destino.parent / "_versoes"
        versoes.mkdir(exist_ok=True)
        carimbo = datetime.fromtimestamp(destino.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
        shutil.move(str(destino), str(versoes / f"{destino.stem}__{carimbo}{destino.suffix}"))
    tmp.replace(destino)
    return "atualizado" if existe else "novo"


def extrair(zip_path: Path, pasta: Path) -> int:
    pasta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            # nomes sem flag UTF-8 vêm em cp437; corrige para cp850
            if info.flag_bits & 0x800 == 0:
                try:
                    info.filename = info.filename.encode("cp437").decode("cp850")
                except Exception:
                    pass
        z.extractall(longo(pasta))
        return len(z.namelist())
