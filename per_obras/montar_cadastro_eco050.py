"""
Monta o cadastro de obras da ECO050 (id 104, EMG): 1 linha por obra esperada na concessão, na versão mais atual
(km corrigido), com o valor do item 4 do modelo econômico-financeiro rateado por obra.

Uso (depois de per_obras/extrair_modelo_eco050.py):
    python per_obras/montar_cadastro_eco050.py

Insumos versionados (per_obras/):
    per_eco050_manuais.csv               obras do PER original (per_id, km, página)
    alteracoes_eco050.csv                km atual e data de conclusão já compilados (por obra_per_ref)
    correspondencias_cadastro_eco050.csv ligações feitas à mão: linha do cadastro <-> PER / alteracoes / acompanhamento
    obras_extra_per_eco050.csv           obras fora do PER que estão no acompanhamento
    marcos_liberacao_eco050.csv          liberação ao tráfego (Relatório mensal 12/2025)
    cronograma_planejamento_anual_2026_eco050.csv  datas previstas/executadas e ID SIGICOR (PA2026 Rev02)
Insumos gerados (dados/): acompanhamento_obras/consolidado/obras.csv; per_obras/modelo_item4_eco050_*.csv

Saída: dados/per_obras/cadastro_obras_eco050.csv (sep ';', UTF-8 BOM) e .xlsx. Regras em documentacao/cadastro_obras.md.
"""
import re
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
DADOS = PROJETO / "dados"
SAIDA = DADOS / "per_obras"
ID_EMP = 104
TOTAL_ITEM4 = 1145919554.57
FONTE_MODELO = "eco050_evtea_modelo"
TOL_KM = 0.05

# ---- regras fixas
TIPO_PER = {"interconexao_trevo_completo": "interconexao_trevo", "retorno_em_desnivel": "retorno_desnivel",
            "retorno_operacional": "outro"}
ITEM_MODELO = {"passarela": "4.1.1.1", "via_marginal": "4.1.1.2", "melhoria_acesso": "4.1.2.3.1",
               "interconexao_diamante": "4.1.2.3.2", "interconexao_trevo": "4.1.2.3.2",
               "interconexao_trombeta": "4.1.2.3.2", "retorno_desnivel": "4.1.2.3.2", "outro": "4.1.2.3.2",
               "duplicacao": "4.1.2.4.2", "faixa_adicional": "4.2.2"}
TIPOS_KM = {"via_marginal", "duplicacao", "faixa_adicional"}  # peso = km
PRAZO_PER = "2019-01-07"  # meta final de duplicação (ano 4); PER 3.2.1: melhorias concomitantes
FONTE_PRAZO = ("PER p.32: metas de pista dupla 35,0/87,4/161,7/218,5 km acumulados até 07/01/2016, 2017, 2018 e 2019 "
               "(assunção 08/01/2014 + 12 meses por ano); Planilha base abr/2026 col. W = 07/01/2019")
FONTE_PA = "PA2026 Rev02 L{}"

COLUNAS = ["id_obra", "id_empreendimento", "nome", "tipo_intervencao", "bloco", "item_per", "rodovia", "uf",
           "municipio", "km_inicial", "km_final", "extensao_km", "quantidade", "unidade", "km_per_original",
           "data_inicio_prevista", "data_termino_prevista", "fonte_datas_previstas", "prazo_contratual",
           "data_inicio_real", "data_conclusao_real", "fonte_datas_reais", "situacao", "fonte_situacao", "item_modelo",
           "valor_grupo_bloco", "soma_pesos_grupo", "peso", "valor", "metodo_valor", "data_base", "fonte_id",
           "localizacao_valor", "per_id_origem", "fracao_da_origem", "origem", "fonte_alteracao",
           "obra_id_acompanhamento", "id_sigicor", "a_confirmar", "observacao"]


def ler(caminho, **kw):
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False, **kw)


def km(v):
    """'98,5' / '98.5' / '247+300' -> float; vazio -> None."""
    v = str(v).strip()
    if not v or v in ("-", "nan"):
        return None
    m = re.fullmatch(r"(\d+)\+(\d{1,3})", v)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 1000
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def km_pa(v):
    """Coluna de km do PA2026: 'km PER (km atual)' -> (antigo, atual)."""
    v = str(v).replace("\n", " ")
    nums = re.findall(r"\d+\+\d{3}|\d+(?:[.,]\d+)?", v)
    if not nums:
        return None, None
    vals = [km(n) for n in nums]
    if "(" in v:
        return vals[0], vals[-1]
    return vals[0], vals[0]


def fmt_km(x):
    return "" if x is None else f"{x:g}".replace(".", ",")


def data_iso(v):
    v = str(v).strip()
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", v)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.match(r"(\d{4})\b", v)
    return m.group(1) if m else ""


def data_pa(v):
    v = str(v).strip()
    if not v or v.startswith("<="):
        return ""
    return v.replace("-(mes n/d)", "")


def tipo_texto(t):
    t = t.lower()
    if "passarela" in t:
        return "passarela"
    if "marginal" in t:
        return "via_marginal"
    if "diamante" in t:
        return "interconexao_diamante"
    if "trombeta" in t:
        return "interconexao_trombeta"
    if "trevo completo" in t:
        return "interconexao_trevo"
    if "retorno em desnível" in t:
        return "retorno_desnivel"
    if "retorno em nível" in t or "retorno operacional" in t:
        return "retorno_nivel"
    if "acesso" in t:
        return "melhoria_acesso"
    if t.startswith("duplicação"):
        return "duplicacao"
    return None


def sentido(t):
    m = re.search(r"(?:sentido|pista)\s+(norte|sul)|-\s*(norte|sul)\b", t.lower())
    return (m.group(1) or m.group(2)) if m else None


def uf_de(t):
    m = re.search(r"\b(GO|MG)\b", str(t))
    return m.group(1) if m else None


def main():
    per = ler(AQUI / "per_eco050_manuais.csv")
    alt = ler(AQUI / "alteracoes_eco050.csv")
    alt = alt[alt.obra_per_ref != ""].drop_duplicates("obra_per_ref").set_index("obra_per_ref", drop=False)
    cor = ler(AQUI / "correspondencias_cadastro_eco050.csv")
    ext = ler(AQUI / "obras_extra_per_eco050.csv")
    marcos = ler(AQUI / "marcos_liberacao_eco050.csv")
    pa = ler(AQUI / "cronograma_planejamento_anual_2026_eco050.csv")
    arq_grupos = SAIDA / "modelo_item4_eco050_grupos.csv"
    if not arq_grupos.exists():
        sys.exit("Rode antes: python per_obras/extrair_modelo_eco050.py")
    grupos = ler(arq_grupos)
    anual = ler(SAIDA / "modelo_item4_eco050_anual.csv")
    acomp = ler(DADOS / "acompanhamento_obras" / "consolidado" / "obras.csv")
    acomp = acomp[acomp.id_empreendimento == str(ID_EMP)].set_index("obra_id", drop=False)

    cor_por_id = {r.id_obra: r for r in cor.itertuples()}
    excluidas = [r for r in cor.itertuples() if r.justificativa.startswith("EXCLUIDA")]
    ids_excluidos = {r.per_id_origem for r in excluidas}

    # município por segmento PNV (para a duplicação, que no PER não traz município)
    mun_pnv = (per[per.municipio != ""].groupby("pnv").municipio.agg(lambda s: s.mode().iat[0]).to_dict())

    linhas = []

    def nova(p, id_obra, ki, kf, ext_km, fracao="", nome=None):
        tipo = TIPO_PER.get(p.tipo_intervencao, p.tipo_intervencao)
        km_orig = "-".join(x for x in (p.km_inicial, p.km_final) if x) if p.km_inicial != p.km_final else p.km_inicial
        return dict(id_obra=id_obra, id_empreendimento=ID_EMP, nome=nome or p.descricao, tipo_intervencao=tipo,
                    bloco=p.bloco, item_per=p.secao_per, rodovia=p.rodovia, uf=p.uf,
                    municipio=p.municipio or mun_pnv.get(p.pnv, ""), km_inicial=ki,
                    km_final=kf, extensao_km=ext_km, quantidade=None, unidade=p.unidade, km_per_original=km_orig,
                    per_id_origem=p.per_id, fracao_da_origem=fracao, origem="per_original", fonte_alteracao="",
                    obra_id_acompanhamento="", id_sigicor="", a_confirmar=False, observacao=p.observacao_per,
                    _sentido=sentido(p.sentido) if p.sentido and " e " not in p.sentido else None,
                    _ref="", _desc_atual="")

    # ---- 1. duplicação: segmentos PNV do PER, quebrados nos trechos de duplicação do acompanhamento
    cortes = set()
    for o in acomp.itertuples():
        if tipo_texto(o.descricao) == "duplicacao":
            cortes.update(x for x in (km(o.km_inicial), km(o.km_final)) if x is not None)
    for p in per[per.tipo_intervencao == "duplicacao"].itertuples():
        a, b = km(p.km_inicial), km(p.km_final)
        pts = sorted({a, b} | {c for c in cortes if a + TOL_KM < c < b - TOL_KM})
        partes = list(zip(pts[:-1], pts[1:]))
        for i, (x, y) in enumerate(partes):
            suf = f"-{chr(97 + i)}" if len(partes) > 1 else ""
            ext_km = round(y - x, 3)
            ln = nova(p, p.per_id + suf, x, y, ext_km, round(ext_km / float(p.extensao_km), 6),
                      nome=f"Duplicação km {fmt_km(x)}-{fmt_km(y)} (segmento {p.pnv})")
            ln["observacao"] = ("Obs.2 do PER: ponte da divisa GO/MG, incluindo duplicação, a cargo da Concessionária"
                                if "Obs.2" in p.observacao_per else "")
            linhas.append(ln)

    # ---- 2. demais obras do PER
    for p in per[per.tipo_intervencao != "duplicacao"].itertuples():
        if p.per_id in ids_excluidos:
            continue
        filhos = [r for r in cor.itertuples() if r.per_id_origem == p.per_id and r.id_obra != p.per_id]
        ids = [(r.id_obra, r.fracao_da_origem) for r in filhos] or [(p.per_id, "")]
        for id_obra, fr in ids:
            ln = nova(p, id_obra, km(p.km_inicial), km(p.km_final), km(p.extensao_km),
                      float(fr) if fr else "")
            linhas.append(ln)

    # ---- 3. obras fora do PER (só as do acompanhamento)
    for e in ext.itertuples():
        linhas.append(dict(id_obra=e.id_obra, id_empreendimento=ID_EMP, nome=e.nome,
                           tipo_intervencao=e.tipo_intervencao, bloco=e.bloco, item_per=e.item_per,
                           rodovia=e.rodovia, uf=e.uf, municipio=e.municipio, km_inicial=km(e.km_inicial),
                           km_final=km(e.km_final), extensao_km=None, quantidade=e.quantidade, unidade=e.unidade,
                           km_per_original="", per_id_origem="", fracao_da_origem="", origem=e.origem,
                           fonte_alteracao=f"{e.fonte} ({e.localizacao})", obra_id_acompanhamento="",
                           id_sigicor="", a_confirmar=e.a_confirmar == "True", observacao=e.observacao,
                           _sentido=None, _ref="", _desc_atual=""))

    # ---- 4. correspondências manuais (km atual, UF/município, acompanhamento, alteracoes)
    por_id = {ln["id_obra"]: ln for ln in linhas}
    for r in cor.itertuples():
        if r.justificativa.startswith("EXCLUIDA"):
            continue
        ln = por_id.get(r.id_obra)
        if ln is None:
            print(f"AVISO: correspondência para id inexistente no cadastro: {r.id_obra}")
            continue
        a = alt.loc[r.ref_alteracoes] if r.ref_alteracoes in alt.index else None
        if r.ref_alteracoes and a is None:
            print(f"AVISO: ref_alteracoes não encontrada: {r.ref_alteracoes}")
        ln["_ref"] = r.ref_alteracoes
        if a is not None and ln["tipo_intervencao"] != "duplicacao" and ln["bloco"] != "extra_per":
            ki, kf = km(a.km_inicial_atual), km(a.km_final_atual)
            if r.km_inicial:
                ki, kf = km(r.km_inicial), km(r.km_final) if r.km_final else km(r.km_inicial)
            mudou_km = ki is not None and (abs(ki - (ln["km_inicial"] or -1)) > 1e-9
                                           or abs((kf or ki) - (ln["km_final"] or ln["km_inicial"] or -1)) > 1e-9)
            if ki is not None:
                ln["km_inicial"], ln["km_final"] = ki, kf
                if ln["tipo_intervencao"] in TIPOS_KM and mudou_km and kf is not None:
                    ln["extensao_km"] = round(kf - ki, 3)
            if a.tipo_alteracao == "reconfiguracao" or (a.tipo_alteracao == "realocacao_km" and mudou_km):
                ln["origem"] = "per_realocada"
                ln["fonte_alteracao"] = a.localizacao
            ln["_desc_atual"] = a.descricao_atual
            s = sentido(a.descricao_atual) or sentido(a.obra_per_ref)
            if s:
                ln["_sentido"] = s
        elif a is not None and ln["tipo_intervencao"] == "duplicacao":
            ln["origem"] = "per_realocada" if a.tipo_alteracao == "reconfiguracao" else ln["origem"]
            ln["fonte_alteracao"] = a.localizacao
        if r.uf:
            ln["uf"] = r.uf
        if r.municipio:
            ln["municipio"] = r.municipio
        ln["obra_id_acompanhamento"] = r.obra_id_acompanhamento
        ln["a_confirmar"] = ln["a_confirmar"] or r.a_confirmar == "True"
        if ln["a_confirmar"] or ln["origem"] == "per_realocada":
            ln["observacao"] = "; ".join(x.rstrip(".") for x in (r.justificativa, ln["observacao"]) if x)

    # ---- 5. datas
    pa["c_tipo"] = pa.desc.map(tipo_texto)
    pa["c_uf"] = pa.rod.map(uf_de)
    pa["ant_i"], pa["atu_i"] = zip(*pa.kmi.map(km_pa))
    pa["ant_f"], pa["atu_f"] = zip(*pa.kmf.map(km_pa))
    mdup = marcos[marcos.descricao.str.startswith("Duplicação") & marcos.rodovia.str.endswith("GO")].copy()
    mpon = marcos.copy()
    mpon["c_tipo"], mpon["c_uf"], mpon["ki"] = mpon.descricao.map(tipo_texto), mpon.rodovia.map(uf_de), mpon.km_inicial.map(km)
    mdup["ki"], mdup["kf"] = mdup.km_inicial.map(km), mdup.km_final.map(km)
    sem_pa = []
    for ln in linhas:
        ki, kf = ln["km_inicial"], ln["km_final"]
        if ln["item_per"].startswith("3.2.1") and ln["bloco"] == "obrigatoria":
            ln["prazo_contratual"] = PRAZO_PER
            ln["_fonte_prazo"] = FONTE_PRAZO
        # PA2026
        if ki is not None:
            cand = pa[(pa.c_tipo == ln["tipo_intervencao"]) & (pa.c_uf == ln["uf"])]
            kpo = km(ln["km_per_original"].split("-")[0]) if ln["km_per_original"] else None
            achou = None
            for r in cand.itertuples():
                if ln["tipo_intervencao"] == "duplicacao":
                    if r.atu_i is not None and r.atu_f is not None and r.atu_i - 0.01 <= ki and kf <= r.atu_f + 0.01:
                        achou = r
                elif ln["tipo_intervencao"] == "via_marginal":
                    if r.atu_i is None or r.atu_f is None or kf is None:
                        continue
                    ov = min(kf, r.atu_f) - max(ki, r.atu_i)
                    s_pa = sentido(r.desc)
                    if ov >= 0.8 * min(kf - ki, r.atu_f - r.atu_i) and (not ln["_sentido"] or not s_pa
                                                                         or s_pa == ln["_sentido"]):
                        achou = r
                elif (r.atu_i is not None and abs(r.atu_i - ki) <= TOL_KM) or (
                        kpo is not None and r.ant_i is not None and abs(r.ant_i - kpo) <= TOL_KM
                        and abs(r.atu_i - ki) <= 2.5):
                    achou = r
                if achou is not None:
                    break
            if achou is not None:
                ln["data_inicio_prevista"] = data_pa(achou.prev_ini)
                ln["data_termino_prevista"] = data_pa(achou.prev_fim)
                ln["fonte_datas_previstas"] = FONTE_PA.format(achou.row)
                ln["data_inicio_real"] = data_pa(achou.exec_ini)
                ln["id_sigicor"] = achou.sigicor if achou.sigicor not in ("-", "") else ""
                ln["_pa_exec"] = float(achou.exec_cum_final or 0)
                ln["_pa_row"] = achou.row
            elif ln["bloco"] in ("obrigatoria", "extra_per"):
                sem_pa.append(ln["id_obra"])
        # conclusão real: alteracoes (compilado do Relatório 12/2025) ou cobertura pelos marcos de duplicação
        a = alt.loc[ln["_ref"]] if ln["_ref"] in alt.index else None
        fontes_reais = []
        if ln["tipo_intervencao"] == "duplicacao" and ki is not None:
            cobre = mdup[(mdup.kf > ki) & (mdup.ki < kf)]
            pts = sorted(cobre[["ki", "kf"]].itertuples(index=False))
            ate = ki
            for i_, f_ in pts:
                if i_ <= ate + 0.05:
                    ate = max(ate, f_)
            if len(cobre) and ate >= kf - 0.05:
                datas = cobre.liberada_ao_trafego.map(data_iso)
                ln["data_conclusao_real"] = max(datas)
                fontes_reais.append("Relatório mensal 12/2025 p." + ",".join(sorted(set(cobre.pagina_pdf)))
                                    + " (marcos de liberação: " + "; ".join(
                                        f"{r.km_inicial}-{r.km_final} em {r.liberada_ao_trafego}"
                                        for r in cobre.itertuples()) + ")")
        if (not ln.get("data_conclusao_real") and ki is not None and ln["tipo_intervencao"] not in TIPOS_KM
                and not (a is not None and a.data_conclusao_real)):
            m = mpon[(mpon.c_tipo == ln["tipo_intervencao"]) & (mpon.c_uf == ln["uf"]) & ((mpon.ki - ki).abs() <= TOL_KM)
                     & (mpon.liberada_ao_trafego != "")]
            if len(m):
                ln["data_conclusao_real"] = data_iso(m.liberada_ao_trafego.iat[0])
                fontes_reais.append(f"Relatório mensal 12/2025 p.{m.pagina_pdf.iat[0]} (marco de liberação: "
                                    f"{m.descricao.iat[0]} km {m.km_inicial.iat[0]})")
        if not ln.get("data_conclusao_real") and a is not None and a.data_conclusao_real:
            ln["data_conclusao_real"] = data_iso(a.data_conclusao_real)
            fontes_reais.append(f"alteracoes_eco050.csv: {a.data_conclusao_real} ({a.localizacao})")
        if ln.get("data_inicio_real"):
            fontes_reais.insert(0, f"início: {FONTE_PA.format(ln['_pa_row'])}")
        ln["fonte_datas_reais"] = "; ".join(fontes_reais)

    for ln in linhas:  # obra pontual: km_final vazio
        if ln["tipo_intervencao"] not in TIPOS_KM and ln["km_final"] == ln["km_inicial"]:
            ln["km_final"] = None

    # ---- 6. situação
    for ln in linhas:
        obras = [acomp.loc[o] for o in ln["obra_id_acompanhamento"].split("|") if o in acomp.index]
        pct = max([float(o.pct_executado_ultimo or 0) for o in obras], default=0)
        if ln["bloco"] == "condicionada":
            s = "condicionada_nao_acionada"
        elif ln.get("data_conclusao_real"):
            s = "concluida"
        elif ln["bloco"] == "manutencao_nivel_servico":
            s = "sem_local_definido"
        elif any(o.situacao_ultima.upper().startswith("CONCLU") for o in obras) or ln.get("_pa_exec", 0) >= 1:
            s = "concluida"
        elif pct > 0 or ln.get("_pa_exec", 0) > 0:
            s = "em_andamento"
        elif "a definir" in ln["_desc_atual"].lower():
            s = "sem_local_definido"
        else:
            s = "nao_iniciada"
        ln["fonte_situacao"] = "PA2026/marcos"
        if obras and ln["bloco"] != "condicionada":
            # com série no acompanhamento, a situação vem do último mês da série principal
            # (mesmo critério do financeiro: duplicação própria; senão a de dados mais recentes)
            cand = obras
            if ln["tipo_intervencao"] == "duplicacao":
                d = [o for o in obras if o.descricao.lower().startswith("duplica")]
                cand = d if len(d) == 1 else obras
            pr = sorted(cand, key=lambda o: (o.ultima_ref, int(o.n_snapshots or 0)), reverse=True)[0]
            ex = float(pr.pct_executado_ultimo or 0)
            s = "concluida" if ex >= 0.99 else "em_andamento" if ex > 0 else "nao_iniciada"
            ln["fonte_situacao"] = f"acompanhamento {pr.ultima_ref}"
        ln["situacao"] = s

    # ---- 7. valor: rateio do grupo (item_modelo x bloco) do modelo
    g = grupos.copy()
    g["valor_bloco"] = g.valor_bloco.astype(float)
    val_grupo = g.groupby(["item", "bloco"]).valor_bloco.sum().to_dict()
    for ln in linhas:
        ln["item_modelo"] = ITEM_MODELO.get(ln["tipo_intervencao"], "") if ln["origem"].startswith("per_") else ""
        if ln["item_modelo"]:
            ln["peso"] = ln["extensao_km"] if ln["tipo_intervencao"] in TIPOS_KM else 1.0
            ln["quantidade"] = ln["extensao_km"] if ln["unidade"] == "km" else 1
        elif ln["quantidade"] is None:
            ln["quantidade"] = ln["extensao_km"] if ln["unidade"] == "km" else 1
    df = pd.DataFrame(linhas)
    df["peso"] = pd.to_numeric(df.get("peso"), errors="coerce")
    tem = df.item_modelo != ""
    df.loc[tem, "soma_pesos_grupo"] = df[tem].groupby(["item_modelo", "bloco"]).peso.transform("sum")
    df.loc[tem, "valor_grupo_bloco"] = [val_grupo.get((i, b), 0.0) for i, b in zip(df[tem].item_modelo, df[tem].bloco)]
    df.loc[tem, "valor"] = df.valor_grupo_bloco * df.peso / df.soma_pesos_grupo
    df.loc[tem, "metodo_valor"] = ["rateio_por_km" if t in TIPOS_KM else "rateio_igual_por_unidade"
                                   for t in df[tem].tipo_intervencao]
    df.loc[tem, "data_base"] = "não informada (contrato: mai/2012)"
    df.loc[tem, "fonte_id"] = FONTE_MODELO
    cel = {}
    for (it, bl), s in anual[anual.nivel == "folha"].groupby(["item", "bloco"]):
        anos = s.ano_concessao.astype(int)
        cel[(it, bl)] = (f"{s.celula.iat[0]} a {s.celula.iat[-1].split('!')[-1]} "
                         f"(linha {s.linha_planilha.iat[0]}, anos {anos.min()}-{anos.max()})")
    df.loc[tem, "localizacao_valor"] = [cel.get((i, b), "") for i, b in zip(df[tem].item_modelo, df[tem].bloco)]
    df["observacao"] = [o if not fp else "; ".join(x for x in (o, f"prazo contratual: {fp}") if x)
                        for o, fp in zip(df.observacao, df.get("_fonte_prazo", pd.Series([None] * len(df))).fillna(""))]

    ordem_bloco = {"obrigatoria": 0, "manutencao_nivel_servico": 1, "condicionada": 2, "extra_per": 3}
    df["_o"] = df.bloco.map(ordem_bloco)
    df = df.sort_values(["_o", "item_per", "tipo_intervencao", "km_inicial", "id_obra"], na_position="last")
    out = df.reindex(columns=COLUNAS)

    SAIDA.mkdir(parents=True, exist_ok=True)
    out.to_csv(SAIDA / "cadastro_obras_eco050.csv", sep=";", index=False, encoding="utf-8-sig", decimal=".")
    out.to_excel(SAIDA / "cadastro_obras_eco050.xlsx", index=False, sheet_name="cadastro_eco050")

    # ---- 8. conferências
    print(f"Cadastro: {len(out)} linhas -> {SAIDA / 'cadastro_obras_eco050.csv'}")
    print("Por tipo:", out.tipo_intervencao.value_counts().to_dict())
    print("Por situação:", out.situacao.value_counts().to_dict())
    print("Por bloco:", out.bloco.value_counts().to_dict())
    TOL = 0.01
    ok = True
    print("Rateio por grupo (item_modelo x bloco):")
    for (it, bl), s in out[out.item_modelo.fillna("") != ""].groupby(["item_modelo", "bloco"]):
        vg = val_grupo.get((it, bl), 0.0)
        bate = abs(s.valor.sum() - vg) < TOL
        ok &= bate
        print(f"  {it} {bl}: {len(s)} obras, peso {s.peso.sum():g}, rateado {s.valor.sum():,.2f} x grupo {vg:,.2f} "
              f"{'ok' if bate else 'DIVERGENTE'}")
    usados = set(zip(out.item_modelo, out.bloco))
    for (it, bl), vg in val_grupo.items():
        if vg > 0 and it != "4.3" and (it, bl) not in usados:
            ok = False
            print(f"  DIVERGENTE: grupo {it} {bl} = {vg:,.2f} sem obra no cadastro")
    v43 = sum(v for (it, _), v in val_grupo.items() if it == "4.3")
    tot = out.valor.sum() + v43
    print(f"Soma rateada {out.valor.sum():,.2f} + 4.3 projetos {v43:,.2f} = {tot:,.2f} x item 4 {TOTAL_ITEM4:,.2f}: "
          f"{'ok' if abs(tot - TOTAL_ITEM4) < TOL else 'DIVERGENTE'}")
    dup = out[out.tipo_intervencao == "duplicacao"].extensao_km.sum()
    print(f"Extensão da duplicação: {dup:.3f} km (esperado 218,5): {'ok' if abs(dup - 218.5) < 0.001 else 'DIVERGENTE'}")
    print("Linhas do PER fora do cadastro (excluídas): " + "; ".join(f"{r.per_id_origem} ({r.justificativa})"
                                                                   for r in excluidas))
    ligadas = set("|".join(out.obra_id_acompanhamento.fillna("")).split("|")) - {""}
    nao = [o for o in acomp.obra_id if o not in ligadas]
    print(f"Obras do acompanhamento (id {ID_EMP}): {len(acomp)}; ligadas {len(acomp) - len(nao)}; não ligadas {len(nao)}")
    for o in nao:
        r = acomp.loc[o]
        print(f"  NÃO LIGADA {o}: {r.descricao} km {r.km_inicial} (motivo: sem correspondência cadastrada)")
    for o in sorted(ligadas - set(acomp.obra_id)):
        print(f"  AVISO: {o} citado no cadastro mas ausente do acompanhamento")
    if sem_pa:
        print(f"Sem linha no PA2026 (datas previstas vazias): {', '.join(sem_pa)}")
    print("a_confirmar=True:", ", ".join(out[out.a_confirmar == True].id_obra))  # noqa: E712
    if not ok:
        sys.exit("Conferência de valores DIVERGENTE")


if __name__ == "__main__":
    main()
