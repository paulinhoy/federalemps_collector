"""
Acompanhamento financeiro de uma concessão: cruza o cadastro de obras (valor do item 4 rateado, ou outro valor da obra)
com o % físico do acompanhamento mensal da ANTT. Usado por acompanhamento_financeiro_<conc>.py, que só define a
configuração (Config).

Saídas (dados/finais/<tabela>/, caminhos em per_obras/caminhos.py; CSV ';' UTF-8 BOM):
    financeiro_mensal/fin_mensal_<conc>.csv, financeiro_acumulado/fin_acumulado_<conc>.csv,
    financeiro_resumo/fin_resumo_<conc>.csv e xlsx/fin_<conc>.xlsx (uma aba por tabela).
Regras em documentacao/cadastro_obras.md; colunas em per_obras/dicionario_colunas.md.

Os valores NÃO são corrigidos por índice: ficam nominais, com data-base e tipo. Nunca se somam tipos diferentes.
"""
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from caminhos import CONSOLIDADO, DADOS, caminho_final, caminho_modelo  # noqa: E402

EPS = 1e-9
TERMINO_MIN = 0.99          # executado acumulado que marca o término (parâmetro)
TOL_R = 0.01                # tolerância das conferências em R$
TIPO_SEM = {"concluida": "concluida_antes_serie", "sem_local_definido": "sem_local_a_alocar",
            "condicionada_nao_acionada": "condicionada_nao_acionada", "nao_iniciada": "nao_iniciada_sem_serie",
            "sem_acompanhamento": "sem_serie_sem_informacao"}


@dataclass
class Config:
    conc: str                       # nome nos arquivos (eco050, cerrado, riominas)
    conc_fonte: str                 # coluna `concessao` do acompanhamento
    id_emp: int
    total_item4: float
    tipo_item4: str
    db_item4: str
    passo0_ids: tuple
    nao_rateado: Callable[[pd.DataFrame], float]   # recebe modelo_item4_<conc>_grupos -> valor do item 4 não rateado
    coluna_nao_rateado: str         # nome da coluna em fin_resumo
    rotulo_nao_rateado: str         # texto do relatório
    valor_extra: Optional[Callable] = None        # (obra_id, obras_valores) -> (valor, tipo, db, fonte, loc) ou None
    avisar_sem_valor: bool = True
    data_base_da_linha: bool = False  # usa a coluna data_base do cadastro em vez de db_item4
    extra: dict = field(default_factory=dict)


def ler(caminho, **kw):
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig", low_memory=False, **kw)


def mes_anterior(m):
    a, n = map(int, m.split("-"))
    return f"{a - 1}-12" if n == 1 else f"{a}-{n - 1:02d}"


def gerar(cfg: Config):
    def gravar(df, tabela):
        df.to_csv(caminho_final(tabela, cfg.conc, "csv"), sep=";", index=False, encoding="utf-8-sig")

    # ---------------------------------------------------------------- insumos
    cad = ler(caminho_final("cadastro_obras", cfg.conc, "csv"))
    obs = ler(CONSOLIDADO / "obras_por_snapshot.csv")
    obs = obs[(obs.id_empreendimento == cfg.id_emp) & (obs.concessao == cfg.conc_fonte)].copy()
    ser = ler(CONSOLIDADO / "serie_mensal.csv")
    ser = ser[ser.concessao == cfg.conc_fonte].copy()
    val = ler(DADOS / "valores_obras" / "obras_valores.csv")
    val = val[val.id_empreendimento == cfg.id_emp]
    grp = ler(caminho_modelo(cfg.conc, "grupos"))
    NAO_RATEADO = cfg.nao_rateado(grp)

    obs["principal"] = obs["principal"].astype(str).str.lower().eq("true")
    if obs.groupby(["obra_id", "mes_referencia"]).size().max() > 1:
        obs = obs[obs.principal]
    assert obs.groupby(["obra_id", "mes_referencia"]).size().max() == 1, "obra x mês duplicado"
    MESES = sorted(obs.mes_referencia.unique())
    SNAP_DO_MES = obs.drop_duplicates("mes_referencia").set_index("mes_referencia")["snapshot"].to_dict()
    por_obra = {k: g.sort_values("mes_referencia").reset_index(drop=True) for k, g in obs.groupby("obra_id")}

    # ---------------------------------------------------------------- Passo 0: o % é da obra inteira?
    def passo0(ids):
        """Confere, em obras que atravessam a virada do ano (dez -> jan), se o executado acumulado é contínuo
        e se os incrementos mensais reproduzem o acumulado (obra inteira, sem rebase)."""
        print("\n=== Passo 0: % executado é da obra inteira? (virada dez -> jan) ===")
        for oid in ids:
            g = por_obra[oid].set_index("mes_referencia")
            ac, mes = g.pct_executado_acum_ate_ref, g.pct_executado_no_mes_ref
            linhas = []
            for m in g.index:
                if m.endswith("-01") and mes_anterior(m) in g.index:
                    d = ac[m] - ac[mes_anterior(m)]
                    linhas.append(f"{mes_anterior(m)}->{m}: acum {ac[mes_anterior(m)]:.4f}->{ac[m]:.4f} "
                                  f"(delta {d:+.4f}; no_mes da fonte {mes[m]:.4f})" if pd.notna(mes[m]) else
                                  f"{mes_anterior(m)}->{m}: acum {ac[mes_anterior(m)]:.4f}->{ac[m]:.4f} (no_mes vazio na fonte)")
            ult = g.snapshot.iloc[-1]
            e = ser[(ser.obra_id == oid) & (ser.snapshot == ult) & (ser.tipo == "executado")].pct.sum()
            ant = g.pct_executado_anos_anteriores.iloc[-1]
            print(f"{oid}: " + " | ".join(linhas))
            print(f"    soma dos incrementos mensais no último arquivo ({ult}) = {e:.4f} + anos anteriores {ant:.4f} "
                  f"= {e + ant:.4f}; acumulado do último mês = {ac.iloc[-1]:.4f}")
        dif_jan, dif_out = [], []
        for oid, g in por_obra.items():
            g = g.set_index("mes_referencia")
            for m in g.index:
                p = mes_anterior(m)
                if p in g.index and pd.notna(g.pct_executado_no_mes_ref[m]):
                    d = abs((g.pct_executado_acum_ate_ref[m] - g.pct_executado_acum_ate_ref[p]) - g.pct_executado_no_mes_ref[m])
                    (dif_jan if m.endswith("-01") else dif_out).append(d)
        for nome, lst in (("virada (jan)", dif_jan), ("demais meses", dif_out)):
            s = pd.Series(lst)
            print(f"  |delta acumulado - no_mes| em {nome}: {len(s)} transições, mediana {s.median():.4f}, "
                  f"{(s > 0.005).sum()} acima de 0,5 p.p.")
        print("  Conclusão: o executado acumulado segue contínuo na virada (não zera nem rebaseia); os desvios são "
              "revisões retroativas da fonte, não rebase.")

    # ---------------------------------------------------------------- escolha da série principal
    def descricao(oid):
        return str(por_obra[oid].descricao.iloc[0])

    def escolher_principal(row, cands):
        if len(cands) == 1:
            return cands[0], "unica"
        if row.tipo_intervencao == "duplicacao":
            d = [c for c in cands if descricao(c).lower().startswith("duplica")]
            if len(d) == 1:
                return d[0], "duplicacao_propria_obra"
        ordem = sorted(cands, key=lambda c: (-int(por_obra[c].mes_referencia.iloc[-1].replace("-", "")),
                                             -len(por_obra[c]), c))
        return ordem[0], "dados_mais_recentes"

    # ---------------------------------------------------------------- previsto do último arquivo
    def prev_acum_ultimo_arquivo(oid):
        g = por_obra[oid]
        snap = g.snapshot.iloc[-1]
        ant = g.pct_executado_anos_anteriores.iloc[-1]
        ant = 0.0 if pd.isna(ant) else float(ant)
        p = ser[(ser.obra_id == oid) & (ser.snapshot == snap) & (ser.tipo == "previsto")].groupby("mes").pct.sum()
        p = p.sort_index().fillna(0).cumsum() + ant
        return {m: (round(float(p[p.index <= m].iloc[-1]), 6) if (p.index <= m).any() else None) for m in MESES}

    # ---------------------------------------------------------------- datas reais
    def datas_reais(g, conclusao_cadastro):
        g = g.sort_values("mes_referencia")
        ex = g.set_index("mes_referencia").pct_executado_acum_ate_ref
        pos = ex[ex > EPS]
        antes = bool(len(ex) and ex.iloc[0] > EPS)
        if antes:
            ini, m_ini = "", "nao_observado_antes_da_serie"
        elif len(pos):
            ini = pos.index[0]
            m_ini = "serie_1o_mes_exec_positivo" + ("_apos_lacuna" if mes_anterior(ini) not in MESES and ini != MESES[0] else "")
        else:
            ini, m_ini = "", "nao_iniciada_na_serie"
        if pd.notna(conclusao_cadastro) and str(conclusao_cadastro):
            fim, m_fim = str(conclusao_cadastro), "cadastro_data_conclusao_real"
        else:
            ok = ex[ex >= TERMINO_MIN - EPS]
            fim, m_fim = (ok.index[0], f"serie_1o_mes_exec_ge_{TERMINO_MIN:.2f}") if len(ok) else ("", "nao_concluida_na_serie")
        return ini, fim, m_ini, m_fim, antes

    def db_linha(r):
        if cfg.data_base_da_linha and pd.notna(r.data_base) and str(r.data_base):
            return str(r.data_base)
        return cfg.db_item4

    # ================================================================ montagem
    cad = cad.reset_index(drop=True)
    linhas_mensal, linhas_acum, usadas, ligadas = [], [], set(), set()
    principal_de = {}
    for _, r in cad.iterrows():
        cands = [c.strip() for c in str(r.obra_id_acompanhamento).split("|") if c.strip() and c.strip() != "nan"]
        ligadas.update(cands)
        faltam = [c for c in cands if c not in por_obra]
        if faltam:
            print(f"AVISO: {r.id_obra} liga {faltam}, que não está no acompanhamento {cfg.id_emp}")
        cands = [c for c in cands if c in por_obra]
        if not cands:
            continue
        principal_de[r.id_obra] = (escolher_principal(r, cands), cands)

    passo0(cfg.passo0_ids)

    for _, r in cad.iterrows():
        if r.id_obra not in principal_de:
            continue
        (oid, motivo), cands = principal_de[r.id_obra]
        usadas.add(oid)
        g = por_obra[oid]
        if pd.notna(r.valor):
            vnom, tipo, db, fonte, loc = float(r.valor), cfg.tipo_item4, db_linha(r), r.fonte_id, r.localizacao_valor
        else:
            x = cfg.valor_extra(oid, val) if cfg.valor_extra else None
            if x is None:
                if cfg.avisar_sem_valor:
                    print(f"AVISO: {r.id_obra} ({oid}) sem valor em obras_valores.csv")
                vnom, tipo, db, fonte, loc = None, "", "", "", ""
            else:
                vnom, tipo, db, fonte, loc = x
        ini, fim, m_ini, m_fim, antes = datas_reais(g, r.data_conclusao_real)
        pult = prev_acum_ultimo_arquivo(oid)
        pe_ant = None
        for _, s in g.iterrows():
            m = s.mes_referencia
            f = lambda c: None if pd.isna(s[c]) else float(s[c])  # noqa: E731
            pp, pe, pm, em = f("pct_previsto_acum_ate_ref"), f("pct_executado_acum_ate_ref"), \
                f("pct_previsto_no_mes_ref"), f("pct_executado_no_mes_ref")
            mul = lambda p: None if (vnom is None or p is None) else vnom * p  # noqa: E731
            linhas_mensal.append({
                "id_obra": r.id_obra, "obra_id_acompanhamento": oid, "serie_principal": True,
                "mes_ref": m, "snapshot": s.snapshot,
                "pct_previsto_acum": pp, "pct_executado_acum": pe, "pct_previsto_mes": pm, "pct_executado_mes": em,
                "pct_previsto_acum_ultimo_arquivo": pult[m],
                "valor_nominal": vnom, "tipo_valor": tipo, "data_base": db,
                "valor_previsto_mes": mul(pm), "valor_executado_mes": mul(em),
                "valor_previsto_acum": mul(pp), "valor_executado_acum": mul(pe),
                "situacao_fonte": s.situacao,
                "revisao_negativa": bool(pe is not None and pe_ant is not None and pe < pe_ant - 1e-9),
                "data_inicio_prevista": r.data_inicio_prevista if pd.notna(r.data_inicio_prevista) else "",
                "data_termino_prevista": r.data_termino_prevista if pd.notna(r.data_termino_prevista) else "",
                "data_inicio_real": ini, "data_termino_real": fim,
                "metodo_data_inicio": m_ini, "metodo_data_termino": m_fim, "inicio_antes_da_serie": antes,
                "fonte_id": fonte, "localizacao_valor": loc,
                "series_ligadas": "|".join(cands), "criterio_serie_principal": motivo,
            })
            pe_ant = pe if pe is not None else pe_ant
    mensal = pd.DataFrame(linhas_mensal)

    # ---- sem série
    for _, r in cad.iterrows():
        if r.id_obra in principal_de:
            continue
        if r.situacao not in TIPO_SEM:
            print(f"AVISO: {r.id_obra} sem série e com situação '{r.situacao}' (tipo_registro vazio)")
        tr = TIPO_SEM.get(r.situacao, "")
        conc = r.situacao == "concluida"
        v = float(r.valor) if pd.notna(r.valor) else None
        linhas_acum.append({
            "id_obra": r.id_obra, "nome": r.nome, "tipo_registro": tr, "situacao": r.situacao,
            "data_inicio_real": r.data_inicio_real if pd.notna(r.data_inicio_real) else "",
            "data_termino_real": r.data_conclusao_real if pd.notna(r.data_conclusao_real) else "",
            "data_inicio_prevista": r.data_inicio_prevista if pd.notna(r.data_inicio_prevista) else "",
            "data_termino_prevista": r.data_termino_prevista if pd.notna(r.data_termino_prevista) else "",
            "pct_executado": 1.0 if conc else 0.0, "valor_nominal": v,
            "valor_executado": (v if conc else 0.0) if v is not None else None,
            "valor_a_executar": (0.0 if conc else v) if v is not None else None,
            "tipo_valor": cfg.tipo_item4 if v is not None else "", "data_base": db_linha(r) if v is not None else "",
            "fonte_id": r.fonte_id if v is not None else "", "localizacao_valor": r.localizacao_valor if v is not None else "",
        })
    acum = pd.DataFrame(linhas_acum)

    # ---- resumo por mes_ref x tipo_valor
    linhas_res = []
    com_valor = mensal[mensal.valor_nominal.notna()]
    for tipo in sorted(com_valor.tipo_valor.unique()):
        mt = com_valor[com_valor.tipo_valor == tipo]
        at = acum[(acum.tipo_valor == tipo)]
        ids_serie = mt.id_obra.unique()
        total_serie = mt.drop_duplicates("id_obra").valor_nominal.sum()
        total_tipo = total_serie + at.valor_nominal.sum()
        conc_antes = at.loc[at.tipo_registro == "concluida_antes_serie", "valor_executado"].sum()
        for m in MESES:
            exe, sem_dado = 0.0, 0
            for oid_row in ids_serie:
                x = mt[mt.id_obra == oid_row].sort_values("mes_ref")
                ate = x[x.mes_ref <= m]
                if (x.mes_ref == m).any():
                    exe += float(x.loc[x.mes_ref == m, "valor_executado_acum"].iloc[0])
                else:
                    sem_dado += 1
                    if len(ate):                       # sumiu da fonte: mantém o último executado conhecido
                        exe += float(ate.valor_executado_acum.iloc[-1])
            saldo = total_tipo - exe - conc_antes
            proj = NAO_RATEADO if tipo == cfg.tipo_item4 else None
            soma = exe + conc_antes + saldo + (proj or 0.0)
            alvo = cfg.total_item4 if tipo == cfg.tipo_item4 else total_tipo
            linhas_res.append({
                "mes_ref": m, "snapshot": SNAP_DO_MES[m], "tipo_valor": tipo,
                "n_linhas_com_serie": len(ids_serie), "n_linhas_serie_sem_dado_no_mes": sem_dado,
                "valor_total_tipo": total_tipo, "valor_executado_acum_com_serie": exe,
                "valor_executado_concluidas_antes_serie": conc_antes, "valor_a_executar": saldo,
                cfg.coluna_nao_rateado: proj, "soma_conferencia": soma, "valor_esperado": alvo,
                "conferencia": "ok" if abs(soma - alvo) <= TOL_R and saldo >= -TOL_R else "divergência",
            })
    res = pd.DataFrame(linhas_res)

    # ---------------------------------------------------------------- saídas
    gravar(mensal, "financeiro_mensal")
    gravar(acum, "financeiro_acumulado")
    gravar(res, "financeiro_resumo")
    with pd.ExcelWriter(caminho_final("xlsx", cfg.conc, "xlsx")) as w:
        mensal.to_excel(w, sheet_name="fin_mensal", index=False)
        acum.to_excel(w, sheet_name="fin_acumulado", index=False)
        res.to_excel(w, sheet_name="fin_resumo", index=False)

    # ---------------------------------------------------------------- relatório
    print("\n=== Resultado ===")
    print(f"Linhas do cadastro: {len(cad)} | com série: {len(principal_de)} | sem série: {len(acum)}")
    print(f"fin_mensal: {len(mensal)} linhas ({mensal.id_obra.nunique()} obras x {len(MESES)} meses de referência)")
    print(acum.tipo_registro.value_counts().to_string())
    print("\nObras com inicio_antes_da_serie:",
          ", ".join(sorted(mensal[mensal.inicio_antes_da_serie].id_obra.unique())) or "nenhuma")
    print("Séries compartilhadas por mais de uma linha do cadastro:",
          {k: v for k, v in mensal.groupby("obra_id_acompanhamento").id_obra.nunique().items() if v > 1})
    sobra = sorted(set(por_obra) - usadas)
    for oid in sobra:
        onde = [i for i, ((p, _), c) in principal_de.items() if oid in c]
        print(f"Sem uso: {oid} ({descricao(oid)[:50]}; {por_obra[oid].mes_referencia.iloc[0]} a {por_obra[oid].mes_referencia.iloc[-1]})"
              f" -> ligada a {onde or 'nenhuma linha do cadastro'}")
    sem_val = mensal[mensal.valor_nominal.isna()].id_obra.unique()
    if len(sem_val):
        print("Linhas com série e sem valor:", list(sem_val))
    mx = mensal.pct_executado_acum.max()
    print(f"Maior pct_executado_acum: {mx:.4f}")
    print(f"Revisões negativas (revisao_negativa): {int(mensal.revisao_negativa.sum())} linhas em "
          f"{mensal[mensal.revisao_negativa].id_obra.nunique()} linhas do cadastro")
    print(f"\nConferência ({cfg.tipo_item4}): executado + concluídas antes + a executar + {cfg.rotulo_nao_rateado} =",
          f"{cfg.total_item4:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    for t, g in res.groupby("tipo_valor"):
        div = g[g.conferencia != "ok"]
        print(f"  {t}: {'ok em todos os ' + str(len(g)) + ' meses' if div.empty else 'divergência em ' + ', '.join(div.mes_ref)}")
    print(f"  {cfg.rotulo_nao_rateado} = {NAO_RATEADO:,.2f}")
    if (res.conferencia != "ok").any():
        sys.exit(1)
