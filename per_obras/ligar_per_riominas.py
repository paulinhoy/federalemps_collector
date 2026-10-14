"""
Liga as obras do PER Atualizado da Ecovias Rio Minas (id 105, ERM) às obras do acompanhamento (ERM-nnnn).

Só a ligação PER <-> acompanhamento (sem valores financeiros). Regras, colunas e pendências em
per_obras/ligacao_riominas.md.

Entradas:
  per_obras/per_riominas_manuais.csv              (gerar_per_riominas_manuais.py)
  per_obras/correspondencias_cadastro_riominas.csv (ligações manuais, com justificativa)
  dados/acompanhamento_obras/consolidado/obras.csv (consolidar.py; id_empreendimento 105)

Saídas (dados/finais/ligacao_per_acompanhamento/):
  ligacao_per_acompanhamento_riominas.csv e .xlsx   uma linha por par (per_id, obra do acompanhamento), mais as
                                                    obras do PER sem acompanhamento e as do acompanhamento fora do PER
  ligacao_per_acompanhamento_riominas_resumo.csv    uma linha por per_id, com o nº de obras do acompanhamento ligadas

Uso:  python per_obras/ligar_per_riominas.py
"""
import re
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
PER = AQUI / "per_riominas_manuais.csv"
MANUAIS = AQUI / "correspondencias_cadastro_riominas.csv"
OBRAS = PROJETO / "dados" / "acompanhamento_obras" / "consolidado" / "obras.csv"
SAIDA = PROJETO / "dados" / "finais" / "ligacao_per_acompanhamento"
SAIDA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- parâmetros
# A quilometragem do acompanhamento (projeto executivo, "SH" = segmento homogêneo) difere da do PER:
# acomp - per = delta. Valores medidos nas obras que casam sem dúvida (duplicações, faixas adicionais, diamantes).
#   BR-116/RJ  km < 150 (SH 29 a 36)  +2,7   (ex.: duplicação PER 57,000-77,900 x SH 29 59,43-80,53)
#   BR-116/RJ  km >= 150 (SH 49 a 58) +7,02  (ex.: diamante PER 195,500 x SH 56 202,520)
#   BR-116/MG  km < 450               -0,6   (ex.: duplicação PER 413,315-421,627 x SH 2 412,722-421,210)
#   BR-116/MG  km >= 450              -0,78  (ex.: duplicação PER 500,111-520,517 x SH 7 499,33-519,73)
#   BR-493/RJ                         -0,15  (ex.: duplicação PER 5,300-15,600 x SH 38 5,17-15,48)
def delta_acomp_menos_per(rod, uf, km):
    if rod == "BR-116" and uf == "RJ":
        return 2.7 if km < 150 else 7.02
    if rod == "BR-116" and uf == "MG":
        return -0.6 if km < 450 else -0.78
    if rod == "BR-493":
        return -0.15
    return 0.0


TOL_PONTO = 2.0        # km: distância máxima (já corrigida) para ligar obras pontuais
LIMITE_CONFIRMAR = 0.75  # km: acima disso a ligação pontual vai como a_confirmar
TOL_BARREIRA = 1.0

# segmento homogêneo (SH) do acompanhamento -> (rodovia, uf)
def sh_para_rodovia(sh):
    if 1 <= sh <= 7:
        return "BR-116", "MG"
    if 29 <= sh <= 37 or 49 <= sh <= 58:
        return "BR-116", "RJ"
    if 38 <= sh <= 40:
        return "BR-493", "RJ"
    return None


# Acessos e pontos de ônibus: o PER dá só a quantidade por "SEGMENTO n" (sem km). O acompanhamento os traz por SH.
# Casamento conferido pela quantidade (ver ligacao_riominas.md): RJ segmentos com apóstrofo n' = SH 48+n; BR-493 n = SH 37+n;
# BR-116/MG 1 e 2 = SH 1 e 2.
def sh_do_segmento(rod, uf, seg):
    prim = seg.endswith("'")
    n = int(seg.rstrip("'"))
    if rod == "BR-116" and uf == "RJ" and prim:
        return 48 + n
    if rod == "BR-493" and n <= 3:
        return 37 + n
    if rod == "BR-116" and uf == "MG" and n <= 2:
        return n
    return None


LETRA_SIGLA = {"B": "MAR", "C": "DIA", "D": "PIN", "E": "TRB", "F": "TRV", "G": "RTU", "H": "RTX", "I": "ROT", "J": "ROA",
               "K": "ALC", "L": "ACE", "M": "BRU", "N": "CPP", "O": "FAU", "P": "PAS", "Q": "ONI", "R": "CIC", "S": "DIV"}
FAIXAS = {"DUP", "FAD", "MAR", "CIC", "DIV"}   # obras em trecho (liga por sobreposição de km)
PONTOS = {"ESC", "DIA", "PIN", "TRB", "TRV", "RTU", "RTX", "ROT", "ROA", "ALC", "BRU", "CPP", "FAU", "PAS"}  # ligam por posição
SEGMENTOS = {"ACE", "ONI"}


# ---------------------------------------------------------------- leitura do acompanhamento
def numeros(txt):
    txt = re.sub(r"BR-\d+(/[A-Z]{2})?", " ", txt)
    txt = re.sub(r"\([^)]*\)", " ", txt)
    txt = re.sub(r"SH\s*\d+", " ", txt)
    txt = re.sub(r"\b[Aa]té\b|\bao\b", " ao ", txt)
    achados = []
    for m in re.finditer(r"(\d{1,3})\+(\d{3})|(\d{1,3}),(\d+)|(\d{1,3})\.(\d+)|\b(\d{1,3})\b", txt):
        if m.group(1):
            achados.append(float(f"{m.group(1)}.{m.group(2)}"))
        elif m.group(3):
            achados.append(float(f"{m.group(3)}.{m.group(4)}"))
        elif m.group(5):
            achados.append(float(f"{m.group(5)}.{m.group(6)}"))
        else:
            achados.append(float(m.group(7)))
    return achados


def sentido_de(desc):
    d = desc.lower()
    if "cresc./decresc" in d or "crescente e decrescente" in d:
        return "ambos"
    if "decrescente" in d or "cecrescente" in d:
        return "Decrescente"
    if "crescente" in d:
        return "Crescente"
    if "transversal" in d:
        return "transversal"
    return ""


PARTES_PASSARELA = ("serviços preliminares", "obras complementares", "infraestrutura", "mesoestrutura", "superestrutura")


def ler_acompanhamento():
    d = pd.read_csv(OBRAS, sep=";", encoding="utf-8-sig")
    d = d[d["id_empreendimento"] == 105].copy()
    registros = []
    ultima_passarela = None
    for _, r in d.sort_values("obra_id").iterrows():
        desc = str(r["descricao"])
        item = str(r["item_per"])
        low = desc.lower()
        reg = dict(obra_id=r["obra_id"], descricao=desc, item_per=item, presente=bool(r["presente_no_ultimo_snapshot"]),
                   sigla="", tipo_acomp="", rodovia="", uf="", km_i=None, km_f=None, sentido=sentido_de(desc), sh=None,
                   n_resumo=None, obs="", pai=None)
        m = re.search(r"SH\s*(\d+)", desc)
        if m:
            reg["sh"] = int(m.group(1))
        # categoria
        if not item.startswith("3.2"):
            reg["tipo_acomp"] = "servico_operacional"
            reg["obs"] = f"item {item} do PER (frente de serviços operacionais), fora da lista de obras da seção 3.2"
            registros.append(reg)
            continue
        letra = item.split(".")[3] if item.count(".") >= 3 else ""
        if item.startswith("3.2.1"):
            sigla = {"A": "DUP", "B": "FAD", "C": "ESC"}.get(letra, "")
        else:
            sigla = LETRA_SIGLA.get(letra, "")
        if low.startswith(PARTES_PASSARELA):
            reg["tipo_acomp"] = "subetapa_passarela"
            reg["pai"] = ultima_passarela
            registros.append(reg)
            continue
        if re.match(r"(ponte|pontilh|viaduto|alarg)", low):
            reg["tipo_acomp"] = "oae"
            sigla = "OAE"
        elif "limpeza e supress" in low:
            reg["tipo_acomp"] = "servico_preliminar"
            sigla = "PRE"
        reg["sigla"] = sigla
        if not reg["tipo_acomp"]:
            reg["tipo_acomp"] = {"DUP": "duplicacao", "FAD": "faixa_adicional", "ESC": "area_escape", "MAR": "via_marginal",
                                 "DIA": "interconexao_diamante", "PIN": "passagem_inferior", "TRB": "interconexao_trombeta",
                                 "TRV": "interconexao_trevo", "RTU": "retorno_em_desnivel", "RTX": "retorno_em_desnivel",
                                 "ROT": "rotatoria", "ROA": "rotatoria", "ALC": "alca_conexao", "ACE": "melhoria_acesso",
                                 "BRU": "barreira_ruido", "CPP": "caixa_produto_perigoso", "FAU": "passagem_fauna",
                                 "PAS": "passarela", "ONI": "ponto_onibus", "CIC": "ciclovia",
                                 "DIV": "divisor_central"}.get(sigla, "outro")
        # rodovia/uf: SH manda; senão texto; senão colunas; senão km
        rod = uf = ""
        mt = re.search(r"(BR-\d{3})/(RJ|MG)", desc)
        if mt:
            rod, uf = mt.group(1), mt.group(2)
        if reg["sh"] is not None and sh_para_rodovia(reg["sh"]):
            rsh = sh_para_rodovia(reg["sh"])
            if rod and (rod, uf) != rsh:
                reg["obs"] += f"UF/rodovia do texto ({rod}/{uf}) corrigida pelo SH {reg['sh']} ({rsh[0]}/{rsh[1]}). "
            rod, uf = rsh
        if not rod and isinstance(r["rodovia"], str) and r["rodovia"].startswith("BR-"):
            rod = r["rodovia"]
            uf = r["uf"] if isinstance(r["uf"], str) else "RJ"
        nums = numeros(desc) if not (pd.notna(r["km_inicial"]) and "local a definir" in low) else []
        if "local a definir" in low:
            nums = []
        mresumo = re.search(r"\((\d+) (?:acessos|Acessos|pontos)", desc)
        if mresumo:
            reg["n_resumo"] = int(mresumo.group(1))
        if pd.notna(r["km_inicial"]) and not nums:
            nums = [float(r["km_inicial"])] + ([float(r["km_final"])] if pd.notna(r["km_final"]) else [])
        if nums:
            reg["km_i"] = nums[0]
            reg["km_f"] = nums[1] if len(nums) > 1 and (" ao " in re.sub(r"\([^)]*\)", " ", desc) or " ao " in desc.lower()) else None
        if not rod and reg["km_i"] is not None:
            if reg["km_i"] >= 405:
                rod, uf = "BR-116", "MG"
            elif reg["km_i"] >= 150:
                rod, uf = "BR-116", "RJ"
        reg["rodovia"], reg["uf"] = rod, uf
        if sigla == "PAS":
            ultima_passarela = reg["obra_id"]
        registros.append(reg)
    return registros


# ---------------------------------------------------------------- alinhamento de obras pontuais
def alinhar(pers, acs, tol):
    """pers/acs: listas de (indice, km), ordenadas por km. DP monotone: casa 1 a 1 se |d|<=tol, minimizando a soma de |d|;
    cada obra sem par custa tol."""
    n, m = len(pers), len(acs)
    INF = float("inf")
    custo = [[0.0] * (m + 1) for _ in range(n + 1)]
    volta = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            melhor, vv = INF, None
            if i > 0:
                c = custo[i - 1][j] + tol
                if c < melhor:
                    melhor, vv = c, "p"
            if j > 0:
                c = custo[i][j - 1] + tol
                if c < melhor:
                    melhor, vv = c, "a"
            if i > 0 and j > 0:
                d = abs(pers[i - 1][1] - acs[j - 1][1])
                if d <= tol:
                    c = custo[i - 1][j - 1] + d
                    if c < melhor:
                        melhor, vv = c, "x"
            custo[i][j], volta[i][j] = melhor, vv
    pares = []
    i, j = n, m
    while i > 0 or j > 0:
        v = volta[i][j]
        if v == "x":
            pares.append((pers[i - 1][0], acs[j - 1][0]))
            i, j = i - 1, j - 1
        elif v == "p":
            i -= 1
        else:
            j -= 1
    return pares[::-1]


def main():
    per = pd.read_csv(PER, sep=";", encoding="utf-8-sig")
    per["sigla"] = per["per_id"].str.split("-").str[2]
    per = per.set_index("per_id", drop=False)
    acs = ler_acompanhamento()
    ac_por_id = {a["obra_id"]: a for a in acs}

    # tipo de segmento (apóstrofo) das linhas de acessos / pontos: vem da descrição do PER
    def segmento_de(per_id):
        m = re.search(r"segmento homogêneo (\d+'?)", per.loc[per_id, "descricao"])
        return m.group(1) if m else None

    ligacoes = {}   # (per_id, obra_id) -> dict
    nao_ligadas_por_ajuste = {}
    usados_ac = set()

    def ligar(per_id, a, regra, a_conf=False, obs="", dki=None, dkf=None, sobrep=None, delta=None, tipo_lig="km"):
        k = (per_id, a["obra_id"])
        ligacoes[k] = dict(per_id=per_id, obra_id_acompanhamento=a["obra_id"], tipo_ligacao=tipo_lig, regra=regra,
                           delta_km_acomp_menos_per=delta, dif_km_inicial=dki, dif_km_final=dkf,
                           sobreposicao_km=sobrep, a_confirmar=a_conf, observacao=obs.strip())
        usados_ac.add(a["obra_id"])

    # ---- ligações manuais (têm precedência)
    manuais = {}
    if MANUAIS.exists():
        mm = pd.read_csv(MANUAIS, sep=";", encoding="utf-8-sig").fillna("")
        for _, r in mm.iterrows():
            manuais[r["obra_id_acompanhamento"]] = r
    for oid, r in manuais.items():
        a = ac_por_id[oid]
        ligar(r["per_id"], a, "manual", a_conf=str(r["a_confirmar"]).lower() == "true", obs=r["justificativa"],
              tipo_lig="manual")

    # ---- agrupa acompanhamento por (sigla, rodovia, uf)
    grupos_ac = {}
    for a in acs:
        if a["obra_id"] in usados_ac or a["sigla"] in ("", "OAE", "PRE") or a["rodovia"] == "":
            continue
        grupos_ac.setdefault((a["sigla"], a["rodovia"], a["uf"]), []).append(a)

    # ---- (1) obras em trecho: sobreposição de km (já na quilometragem do PER)
    for (sigla, rod, uf), lst in grupos_ac.items():
        if sigla not in FAIXAS:
            continue
        cand = per[(per.sigla == sigla) & (per.rodovia == rod) & (per.uf == uf)]
        for a in lst:
            if a["km_i"] is None or a["km_f"] is None:
                continue
            delta = delta_acomp_menos_per(rod, uf, a["km_i"])
            ai, af = sorted((a["km_i"] - delta, a["km_f"] - delta))
            larg = af - ai
            achados = []
            for pid, p in cand.iterrows():
                if a["sentido"] in ("Crescente", "Decrescente") and p["sentido"] in ("Crescente", "Decrescente") \
                        and a["sentido"] != p["sentido"]:
                    continue
                if a["sentido"] not in ("Crescente", "Decrescente", "ambos", "") and p["sentido"] in ("Crescente", "Decrescente"):
                    continue
                pi, pf = sorted((p["km_inicial"], p["km_final"]))
                ov = min(af, pf) - max(ai, pi)
                if ov > 0 and (ov >= 0.1 * larg or ov >= 0.5 * (pf - pi)):
                    achados.append((pid, ov, pi, pf))
            if not achados:
                continue
            # sentido do acompanhamento ausente (duplicação) ou "ambos": liga a todos os trechos sobrepostos
            for pid, ov, pi, pf in achados:
                frac = ov / larg if larg else 1
                dki, dkf = round(ai - pi, 3), round(af - pf, 3)
                a_conf, obs = False, ""
                if len(achados) > 1:
                    a_conf, obs = True, f"obra do acompanhamento cobre {len(achados)} trechos do PER (ver outras linhas); "
                elif max(abs(dki), abs(dkf)) > LIMITE_CONFIRMAR:
                    a_conf, obs = True, f"extremidades diferem {dki:+.2f}/{dkf:+.2f} km do trecho do PER; "
                if len(achados) == 1 and (ov / (pf - pi)) < 0.3:
                    obs += f"a obra do acompanhamento cobre só {ov / (pf - pi):.0%} do trecho do PER; "
                ligar(pid, a, "km_trecho", a_conf, obs, dki=dki, dkf=dkf, sobrep=round(ov, 3), delta=delta)

    # ---- (1b) trecho do PER que já tem acompanhamento bem ajustado: descarta ajuste ruim (extremidades > limite)
    por_per = {}
    for (pid, oid), l in ligacoes.items():
        if l["regra"] == "km_trecho":
            por_per.setdefault(pid, []).append((oid, l))
    for pid, lst in por_per.items():
        bons = [x for x in lst if max(abs(x[1]["dif_km_inicial"]), abs(x[1]["dif_km_final"])) <= LIMITE_CONFIRMAR]
        for oid, l in lst:
            ruim = max(abs(l["dif_km_inicial"]), abs(l["dif_km_final"])) > LIMITE_CONFIRMAR
            if ruim and bons:
                # só descarta se a obra do acompanhamento não liga a nenhum outro trecho
                outros = [k for k in ligacoes if k[1] == oid and k[0] != pid]
                if not outros:
                    del ligacoes[(pid, oid)]
                    usados_ac.discard(oid)
                    nao_ligadas_por_ajuste[oid] = pid

    # ---- (2) obras pontuais: alinhamento por posição
    for (sigla, rod, uf), lst in grupos_ac.items():
        if sigla not in PONTOS:
            continue
        cand = per[(per.sigla == sigla) & (per.rodovia == rod) & (per.uf == uf)]
        pers = sorted((pid, p["km_inicial"]) for pid, p in cand.iterrows())
        pers.sort(key=lambda t: t[1])
        aclist = []
        for a in lst:
            if a["km_i"] is None:
                continue
            delta = delta_acomp_menos_per(rod, uf, a["km_i"])
            aclist.append((a["obra_id"], a["km_i"] - delta, delta))
        aclist.sort(key=lambda t: t[1])
        tol = TOL_BARREIRA if sigla == "BRU" else TOL_PONTO
        pares = alinhar(pers, [(o, k) for o, k, _ in aclist], tol)
        dd = {o: (k, dl) for o, k, dl in aclist}
        for pid, oid in pares:
            a = ac_por_id[oid]
            kper = per.loc[pid, "km_inicial"]
            kac, dl = dd[oid]
            dif = round(kac - kper, 3)
            conf = abs(dif) > LIMITE_CONFIRMAR
            ligar(pid, a, "km_ponto", conf, f"diferença de {dif:+.2f} km após a correção; " if conf else "", dki=dif, delta=dl)

    # ---- (3) acessos e pontos de ônibus: por segmento homogêneo, conferido pela quantidade
    for sigla in SEGMENTOS:
        for pid, p in per[per.sigla == sigla].iterrows():
            seg = segmento_de(pid)
            sh = sh_do_segmento(p["rodovia"], p["uf"], seg) if seg else None
            if sh is None:
                continue
            lst = [a for a in acs if a["sigla"] == sigla and a["sh"] == sh and sh_para_rodovia(sh) == (p["rodovia"], p["uf"])
                   and a["obra_id"] not in usados_ac]
            if not lst:
                continue
            resumos = [a["n_resumo"] for a in lst if a["n_resumo"]]
            indiv = [a for a in lst if not a["n_resumo"]]
            qtd = int(p["quantidade"])
            ok = (resumos and qtd == resumos[0]) or (not resumos and len(indiv) == qtd)
            for a in lst:
                ligar(pid, a, "segmento_sh", not ok,
                      f"SH {sh}: {'resumo do segmento' if a['n_resumo'] else 'unidade individual'}; "
                      + ("" if ok else f"quantidade do PER ({qtd}) difere do acompanhamento (resumo {resumos}, individuais {len(indiv)}); "))

    # ---- (4) subetapas de passarela herdam a ligação da passarela anterior
    for a in acs:
        if a["tipo_acomp"] == "subetapa_passarela" and a["pai"]:
            for (pid, oid), l in list(ligacoes.items()):
                if oid == a["pai"]:
                    ligar(pid, a, "subetapa_da_passarela", l["a_confirmar"],
                          f"etapa da passarela {oid} ({a['descricao']}); " + l["observacao"], delta=l["delta_km_acomp_menos_per"])

    # ---- montagem das linhas
    linhas = []
    for (pid, oid), l in ligacoes.items():
        p, a = per.loc[pid], ac_por_id[oid]
        linhas.append({**_cols_per(p), **_cols_ac(a), **l, "per_id_relacionado": ""})
    # PER sem acompanhamento
    ligados = {pid for pid, _ in ligacoes}
    for pid, p in per.iterrows():
        if pid not in ligados:
            linhas.append({**_cols_per(p), **_cols_ac(None), "per_id": pid, "tipo_ligacao": "sem_acompanhamento", "regra": "",
                           "a_confirmar": False, "observacao": "", "per_id_relacionado": ""})
    # acompanhamento fora do PER
    for a in acs:
        if a["obra_id"] in usados_ac:
            continue
        rel, obs = "", a["obs"]
        if a["tipo_acomp"] == "oae" and a["km_i"] is not None:
            delta = delta_acomp_menos_per(a["rodovia"], a["uf"], a["km_i"])
            k = a["km_i"] - delta
            c = per[(per.rodovia == a["rodovia"]) & (per.uf == a["uf"]) & per.sigla.isin(["DUP", "FAD"])]
            c = c[(c.km_inicial - 0.3 <= k) & (c.km_final + 0.3 >= k)]
            if a["sentido"] in ("Crescente", "Decrescente"):
                c2 = c[c.sentido == a["sentido"]]
                c = c2 if len(c2) else c
            rel = ";".join(c.index)
            obs += ("OAE (ponte/viaduto) que o PER não lista à parte; fica dentro do trecho de " + rel if rel
                    else "OAE (ponte/viaduto) que o PER não lista à parte; fora dos trechos de duplicação/faixa adicional do PER")
        elif a["tipo_acomp"] == "servico_preliminar":
            obs += "serviço de limpeza e supressão vegetal das faixas/marginais; o PER não o lista à parte"
        elif a["tipo_acomp"] == "subetapa_passarela":
            obs += "etapa de passarela sem passarela do PER ligada"
        elif a["obra_id"] in nao_ligadas_por_ajuste:
            obs += (f"sobrepõe o trecho {nao_ligadas_por_ajuste[a['obra_id']]} do PER, mas as extremidades não casam "
                    "e esse trecho já tem outra obra do acompanhamento bem ajustada: trecho extra, fora do PER")
        elif a["sigla"] and a["tipo_acomp"] not in ("servico_operacional",):
            obs += "sem obra do PER do mesmo tipo/rodovia na posição correspondente"
        linhas.append({**_cols_per(None), **_cols_ac(a), "per_id": "", "tipo_ligacao": "fora_do_per", "regra": "",
                       "a_confirmar": False, "observacao": obs.strip(), "per_id_relacionado": rel,
                       "tipo_intervencao": a["tipo_acomp"], "rodovia": a["rodovia"], "uf": a["uf"]})

    df = pd.DataFrame(linhas)
    cols = ["per_id", "tipo_ligacao", "regra", "a_confirmar", "observacao", "tipo_intervencao", "rodovia", "uf",
            "per_km_inicial", "per_km_final", "per_quantidade", "per_unidade", "per_sentido", "per_ano_concessao",
            "per_pagina", "obra_id_acompanhamento", "acomp_descricao", "acomp_item_per", "acomp_tipo", "acomp_km_inicial",
            "acomp_km_final", "acomp_sentido", "acomp_sh", "presente_ultimo_snapshot", "delta_km_acomp_menos_per",
            "dif_km_inicial", "dif_km_final", "sobreposicao_km", "per_id_relacionado"]
    for c in cols:
        if c not in df:
            df[c] = None
    df = df[cols]
    ordem = {"km": 0, "manual": 0, "sem_acompanhamento": 1, "fora_do_per": 2}
    df["_o"] = df["tipo_ligacao"].map(ordem)
    df = df.sort_values(["_o", "per_id", "obra_id_acompanhamento"], na_position="last").drop(columns="_o")
    df.to_csv(SAIDA / "ligacao_per_acompanhamento_riominas.csv", sep=";", index=False, encoding="utf-8-sig")

    # ---- resumo por per_id
    lig = df[df["tipo_ligacao"].isin(["km", "manual"])]
    agg = lig.groupby("per_id").agg(
        n_obras_acompanhamento=("obra_id_acompanhamento", "nunique"),
        n_no_ultimo_snapshot=("presente_ultimo_snapshot", lambda s: int((s == True).sum())),
        obras_acompanhamento=("obra_id_acompanhamento", lambda s: ",".join(sorted(set(s)))),
        a_confirmar=("a_confirmar", "any"), regras=("regra", lambda s: ",".join(sorted(set(s)))))
    res = per[["per_id", "tipo_intervencao", "rodovia", "uf", "km_inicial", "km_final", "quantidade", "unidade", "sentido",
               "ano_concessao", "pagina"]].reset_index(drop=True).join(agg, on="per_id")
    res["n_obras_acompanhamento"] = res["n_obras_acompanhamento"].fillna(0).astype(int)
    res["status"] = res.apply(lambda r: "sem_acompanhamento" if r["n_obras_acompanhamento"] == 0
                              else ("a_confirmar" if r["a_confirmar"] is True else "ligado"), axis=1)
    res["a_confirmar"] = res["a_confirmar"].fillna(False)
    res.to_csv(SAIDA / "ligacao_per_acompanhamento_riominas_resumo.csv", sep=";", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(SAIDA / "ligacao_per_acompanhamento_riominas.xlsx") as xw:
        df.to_excel(xw, sheet_name="ligacao", index=False)
        res.to_excel(xw, sheet_name="resumo_por_per_id", index=False)

    relatorio(df, res, per)


def _cols_per(p):
    if p is None:
        return dict(tipo_intervencao="", rodovia="", uf="", per_km_inicial=None, per_km_final=None, per_quantidade=None,
                    per_unidade="", per_sentido="", per_ano_concessao="", per_pagina=None)
    return dict(per_id=p["per_id"], tipo_intervencao=p["tipo_intervencao"], rodovia=p["rodovia"], uf=p["uf"],
                per_km_inicial=p["km_inicial"], per_km_final=p["km_final"], per_quantidade=p["quantidade"],
                per_unidade=p["unidade"], per_sentido=p["sentido"] if isinstance(p["sentido"], str) else "",
                per_ano_concessao=p["ano_concessao"], per_pagina=p["pagina"])


def _cols_ac(a):
    if a is None:
        return dict(obra_id_acompanhamento="", acomp_descricao="", acomp_item_per="", acomp_tipo="", acomp_km_inicial=None,
                    acomp_km_final=None, acomp_sentido="", acomp_sh=None, presente_ultimo_snapshot=None)
    return dict(obra_id_acompanhamento=a["obra_id"], acomp_descricao=a["descricao"], acomp_item_per=a["item_per"],
                acomp_tipo=a["tipo_acomp"], acomp_km_inicial=a["km_i"], acomp_km_final=a["km_f"],
                acomp_sentido=a["sentido"], acomp_sh=a["sh"], presente_ultimo_snapshot=a["presente"])


def relatorio(df, res, per):
    print(f"PER: {len(per)} obras ({per.quantidade.where(per.unidade=='un').sum():.0f} un + km)")
    print("\nStatus por tipo (obras do PER):")
    print(pd.crosstab(res["tipo_intervencao"], res["status"], margins=True).to_string())
    print("\nPares ligados:", int(df.tipo_ligacao.isin(['km', 'manual']).sum()), "| por regra:",
          df[df.tipo_ligacao.isin(['km', 'manual'])].regra.value_counts().to_dict())
    print("Obras do acompanhamento ligadas:", df[df.tipo_ligacao.isin(['km', 'manual'])].obra_id_acompanhamento.nunique())
    fora = df[df.tipo_ligacao == "fora_do_per"]
    print("\nFora do PER (obras do acompanhamento):", len(fora))
    print(fora.tipo_intervencao.value_counts().to_string())
    print("\na_confirmar:", int(df[df.tipo_ligacao.isin(['km', 'manual'])].a_confirmar.sum()), "pares;",
          int((res.status == 'a_confirmar').sum()), "per_id")
    tot = len(pd.read_csv(OBRAS, sep=";", encoding="utf-8-sig").query("id_empreendimento == 105"))
    cont = df[df.tipo_ligacao.isin(['km', 'manual', 'fora_do_per'])].obra_id_acompanhamento.nunique()
    print(f"\nConferência: {tot} obras ERM no acompanhamento; {cont} aparecem na ligação",
          "OK" if tot == cont else "FALTAM!")
    if tot != cont:
        sys.exit(1)


if __name__ == "__main__":
    main()
