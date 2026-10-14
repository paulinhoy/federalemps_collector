"""
Monta o cadastro de obras da Ecovias do Cerrado (id 103, ECC): 1 linha por obra esperada no PER atualizado, ligada ao
acompanhamento da ANTT, com km atual e o valor do item 4 do modelo econômico-financeiro rateado por obra.

Uso (depois de per_obras/extrair_modelo_cerrado.py):
    python per_obras/montar_cadastro_cerrado.py

Insumos versionados (per_obras/):
    per_cerrado_manuais.csv                obras do PER atualizado (gerar_per_cerrado_manuais.py), com a linha do Fator D
    correspondencias_cadastro_cerrado.csv  ligações feitas à mão: linha do cadastro <-> obras do acompanhamento
Insumos gerados (dados/): acompanhamento_obras/consolidado/obras.csv e obras_por_snapshot.csv;
    per_obras/intermediario/modelo_item4_cerrado_grupos.csv; valores_obras/fontes/ecc_evtea_fator_d/fator-d.xlsx
Saída: dados/finais/cadastro_obras/cadastro_obras_cerrado.csv (sep ';', UTF-8 BOM) e .xlsx.
Regras em documentacao/cadastro_obras.md (seção Cerrado); colunas em per_obras/dicionario_colunas.md.

Resumo do método:
 1. Cada linha do PER vira uma ou mais linhas do cadastro: quantidade em unidades (acessos, praças...) vira uma linha
    por unidade; acostamento e faixa adicional viram uma linha por trecho do acompanhamento (+ uma linha de saldo).
    Todas guardam per_id_origem e fracao_da_origem.
 2. As séries do acompanhamento são agrupadas em obras físicas (mesmo tipo, mesmo km, sem coexistir no mesmo mês).
    Ligação: correspondências manuais primeiro; depois automática por tipo + km (dispositivos: km do EVTEA mais perto;
    acessos: trecho homogêneo; acostamento/faixa: trecho homogêneo e ano). Séries de tipos do item 4 que sobram viram
    linhas ECC-EXT-* sem valor.
 3. Valor: grupo = item_modelo x bloco (4.1, 4.2, 4.3, 4.5). peso = custo da obra no estudo (Fator D, jul/2016);
    valor = valor_grupo_bloco x peso / soma_pesos_grupo.
"""
import re
import sys
import unicodedata
from pathlib import Path

import openpyxl
import pandas as pd

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
sys.path.insert(0, str(AQUI))
from caminhos import CONSOLIDADO, DADOS, caminho_final, caminho_modelo  # noqa: E402

ID_EMP = 103
TOTAL_ITEM4 = 717702925.02
FONTE_MODELO = "ecc_leilao_modelo"
FONTE_FD = "ecc_evtea_fator_d"
DB_MODELO = "2016-07"
DB_FD = "2016-07"
ARQ_FD = DADOS / "valores_obras" / "fontes" / FONTE_FD / "fator-d.xlsx"
ANO1 = 2020            # ano de concessão 1 = 2020 (a concessão vira o ano em janeiro; ver documentacao)
ANO_ATUAL = 7          # ano de concessão de abr/2026, último mês do acompanhamento
SAIDA_CSV = caminho_final("cadastro_obras", "cerrado", "csv")

TOL_PONTUAL = 0.6      # km: mesma obra física (dispositivos pontuais)
TOL_ACESSO = 0.1       # km: mesma obra física (acessos, que podem estar a poucos metros uns dos outros)
TOL_LINEAR = 0.35      # km: extremos de obras lineares
TOL_DISP = 6.0         # km: distância máxima entre o km do EVTEA e o do acompanhamento (dispositivos)
SALDO_MIN = 0.1        # km: saldo mínimo para criar linha de saldo (e 5% da extensão)

SIGLA = {"duplicacao": "DUP", "faixa_adicional": "FXA", "via_marginal": "MAR", "acostamento": "ACO",
         "correcao_tracado": "CTR", "melhoria_acesso": "ACE", "intersecao": "INT", "rotatoria": "ROT",
         "passarela": "PAS", "retorno_nivel": "RET", "iluminacao": "ILU", "posto_pesagem": "EDI",
         "fibra_optica": "EDI", "interconexao_trevo": "CMP"}
LINEARES = {"duplicacao", "faixa_adicional", "via_marginal", "acostamento", "correcao_tracado", "iluminacao",
            "fibra_optica"}
POR_SEGMENTO = {"acostamento", "faixa_adicional"}            # linha do PER quebrada nos trechos do acompanhamento
POR_KM_EVTEA = {"rotatoria", "intersecao", "passarela", "correcao_tracado", "retorno_nivel"}
TIPOS_AUTO = POR_SEGMENTO | POR_KM_EVTEA | {"melhoria_acesso", "duplicacao"}
TIPOS_ITEM4 = TIPOS_AUTO | {"via_marginal", "iluminacao", "posto_pesagem", "fibra_optica", "cmp_trevao",
                            "cmp_xapetuba", "oae_nova"}

COLUNAS = ["id_obra", "id_empreendimento", "nome", "tipo_intervencao", "bloco", "item_per", "rodovia", "uf",
           "municipio", "km_inicial", "km_final", "extensao_km", "quantidade", "unidade", "km_per_original",
           "data_inicio_prevista", "data_termino_prevista", "fonte_datas_previstas", "prazo_contratual",
           "data_inicio_real", "data_conclusao_real", "fonte_datas_reais", "situacao", "fonte_situacao", "item_modelo",
           "valor_grupo_bloco", "soma_pesos_grupo", "peso", "valor", "metodo_valor", "data_base", "fonte_id",
           "localizacao_valor", "per_id_origem", "fracao_da_origem", "origem", "fonte_alteracao",
           "obra_id_acompanhamento", "id_sigicor", "a_confirmar", "observacao",
           # colunas próprias da Cerrado
           "subtipo", "trecho_homogeneo", "prazo_per", "ano_prazo", "fonte_km", "valor_estudo_obra",
           "data_base_estudo", "fonte_estudo", "localizacao_estudo"]


def ler(caminho, **kw):
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False, **kw)


def norm(t):
    t = "".join(c for c in unicodedata.normalize("NFD", str(t or "")) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip().lower()


def f(v):
    try:
        x = float(str(v).replace(",", "."))
        return None if x != x else x
    except ValueError:
        return None


def fmt(x):
    return "" if x is None else f"{x:g}".replace(".", ",")


# ---------------------------------------------------------------- séries do acompanhamento
FORA = [(r"\bcamera|cftv|paineis|deteccao e sensoriamento|sensoriamento|controle de velocidade|deteccao de altura$",
         "sistema operacional (3.4.3): item 6 do modelo, fora do item 4"),
        (r"desvio", "obra emergencial não prevista no PER"),
        (r"foto da ausencia", "registro fotográfico, não é obra"),
        (r"^oae|^recuperacao, reforco","recuperação/reforço de OAE (3.1.3): item 2/3 do modelo, fora do item 4")]


def tipo_serie(d, item_per):
    n = norm(d)
    if "pesagem" in n:
        return "posto_pesagem", None
    for rx, motivo in FORA:
        if re.search(rx, n) and not n.startswith("nova oae"):
            return None, motivo
    regras = [("cmp_xapetuba", r"xapetuba"), ("cmp_trevao", r"trevao"), ("oae_nova", r"^nova oae"),
              ("fibra_optica", r"fibra"), ("iluminacao", r"^ilumina"), ("duplicacao", r"duplica"),
              ("faixa_adicional", r"faixas? adiciona"), ("via_marginal", r"margina"),
              ("acostamento", r"acostamento"), ("correcao_tracado", r"correcao de tracado"),
              ("melhoria_acesso", r"acesso"), ("intersecao", r"intersec"), ("rotatoria", r"rotatoria"),
              ("passarela", r"passarela")]
    for t, rx in regras:
        if re.search(rx, n):
            return t, None
    return None, "tipo não reconhecido"


def kms(d):
    n = norm(d)
    ks = [int(a) + int(b) / 1000 for a, b in re.findall(r"(\d{1,3})\s*\+\s*(\d{3})", n)]
    if not ks:
        ks = [float(f"{a}.{b}") for a, b in re.findall(r"(\d{1,3}),(\d{1,3})", n)]
    if not ks:
        ks = [float(a) for a in re.findall(r"km (\d{1,3})\b", n)]
    return (ks[0], ks[1] if len(ks) > 1 else None) if ks else (None, None)


def lado(d):
    n = norm(d)
    return "leste" if "leste" in n else "oeste" if "oeste" in n else None


def carregar_series():
    o = ler(CONSOLIDADO / "obras.csv")
    o = o[o.id_empreendimento == str(ID_EMP)].copy()
    snap = ler(CONSOLIDADO / "obras_por_snapshot.csv", usecols=["obra_id", "mes_referencia", "id_empreendimento"])
    meses = snap[snap.id_empreendimento == str(ID_EMP)].groupby("obra_id").mes_referencia.agg(set).to_dict()
    ss = []
    for r in o.itertuples():
        t, fora = tipo_serie(r.descricao, r.item_per)
        ki, kf = f(r.km_inicial), f(r.km_final)
        if ki is None:
            ki, kf = kms(r.descricao)
        rod = None if ki is None else ("BR-365" if ki >= 600 else "BR-364")
        ss.append(dict(obra_id=r.obra_id, descricao=r.descricao, item_per=r.item_per, tipo=t, fora=fora, ki=ki, kf=kf,
                       lado=lado(r.descricao), rodovia=rod, municipio=r.municipio, ultima=r.ultima_ref,
                       primeira=r.primeira_ref, n=int(r.n_snapshots or 0), pct=f(r.pct_executado_ultimo) or 0.0,
                       situacao=r.situacao_ultima, meses=meses.get(r.obra_id, set())))
    return {s["obra_id"]: s for s in ss}


def dist(a, b):
    """Distância entre duas séries/obras do mesmo tipo (None = incompatível)."""
    if a["ki"] is None or b["ki"] is None:
        return None
    if a["lado"] and b["lado"] and a["lado"] != b["lado"]:
        return None
    if a["tipo"] in LINEARES and a["kf"] is not None and b["kf"] is not None:
        ov = min(a["kf"], b["kf"]) - max(a["ki"], b["ki"])
        curto = min(a["kf"] - a["ki"], b["kf"] - b["ki"])
        d = abs(a["ki"] - b["ki"]) + abs(a["kf"] - b["kf"])
        return d if (curto > 0 and ov >= 0.5 * curto) or d <= 2 * TOL_LINEAR else None
    d = abs(a["ki"] - b["ki"])
    return d if d <= (TOL_ACESSO if a["tipo"] == "melhoria_acesso" else TOL_PONTUAL) else None


def agrupar(series):
    """Agrupa séries em obras físicas. Duas séries que aparecem no mesmo mês são obras diferentes, a não ser que o km
    seja idêntico (o mesmo arquivo às vezes repete a obra em duas seções) e o tipo não seja acesso."""
    grupos = []
    ordem = sorted((s for s in series.values() if s["tipo"]), key=lambda s: (s["ultima"], s["n"]), reverse=True)
    for s in ordem:
        melhor = None
        for g in grupos:
            if g["tipo"] != s["tipo"]:
                continue
            ok = True
            for m in g["membros"]:
                if m["meses"] & s["meses"]:
                    iguais = (m["ki"] == s["ki"] and m["kf"] == s["kf"] and s["tipo"] != "melhoria_acesso")
                    if not iguais:
                        ok = False
                        break
            if not ok:
                continue
            d = dist(g["membros"][0], s)
            if d is not None and (melhor is None or d < melhor[0]):
                melhor = (d, g)
        if melhor:
            melhor[1]["membros"].append(s)
        else:
            grupos.append(dict(tipo=s["tipo"], membros=[s]))
    for g in grupos:
        rep = g["membros"][0]                       # o mais recente
        g.update(id=rep["obra_id"], ki=rep["ki"], kf=rep["kf"], rodovia=rep["rodovia"], lado=rep["lado"],
                 ids=[m["obra_id"] for m in g["membros"]], municipio=rep["municipio"], usado=False)
    return grupos


# ---------------------------------------------------------------- Fator D
def ler_fator_d():
    wb = openpyxl.load_workbook(ARQ_FD, read_only=True, data_only=True)
    ws = wb["Ampliação"]
    fd = {i: r for i, r in enumerate(ws.iter_rows(min_row=1, max_row=140, max_col=10, values_only=True), 1)}
    wb.close()
    return fd


def custo_estudo(p, fd):
    """Custo da linha do PER no Fator D (R$ jul/2016) e a localização."""
    if not p.fd_linha:
        return None, ""
    r = fd[int(p.fd_linha)]
    desc, qtd, unit, tot = r[4], r[7], r[8], r[9]
    if p.fd_modo == "total":
        fr = float(p.fd_fracao or 1)
        return float(tot) * fr, f"Ampliação!J{p.fd_linha} ({desc}) x {fr:.6g}"
    if unit is None:  # sem unitário (postos PRF): total / quantidade
        return float(tot) / float(qtd) * float(p.quantidade), \
            f"Ampliação!J{p.fd_linha}/H{p.fd_linha} ({desc}) x {p.quantidade}"
    return float(unit) * float(p.quantidade), f"Ampliação!I{p.fd_linha} ({desc}, unitário) x {p.quantidade}"


# ================================================================ montagem
def main():
    per = ler(AQUI / "per_cerrado_manuais.csv")
    cor = ler(AQUI / "correspondencias_cadastro_cerrado.csv")
    grupos_mod = ler(caminho_modelo("cerrado", "grupos"))
    fd = ler_fator_d()
    series = carregar_series()
    obras = agrupar(series)
    por_serie = {i: g for g in obras for i in g["ids"]}

    # ---- 1. linhas do PER -> linhas-base do cadastro (unidades separadas)
    base = []
    for p in per.itertuples():
        custo, loc = custo_estudo(p, fd)
        q = f(p.quantidade)
        n = int(q) if p.unidade == "un" and q and q > 1 else 1
        for k in range(n):
            ln = dict(id_obra=p.id_linha + (f"-{k + 1:02d}" if n > 1 else ""), per=p, custo=None if custo is None
                      else custo / n, loc_estudo=loc, fracao=float(p.fracao_linha) / n, quantidade=1 if n > 1 else q,
                      ki=f(p.km_inicial), kf=f(p.km_final), ext=f(p.extensao_km), obras=[], segs=[], a_conf=False,
                      just=[], origem="per_original" if p.documento_fonte == "ecc_per_atualizado" else "evtea_fator_d",
                      fonte_alt="", nome=p.descricao + (f" - unidade {k + 1} de {n}" if n > 1 else ""))
            if p.per_id == "ECC-PER-PAS-07":
                ln["origem"], ln["fonte_alt"] = "per_realocada", "2º TA (Deliberação 353/2024): TH 15 -> 16, prazo 4º ano"
            elif p.prazo_per_original:
                ln["fonte_alt"] = "2º TA (Deliberação 353/2024): prazo da passarela"
            base.append(ln)
    por_id = {ln["id_obra"]: ln for ln in base}

    # ---- 2. correspondências manuais
    for c in cor.itertuples():
        ln = por_id.get(c.id_obra)
        if ln is None:
            sys.exit(f"Correspondência para id inexistente: {c.id_obra}")
        for oid in c.obra_id_acompanhamento.split("|"):
            if oid not in por_serie:
                sys.exit(f"{c.id_obra}: série {oid} não existe ou foi excluída (fora do item 4)")
            g = por_serie[oid]
            if g not in ln["obras"]:
                ln["obras"].append(g)
            g["usado"] = True
            if ln["per"].tipo_intervencao in POR_SEGMENTO:   # vale só para o trecho, não para a linha toda do PER
                g["cor_conf"], g["cor_just"] = c.a_confirmar == "True", c.justificativa
        if ln["per"].tipo_intervencao not in POR_SEGMENTO:
            ln["a_conf"] |= c.a_confirmar == "True"
            ln["just"].append(c.justificativa)

    # ---- 3. ligação automática
    livres = lambda tipo: [g for g in obras if g["tipo"] == tipo and not g["usado"] and g["ki"] is not None]  # noqa: E731
    # 3a. dispositivos com km do EVTEA: par mais próximo primeiro
    for tipo in POR_KM_EVTEA:
        cand = [ln for ln in base if ln["per"].tipo_intervencao == tipo and not ln["obras"] and f(ln["per"].km_evtea)]
        pares = []
        for ln in cand:
            for g in livres(tipo):
                if g["rodovia"] != ln["per"].rodovia:
                    continue
                kg = g["ki"] if g["kf"] is None else (g["ki"] + g["kf"]) / 2
                d = abs(kg - f(ln["per"].km_evtea))
                if d <= TOL_DISP:
                    pares.append((d, ln["id_obra"], g["id"], ln, g))
        for d, _, _, ln, g in sorted(pares, key=lambda x: x[:3]):
            if ln["obras"] or g["usado"]:
                continue
            ln["obras"].append(g)
            g["usado"] = True
            ln["a_conf"] |= d > 3.0
            ln["just"].append(f"automática: {tipo}, km do EVTEA {fmt(f(ln['per'].km_evtea))} x acompanhamento "
                              f"{fmt(g['ki'])} (dif. {d:.2f} km)")
    # 3b. acessos: por trecho homogêneo, em ordem de km
    for p in per[per.tipo_intervencao == "melhoria_acesso"].itertuples():
        a, b = f(p.km_inicial), f(p.km_final)
        unid = [ln for ln in base if ln["per"].id_linha == p.id_linha]
        gs = sorted([g for g in livres("melhoria_acesso") if g["rodovia"] == p.rodovia and a - 0.05 <= g["ki"] <= b + 0.05],
                    key=lambda g: g["ki"])
        for ln, g in zip(unid, gs):
            ln["obras"].append(g)
            g["usado"] = True
            ln["just"].append(f"automática: acesso no TH {p.th} ({fmt(a)}-{fmt(b)}), {len(gs)} no acompanhamento para "
                              f"{len(unid)} no PER; unidades na ordem de km")
    # 3c. acostamentos e faixas: trechos do acompanhamento dentro do TH, preenchendo os anos em ordem
    for tipo in POR_SEGMENTO:
        linhas_t = [ln for ln in base if ln["per"].tipo_intervencao == tipo and ln["per"].secao_per != "3.2.3.2"]
        for ln in linhas_t:   # manuais viram segmentos da própria linha
            if ln["obras"]:
                ln["segs"], ln["obras"] = list(ln["obras"]), []
        for g in sorted(livres(tipo), key=lambda g: g["ki"]):
            if g["kf"] is None:
                continue
            mid = (g["ki"] + g["kf"]) / 2
            th_l = sorted([ln for ln in linhas_t if g["rodovia"] == ln["per"].rodovia
                           and f(ln["per"].km_inicial) - 0.05 <= mid <= f(ln["per"].km_final) + 0.05],
                          key=lambda ln: int(ln["per"].ano_prazo or 99))
            for ln in th_l:
                usado = sum(s["kf"] - s["ki"] for s in ln["segs"])
                if ln["ext"] - usado > SALDO_MIN or ln is th_l[-1]:
                    ln["segs"].append(g)
                    g["usado"] = True
                    break

    # ---- 4. linhas finais (segmentos + saldo) e obras fora do PER
    linhas = []
    for ln in base:
        if not ln["segs"]:
            linhas.append(ln)
            continue
        segs = sorted(ln["segs"], key=lambda g: g["ki"])
        soma = sum(g["kf"] - g["ki"] for g in segs)
        saldo = ln["ext"] - soma
        tem_saldo = saldo > max(SALDO_MIN, 0.05 * ln["ext"])
        den = ln["ext"] if tem_saldo else soma
        if len(segs) == 1 and not tem_saldo:
            ln["obras"] = segs
            ln["a_conf"] |= segs[0].get("cor_conf", False)
            ln["just"] += [segs[0]["cor_just"]] if segs[0].get("cor_just") else []
            ln["just"].append(f"trecho do acompanhamento {fmt(segs[0]['ki'])}-{fmt(segs[0]['kf'])} "
                              f"({soma:.2f} km para {ln['ext']:g} km do PER)")
            linhas.append(ln)
            continue
        partes = [(g, g["kf"] - g["ki"]) for g in segs] + ([(None, saldo)] if tem_saldo else [])
        for k, (g, km_) in enumerate(partes, 1):
            fr = km_ / den
            novo = dict(ln, id_obra=f"{ln['id_obra']}-{'saldo' if g is None else f's{k:02d}'}",
                        custo=ln["custo"] * fr, fracao=ln["fracao"] * fr, ext=round(km_, 3), quantidade=round(km_, 3),
                        obras=[g] if g else [], segs=[], just=list(ln["just"]),
                        a_conf=ln["a_conf"] or bool(g and g.get("cor_conf")))
            if g is not None and g.get("cor_just"):
                novo["just"].append(g["cor_just"])
            if g is None:
                novo["nome"] = f"{ln['nome']} - saldo sem trecho no acompanhamento ({km_:.2f} km)"
                novo["ki"] = novo["kf"] = None
            else:
                novo["nome"] = f"{ln['nome']} - trecho km {fmt(g['ki'])}-{fmt(g['kf'])}"
                novo["just"].append(f"trecho do acompanhamento no TH {ln['per'].th}; {len(segs)} trechos somam "
                                    f"{soma:.2f} km para {ln['ext']:g} km do PER"
                                    + ("" if tem_saldo else " (sem saldo: fração = km do trecho / soma dos trechos)"))
            linhas.append(novo)
    # obras do acompanhamento de tipos do item 4 que sobraram -> ECC-EXT
    n_ext = {}
    for g in sorted(obras, key=lambda g: (g["tipo"], g["rodovia"] or "", g["ki"] or 0)):
        if g["usado"] or g["tipo"] not in TIPOS_ITEM4:
            continue
        sig = SIGLA.get(g["tipo"], "OUT")
        n_ext[sig] = n_ext.get(sig, 0) + 1
        rep = g["membros"][0]
        linhas.append(dict(id_obra=f"ECC-EXT-{sig}-{n_ext[sig]:02d}", per=None, custo=None, loc_estudo="", fracao=None,
                           quantidade=(round(g["kf"] - g["ki"], 3) if g["kf"] else 1), ki=g["ki"], kf=g["kf"],
                           ext=round(g["kf"] - g["ki"], 3) if g["kf"] else None, obras=[g], segs=[], a_conf=True,
                           just=["obra do acompanhamento sem correspondente no PER atualizado"],
                           origem="acompanhamento_extra", fonte_alt=f"acompanhamento ANTT ({', '.join(g['ids'])})",
                           nome=rep["descricao"], tipo_ext=g["tipo"]))
        g["usado"] = True

    # ---- 5. colunas
    grp = {(r.item, r.bloco): (float(r.valor_bloco), r.celula_total, r.anos) for r in grupos_mod.itertuples()}
    out = []
    for ln in linhas:
        p = ln["per"]
        obras_l = ln["obras"]
        ids = [i for g in obras_l for i in g["ids"]]
        principal = max((m for g in obras_l for m in g["membros"]), key=lambda m: (m["ultima"], m["n"]), default=None)
        tipo = p.tipo_intervencao if p is not None else ln["tipo_ext"]
        bloco = p.bloco if p is not None else "extra_per"
        # km atual: acompanhamento (série mais recente) > km do PER > km do EVTEA > vazio (o PER só dá o TH)
        sec = p.secao_per if p is not None else ""
        per_tem_km = p is not None and bool(p.km_inicial) and (
            sec.startswith("3.2.3") or tipo not in {"melhoria_acesso"} | POR_SEGMENTO)
        saldo = str(ln["id_obra"]).endswith("saldo")
        if p is not None and sec == "3.2.1.1":
            ki, kf, fonte_km = ln["ki"], ln["kf"], f"PER atualizado p.{p.pagina} (Tabela 1)"
        elif principal is not None and principal["ki"] is not None and not saldo:
            ki, kf = principal["ki"], principal["kf"]
            fonte_km = f"acompanhamento {principal['obra_id']} ({principal['ultima']})"
        elif per_tem_km and not saldo:
            ki, kf, fonte_km = f(p.km_inicial), f(p.km_final), f"PER atualizado p.{p.pagina}"
        elif p is not None and f(p.km_evtea) and not saldo:
            ki, kf, fonte_km = f(p.km_evtea), None, f"EVTEA ({p.fonte_km_evtea})"
        else:
            ki = kf = None
            fonte_km = (f"sem km: o PER só dá o trecho homogêneo {p.th}" if p is not None and p.th else "sem km")
        if kf is not None and ki is not None and abs(kf - ki) < 1e-9:
            kf = None
        km_per = ""
        if per_tem_km:
            km_per = p.km_inicial + (f"-{p.km_final}" if p.km_final and p.km_final != p.km_inicial else "")
        elif p is not None and p.th and p.km_inicial:
            km_per = f"TH {p.th}: {p.km_inicial}-{p.km_final}"
        # situação
        if principal is not None:
            ex = principal["pct"]
            sit = "concluida" if ex >= 0.99 else "em_andamento" if ex > 0 else "nao_iniciada"
            fonte_sit = f"acompanhamento {principal['ultima']} ({principal['obra_id']})"
        elif bloco == "condicionada":
            sit, fonte_sit = "condicionada_nao_acionada", "regra: obra condicionada (4.2 ou 3.2.3) sem série"
        else:
            sit, fonte_sit = "sem_acompanhamento", "regra: sem série no acompanhamento (abr/2024 a abr/2026)"
        # origem: km do acompanhamento longe do PER/EVTEA
        obs = [] if p is None else [p.observacao_per]
        km_ref = None if p is None else (f(p.km_evtea) or (f(p.km_inicial) if tipo in ("via_marginal", "retorno_nivel",
                                                                                        "correcao_tracado") else None))
        if principal is not None and km_ref is not None and principal["ki"] is not None and ln["origem"] == "per_original":
            if abs(principal["ki"] - km_ref) > 1.0:
                ln["origem"] = "per_realocada"
                ln["fonte_alt"] = (f"acompanhamento {principal['obra_id']}: km {fmt(principal['ki'])} x "
                                   f"{fmt(km_ref)} no PER/EVTEA")
        ano = int(p.ano_prazo) if p is not None and p.ano_prazo else None
        r = dict(id_obra=ln["id_obra"], id_empreendimento=ID_EMP, nome=ln["nome"], tipo_intervencao=tipo, bloco=bloco,
                 item_per=p.secao_per if p is not None else "", rodovia=p.rodovia if p is not None else (ln["obras"][0]["rodovia"] or ""),
                 uf=(p.uf if p is not None else {"BR-364": "GO", "BR-365": "MG"}.get(ln["obras"][0]["rodovia"], "")),
                 municipio=(p.municipio if p is not None and p.municipio else
                            (principal["municipio"] if principal is not None else "")),
                 km_inicial=ki, km_final=kf, extensao_km=ln["ext"] if tipo in LINEARES else None,
                 quantidade=ln["quantidade"], unidade=p.unidade if p is not None else ("km" if ln["kf"] else "un"),
                 km_per_original=km_per, prazo_contratual=str(ANO1 - 1 + ano) if ano else "",
                 situacao=sit, fonte_situacao=fonte_sit, item_modelo=p.item_modelo if p is not None else "",
                 per_id_origem=p.per_id if p is not None else "",
                 fracao_da_origem=round(ln["fracao"], 6) if ln["fracao"] is not None else "",
                 origem=ln["origem"], fonte_alteracao=ln["fonte_alt"], obra_id_acompanhamento="|".join(ids),
                 a_confirmar=ln["a_conf"],
                 observacao="; ".join(x.rstrip(".") for x in obs + ln["just"] if x),
                 subtipo=p.subtipo if p is not None else "", trecho_homogeneo=p.th if p is not None else "",
                 prazo_per=p.prazo_per if p is not None else "", ano_prazo=ano,
                 fonte_km=fonte_km, valor_estudo_obra=ln["custo"], data_base_estudo=DB_FD if ln["custo"] else "",
                 fonte_estudo=FONTE_FD if ln["custo"] else "", localizacao_estudo=ln["loc_estudo"])
        if p is not None and p.prazo_per_original:
            r["observacao"] = "; ".join(x for x in (r["observacao"], f"prazo no PER original: {p.prazo_per_original}") if x)
        out.append(r)
    df = pd.DataFrame(out)

    # ---- 6. valor: rateio do grupo (item_modelo x bloco) pelo custo do estudo
    tem = df.item_modelo != ""
    df["metodo_valor"] = ""
    df["peso"] = pd.to_numeric(df.valor_estudo_obra, errors="coerce")
    sem_custo = tem & df.peso.isna()
    if sem_custo.any():   # peso igual dentro do grupo (não ocorre hoje)
        df.loc[sem_custo, "peso"] = 1.0
    df.loc[tem, "soma_pesos_grupo"] = df[tem].groupby(["item_modelo", "bloco"]).peso.transform("sum")
    df.loc[tem, "valor_grupo_bloco"] = [grp[(i, b)][0] for i, b in zip(df[tem].item_modelo, df[tem].bloco)]
    df.loc[tem, "valor"] = df.valor_grupo_bloco * df.peso / df.soma_pesos_grupo
    df.loc[tem, "metodo_valor"] = ["peso_igual_sem_custo_no_estudo" if s else "rateio_por_custo_estudo"
                                   for s in sem_custo[tem]]
    df.loc[tem, "data_base"] = DB_MODELO
    df.loc[tem, "fonte_id"] = FONTE_MODELO
    df.loc[tem, "localizacao_valor"] = [f"PER!F{grp[(i, b)][1][5:]}:AI{grp[(i, b)][1][5:]} (total {grp[(i, b)][1]}; "
                                        f"anos {grp[(i, b)][2]})" for i, b in zip(df[tem].item_modelo, df[tem].bloco)]
    df.loc[~tem, "peso"] = None
    ordem_bloco = {"complementacao_dnit": 0, "obrigatoria": 1, "condicionada": 2, "edificacoes_operacionais": 3,
                   "iluminacao_recuperacao": 4, "extra_per": 5}
    df["_o"] = df.bloco.map(ordem_bloco)
    df["_k"] = df.km_inicial.astype(float)
    df = df.sort_values(["_o", "item_per", "tipo_intervencao", "id_obra"])
    out = df.reindex(columns=COLUNAS)
    out.to_csv(SAIDA_CSV, sep=";", index=False, encoding="utf-8-sig", decimal=".")
    out.to_excel(SAIDA_CSV.with_suffix(".xlsx"), index=False, sheet_name="cadastro_cerrado")

    # ---- 7. conferências
    TOL = 0.01
    ok = True
    print(f"Cadastro: {len(out)} linhas ({out.per_id_origem.replace('', pd.NA).nunique()} obras do PER) -> {SAIDA_CSV}")
    print("Por situação:", out.situacao.value_counts().to_dict())
    print("Por bloco:", out.bloco.value_counts().to_dict())
    print("Por origem:", out.origem.value_counts().to_dict())
    print("Rateio por grupo (item_modelo x bloco), peso = custo do Fator D (jul/2016):")
    for (it, bl), s in out[out.item_modelo.fillna("") != ""].groupby(["item_modelo", "bloco"]):
        vg = grp[(it, bl)][0]
        bate = abs(s.valor.sum() - vg) < TOL
        ok &= bate
        print(f"  {it} {bl}: {len(s)} linhas, soma custo estudo {s.peso.sum():,.2f}, rateado {s.valor.sum():,.2f} x "
              f"modelo {vg:,.2f} {'ok' if bate else 'DIVERGENTE'} (modelo/estudo = {vg / s.peso.sum():.5f})")
    for (it, bl), (vg, _, _) in grp.items():
        if vg > 0 and (it, bl) not in set(zip(out.item_modelo, out.bloco)):
            ok = False
            print(f"  DIVERGENTE: grupo {it} {bl} = {vg:,.2f} sem obra no cadastro")
    tot = out.valor.sum()
    print(f"Soma rateada {tot:,.2f} x item 4 {TOTAL_ITEM4:,.2f}: {'ok' if abs(tot - TOTAL_ITEM4) < TOL else 'DIVERGENTE'}")
    ok &= abs(tot - TOTAL_ITEM4) < TOL
    print("Métodos de valor:", out.metodo_valor.value_counts().to_dict())
    # Fator D x modelo por seção
    secoes = {"4.1": (14, "1.2 Obras de melhorias"), "4.2": (67, "1.3 Manutenção de nível de serviço"),
              "4.3": (113, "2 Edificações e instalações operacionais"), "4.5": (8, "1.1 Complementação DNIT")}
    print("Fator D (aba Ampliação, coluna J) x modelo (aba PER):")
    for it, (lin, nome) in secoes.items():
        vfd = float(fd[lin][9])
        vm = grp[(it, next(b for (i, b) in grp if i == it))][0]
        soma_cad = out.loc[out.item_modelo == it, "peso"].sum()
        print(f"  {it} x Fator D L{lin} ({nome}): Fator D {vfd:,.2f}; modelo {vm:,.2f}; dif. {vm - vfd:,.2f} "
              f"({vm / vfd - 1:+.3%}); soma dos pesos no cadastro {soma_cad:,.2f} (dif. p/ Fator D {soma_cad - vfd:,.2f})")
    # acompanhamento
    excl = [s for s in series.values() if not s["tipo"]]
    usados = {i for g in obras if g["usado"] for i in g["ids"]}
    nao = [s for s in series.values() if s["tipo"] and s["obra_id"] not in usados]
    print(f"Séries do acompanhamento (id {ID_EMP}): {len(series)}; ligadas a linhas do PER "
          f"{len({i for i in '|'.join(out[out.origem != 'acompanhamento_extra'].obra_id_acompanhamento).split('|') if i})}; "
          f"em linhas ECC-EXT (fora do PER) "
          f"{len({i for i in '|'.join(out[out.origem == 'acompanhamento_extra'].obra_id_acompanhamento).split('|') if i})}; "
          f"fora do item 4 {len(excl)}; sem ligação {len(nao)}")
    motivos = pd.Series([s["fora"] for s in excl]).value_counts()
    for m, n in motivos.items():
        print(f"  fora do item 4 ({n}): {m}: " + ", ".join(s["obra_id"] for s in excl if s["fora"] == m))
    for s in nao:
        print(f"  NÃO LIGADA {s['obra_id']}: {s['descricao']}")
    print(f"Obras físicas (grupos de séries): {len(obras)}; com mais de uma série: "
          f"{sum(len(g['ids']) > 1 for g in obras)}")
    rel = out[out.origem == "per_realocada"]
    print(f"Linhas com km do acompanhamento longe do PER/EVTEA (>1 km) ou alteradas: {len(rel)}")
    for r in rel.itertuples():
        print(f"  {r.id_obra}: {r.fonte_alteracao}")
    print("Acessos: por TH, unidades no PER x ligadas:")
    ac = out[out.tipo_intervencao == "melhoria_acesso"]
    for pid, s in ac.groupby("per_id_origem"):
        print(f"  {pid} (TH {s.trecho_homogeneo.iat[0]}): {len(s)} no PER, {(s.obra_id_acompanhamento != '').sum()} ligadas")
    print("a_confirmar=True:", ", ".join(out[out.a_confirmar == True].id_obra))  # noqa: E712
    # 4.2 por ano: custo do estudo x ano do prazo vs modelo (informativo)
    an = ler(caminho_modelo("cerrado", "anual"))
    an = an[(an["item"] == "4.2")].astype({"valor": float, "ano_concessao": int}).set_index("ano_concessao").valor
    c42 = out[out.item_modelo == "4.2"].groupby("ano_prazo").valor.sum()
    print("4.2 por ano (valor rateado pelo ano do prazo do PER x modelo): " + "; ".join(
        f"ano {int(a)}: {c42.get(a, 0) / 1e6:,.2f} x {an.get(int(a), 0) / 1e6:,.2f} mi" for a in sorted(
            set(c42.index.dropna().astype(int)) | set(an[an > 0].index))))
    if not ok:
        sys.exit("Conferência de valores DIVERGENTE")


if __name__ == "__main__":
    main()
