"""
Organiza os valores financeiros encontrados no portal da ANTT e liga cada valor às obras de
dados/acompanhamento_obras/consolidado/lista_obras.csv.

Uso (depois de acompanhamento_obras/consolidar.py):
    pip install pyxlsb
    python valores_obras/organizar.py

Hierarquia da ligação (coluna `forma` de obras_valores):
    direto          o valor é da própria obra (ou do trecho que coincide com ela)
    unitario_tipo   valor de referência por unidade de um tipo de dispositivo (ex.: rotatória tipo 1 em GO);
                    vale para cada obra daquele tipo, mas não é exclusivo dela
    grupo           valor total de um grupo/trecho que contém várias obras: o valor NÃO é da obra, está
                    dividido entre as `n_obras_no_grupo` obras (e, quando `grupo_maior_que_lista`, também entre
                    obras que não estão na nossa lista)
Obras sem nenhum valor ficam sem linha em obras_valores (e aparecem em resumo_por_obra com sem_valor=True).

Saída em dados/valores_obras/:
    valores_encontrados.csv         1 linha por valor achado, como está na fonte (valor, data-base, onde está)
    obras_valores.csv               ligação obra x valor (forma, método, confiança)
    resumo_por_obra.csv             1 linha por obra: melhor valor de cada tipo, quantas fontes, fontes concorrentes
    valor_total_empreendimento.csv  totais do empreendimento (Capex, Opex, contrato, realizado por ano)
    valores_obras.xlsx              as 4 tabelas em abas
"""
import fnmatch
import os
import re
import sys
import unicodedata
import warnings
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd
from pyxlsb import open_workbook

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
sys.path.insert(0, str(PROJETO / "acompanhamento_obras"))
from portal_antt import empreendimentos, extrair, longo, sincronizar  # noqa: E402
from fontes import FONTES  # noqa: E402

warnings.filterwarnings("ignore")

DADOS = PROJETO / "dados" / "valores_obras"
PASTA_FONTES = DADOS / "fontes"
LISTA_OBRAS = PROJETO / "dados" / "acompanhamento_obras" / "consolidado" / "lista_obras.csv"
NOMES = {e["id_empreendimento"]: e["nome"] for e in empreendimentos()}

TOL_PONTO = 0.6  # km: distância máxima entre obra pontual e o local do valor (versões do SNV diferem um pouco)
ORDEM_FORMA = {"direto": 0, "unitario_tipo": 1, "grupo": 2}
TIPOS_VALOR = ["inicial_leilao", "inicial_inclusao", "aprovado_revisao", "estimativa_concessionaria"]


# ----------------------------------------------------------------------------- utilitários

def norm(t) -> str:
    t = "".join(c for c in unicodedata.normalize("NFD", str(t or "")) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip().lower()


def tipo_obra(texto) -> str | None:
    """Tipo da obra a partir da descrição (ordem importa: 'Trevo ... (acompanha a duplicação)' é interseção)."""
    n = norm(texto)
    regras = [
        # "Vias Marginais (inclusive OAE e iluminação)" é marginal: iluminação só quando é o objeto da obra
        ("iluminacao", r"^(\[[^\]]*\] )?ilumina|^(implantacao|troca) de (tecnologia|ilumina)"), ("passarela", r"passarela"), ("rotatoria", r"rotatori"),
        ("retorno", r"retorno em nivel"), ("intersecao", r"retorno em desnivel|trevo|interconex|interse|entroncamento"),
        ("acesso", r"acesso"), ("marginal", r"margina|vias? laterais"), ("acostamento", r"acostamento"),
        ("faixa_adicional", r"faixas? adiciona"), ("correcao_tracado", r"correcao de tracado"),
        ("oae", r"\boae\b|ponte|obras?-de-arte"), ("adequacao_pista", r"adequacao da pista"),
        ("recuperacao", r"restaura|recupera"), ("duplicacao", r"duplica"),
    ]
    for tipo, rx in regras:
        if re.search(rx, n):
            return tipo
    return None


def kms_da_descricao(texto):
    """'km 006+000 ao km 009+130' / '870+650 ao 872+260' / 'km 95,700 ao 99,440' -> (6.0, 9.13)."""
    n = norm(texto)
    ks = [int(a) + int(b) / 1000 for a, b in re.findall(r"(\d{1,3})\s*\+\s*(\d{3})", n)]
    if not ks:
        ks = [float(f"{a}.{b}") for a, b in re.findall(r"km\s*(\d{1,3}),(\d{1,3})", n)]
    if not ks:
        return None, None
    return ks[0], (ks[1] if len(ks) > 1 else None)


def rodovia_de(texto) -> str | None:
    """'BR-364/GO', 'br 365', 365, '050' -> 'BR-364' ..."""
    if isinstance(texto, (int, float)) and not isinstance(texto, bool) and texto == texto:
        return f"BR-{int(texto):03d}"
    n = norm(texto)
    m = re.search(r"br[-\s]?(\d{2,3})\b", n) or re.fullmatch(r"(\d{2,3})", n)
    return f"BR-{int(m.group(1)):03d}" if m else None


def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def ler_xlsb(caminho: Path, aba: str) -> list[list]:
    with open_workbook(longo(caminho)) as wb:
        with wb.get_sheet(aba) as sh:
            linhas = []
            for row in sh.rows():
                linha = [None] * (max((c.c for c in row), default=-1) + 1)
                for c in row:
                    linha[c.c] = c.v
                linhas.append(linha)
    return linhas


def celula(linha, j):
    return linha[j] if j < len(linha) else None


# ----------------------------------------------------------------------------- fontes

def baixar_fontes() -> dict:
    """Baixa as planilhas (e extrai os membros dos ZIPs). Devolve {fonte_id: [arquivos locais]}."""
    locais = {}
    for fid, f in FONTES.items():
        if not f.get("baixar"):
            continue
        pasta = PASTA_FONTES / fid
        destino = pasta / Path(f["url"]).name
        acao = sincronizar(f["url"], destino)
        print(f"    {acao:10s} {fid}")
        if f.get("membros"):
            ext = pasta / "extraido"
            if acao != "inalterado" or not ext.exists():
                extrair(destino, ext)
            arquivos = []
            for raiz, _, nomes in os.walk(longo(ext)):
                for nome in nomes:
                    if any(fnmatch.fnmatch(nome.lower(), m.lower()) for m in f["membros"]):
                        arquivos.append(Path(raiz.replace("\\\\?\\", "", 1)) / nome)
            locais[fid] = sorted(arquivos)
        else:
            locais[fid] = [destino]
    return locais


def valor(**kw) -> dict:
    base = dict(valor_id=None, id_empreendimento=None, tipo_valor=None, natureza="capex", nivel=None, tipo_obra=None,
                subtipo=None, uf=None, descricao_fonte=None, item_per_fonte=None, nome_chave=None, rodovia=None,
                km_inicial=None, km_final=None,
                quantidade=None, componente=None, valor=None, data_base=None, valor_precos_iniciais=None,
                data_base_precos_iniciais=None, fonte_id=None, localizacao=None, conferido_por="extração automática",
                observacao=None, tipos_do_grupo=None, grupo_maior_que_lista=None)
    base.update(kw)
    return base


# ----------------------------------------------------------------------------- extratores

def ecc_evtea(arq: Path) -> tuple[list, list]:
    """EVTEA do leilão da Cerrado (fator-d.xlsx): aba Ampliação (valores por obra, trecho e unitário por tipo x UF),
    aba OAEs_novas (pontes da duplicação) e aba PER 364-365 (Capex/Opex totais)."""
    wb = openpyxl.load_workbook(longo(arq), read_only=True, data_only=True)
    per = [list(r) for r in wb["PER 364-365"].iter_rows(min_row=1, max_row=80, max_col=6, values_only=True)]
    m = re.search(r"(janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)/(\d{4})",
                  norm(" ".join(str(c) for c in per[4] if c)))
    meses = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
             "novembro", "dezembro"]
    data_base = f"{m.group(2)}-{meses.index(m.group(1)) + 1:02d}" if m else "não informada"
    fid = "ecc_evtea_fator_d"

    valores, totais = [], []
    for i, r in enumerate(per, 1):
        j = next((j for j, c in enumerate(r) if norm(c) in ("capex", "opex")), None)
        v = next(((k, num(c)) for k, c in enumerate(r) if j is not None and k > j and num(c)), None)
        if v:
            rotulo = norm(r[j])
            totais.append(dict(total_id=f"ECC-EVTEA-{rotulo.upper()}", id_empreendimento=103, tipo_valor="inicial_leilao",
                               natureza=rotulo, descricao=f"{rotulo.upper()} total do EVTEA do leilão (30 anos)",
                               valor=v[1], data_base=data_base, periodo="30 anos", fonte_id=fid,
                               localizacao=f"aba PER 364-365, linha {i}, coluna {openpyxl.utils.get_column_letter(v[0] + 1)}",
                               precisao="alta", conferido_por="extração automática", observacao=None))

    secoes = {"1.1": None, "1.2.1": "marginal", "1.2.2": "acostamento", "1.2.3": "acostamento",
              "1.3.1.1": "faixa_adicional", "1.3.1.2": "correcao_tracado", "1.3.3": "duplicacao", "1.3.4": "retorno"}
    disp = {"passarela em pista simples": ("passarela", "PPS"), "passarela em pista dupla": ("passarela", "PPD"),
            "melhoria de intersecao": ("intersecao", None), "rotatoria alongada - tipo 1": ("rotatoria", "RA-1A"),
            "rotatoria alongada - tipo 2": ("rotatoria", "RA-2A"),
            "melhoria em acessos - pista simples": ("acesso", "APS"), "melhoria em acessos - pista dupla": ("acesso", "APD")}
    for i, r in enumerate(wb["Ampliação"].iter_rows(min_row=130, max_row=140, max_col=10, values_only=True), 130):
        if norm(r[4]).startswith("total obras de melhorias") and num(r[9]):
            totais.append(dict(total_id="ECC-EVTEA-AMPLIACAO", id_empreendimento=103, tipo_valor="inicial_leilao",
                               natureza="ampliacao", descricao=f"{r[4]} (EVTEA do leilão)", valor=num(r[9]),
                               data_base=data_base, periodo="30 anos", fonte_id=fid,
                               localizacao=f"aba Ampliação, linha {i}, coluna J", precisao="alta",
                               conferido_por="extração automática", observacao=None))
    linhas = list(wb["Ampliação"].iter_rows(min_row=6, max_row=112, max_col=11, values_only=True))
    itens = [str(r[3] or "").strip().rstrip(".") for r in linhas]
    uf = None
    for i, (r, item) in enumerate(zip(linhas, itens), 6):
        desc, k0, k1, qtd, unit, total = r[4], num(r[5]), r[6], r[7], num(r[8]), num(r[9])
        nd = norm(desc)
        if nd in ("goias", "minas gerais"):
            uf = "GO" if nd == "goias" else "MG"
            continue
        # só linhas-folha (sem sub-itens); cabeçalhos trazem subtotais
        if not total or not item or any(x.startswith(item + ".") for x in itens):
            continue
        pref = max((p for p in secoes if item.startswith(p + ".")), key=len, default=None)
        secao = (pref, secoes[pref]) if pref else None
        loc = f"aba Ampliação, linha {i}, coluna J (total)"
        rod = {"GO": "BR-364", "MG": "BR-365"}.get(uf)
        if nd in disp:  # dispositivo pontual: unitário por tipo x UF
            tp, sub = disp[nd]
            valores.append(valor(valor_id=f"ECC-EVTEA-L{i}", id_empreendimento=103, tipo_valor="inicial_leilao", nivel="tipo",
                                 tipo_obra=tp, subtipo=sub, uf=uf, rodovia=rod, descricao_fonte=f"{desc} ({uf})",
                                 quantidade=qtd, componente="por unidade", valor=unit, data_base=data_base, fonte_id=fid,
                                 localizacao=f"aba Ampliação, linha {i}, coluna I (unitário)",
                                 observacao=f"Total do item: {qtd:g} un. = R$ {total:,.2f} (coluna J)"))
            continue
        if item.startswith("1.1."):  # complementação de obras do DNIT (Xapetuba, Trevão): orçamento próprio
            chave = "xapetuba" if "xapetuba" in nd else "trevao" if "trevao" in nd else None
            valores.append(valor(valor_id=f"ECC-EVTEA-L{i}", id_empreendimento=103, tipo_valor="inicial_leilao", nivel="obra",
                                 tipo_obra="intersecao", uf="MG", rodovia="BR-365", nome_chave=chave, descricao_fonte=desc,
                                 quantidade=qtd, componente="obra", valor=total, data_base=data_base, fonte_id=fid, localizacao=loc))
            continue
        tp = secao[1] if secao else None
        if tp == "correcao_tracado":  # "BR-364/GO - km 25": rodovia e km vêm da descrição
            k0 = float(re.search(r"km (\d+)", nd).group(1))
            rod, uf = rodovia_de(desc), "GO" if "/go" in nd else "MG"
        if k0 is None and tp != "correcao_tracado":
            if tp == "acostamento":  # adequação de acostamentos "Subtrechos 10 a 16": sem km, vale como grupo do tipo em MG
                valores.append(valor(valor_id=f"ECC-EVTEA-L{i}", id_empreendimento=103, tipo_valor="inicial_leilao", nivel="grupo",
                                     tipo_obra=tp, uf=uf, rodovia=rod, descricao_fonte=f"Adequação de acostamentos - {desc} ({uf})",
                                     quantidade=qtd, componente="grupo", valor=total, data_base=data_base, fonte_id=fid,
                                     localizacao=loc, tipos_do_grupo="acostamento", grupo_maior_que_lista=True,
                                     observacao="Sem km na fonte: ligado às obras de acostamento da BR-365/MG"))
            continue
        k1 = num(k1)
        nivel = "obra" if tp in ("marginal", "correcao_tracado") else "trecho"
        valores.append(valor(valor_id=f"ECC-EVTEA-L{i}", id_empreendimento=103, tipo_valor="inicial_leilao", nivel=nivel,
                             tipo_obra=tp, uf=uf, rodovia=rod, descricao_fonte=f"{desc} ({uf})", km_inicial=k0, km_final=k1,
                             quantidade=qtd, componente="obra" if nivel == "obra" else "trecho", valor=total,
                             data_base=data_base, fonte_id=fid, localizacao=loc,
                             observacao=None if nivel == "obra" else
                             "Valor do subtrecho inteiro: pode conter várias obras da lista"))
        if tp == "duplicacao":
            valores[-1]["observacao"] = "Duplicação do subtrecho inteiro (inclui as OAEs da aba OAEs_novas? não confirmado)"

    ws = wb["OAEs_novas"]
    for i, r in enumerate(ws.iter_rows(min_row=7, max_row=14, max_col=9, values_only=True), 7):
        r = r[1:]  # coluna A vazia: B item, C descrição, D unid, E trecho, F área, G preço total
        desc, total = r[1], num(r[5])
        if not desc or not total:
            continue
        mk = re.search(r"km (\d+),(\d+)", norm(desc))
        k = float(f"{mk.group(1)}.{mk.group(2)}") if mk else None
        nome = re.search(r"(?i)sobre (?:o |a )?(?:rio |ribeirao |corrego )?([a-zçãéí ]+?) -", norm(desc))
        valores.append(valor(valor_id=f"ECC-EVTEA-OAE-L{i}", id_empreendimento=103, tipo_valor="inicial_leilao", nivel="obra",
                             tipo_obra="oae", uf="MG", rodovia="BR-365", descricao_fonte=desc, km_inicial=k,
                             nome_chave=nome.group(1).strip() if nome and "sem nome" not in nome.group(1) else None,
                             quantidade=r[4], componente="obra", valor=total, data_base=data_base, fonte_id=fid,
                             localizacao=f"aba OAEs_novas, linha {i}, coluna G",
                             observacao=f"Nova OAE da duplicação ({r[3]}); pode estar contida no valor da duplicação do subtrecho - não somar"))
    wb.close()
    return valores, totais


def ecc_locais(arq: Path) -> pd.DataFrame:
    """Localização de cada dispositivo do EVTEA da Cerrado (RESUMO_OBRAS_MELHORIAS, sem valores)."""
    locs = []
    for aba, tp, col_km, col_sub in (("ROTATÓRIAS ALONGADAS", "rotatoria", 4, 5), ("PASSARELAS", "passarela", 4, 5),
                                      ("MELHORIA DE INTERSEÇÕES", "intersecao", 5, None), ("RETORNO EM NÍVEL", "retorno", 5, None)):
        uf = None
        for i, r in enumerate(ler_xlsb(arq, aba), 1):
            k, ident = num(celula(r, col_km)), num(celula(r, 0))
            if k is None or ident is None:
                continue
            uf = celula(r, 2) or uf
            locs.append(dict(tipo_obra=tp, uf=uf, km=k, subtipo=celula(r, col_sub) if col_sub else None,
                             local=celula(r, 6), linha=i, aba=aba))
    for i, r in enumerate(ler_xlsb(arq, "MELHORIA DE ACESSOS"), 1):  # acessos: só por subtrecho
        if num(celula(r, 0)) is not None and num(celula(r, 6)) is not None:
            locs.append(dict(tipo_obra="acesso", uf=celula(r, 2), km=num(celula(r, 6)), km_final=num(celula(r, 7)),
                             subtipo=celula(r, 5), local=f"subtrecho {celula(r, 1):g}", linha=i, aba="MELHORIA DE ACESSOS"))
    return pd.DataFrame(locs)


def eco050_evtea(arq: Path) -> tuple[list, list]:
    """Estudo do leilão da ECO050 (aba PER): só grupos do PER x ano. Ligado às obras pelo tipo."""
    wb = openpyxl.load_workbook(longo(arq), read_only=True, data_only=True)
    linhas = [list(r) for r in wb["PER"].iter_rows(min_row=1, max_row=270, max_col=5, values_only=True)]
    wb.close()
    fid, db = "eco050_evtea_modelo", "não informada"
    obs_db = "Planilha sem data-base explícita; edital e contrato referenciados a mai/2012"
    grupos = {"4.1.1.1": ("passarela", "Passarelas"), "4.1.1.2": ("marginal", "Vias laterais (marginais)"),
              "4.1.2.3.1": ("acesso", "Acessos"), "4.1.2.3.2": ("intersecao", "Interseções"),
              "4.1.2.4": ("duplicacao,adequacao_pista", "Duplicações"),
              "4.2.2": ("faixa_adicional", "Faixas adicionais (obras condicionadas)")}
    valores, totais, vistos = [], [], set()
    for i, r in enumerate(linhas, 1):
        item, desc, v = str(celula(r, 2) or "").strip(), celula(r, 3), num(celula(r, 4))
        if item in grupos and item not in vistos and v:
            vistos.add(item)
            tipos, nome = grupos[item]
            valores.append(valor(valor_id=f"EMG-EVTEA-L{i}", id_empreendimento=104, tipo_valor="inicial_leilao", nivel="grupo",
                                 tipo_obra=tipos.split(",")[0], rodovia="BR-050", descricao_fonte=f"{item} {desc}",
                                 componente="grupo", valor=v, data_base=db, fonte_id=fid,
                                 localizacao=f"aba PER, linha {i}, coluna E", tipos_do_grupo=tipos, grupo_maior_que_lista=True,
                                 observacao=f"{obs_db}. Grupo do PER da concessão inteira (inclui obras já concluídas antes de 2024)"))
        nd = norm(desc)
        rot = {"4": ("ampliacao", "Obras de ampliação da capacidade e outras melhorias")}.get(item)
        if rot or nd in ("investimentos", "custos operacionais"):
            nat = rot[0] if rot else ("capex" if nd == "investimentos" else "opex")
            totais.append(dict(total_id=f"EMG-EVTEA-{nat.upper()}", id_empreendimento=104, tipo_valor="inicial_leilao",
                               natureza=nat, descricao=(rot[1] if rot else desc) + " (estudo do leilão, 30 anos)", valor=v,
                               data_base=db, periodo="30 anos", fonte_id=fid, localizacao=f"aba PER, linha {i}, coluna E",
                               precisao="média", conferido_por="extração automática", observacao=obs_db))
    return valores, totais


def planilha_base(arq: Path, fid: str, emp: int, sigla: str) -> list:
    """Aba 'Planilha base' do acompanhamento: Capex estimado pela concessionária, por obra, com datas."""
    wb = openpyxl.load_workbook(longo(arq), read_only=True, data_only=True)
    ws = wb["Planilha base"]
    linhas = list(ws.iter_rows(min_row=1, max_row=200, max_col=32, values_only=True))
    wb.close()
    cab = [norm(c) for c in linhas[0]]
    col = lambda rx: next(j for j, c in enumerate(cab) if re.search(rx, c))
    j = dict(ref=col(r"^referencia"), grupo=col(r"^idgrupo"), item=col(r"^item per"), tipo=col(r"^tipo de intervencao"),
             desc=col(r"^descricao$"), br=col(r"^br$"), k0=col(r"^km inicial"), k1=col(r"^km final"), qtd=col(r"^quantidade"),
             ini=col(r"^data\s*inicio"), est=col(r"^data entrega estimada"), real=col(r"^data entrega\s*real"),
             capex=col(r"capex"))
    data = lambda v: v.date().isoformat() if hasattr(v, "date") else (str(v) if v else None)
    out, por_grupo = [], {}
    for i, r in enumerate(linhas[1:], 2):
        v = num(r[j["capex"]])
        if not v:
            continue
        ref = data(r[j["ref"]])
        desc = f"{r[j['tipo']] or ''} - {r[j['desc']] or ''}".strip(" -")
        out.append(valor(valor_id=f"{sigla}-PB2604-L{i}", id_empreendimento=emp, tipo_valor="estimativa_concessionaria",
                         nivel="obra", tipo_obra=tipo_obra(desc), rodovia=rodovia_de(r[j["br"]]) or rodovia_de(desc),
                         descricao_fonte=f"[{r[j['item']]}] {desc}", item_per_fonte=str(r[j["item"]] or "").strip() or None,
                         km_inicial=num(r[j["k0"]]), km_final=num(r[j["k1"]]),
                         quantidade=r[j["qtd"]], componente="obra", valor=v, data_base="não informada", fonte_id=fid,
                         localizacao=f"aba Planilha base, linha {i}, coluna AC",
                         observacao=f"Referência da planilha: {ref}; início {data(r[j['ini']])}, entrega estimada "
                                    f"{data(r[j['est']])}, entrega real {data(r[j['real']])}"))
        por_grupo.setdefault((r[j["grupo"]], v), []).append(out[-1])
    for (g, v), itens in por_grupo.items():  # mesmo idGrupo com o mesmo valor em várias linhas: provável total repetido
        if g is not None and len(itens) > 1:
            for it in itens:
                it["observacao"] += f". Mesmo valor repetido em {len(itens)} linhas do idGrupo {g}: pode ser o total do grupo"
    return out


def manuais() -> list:
    m = pd.read_csv(AQUI / "valores_manuais.csv", sep=";", dtype={"data_base": str, "data_base_precos_iniciais": str})
    m = m.astype(object).where(m.notna(), None)
    return [valor(**r) for r in m.to_dict("records")]


# ----------------------------------------------------------------------------- obras

def carregar_obras() -> pd.DataFrame:
    ob = pd.read_csv(LISTA_OBRAS, sep=";")
    ob = ob[ob["id_empreendimento"].isin([103, 104, 105])].copy()
    k = [kms_da_descricao(d) if pd.isna(a) else (a, b) for d, a, b in zip(ob["descricao"], ob["km_inicial"], ob["km_final"])]
    ob["k0"] = [x[0] for x in k]
    ob["k1"] = [x[1] if x[1] is not None and x[1] == x[1] else None for x in k]
    ob["tipo"] = [tipo_obra(d) or tipo_obra(a) for d, a in zip(ob["descricao"], ob["descricoes_anteriores"].fillna(""))]
    rod = [rodovia_de(r) if isinstance(r, str) else rodovia_de(d) for r, d in zip(ob["rodovia"], ob["descricao"])]
    for i, (emp, r, k0) in enumerate(zip(ob["id_empreendimento"], rod, ob["k0"])):
        if emp == 104:
            rod[i] = "BR-050"
        elif emp == 103 and (r not in ("BR-364", "BR-365")) and k0 is not None and k0 == k0:
            rod[i] = "BR-364" if k0 < 400 else "BR-365"  # Cerrado: BR-364/GO até ~200, BR-365/MG de ~620 em diante
    ob["rod"] = rod
    ob["uf"] = ob["rod"].map({"BR-364": "GO", "BR-365": "MG"})
    ob["texto"] = (ob["descricao"].fillna("") + " " + ob["descricoes_anteriores"].fillna("")).map(norm)
    return ob


def sobreposicao(a0, a1, b0, b1) -> float:
    """Fração do menor intervalo coberta pela interseção (pontos viram intervalos de ± TOL_PONTO/2)."""
    # ponto ou intervalo curto (ex.: OAE 752,320-752,357) vira janela de TOL_PONTO em volta do centro
    if a1 is None or a1 != a1:
        a1 = a0
    if b1 is None or b1 != b1:
        b1 = b0
    if abs(a1 - a0) < TOL_PONTO:
        c = (a0 + a1) / 2
        a0, a1 = c - TOL_PONTO / 2, c + TOL_PONTO / 2
    if abs(b1 - b0) < TOL_PONTO:
        c = (b0 + b1) / 2
        b0, b1 = c - TOL_PONTO / 2, c + TOL_PONTO / 2
    a0, a1, b0, b1 = min(a0, a1), max(a0, a1), min(b0, b1), max(b0, b1)
    inter = min(a1, b1) - max(a0, b0)
    return max(0.0, inter) / max(1e-9, min(a1 - a0, b1 - b0))


def jaccard(a0, a1, b0, b1) -> float:
    """Interseção / união dos intervalos de km (para escolher a obra de km mais parecido)."""
    a1 = a0 if a1 is None or a1 != a1 else a1
    b1 = b0 if b1 is None or b1 != b1 else b1
    a0, a1, b0, b1 = min(a0, a1), max(a0, a1), min(b0, b1), max(b0, b1)
    uniao = max(a1, b1) - min(a0, b0)
    return 1.0 if uniao < 1e-9 else max(0.0, min(a1, b1) - max(a0, b0)) / uniao


def vincular(vals: pd.DataFrame, ob: pd.DataFrame, locs: pd.DataFrame) -> pd.DataFrame:
    lig = []

    def add(v, o, forma, metodo, confianca, n=None, extra=None):
        lig.append(dict(obra_id=o["obra_id"], valor_id=v["valor_id"], forma=forma, metodo=metodo, confianca=confianca,
                        n_obras_no_grupo=n, grupo_maior_que_lista=v["grupo_maior_que_lista"] if forma == "grupo" else None,
                        observacao=extra))

    for _, v in vals.iterrows():
        cand = ob[ob["id_empreendimento"] == v["id_empreendimento"]]
        if v["nivel"] in ("obra", "trecho"):
            achou = []
            if v["nome_chave"]:
                achou = [(o, "nome", "alta") for _, o in cand.iterrows() if v["nome_chave"] in o["texto"]]
            if not achou and v["km_inicial"] is not None and v["km_inicial"] == v["km_inicial"]:
                c = cand[(cand["rod"] == v["rodovia"]) & cand["k0"].notna()]
                if v["tipo_obra"]:
                    c = c[c["tipo"] == v["tipo_obra"]]
                sob = [(sobreposicao(v["km_inicial"], v["km_final"], o["k0"], o["k1"]), o) for _, o in c.iterrows()]
                for s, o in sob:
                    if s >= 0.5 or (v["nivel"] == "trecho" and s > 0):
                        achou.append((o, "tipo + rodovia + km", "alta" if s >= 0.9 else "média"))
                if not achou and v["nivel"] == "obra":  # km do EVTEA (SNV antigo) deslocado: aceita pouca sobreposição
                    achou = [(o, f"tipo + rodovia + km (sobreposição de só {s:.0%})", "baixa") for s, o in sob if s > 0]
                # a fonte informa o item PER: se alguma candidata tem o mesmo item, fica só com ela(s)
                if v["item_per_fonte"] and len(achou) > 1:
                    mesmo = [a for a in achou if str(a[0]["item_per"]) == v["item_per_fonte"]]
                    achou = mesmo or achou
            if v["nivel"] == "obra":
                # várias candidatas: se nunca aparecem no mesmo mês, são versões da mesma obra (renomeada) -> direto;
                # se coexistem, são obras diferentes (ex.: marginal lado leste e oeste)
                coexistem = any(a[0]["primeira_ref"] <= b[0]["ultima_ref"] and b[0]["primeira_ref"] <= a[0]["ultima_ref"]
                                for i, a in enumerate(achou) for b in achou[i + 1:])
                if coexistem and v["item_per_fonte"]:
                    # fonte com 1 linha por obra (Planilha base): fica a de km mais parecido (e suas versões antigas)
                    km_v = (v["km_inicial"], v["km_final"])
                    melhor = max(achou, key=lambda a: jaccard(*km_v, a[0]["k0"], a[0]["k1"]))[0]
                    achou = [a for a in achou if a[0]["obra_id"] == melhor["obra_id"] or not (
                        a[0]["primeira_ref"] <= melhor["ultima_ref"] and melhor["primeira_ref"] <= a[0]["ultima_ref"])]
                    coexistem = False
                for o, met, conf in achou:
                    if coexistem:
                        add(v, o, "grupo", met, conf, n=len(achou),
                            extra="Valor único da fonte para obras que coexistem na lista (ex.: os dois lados da marginal)")
                    else:
                        add(v, o, "direto", met, conf, extra=(f"Valor ligado a {len(achou)} obras da lista que nunca aparecem "
                                                              f"no mesmo mês (versões da mesma obra)") if len(achou) > 1 else None)
            else:
                forma = "direto" if len(achou) == 1 else "grupo"
                for o, met, conf in achou:
                    add(v, o, forma, met, conf, n=len(achou) if forma == "grupo" else None,
                        extra="Trecho do valor coincide com uma única obra da lista" if forma == "direto" else None)
        elif v["nivel"] == "grupo":
            tipos = set((v["tipos_do_grupo"] or "").split(","))
            c = cand[cand["tipo"].isin(tipos)]
            if v["uf"]:
                c = c[c["uf"] == v["uf"]]
            for _, o in c.iterrows():
                add(v, o, "grupo", "tipo da obra (grupo do PER)", "média", n=len(c))
        elif v["nivel"] == "tipo":
            c = cand[cand["tipo"] == v["tipo_obra"]]
            if v["uf"]:
                c = c[c["uf"] == v["uf"]]
            for _, o in c.iterrows():
                sub, met = None, "tipo + UF"
                if v["id_empreendimento"] == 103 and v["subtipo"] and len(locs):
                    l = locs[(locs["tipo_obra"] == v["tipo_obra"]) & (locs["uf"] == v["uf"])]
                    if o["k0"] is None or o["k0"] != o["k0"]:
                        continue
                    if v["tipo_obra"] == "acesso":
                        l = l[(l["km"] <= o["k0"]) & (o["k0"] <= l["km_final"])]
                    else:
                        l = l.assign(d=(l["km"] - o["k0"]).abs())
                        l = l[l["d"] <= TOL_PONTO].sort_values("d").head(1)
                    if l.empty:
                        continue  # sem local no EVTEA: subtipo indefinido, não liga
                    sub = l["subtipo"].iloc[0]
                    if sub != v["subtipo"]:
                        continue
                    met = f"tipo + UF + local no EVTEA ({l['aba'].iloc[0]}, linha {l['linha'].iloc[0]})"
                # baixa: tipo com subtipos (ex.: rotatória 1/2) sem local no EVTEA para confirmar qual
                add(v, o, "unitario_tipo", met, "média" if sub or not v["subtipo"] else "baixa",
                    extra=f"Valor de referência por unidade ({v['quantidade']:g} un. no total do item)" if v["quantidade"] else None)
    # correspondências manuais (casos que a regra não alcança, com a referência que justifica)
    man = pd.read_csv(AQUI / "correspondencias_manuais.csv", sep=";")
    vv = vals.set_index("valor_id")
    for r in man.itertuples():
        lig = [x for x in lig if not (x["valor_id"] == r.valor_id)]
        lig.append(dict(obra_id=r.obra_id, valor_id=r.valor_id, forma="direto", metodo="correspondência manual",
                        confianca="alta", n_obras_no_grupo=None, grupo_maior_que_lista=None,
                        observacao=f"{r.motivo}. Ref.: {r.referencia}"))
        assert r.valor_id in vv.index, r.valor_id
    lig = pd.DataFrame(lig)
    if lig.empty:
        return lig
    # não contar duas vezes: grupo/unitário do mesmo tipo de valor fica marcado se a obra já tem valor direto
    tv = lig["valor_id"].map(vals.set_index("valor_id")["tipo_valor"])
    diretos = set(zip(lig.loc[lig["forma"] == "direto", "obra_id"], tv[lig["forma"] == "direto"]))
    lig["coberto_por_valor_direto"] = [f != "direto" and (o, t) in diretos for o, f, t in zip(lig["obra_id"], lig["forma"], tv)]
    return lig


# ----------------------------------------------------------------------------- resumo

def resumo_por_obra(ob: pd.DataFrame, vals: pd.DataFrame, lig: pd.DataFrame) -> pd.DataFrame:
    j = lig.merge(vals, on="valor_id", suffixes=("", "_valor")) if len(lig) else pd.DataFrame()
    linhas = []
    for _, o in ob.iterrows():
        r = {"id_empreendimento": o["id_empreendimento"], "empreendimento": NOMES[o["id_empreendimento"]],
             "obra_id": o["obra_id"], "item_per": o["item_per"], "descricao": o["descricao"], "tipo_obra": o["tipo"],
             "rodovia": o["rod"], "km_inicial": o["k0"], "km_final": o["k1"],
             "presente_no_ultimo_snapshot": o["presente_no_ultimo_snapshot"]}
        g = j[j["obra_id"] == o["obra_id"]] if len(j) else j
        for t in TIPOS_VALOR:
            h = g[(g["tipo_valor"] == t)] if len(g) else g
            if len(h):
                h = h.assign(ordem=h["forma"].map(ORDEM_FORMA),
                             mesmo_item=(h["item_per_fonte"].astype(str) == str(o["item_per"])).map({True: 0, False: 1}),
                             conf=h["confianca"].map({"alta": 0, "média": 1, "baixa": 2}))
                h = h.sort_values(["ordem", "mesmo_item", "conf", "valor_id"])
                melhor = h[h["forma"] == h["forma"].iloc[0]]
                # da mesma fonte e data-base, soma componentes DIFERENTES (execução + projeto); linhas repetidas do
                # mesmo componente (ex.: valor do grupo repetido em 2 linhas da Planilha base) não somam: vale a 1ª
                b = melhor[(melhor["fonte_id"] == melhor["fonte_id"].iloc[0]) &
                           (melhor["data_base"] == melhor["data_base"].iloc[0])].drop_duplicates("componente")
                r[f"{t}_valor"] = round(b["valor"].sum(), 2)
                mais = (" + obras fora da lista" if b["grupo_maior_que_lista"].iloc[0] is True else "")
                r[f"{t}_forma"] = b["forma"].iloc[0] + (f" (÷ {int(b['n_obras_no_grupo'].iloc[0])} obras da lista{mais})"
                                                        if b["forma"].iloc[0] == "grupo" else "")
                r[f"{t}_valor_ids"] = ", ".join(b["valor_id"])
                r[f"{t}_outros_valores"] = len(h) - len(b)
                r[f"{t}_data_base"] = b["data_base"].iloc[0]
                r[f"{t}_fonte"] = f"{b['fonte_id'].iloc[0]}: {'; '.join(b['localizacao'])}"
        r["n_valores"] = len(g)
        r["n_fontes"] = g["fonte_id"].nunique() if len(g) else 0
        r["fontes"] = ", ".join(sorted(g["fonte_id"].unique())) if len(g) else None
        r["fontes_concorrentes"] = r["n_fontes"] > 1  # mais de uma fonte com valor para a obra (qualquer forma)
        r["sem_valor"] = len(g) == 0
        linhas.append(r)
    return pd.DataFrame(linhas)


def completar_rodovia(vals: pd.DataFrame) -> pd.DataFrame:
    """Rodovia ausente na fonte: ECO050 é toda BR-050; Cerrado separa pelo km (BR-364/GO < 400 < BR-365/MG)."""
    for i, r in vals.iterrows():
        if not r["rodovia"]:
            if r["id_empreendimento"] == 104:
                vals.at[i, "rodovia"] = "BR-050"
            elif r["id_empreendimento"] == 103 and r["km_inicial"] == r["km_inicial"] and r["km_inicial"] is not None:
                vals.at[i, "rodovia"] = "BR-364" if r["km_inicial"] < 400 else "BR-365"
    return vals


def com_documento(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta nome do empreendimento e, a partir do fonte_id (cadastro em fontes.py), o documento e o link."""
    df.insert(2, "empreendimento", df["id_empreendimento"].map(NOMES))
    df["documento"] = df["fonte_id"].map(lambda f: FONTES[f]["documento"])
    df["url"] = df["fonte_id"].map(lambda f: FONTES[f]["url"])
    return df


def main() -> int:
    DADOS.mkdir(parents=True, exist_ok=True)
    print("[fontes]")
    arq = baixar_fontes()
    print("[extração]")
    v_ecc, t_ecc = ecc_evtea(arq["ecc_evtea_fator_d"][0])
    locs = ecc_locais(arq["ecc_evtea_modelagem"][0])
    v_emg, t_emg = eco050_evtea(arq["eco050_evtea_modelo"][0])
    vals = (v_ecc + v_emg + manuais()
            + planilha_base(arq["eco050_planilha_base_2026_04"][0], "eco050_planilha_base_2026_04", 104, "EMG")
            + planilha_base(arq["ecc_planilha_base_2026_04"][0], "ecc_planilha_base_2026_04", 103, "ECC"))
    vals = com_documento(completar_rodovia(pd.DataFrame(vals)))

    ob = carregar_obras()
    lig = vincular(vals, ob, locs)
    n = lig.groupby("valor_id")["obra_id"].nunique() if len(lig) else pd.Series(dtype=int)
    vals["n_obras_ligadas"] = vals["valor_id"].map(n).fillna(0).astype(int)
    vals["fontes_concorrentes"] = False  # alguma obra ligada a este valor também tem valor de outra fonte
    if len(lig):
        d = lig.merge(vals[["valor_id", "fonte_id"]], on="valor_id")
        conc = d.groupby("obra_id")["fonte_id"].nunique()
        obras_conc = set(conc[conc > 1].index)
        vals["fontes_concorrentes"] = vals["valor_id"].isin(d.loc[d["obra_id"].isin(obras_conc), "valor_id"])
        lig = lig.merge(vals[["valor_id", "id_empreendimento", "tipo_valor", "valor", "data_base", "fonte_id", "localizacao"]],
                        on="valor_id")
        lig = lig.merge(ob[["obra_id", "descricao"]], on="obra_id")

    tot = pd.DataFrame(t_ecc + t_emg)
    tm = pd.read_csv(AQUI / "totais_manuais.csv", sep=";", dtype={"data_base": str, "periodo": str})
    tot = pd.concat([tot, tm], ignore_index=True)
    tot = com_documento(tot)
    prev = tot[tot["tipo_valor"] != "realizado"]
    nf = prev.groupby(["id_empreendimento", "natureza"])["fonte_id"].nunique()
    tot["fontes_concorrentes"] = [r.tipo_valor != "realizado" and nf.get((r.id_empreendimento, r.natureza), 0) > 1
                                  for r in tot.itertuples()]

    res = resumo_por_obra(ob, vals, lig)
    cols_v = ["valor_id", "id_empreendimento", "empreendimento", "tipo_valor", "natureza", "nivel", "tipo_obra", "subtipo",
              "uf", "rodovia", "km_inicial", "km_final", "descricao_fonte", "item_per_fonte", "quantidade", "componente", "valor", "data_base",
              "valor_precos_iniciais", "data_base_precos_iniciais", "n_obras_ligadas", "fontes_concorrentes", "fonte_id",
              "documento", "url", "localizacao", "conferido_por", "observacao", "tipos_do_grupo", "grupo_maior_que_lista"]
    vals = vals[cols_v]
    for nome, df in (("valores_encontrados", vals), ("obras_valores", lig), ("resumo_por_obra", res),
                     ("valor_total_empreendimento", tot)):
        df.to_csv(DADOS / f"{nome}.csv", index=False, sep=";", encoding="utf-8-sig")
    with pd.ExcelWriter(DADOS / "valores_obras.xlsx") as xw:
        res.to_excel(xw, sheet_name="resumo_por_obra", index=False)
        lig.to_excel(xw, sheet_name="obras_valores", index=False)
        vals.to_excel(xw, sheet_name="valores_encontrados", index=False)
        tot.to_excel(xw, sheet_name="valor_total_empreendimento", index=False)

    print(f"\n{len(vals)} valores encontrados | {len(lig)} ligações obra x valor | {len(tot)} totais -> {DADOS}")
    for emp, g in res.groupby("id_empreendimento"):
        print(f"  {emp} {NOMES[emp]:32s} obras={len(g):4d}  com valor={int((~g['sem_valor']).sum()):4d}  "
              f"inicial_leilao={g.get('inicial_leilao_valor', pd.Series()).notna().sum():4d}  "
              f"estimativa_conc={g.get('estimativa_concessionaria_valor', pd.Series()).notna().sum():3d}  "
              f"fontes_concorrentes={int(g['fontes_concorrentes'].sum())}")
    sem = vals[vals["n_obras_ligadas"] == 0]
    print(f"  valores sem obra ligada: {len(sem)} (ex.: {', '.join(sem['valor_id'].head(8))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
