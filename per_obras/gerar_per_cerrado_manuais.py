"""
Gera per_obras/per_cerrado_manuais.csv: obras do PER ATUALIZADO da Ecovias do Cerrado (ECC, id 103), transcritas à mão
das tabelas do item 3.2 (fonte ecc_per_atualizado; página = página do PDF, que coincide com a numeração impressa).

Uso:  python per_obras/gerar_per_cerrado_manuais.py

1 linha por "linha do PER" (id_linha): em geral a obra inteira (id_linha = per_id); a marginal de cada trecho homogêneo
(TH) vira uma linha por lado (LD/LE) e a faixa adicional de cada TH, uma linha por ano de implantação (Tabela 3).
`fracao_linha` = parte da obra do PER (per_id) que a linha representa.

Colunas do custo do estudo (Fator D, fator-d.xlsx aba "Ampliação", fonte ecc_evtea_fator_d, data-base jul/2016):
    fd_linha  linha da aba Ampliação; fd_modo  'total' (coluna J x fd_fracao) ou 'unitario' (coluna I x quantidade;
    quando I está vazio, J / H); fd_fracao  parte do total da linha do Fator D que cabe a esta linha do PER.
`item_modelo`: subitem do item 4 do modelo (aba PER) em que o custo do Fator D está (Fator D 1.1 -> 4.5; 1.2 -> 4.1;
1.3 -> 4.2; 2 -> 4.3). Vazio = sem valor no item 4 (iluminação: "considerado na Recuperação", Fator D L57/L61;
obras condicionadas do 3.2.3: fora do modelo).
`km_evtea`: km do dispositivo no estudo (BR_364_365_RESUMO_OBRAS_MELHORIAS_REV8.xlsb, fonte ecc_evtea_modelagem),
usado para ligar dispositivos sem km no PER ao acompanhamento; `fonte_km_evtea` diz a aba e a linha.
`prazo_per_original`: só preenchido quando difere do PER original (per-original.pdf).
Os TH (trechos homogêneos) e seus km vêm da Tabela 3 (p.37) e da tabela de acostamentos (p.40, TH 10-12).
"""
import csv
from pathlib import Path

SAIDA = Path(__file__).resolve().parent / "per_cerrado_manuais.csv"
DOC = "ecc_per_atualizado"
RES = "RESUMO_OBRAS_MELHORIAS_REV8"

# trecho homogêneo -> (rodovia, uf, km inicial, km final). PER p.37 (Tabela 3) e p.40 (TH 10-12)
TH = {1: ("BR-364", "GO", 0.0, 4.9), 2: ("BR-364", "GO", 4.9, 9.3), 3: ("BR-364", "GO", 9.3, 16.0),
      4: ("BR-364", "GO", 16.0, 64.7), 5: ("BR-364", "GO", 64.7, 113.2), 6: ("BR-364", "GO", 113.2, 115.2),
      7: ("BR-364", "GO", 115.2, 159.9), 8: ("BR-364", "GO", 159.9, 162.4), 9: ("BR-364", "GO", 162.4, 192.7),
      10: ("BR-365", "MG", 629.0, 688.2), 11: ("BR-365", "MG", 688.2, 691.5), 12: ("BR-365", "MG", 691.5, 709.0),
      13: ("BR-365", "MG", 709.0, 735.6), 14: ("BR-365", "MG", 735.6, 751.6), 15: ("BR-365", "MG", 751.6, 753.2),
      16: ("BR-365", "MG", 753.2, 793.4), 17: ("BR-365", "MG", 793.4, 795.9), 18: ("BR-365", "MG", 795.9, 871.1),
      19: ("BR-365", "MG", 871.1, 873.3)}

COLS = ["per_id", "id_linha", "fracao_linha", "secao_per", "bloco", "tipo_intervencao", "subtipo", "descricao", "th",
        "rodovia", "uf", "municipio", "km_inicial", "km_final", "extensao_km", "quantidade", "unidade", "sentido",
        "prazo_per", "ano_prazo", "prazo_per_original", "km_evtea", "fonte_km_evtea", "item_modelo", "fd_linha",
        "fd_modo", "fd_fracao", "observacao_per", "pagina", "documento_fonte"]
linhas = []


def add(per_id, secao, bloco, tipo, desc, th, qtd, unid, pag, *, id_linha=None, fracao=1.0, subtipo="", mun="",
        ki=None, kf=None, ext=None, sentido="", prazo="", ano=None, prazo_orig="", km_ev=None, fonte_km="",
        item="", fd=None, modo="", fdfr=None, obs="", rod=None, uf=None):
    r, u = (TH[th][0], TH[th][1]) if isinstance(th, int) else (rod, uf)
    linhas.append(dict(per_id=per_id, id_linha=id_linha or per_id, fracao_linha=round(fracao, 10), secao_per=secao,
                       bloco=bloco, tipo_intervencao=tipo, subtipo=subtipo, descricao=desc, th=th, rodovia=rod or r,
                       uf=uf or u, municipio=mun, km_inicial=ki, km_final=kf, extensao_km=ext, quantidade=qtd,
                       unidade=unid, sentido=sentido, prazo_per=prazo, ano_prazo=ano, prazo_per_original=prazo_orig,
                       km_evtea=km_ev, fonte_km_evtea=fonte_km, item_modelo=item, fd_linha=fd, fd_modo=modo,
                       fd_fracao=None if fdfr is None else round(fdfr, 10), observacao_per=obs, pagina=pag,
                       documento_fonte=DOC))


# ---- 3.2.1.1 Duplicação em pista simples (Tabela 1, p.36). Fator D 1.3.3 (L103-105) -> 4.2
for i, (th, ki, kf, ext, ano, fd) in enumerate([(13, 709.0, 735.6, 26.6, 13, 103), (14, 735.6, 751.6, 16.0, 14, 104),
                                                (15, 751.6, 753.2, 1.6, 14, 105)], 1):
    add(f"ECC-PER-DUP-{i:02d}", "3.2.1.1", "condicionada", "duplicacao", f"Duplicação TH {th} (inclusive OAE)", th,
        ext, "km", "36", ki=ki, kf=kf, ext=ext, prazo=f"{ano}º ano", ano=ano, item="4.2", fd=fd, modo="total", fdfr=1,
        obs="Antecipação se o gatilho volumétrico (Tabela 2: 9.355 VDM eq.) for atingido; medição até o 10º ano (TH 13) "
            "e 11º ano (TH 14-15); prazo de 36 meses após o gatilho")

# ---- 3.2.1.2 Faixas adicionais em pista simples (Tabela 3, p.37): km de 3ª faixa por TH e ano. Fator D 1.3.1.1 -> 4.2
FAIXAS = {1: (3.33, {16: 3.33}, 71), 2: (2.74, {16: 2.74}, 72), 3: (1.17, {16: 1.17}, 73),
          4: (21.13, {15: 12.02, 16: 9.11}, 74), 5: (27.76, {7: 11.13, 15: 16.63}, 75), 7: (1.35, {3: 1.35}, 77),
          9: (8.33, {2: 2.23, 22: 6.10}, 79), 16: (21.19, {4: 21.19}, 85), 17: (1.21, {24: 1.21}, 86),
          18: (43.94, {5: 3.03, 22: 10.23, 23: 20.45, 24: 10.23}, 87), 19: (2.19, {5: 2.19}, 88)}
for th, (tot, anos, fd) in FAIXAS.items():
    pid = f"ECC-PER-FXA-{th:02d}"
    for j, (ano, kmano) in enumerate(sorted(anos.items())):
        suf = f"-{chr(97 + j)}" if len(anos) > 1 else ""
        add(pid, "3.2.1.2", "condicionada", "faixa_adicional", f"Faixa adicional TH {th} ({kmano:g} km no {ano}º ano)",
            th, kmano, "km", "37", id_linha=pid + suf, fracao=kmano / tot, ki=TH[th][2], kf=TH[th][3], ext=kmano,
            prazo=f"{ano}º ano", ano=ano, item="4.2", fd=fd, modo="total", fdfr=kmano / tot,
            obs=f"PER dá só o km total de 3ª faixa no TH ({tot:g} km) por ano; a localização dentro do TH não é dada")

# ---- 3.2.1.3 Complementação de obras (p.37-38). Fator D 1.1 (L11, L12) -> 4.5
add("ECC-PER-CMP-01", "3.2.1.3", "complementacao_dnit", "interconexao_trevo", "Complementação do Trevão (entroncamento "
    "BR-365/MG com BR-153/MG), trevo completo, incluída a iluminação", 13, 1, "un", "37-38", mun="Monte Alegre de Minas",
    ki=709.0, prazo="30% no 1º ano, 70% no 2º ano", ano=2, km_ev=709.0, fonte_km=f"{RES} aba COMPLEMENTAÇÃO OBRAS DNIT L11",
    item="4.5", fd=12, modo="total", fdfr=1)
add("ECC-PER-CMP-02", "3.2.1.3", "complementacao_dnit", "interconexao_trombeta", "Complementação do dispositivo de "
    "interseção no entroncamento de Xapetuba (BR-452), tipo trombeta", 10, 1, "un", "37-38", mun="Uberlândia",
    ki=656.3, prazo="1º ano", ano=1, km_ev=656.3, fonte_km=f"{RES} aba COMPLEMENTAÇÃO OBRAS DNIT L6", item="4.5",
    fd=11, modo="total", fdfr=1)

# ---- 3.2.1.4 Vias marginais (p.39). Extensão útil por lado. Fator D 1.2.1 (VM-1..VM-6) -> 4.1
MAR = [(2, [("LD", 5.0, 8.5, 3.5)], "São Simão", 4, 17, 3.5),
       (4, [("LD", 57.0, 58.0, 1.0), ("LE", 57.0, 58.0, 1.0)], "Cachoeira Alta", 4, 18, 2.0),
       (6, [("LD", 113.9, 114.6, 0.7), ("LE", 113.8, 114.6, 0.8)], "Aparecida do Rio Doce", 5, 19, 1.5),
       (11, [("LD", 688.0, 691.5, 3.5), ("LE", 688.0, 691.5, 3.5)], "Monte Alegre de Minas", 3, 22, 7.0),
       (15, [("LD", 752.6, 753.2, 0.6), ("LE", 752.6, 753.2, 0.6)], "Ituiutaba", 5, 23, 3.8),
       (16, [("LD", 753.2, 754.5, 1.3), ("LE", 753.2, 754.5, 1.3)], "Ituiutaba", 5, 23, 3.8),
       (19, [("LD", 870.7, 872.3, 1.6)], "Chaveslândia", 4, 24, 1.6)]
for th, lados, mun, ano, fd, km_fd in MAR:
    pid = f"ECC-PER-MAR-{th:02d}"
    tot = sum(x[3] for x in lados)
    for lado, ki, kf, ext in lados:
        add(pid, "3.2.1.4", "obrigatoria", "via_marginal", f"Via marginal TH {th} {lado} km {ki:g}-{kf:g} ({mun})", th,
            ext, "km", "39", id_linha=f"{pid}-{lado}" if len(lados) > 1 else pid, fracao=ext / tot, mun=mun, ki=ki,
            kf=kf, ext=ext, sentido=lado, prazo=f"{ano}º ano", ano=ano, item="4.1", fd=fd, modo="total",
            fdfr=ext / km_fd, obs="LD = sentido Uberlândia-Jataí, LE = sentido Jataí-Uberlândia (legenda do RESUMO_OBRAS "
                                  "do EVTEA); extensão útil, sem alças/tapers"
                                  + ("; VM-5 do Fator D (752,6-754,5, 3,8 km) cobre TH 15 e 16" if fd == 23 else ""))

# ---- Implantação ou adequação de acostamentos (p.40). Fator D 1.2.2 (GO, por subtrecho) e 1.2.3 (MG, L34 em grupo) -> 4.1
ACO = [(1, 4, 2.0, "Implantação", "5º ano", 5, 28, 1), (2, 7, 36.0, "Implantação", "16 km no 4º ano e 20 km no 5º ano", 5, 29, 1),
       (3, 9, 42.0, "Implantação", "2º ano", 2, 30, 1)] + \
      [(i, th, ext, "Adequação", "2º ao 5º ano, concomitante à recuperação", 5, 34, ext / 7.8)
       for i, th, ext in [(4, 10, 2.0), (5, 12, 1.8), (6, 13, 1.0), (7, 14, 0.6), (8, 15, 1.6), (9, 16, 0.8)]]
for i, th, ext, serv, prazo, ano, fd, fdfr in ACO:
    add(f"ECC-PER-ACO-{i:02d}", "3.2.1.4", "obrigatoria", "acostamento", f"{serv} de acostamentos TH {th} ({ext:g} km)",
        th, ext, "km", "40", subtipo=serv.lower(), ki=TH[th][2], kf=TH[th][3], ext=ext, prazo=prazo, ano=ano,
        item="4.1", fd=fd, modo="total", fdfr=fdfr,
        obs="Extensão = soma dos trechos com intervenção ao longo do TH (nota do PER); km = limites do TH"
            + ("; Fator D L34 traz os TH 10 a 16 (MG) num valor só (7,8 km): fração = km / 7,8" if fd == 34 else ""))

# ---- Correção de traçado (p.40). Fator D 1.3.1.2 (L91-92) -> 4.2
for i, th, k, ano, fd in [(1, 4, 25.0, 4, 91), (2, 9, 188.0, 5, 92)]:
    add(f"ECC-PER-CTR-{i:02d}", "3.2.1.4", "condicionada", "correcao_tracado", f"Correção de traçado km {k:g}", th, 1,
        "un", "40", ki=k, prazo=f"{ano}º ano", ano=ano, km_ev=k, fonte_km=f"{RES} aba CORREÇÃO DE TRAÇADO L{3 + i}",
        item="4.2", fd=fd, modo="total", fdfr=1,
        obs="No PER está em 3.2.1.4 (melhorias); no Fator D e no modelo está nas obras condicionadas (1.3.1.2 / 4.2)")

# ---- Melhorias de acessos (p.40-41): quantidade por TH. Fator D unitário por tipo x UF -> 4.1
ACE = [(1, 1, 4, "APS"), (2, 2, 3, "APS"), (3, 3, 4, "APS"), (4, 4, 9, "APS"), (5, 5, 12, "APS"), (6, 7, 10, "APS"),
       (7, 9, 9, "APS"), (8, 10, 19, "APD"), (9, 12, 10, "APD"), (10, 13, 13, "APS"), (11, 14, 11, "APS"),
       (12, 15, 2, "APS"), (13, 16, 19, "APS"), (14, 18, 20, "APS")]
FD_ACE = {("GO", "APS"): 43, ("MG", "APS"): 52, ("MG", "APD"): 53}
for i, th, q, tp in ACE:
    add(f"ECC-PER-ACE-{i:02d}", "3.2.1.4", "obrigatoria", "melhoria_acesso", f"Melhorias de acessos TH {th} ({q} {tp})",
        th, q, "un", "40-41", subtipo=tp, ki=TH[th][2], kf=TH[th][3], prazo="2º ao 5º ano (APS 28/29/29/30; APD 7/7/7/8 "
        "por ano no total)", ano=5, item="4.1", fd=FD_ACE[(TH[th][1], tp)], modo="unitario",
        obs="PER dá só a quantidade por TH; km = limites do TH. APS = acesso em pista simples, APD = pista dupla")

# ---- Melhorias de interseções (p.41). Fator D unitário (L40 GO, L49 MG) -> 4.1
INTS = [(1, 1, "1º Trevo de Acesso a São Simão", 6, 4.9, None, 3), (2, 2, "2º Trevo de Acesso a São Simão", 6, 9.3, None, 4),
        (3, 4, "Trevo de Acesso a Paranaiguara", 6, 16.0, None, 5), (4, 14, "Entroncamento BR-154 (A)", 8, 751.6, None, 6),
        (5, 15, "1º Trevo de Acesso a Ituiutaba", 12, 753.2, None, 7), (6, 16, "2º Trevo de Acesso a Ituiutaba", 8, 758.9, None, 8),
        (7, 18, "Trevo de Acesso a Santa Vitória", 6, 825.7, None, 9)]
for i, th, loc, tap, k, _, lres in INTS:
    add(f"ECC-PER-INT-{i:02d}", "3.2.1.4", "obrigatoria", "intersecao", f"Melhoria de interseção: {loc} (taper, {tap:02d} "
        "unidades)", th, 1, "un", "41", prazo="2º ao 5º ano (2/2/2/1 por ano no total)", ano=5, km_ev=k,
        fonte_km=f"{RES} aba MELHORIA DE INTERSEÇÕES L{lres}", item="4.1", fd=40 if TH[th][1] == "GO" else 49,
        modo="unitario", obs="Inclusive iluminação")

# ---- Rotatórias alongadas (p.42). TH e km do RESUMO_OBRAS (células mescladas no PDF). Fator D unitário -> 4.1
ROT = [(1, 1, "RA-1A", "Acesso ao Terminal de Carga Fluvial", 1.0, "São Simão"),
       (2, 3, "RA-2A", "Entroncamento BR-364 com BR-483(A)/GO-164(A)", 16.0, ""),
       (3, 4, "RA-1A", "Cachoeira Alta - Acesso Sul", 54.0, "Cachoeira Alta"),
       (4, 4, "RA-1A", "Cachoeira Alta - Acesso Indústria", 55.8, "Cachoeira Alta"),
       (5, 4, "RA-2A", "Entroncamento da BR-364 com GO-174(A)/Acesso Cachoeira Alta", 57.6, "Cachoeira Alta"),
       (6, 4, "RA-2A", "Cachoeira Alta - Estrada Posto Camaleão", 58.7, "Cachoeira Alta"),
       (7, 4, "RA-1A", "Cachoeira Alta - Acesso Norte", 59.6, "Cachoeira Alta"),
       (8, 4, "RA-1A", "Entroncamento BR-364 com GO-174(B)", 63.2, ""),
       (9, 5, "RA-2A", "Entroncamento BR-364 com GO-206/Acesso Caçu", 89.6, ""),
       (10, 5, "RA-1A", "Entroncamento BR-364 com GO-422", 113.2, ""),
       (11, 6, "RA-2A", "Acesso Aparecida do Rio Doce", 114.6, "Aparecida do Rio Doce"),
       (12, 7, "RA-1A", "Entroncamento BR-364 com GO-178", 151.0, ""),
       (13, 7, "RA-2A", "Acesso Naveslândia", 159.2, ""), (14, 8, "RA-2A", "Acesso Naveslândia", 160.0, ""),
       (15, 9, "RA-1A", "Entroncamento BR-364 com GO-180", 174.8, ""),
       (16, 10, "RA-2A", "Acesso Ribeirão das Pedras e Carlos de Vasconcelos", 635.0, ""),
       (17, 17, "RA-1A", "Acesso Gurinhatã", 793.4, "Gurinhatã"), (18, 17, "RA-1A", "Acesso Flor de Minas", 795.0, ""),
       (19, 18, "RA-1A", "Entroncamento BR-365 com BR-364(A)", 863.4, ""),
       (20, 19, "RA-2A", "Acesso Chaveslândia", 872.4, "")]
FD_ROT = {("GO", "RA-1A"): 41, ("GO", "RA-2A"): 42, ("MG", "RA-1A"): 50, ("MG", "RA-2A"): 51}
for i, th, tp, loc, k, mun in ROT:
    add(f"ECC-PER-ROT-{i:02d}", "3.2.1.4", "obrigatoria", "rotatoria", f"Rotatória alongada {tp}: {loc}", th, 1, "un",
        "42", subtipo=tp, mun=mun, prazo="2º ao 5º ano (por TH, ver p.42)", ano=5, km_ev=k,
        fonte_km=f"{RES} aba ROTATÓRIAS ALONGADAS L{3 + i}", item="4.1", fd=FD_ROT[(TH[th][1], tp)], modo="unitario",
        obs="Inclusive iluminação em trechos urbanos. RA-1A = 1 acesso, RA-2A = 2 acessos")

# ---- Passarelas (p.43, redação do 2º TA). Fator D unitário (L38 GO PPS, L47 MG PPS, L48 MG PPD) -> 4.1
PAS = [(1, 4, "PPS", "Cachoeira Alta", 4, 58.0, "PPS no 2º, 3º, 4º e 5º ano (1/1/2/1, sem ID)"),
       (2, 5, "PPS", "Aparecida do Rio Doce", 2, 114.2, "idem"),
       (3, 7, "PPS", "Naveslândia", 5, 159.5, "idem"),
       (4, 11, "PPD", "Monte Alegre de Minas", 3, 689.0, "PPD no 3º e 5º ano (1/1, sem ID)"),
       (5, 11, "PPD", "Monte Alegre de Minas", 3, 690.0, "PPD no 3º e 5º ano (1/1, sem ID)"),
       (6, 15, "PPS", "Ituiutaba", 5, 752.0, "PPS no 2º a 5º ano; TH 15"),
       (7, 16, "PPS", "Ituiutaba", 4, None, "PPS no 2º a 5º ano; TH 15 (o 2º TA passou para o TH 16)")]
for i, th, tp, mun, ano, k, orig in PAS:
    add(f"ECC-PER-PAS-{i:02d}", "3.2.1.4", "obrigatoria", "passarela", f"Passarela {tp} {mun}", th, 1, "un", "43",
        subtipo=tp, mun=mun, prazo=f"{ano}º ano", ano=ano, prazo_orig=f"{orig} (PER original p.44)", km_ev=k,
        fonte_km=f"{RES} aba PASSARELAS L{3 + i}" if k else "", item="4.1",
        fd={"GO": 38, "MG": 47}[TH[th][1]] if tp == "PPS" else 48, modo="unitario",
        obs="Inclusive iluminação. PPS = pista simples, PPD = pista dupla. Tabela com redação do 2º TA (Deliberação "
            "353/2024, nota 3 da p.43)" + ("; km do EVTEA (753,0) não usado: o TH mudou" if i == 7 else ""))

# ---- Retornos em nível (p.43): km aproximado, concomitante às duplicações (13º/14º ano). Fator D 1.3.4 -> 4.2
for i, (th, k) in enumerate([(13, 714.0), (13, 719.0), (13, 724.0), (13, 729.0), (13, 734.0), (14, 738.0), (15, 743.0),
                             (15, 748.0)], 1):
    add(f"ECC-PER-RET-{i:02d}", "3.2.1.4", "condicionada", "retorno_nivel", f"Retorno em nível km {k:g} (TH {th})", th,
        1, "un", "43", ki=k, prazo="Concomitante com as duplicações, 13º e 14º ano", ano=14 if th > 13 else 13, km_ev=k,
        fonte_km=f"{RES} aba RETORNO EM NÍVEL L{2 + i}", item="4.2", fd={13: 109, 14: 110, 15: 111}[th], modo="unitario",
        obs="Localização aproximada, a confirmar quando da implantação das duplicações. Obs.: o km 743 e o 748 estão no "
            "TH 14 pelos limites da Tabela 3, mas o PER diz TH 15" if th == 15 else
        "Localização aproximada, a confirmar quando da implantação das duplicações")

# ---- Iluminação (p.43-44): sem valor no item 4 (Fator D L57/L61: "considerado na Recuperação", item 2.7 do modelo)
OBS_ILU = "Sem valor no item 4: o Fator D (L57/L61) diz 'considerado na Recuperação' (item 2.7 do modelo)"
add("ECC-PER-ILT-01", "3.2.1.4", "iluminacao_recuperacao", "iluminacao", "Iluminação em travessias urbanas BR-364/GO "
    "(TH 2-6-8)", "2-6-8", 5.4, "km", "43", ext=5.4, prazo="4,4 km no 2º ano, 1 km no 3º ano", ano=3, obs=OBS_ILU
    + "; trechos urbanos: São Simão, Naveslândia (e Aparecida do Rio Doce, TH 6)", rod="BR-364", uf="GO")
add("ECC-PER-ILT-02", "3.2.1.4", "iluminacao_recuperacao", "iluminacao", "Iluminação em travessias urbanas BR-365/MG "
    "(TH 10-16-17)", "10-16-17", 15.6, "km", "43", ext=15.6, prazo="2 km no 2º, 4,6 km no 3º, 2 km no 4º, 7 km no 5º ano",
    ano=5, obs=OBS_ILU + "; trechos urbanos: Uberlândia, Monte Alegre de Minas, Ituiutaba, Flor de Minas",
    rod="BR-365", uf="MG")
add("ECC-PER-ILM-01", "3.2.1.4", "iluminacao_recuperacao", "iluminacao", "Iluminação em via marginal existente - "
    "Naveslândia (TH 8)", 8, 2.0, "km", "44", mun="Naveslândia", ext=2.0, prazo="4º ano", ano=4, obs=OBS_ILU)
for i, (ki, kf) in enumerate([(633.2, 635.0), (640.5, 641.3), (649.2, 650.4), (652.9, 654.3)], 1):
    add(f"ECC-PER-ILR-{i:02d}", "3.2.1.4", "iluminacao_recuperacao", "iluminacao", f"Iluminação em retorno existente km "
        f"{ki:g}-{kf:g}", 10, round(kf - ki, 3), "km", "44", ki=ki, kf=kf, ext=round(kf - ki, 3),
        prazo="10,40 km no total: 3,6 km no 2º, 4,0 km no 4º e 2,8 km no 5º ano", ano=5, obs=OBS_ILU)
for i, (th, rod, uf, ano, loc) in enumerate([(2, "BR-364", "GO", 3, "Interseção - Trecho Urbano - São Simão"),
                                             (10, "BR-365", "MG", 2, "Interseção - Trecho Urbano - Uberlândia"),
                                             (10, "BR-365", "MG", 3, "Interseção Estaca 615 - Monte Alegre de Minas"),
                                             (11, "BR-365", "MG", 5, "PI Rua da Saudade - Monte Alegre de Minas"),
                                             (12, "BR-365", "MG", 4, "Interseção Estaca 438 - Monte Alegre de Minas")], 1):
    add(f"ECC-PER-ILI-{i:02d}", "3.2.1.4", "iluminacao_recuperacao", "iluminacao", f"Iluminação em interseção/rotatória "
        f"existente: {loc}", th, 1, "un", "44", prazo=f"{ano}º ano", ano=ano, rod=rod, uf=uf,
        obs=OBS_ILU + ("; o PER grafa 'BR-365/MG' no TH 2 (São Simão, BR-364/GO)" if th == 2 else
                       "; o PER grafa 'BR-364/MG' (é a BR-365/MG)"))

# ---- 3.2.3 Obras condicionadas ao volume de tráfego (p.47-48): sem local nem prazo, fora do modelo
for th in [1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19]:
    g = {1: 9700, 2: 9700, 3: 9700, 4: 9700, 5: 9265, 6: 11015, 7: 11015, 8: 11015, 9: 11015, 16: 9355, 17: 9970,
         18: 9970, 19: 9970}[th]
    add(f"ECC-PER-DCO-{th:02d}", "3.2.3.1", "condicionada", "duplicacao", f"Duplicação condicionada ao volume de tráfego "
        f"TH {th}", th, round(TH[th][3] - TH[th][2], 3), "km", "47", ki=TH[th][2], kf=TH[th][3],
        ext=round(TH[th][3] - TH[th][2], 3), prazo="36 meses após o gatilho (aferição até o 25º ano)",
        obs=f"Gatilho {g:,} VDM equivalente (Tabela 4). Sem valor no item 4 do modelo (custeio pelo Anexo 9)".replace(",", "."))
for th, g in [(10, 55165), (11, 55165), (12, 54915)]:
    add(f"ECC-PER-FCO-{th:02d}", "3.2.3.2", "condicionada", "faixa_adicional", f"Faixas adicionais em pista dupla "
        f"condicionadas ao volume de tráfego TH {th}", th, round(TH[th][3] - TH[th][2], 3), "km", "48", ki=TH[th][2],
        kf=TH[th][3], ext=round(TH[th][3] - TH[th][2], 3), prazo="36 meses após o gatilho (aferição até o 25º ano)",
        obs=f"Gatilho {g:,} VDM equivalente (Tabela 6). Sem valor no item 4 do modelo (custeio pelo Anexo 9)".replace(",", "."))

# ---- Edificações e instalações operacionais (4.3): o PER não lista por obra; quantidades do Fator D (aba Ampliação L115-132)
EDI = [(115, "GO", "praca_pedagio", "Praças de pedágio", 3, "un", "3.4.5"), (116, "GO", "posto_prf", "Postos PRF", 2, "un", "3.4.10"),
       (118, "GO", "base_operacional", "BSO - bases operacionais tipo 1", 1, "un", "3.4.4"),
       (119, "GO", "base_operacional", "BSO - bases operacionais tipo 2", 3, "un", "3.4.4"),
       (120, "GO", "posto_pesagem", "Posto de pesagem fixa", 2, "un", "3.4.7"),
       (121, "GO", "fibra_optica", "Rede de fibra ótica", 202.34, "km", "3.4.6"),
       (124, "MG", "praca_pedagio", "Praças de pedágio", 4, "un", "3.4.5"),
       (125, "MG", "centro_controle", "Centro de Controle Operacional", 1, "un", "3.4.1"),
       (126, "MG", "posto_prf", "Postos PRF", 2, "un", "3.4.10"),
       (128, "MG", "base_operacional", "BSO - bases operacionais tipo 1", 2, "un", "3.4.4"),
       (129, "MG", "base_operacional", "BSO - bases operacionais tipo 2", 3, "un", "3.4.4"),
       (130, "MG", "posto_pesagem", "Posto de pesagem fixa", 2, "un", "3.4.7"),
       (131, "MG", "fibra_optica", "Rede de fibra ótica", 256.52, "km", "3.4.6"),
       (132, "MG", "edificio_sede", "Edifício sede", 1, "un", "3.1.7")]
for i, (fd, uf, tipo, desc, q, un, sec) in enumerate(EDI, 1):
    add(f"ECC-PER-EDI-{i:02d}", sec, "edificacoes_operacionais", tipo, f"{desc} ({uf})", None, q, un, "",
        rod={"GO": "BR-364", "MG": "BR-365"}[uf], uf=uf, ext=q if un == "km" else None, item="4.3", fd=fd,
        modo="total" if un == "km" else "unitario",
        obs="Não está nas tabelas do item 3.2 do PER: linha do Fator D (aba Ampliação, item 2 Edificações e instalações "
            "operacionais), que é o 4.3 do modelo; seção do PER pelo sumário (p.2)")
linhas[-len(EDI):] = [dict(r, documento_fonte="ecc_evtea_fator_d") for r in linhas[-len(EDI):]]

with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, delimiter=";")
    w.writeheader()
    for r in linhas:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})
print(f"{len(linhas)} linhas ({len({r['per_id'] for r in linhas})} obras do PER) em {SAIDA}")
