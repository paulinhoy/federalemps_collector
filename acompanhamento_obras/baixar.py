"""
Baixa TODOS os anos (histórico completo) de "Percentuais de Avanço Físico..." dos empreendimentos de
empreendimentos.json. Só baixa o que é novo ou mudou (por tamanho); ZIPs são descompactados.

Uso:
    python acompanhamento_obras/baixar.py            # todos os empreendimentos
    python acompanhamento_obras/baixar.py eco050     # só alguns (slug_antt)

Saída em dados/acompanhamento_obras/:
    brutos/<slug>/<ano>/arquivos/<arquivo>          arquivos originais (versões antigas em arquivos/_versoes/)
    brutos/<slug>/<ano>/extraido/<nome-do-zip>/     conteúdo de cada ZIP
    manifesto.json                                  estado de cada arquivo (url, tamanho, sha256, quando mudou)
    alteracoes.jsonl                                log do que apareceu/mudou em cada execução
    historico_resumo.json                           o que foi encontrado por empreendimento e ano
"""
import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from portal_antt import (BRUTOS, DADOS, achar_pagina, anos_da_pagina, arquivos_do_ano, empreendimentos, extrair,
                         longo, sha256, sincronizar)


def processar(e: dict) -> dict:
    slug = e["slug_antt"]
    res = {"id_empreendimento": e["id_empreendimento"], "slug": slug, "nome": e["nome"], "anos": {}, "erros": []}
    url_pagina = achar_pagina(e["url_antt"])
    anos = anos_da_pagina(url_pagina) if url_pagina else None
    if not anos:
        res["erros"].append("sem página de percentuais de avanço físico")
        return res
    for ano in sorted(anos):
        urls = arquivos_do_ano(url_pagina, ano)
        base = BRUTOS / slug / str(ano)
        print(f"[{slug}] {ano}: {len(urls)} arquivo(s)")
        itens = []
        for url in urls:
            nome = unquote(Path(urlparse(url).path).name)
            destino = base / "arquivos" / nome
            try:
                acao = sincronizar(url, destino)
                print(f"    {acao:10s}  {nome}")
                item = {"arquivo": nome, "url": url, "tamanho": destino.stat().st_size, "acao": acao}
                # .xlsx/.xlsm também são ZIPs por dentro: só extrai o que é .zip de fato
                if destino.suffix.lower() == ".zip" and zipfile.is_zipfile(destino):
                    pasta = base / "extraido" / destino.stem
                    if acao != "inalterado" or not pasta.exists():
                        if pasta.exists():  # versão nova: não deixa sobra da antiga
                            shutil.rmtree(longo(pasta))
                        item["extraidos"] = extrair(destino, pasta)
                itens.append(item)
            except Exception as ex:
                res["erros"].append(f"{ano}/{nome}: {ex}")
                print(f"    ERRO {nome}: {ex}", file=sys.stderr)
        res["anos"][str(ano)] = itens
    return res


def main(argv: list[str]) -> int:
    alvo = [e for e in empreendimentos() if not argv or e["slug_antt"] in argv]
    BRUTOS.mkdir(parents=True, exist_ok=True)
    resumo = [processar(e) for e in alvo]

    agora = datetime.now().isoformat(timespec="seconds")
    arq_man = DADOS / "manifesto.json"
    manifesto = json.loads(arq_man.read_text(encoding="utf-8")) if arq_man.exists() else {}
    novidades = []
    for r in resumo:
        for ano, itens in r["anos"].items():
            for a in itens:
                chave = f"{r['slug']}/{ano}/{a['arquivo']}"
                ent = manifesto.get(chave, {"primeira_vez": agora})
                if a["acao"] != "inalterado" or "sha256" not in ent:
                    ent.update(sha256=sha256(BRUTOS / r["slug"] / ano / "arquivos" / a["arquivo"]), atualizado_em=agora)
                ent.update(url=a["url"], tamanho=a["tamanho"], visto_em=agora)
                manifesto[chave] = ent
                if a["acao"] != "inalterado":
                    novidades.append({"quando": agora, "slug": r["slug"], "ano": int(ano), "arquivo": a["arquivo"],
                                      "acao": a["acao"]})
    arq_man.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    if novidades:
        with open(DADOS / "alteracoes.jsonl", "a", encoding="utf-8") as f:
            for n in novidades:
                f.write(json.dumps(n, ensure_ascii=False) + "\n")

    # execução parcial (só alguns slugs) atualiza esses empreendimentos sem apagar os outros do resumo
    arq_hist = DADOS / "historico_resumo.json"
    anterior = {r["slug"]: r for r in json.loads(arq_hist.read_text(encoding="utf-8"))} if arq_hist.exists() else {}
    anterior.update({r["slug"]: r for r in resumo})
    arq_hist.write_text(json.dumps(list(anterior.values()), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== Novidades: {len(novidades)} ===")
    for n in novidades[:50]:
        print(f"  {n['acao']:10s} {n['slug']}/{n['ano']}  {n['arquivo']}")
    print("\n=== Resumo ===")
    for r in resumo:
        anos = ", ".join(f"{a}:{len(i)}" for a, i in r["anos"].items())
        print(f"  {r['id_empreendimento']:4d} {r['slug']:22s} {anos}  erros={len(r['erros'])}")
    return 1 if any(r["erros"] for r in resumo) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
