"""
Gera per_obras/per_eco050_manuais.csv: obras previstas no PER original da ECO050 (EMG, id 104), transcritas
à mão do per-original.pdf (fonte_id eco050_per_original) e conferidas contra as tabelas do PDF.

Uso:  python per_obras/gerar_per_eco050_manuais.py
"""
import csv
from pathlib import Path

SAIDA = Path(__file__).resolve().parent / "per_eco050_manuais.csv"
DOC = "eco050_per_original"
COLS = ["per_id", "secao_per", "bloco", "tipo_intervencao", "descricao", "pnv", "rodovia", "uf", "municipio",
        "km_inicial", "km_final", "extensao_km", "quantidade", "unidade", "sentido", "observacao_per", "pagina",
        "documento_fonte"]
linhas = []


def add(per_id, secao, bloco, tipo, desc, pnv="", uf="", mun="", ki="", kf="", ext="", qtd=1, un="un", sent="",
        obs="", pag=""):
    linhas.append(dict(per_id=per_id, secao_per=secao, bloco=bloco, tipo_intervencao=tipo, descricao=desc, pnv=pnv,
                       rodovia="BR-050", uf=uf, municipio=mun, km_inicial=ki, km_final=kf, extensao_km=ext,
                       quantidade=qtd, unidade=un, sentido=sent, observacao_per=obs, pagina=pag, documento_fonte=DOC))


def uf_pnv(pnv):
    return "GO" if "GO" in pnv else "MG"


# --- Apêndice A (p.84): segmentos PAV (pista simples) -> duplicação
PAV = [("050BGO0070", 95.7, 106.7, 11.0), ("050BGO0075", 106.7, 119.2, 12.5), ("050BGO0080", 119.2, 125.2, 6.0),
       ("050BGO0090", 125.2, 154.5, 29.3), ("050BGO0095", 154.5, 163.5, 9.0), ("050BGO0110", 163.5, 207.6, 44.1),
       ("050BGO0120", 207.6, 209.8, 2.2), ("050BGO0130", 209.8, 245.4, 35.6), ("050BGO0135", 245.4, 265.1, 19.7),
       ("050BGO0140", 265.1, 270.1, 5.0), ("050BGO0150", 270.1, 280.5, 10.4), ("050BGO0152", 280.5, 311.7, 31.2),
       ("050BGO0154", 311.7, 314.2, 2.5)]
OBS_DUP = ("PER dá só metas anuais de pista dupla para o lote (ano 1: 35,0 km; ano 2: 52,4; ano 3: 74,3; ano 4: 56,8; "
           "total 218,5 km), sem indicar qual segmento em qual ano; segmento PAV (pista simples) do Apêndice A")
for i, (pnv, ki, kf, ext) in enumerate(PAV, 1):
    obs = OBS_DUP + ("; Obs.2: ponte da divisa GO/MG, incluindo duplicação, a cargo da Concessionária"
                     if pnv.endswith("0154") else "")
    add(f"EMG-PER-DUP-{i:02d}", "3.2.1.1", "obrigatoria", "duplicacao", f"Duplicação do segmento {pnv}", pnv, "GO", "",
        ki, kf, ext, ext, "km", "", obs, "32 e 84")

# --- Vias marginais (p.33): id, pnv, km ini, km fim, extensão Sul (m), Norte (m), município
MAR = [(1, "050BMG0210", 40.0, 41.0, 900, 900, "Araguari"), (2, "050BGO0070", 98.0, 100.8, 2800, 2700, "Cristalina"),
       (3, "050BGO0075", 106.7, 107.3, 550, 0, "Cristalina"), (4, "050BGO0075", 107.3, 108.0, 0, 700, "Cristalina"),
       (5, "050BGO0120", 207.4, 209.6, 0, 2200, "Campo Alegre de Goiás"), (6, "050BGO0135", 245.4, 246.9, 0, 1500, "Catalão"),
       (7, "050BGO0150", 276.5, 280.5, 0, 4000, "Catalão"), (8, "050BGO0150", 276.9, 283.1, 6200, 0, "Catalão")]
for i, pnv, ki, kf, s, n, mun in MAR:
    obs = (f"Extensão útil (m): Sul {s if s else '-'}; Norte {n if n else '-'}; total {s + n} m (vias marginais nos dois "
           "sentidos, sem alças/tapers e faixas de aceleração/desaceleração); prazo: até 12 meses após a duplicação do subtrecho")
    sent = "Sul e Norte" if s and n else ("Sul" if s else "Norte")
    add(f"EMG-PER-MAR-{i:02d}", "3.2.1.2", "obrigatoria", "via_marginal", f"Via marginal ID {i} ({mun})", pnv, uf_pnv(pnv),
        mun, ki, kf, (s + n) / 1000, (s + n) / 1000, "km", sent, obs, "33")

# --- Acessos (p.33)
ACE = [(1, "050BGO0135", 247.0, "Catalão"), (2, "050BGO0135", 258.0, "Catalão"), (3, "050BGO0135", 264.0, "Catalão"),
       (4, "050BGO0152", 282.0, "Catalão"), (5, "050BGO0152", 282.7, "Catalão"), (6, "050BGO0152", 287.0, "Catalão"),
       (7, "050BGO0152", 289.0, "Catalão"), (8, "050BGO0152", 301.0, "Cumari")]
for i, pnv, km, mun in ACE:
    add(f"EMG-PER-ACE-{i:02d}", "3.2.1.2", "obrigatoria", "melhoria_acesso", f"Melhoria em acesso ID {i}", pnv, "GO",
        mun, km, km, "", 1, "un", "", "", "33")

# --- Interconexão diamante (p.33-34)
CAG = "Campo Alegre de Goiás"
DIA = [(1, "050BMG0250", 124.0, "Uberaba", ""), (2, "050BMG0250", 131.3, "Uberaba", ""), (3, "050BMG0260", 140.3, "Uberaba", ""),
       (4, "050BMG0260", 151.5, "Uberaba", ""), (5, "050BGO0070", 97.3, "Cristalina", ""), (6, "050BGO0075", 111.7, "Cristalina", ""),
       (7, "050BGO0080", 119.2, "Ipameri", "ENTR GO-519 (DOMICIANO RIBEIRO)"), (8, "050BGO0110", 187.0, CAG, ""),
       (9, "050BGO0110", 202.4, CAG, ""), (10, "050BGO0120", 207.6, CAG, "ENTR GO-213(A) (CAMPO ALEGRE DE GOIÁS)"),
       (11, "050BGO0130", 209.8, CAG, "ENTR BR-490/GO-213(B)"), (12, "050BGO0135", 245.4, "Catalão", "ENTR GO-506"),
       (13, "050BGO0150", 270.1, "Catalão", "ENTR GO-504"), (14, "050BGO0150", 273.2, "Catalão", ""),
       (15, "050BGO0152", 280.5, "Catalão", "ENTR BR-352(B)/GO-210(B)/330 (CATALÃO)"), (16, "050BGO0152", 296.0, "Cumari", "")]
for i, pnv, km, mun, ob in DIA:
    add(f"EMG-PER-DIA-{i:02d}", "3.2.1.2", "obrigatoria", "interconexao_diamante", f"Interconexão diamante ID {i}", pnv,
        uf_pnv(pnv), mun, km, km, "", 1, "un", "", ob, "33-34")

# --- Passarelas (p.34)
PAS = [(1, "050BMG0210", 40.5, "Araguari"), (2, "050BMG0265", 179.0, "Uberaba"), (3, "050BGO0070", 101.0, "Cristalina"),
       (4, "050BGO0070", 96.4, "Cristalina"), (5, "050BGO0070", 98.7, "Cristalina"), (6, "050BGO0150", 277.5, "Catalão"),
       (7, "050BGO0150", 279.5, "Catalão")]
for i, pnv, km, mun in PAS:
    add(f"EMG-PER-PAS-{i:02d}", "3.2.1.2", "obrigatoria", "passarela", f"Passarela ID {i}", pnv, uf_pnv(pnv), mun,
        km, km, "", 1, "un", "", "", "34")

add("EMG-PER-TRV-01", "3.2.1.2", "obrigatoria", "interconexao_trevo_completo", "Interconexão tipo trevo completo ID 1",
    "050BGO0150", "GO", "Catalão", 276.5, 276.5, "", 1, "un", "", "", "34")

# --- Trombetas (p.34)
TRB = [(1, "050BMG0170", 4.0, "Araguari", ""), (2, "050BMG0190", 22.0, "Araguari", "ENTR MG-223(A) (AMANHECE)"),
       (3, "050BMG0260", 157.5, "Uberaba", ""), (4, "050BGO0090", 125.2, "Ipameri", "ENTR BR-457(B)/GO-219"),
       (5, "050BGO0095", 154.5, CAG, "ENTR GO-020(A)"), (6, "050BGO0110", 163.5, CAG, "ENTR GO-020(B)"),
       (7, "050BGO0140", 265.1, "Catalão", "ENTR BR-352(A)/GO-210(A)"), (8, "050BGO0154", 311.7, "Cumari", "ENTR GO-402")]
for i, pnv, km, mun, ob in TRB:
    add(f"EMG-PER-TRB-{i:02d}", "3.2.1.2", "obrigatoria", "interconexao_trombeta", f"Interconexão trombeta ID {i}", pnv,
        uf_pnv(pnv), mun, km, km, "", 1, "un", "", ob, "34")

# --- Retornos em desnível (p.35)
RET = [(1, "050BMG0250", 101.0, "Uberlândia"), (2, "050BGO0090", 140.0, "Ipameri"), (3, "050BGO0130", 222.0, CAG),
       (4, "050BGO0130", 233.0, "Catalão"), (5, "050BGO0135", 255.0, "Catalão")]
for i, pnv, km, mun in RET:
    add(f"EMG-PER-RET-{i:02d}", "3.2.1.2", "obrigatoria", "retorno_em_desnivel", f"Retorno em desnível ID {i}", pnv,
        uf_pnv(pnv), mun, km, km, "", 1, "un", "", "", "35")

# --- Faixas adicionais condicionadas (p.37 e Apêndice B p.87): subtrecho, km ini, km fim, ext, VDMA, UF
FAD = [("A", 95.7, 119.2, 23.5, 42500, "GO"), ("B", 119.2, 163.5, 44.3, 39900, "GO"),
       ("C", 163.5, 265.1, 101.6, 40700, "GO"), ("D", 265.1, 314.2, 89.1, 41900, "GO/MG"),
       ("E", 40.0, 65.7, 25.7, 42000, "MG"), ("F", "", 156.8, 101.9, 66000, "MG"), ("G", 156.8, 207.3, 50.5, 41600, "MG")]
for i, (sub, ki, kf, ext, vdma, uf) in enumerate(FAD, 1):
    obs = (f"Subtrecho {sub}; gatilho VDMA equivalente {vdma:,}".replace(",", ".") +
           " veículos equivalentes/dia (média móvel de 365 dias, ambos sentidos): ao atingir, 12 meses para concluir a "
           "faixa adicional (inclui OAEs, acessos e interconexões); só em trechos em pista dupla")
    if sub == "D":
        obs += ("; Apêndice B dá dois trechos: 265,1-314,2 km (49,1 km, BR-050/GO) e 0,0-40,0 km (40,0 km, BR-050/MG); "
                "km_inicial/km_final guardam só o trecho GO e extensao_km soma os dois (89,1 km)")
    if sub == "E":
        obs += "; trecho do contorno (existente) de Uberlândia"
    if sub == "F":
        obs += ("; Apêndice B: km inicial não numérico (entroncamento BR-050 x Contorno de Uberlândia), final 156,8, "
                "extensão 101,9 km (inclui trecho do contorno existente)")
    add(f"EMG-PER-FAD-{i:02d}", "3.2.3.1", "condicionada", "faixa_adicional",
        f"Faixa adicional condicionada, subtrecho {sub}", "", uf, "", ki, kf, ext, ext, "km", "Ambos", obs, "37 e 87")

# --- Estoque 3.2.3.3 (p.38): quantitativos máximos, sem local
OBS_EST = ("Quantitativo máximo de melhoria de manutenção de nível de serviço, sem local definido; prazo a critério da "
           "ANTT (12 meses da solicitação formal; +6 se houver desapropriação); a partir do 61º mês")
EST = [("MAR", "via_marginal", "Vias marginais (extensão útil)", 1), ("ACE", "melhoria_acesso", "Acessos", 2),
       ("DIA", "interconexao_diamante", "Interconexão diamante", 3), ("PAS", "passarela", "Passarelas", 2),
       ("TRV", "interconexao_trevo", "Interconexão trevo", 1), ("TRB", "interconexao_trombeta", "Interconexão trombeta", 2),
       ("RET", "retorno_operacional", "Retorno operacional", 1)]
for sig, tipo, nome, n in EST:
    for j in range(1, n + 1):
        if sig == "MAR":
            add(f"EMG-PER-EST-{sig}-{j:02d}", "3.2.3.3", "manutencao_nivel_servico", tipo,
                f"{nome}: estoque total de 4,0 km (duas faixas de rolamento)", ext=4.0, qtd=4.0, un="km",
                obs=OBS_EST + "; sem alças/tapers e faixas de aceleração/desaceleração", pag="38")
        else:
            add(f"EMG-PER-EST-{sig}-{j:02d}", "3.2.3.3", "manutencao_nivel_servico", tipo, f"{nome}: unidade {j} de {n}",
                qtd=1, un="un", obs=OBS_EST, pag="38")

with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, COLS, delimiter=";")
    w.writeheader()
    w.writerows(linhas)


def soma(tipo, bloco):
    return sum(float(l["quantidade"]) for l in linhas if l["tipo_intervencao"] == tipo and l["bloco"] == bloco)


print(f"{len(linhas)} linhas em {SAIDA}")
print("duplicação km:", round(soma("duplicacao", "obrigatoria"), 1), "(PER: 218,5)")
print("marginais m:", round(sum(l["extensao_km"] for l in linhas
                                if l["tipo_intervencao"] == "via_marginal" and l["bloco"] == "obrigatoria") * 1000), "(PER: 22.450)")
for t, e in [("melhoria_acesso", 8), ("interconexao_diamante", 16), ("passarela", 7), ("interconexao_trevo_completo", 1),
             ("interconexao_trombeta", 8), ("retorno_em_desnivel", 5)]:
    print(t, soma(t, "obrigatoria"), "(PER:", e, ")")
