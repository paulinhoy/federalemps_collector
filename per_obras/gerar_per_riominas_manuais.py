"""
Gera per_obras/per_riominas_manuais.csv: obras previstas no PER Atualizado da Ecovias Rio Minas (id 105, ERM),
seção 3.2 (Frente de Ampliação de Capacidade, Melhorias e Manutenção de Nível de Serviço), p.52 a p.87.

As tabelas do PDF são lidas com pdfplumber (texto) e interpretadas por expressões regulares; o resultado é
conferido contra a tabela "Resumo" da p.88 do próprio PER. O script para com erro se algum total não fechar.
Só a lista de alças de conexão (p.74-75, 7 itens, texto em duas linhas) é transcrita à mão aqui.

Fora desta lista (de propósito):
  - 3.2.2.A Travessias urbanas (p.62-64): relação de trechos urbanos que exigem iluminação, não é obra com quantitativo;
    não consta da tabela Resumo da p.88.
  - 3.2.3 Manutenção de nível de serviço (p.89 em diante): só gatilhos volumétricos por trecho homogêneo, sem obra
    com localização definida.

Uso:  python per_obras/gerar_per_riominas_manuais.py
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pdfplumber

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
sys.path.insert(0, str(PROJETO))
from acompanhamento_obras.portal_antt import longo  # noqa: E402

SAIDA = AQUI / "per_riominas_manuais.csv"
DOC = "riominas_per_atualizado"
PAG_INI, PAG_FIM = 52, 88
COLS = ["per_id", "secao_per", "bloco", "tipo_intervencao", "descricao", "rodovia", "uf", "km_inicial", "km_final",
        "extensao_km", "quantidade", "unidade", "sentido", "ano_concessao", "observacao_per", "pagina",
        "documento_fonte"]

# (secao do PER) -> (sigla, tipo_intervencao, nome para a descrição). Mesmos nomes de tipo do cadastro da ECO050
# quando existem equivalentes (duplicacao, faixa_adicional, via_marginal, interconexao_*, melhoria_acesso, passarela).
SECOES = {
    ("1", "A"): ("DUP", "duplicacao", "Duplicação"),
    ("1", "B"): ("FAD", "faixa_adicional", "Faixa adicional"),
    ("1", "C"): ("ESC", "area_escape", "Área de escape"),
    ("2", "B"): ("MAR", "via_marginal", "Via marginal"),
    ("2", "C"): ("DIA", "interconexao_diamante", "Interseção diamante"),
    ("2", "D"): ("PIN", "passagem_inferior", "Interseção em passagem inferior"),
    ("2", "E"): ("TRB", "interconexao_trombeta", "Interseção trombeta"),
    ("2", "F"): ("TRV", "interconexao_trevo", "Interseção trevo"),
    ("2", "G"): ("RTU", "retorno_em_desnivel", "Retorno tipo U"),
    ("2", "H"): ("RTX", "retorno_em_desnivel", "Retorno tipo X"),
    ("2", "I"): ("ROT", "rotatoria", "Rotatória em nível"),
    ("2", "J"): ("ROA", "rotatoria", "Rotatória alongada"),
    ("2", "K"): ("ALC", "alca_conexao", "Alça de conexão"),
    ("2", "L"): ("ACE", "melhoria_acesso", "Acessos"),
    ("2", "M"): ("BRU", "barreira_ruido", "Barreira de ruído"),
    ("2", "N"): ("CPP", "caixa_produto_perigoso", "Caixa de produtos perigosos"),
    ("2", "O"): ("FAU", "passagem_fauna", "Passagem de fauna"),
    ("2", "P"): ("PAS", "passarela", "Passarela"),
    ("2", "Q"): ("ONI", "ponto_onibus", "Pontos de ônibus"),
    ("2", "R"): ("CIC", "ciclovia", "Ciclovia"),
    ("2", "S"): ("DIV", "divisor_central", "Divisor central com barreira rígida (pista simples)"),
}
ORDEM_ROD = {("BR-116", "RJ"): 0, ("BR-116", "MG"): 1, ("BR-465", "RJ"): 2, ("BR-493", "RJ"): 3}

# Resumo da p.88: (sigla) -> {(rodovia, uf): quantidade}; None = tipo não está no Resumo por rodovia
RESUMO = {
    "DUP": {("BR-116", "RJ"): 91.215, ("BR-116", "MG"): 192.099, ("BR-493", "RJ"): 19.914},
    "FAD": {("BR-116", "RJ"): 124.693, ("BR-116", "MG"): 130.543},
    "ESC": {("BR-116", "RJ"): 3},
    "MAR": {("BR-116", "RJ"): 37.041, ("BR-116", "MG"): 23.395, ("BR-465", "RJ"): 7.920, ("BR-493", "RJ"): 17.161},
    "DIA": {("BR-116", "RJ"): 5, ("BR-116", "MG"): 5},
    "PIN": {("BR-116", "RJ"): 4, ("BR-116", "MG"): 3, ("BR-493", "RJ"): 6},
    "TRB": {("BR-116", "MG"): 3, ("BR-493", "RJ"): 1},
    "TRV": {("BR-493", "RJ"): 1},
    "RTU": {("BR-116", "RJ"): 6, ("BR-116", "MG"): 7, ("BR-465", "RJ"): 1, ("BR-493", "RJ"): 1},
    "RTX": {("BR-116", "RJ"): 19, ("BR-116", "MG"): 62, ("BR-493", "RJ"): 4},
    "ROT": {("BR-116", "MG"): 9},
    "ROA": {("BR-116", "RJ"): 3, ("BR-465", "RJ"): 7},
    "ALC": {("BR-116", "RJ"): 5, ("BR-465", "RJ"): 1, ("BR-493", "RJ"): 1},
    "ACE": {("BR-116", "RJ"): 357, ("BR-116", "MG"): 275, ("BR-465", "RJ"): 49, ("BR-493", "RJ"): 94},
    "BRU": {("BR-116", "RJ"): 3.332, ("BR-116", "MG"): 0.852, ("BR-465", "RJ"): 0.525, ("BR-493", "RJ"): 0.268},
    "CPP": {("BR-116", "RJ"): 13, ("BR-116", "MG"): 9, ("BR-465", "RJ"): 1, ("BR-493", "RJ"): 6},
    "FAU": {("BR-116", "RJ"): 15, ("BR-116", "MG"): 38, ("BR-465", "RJ"): 1, ("BR-493", "RJ"): 3},
    "PAS": {("BR-116", "RJ"): 49, ("BR-116", "MG"): 21, ("BR-465", "RJ"): 2, ("BR-493", "RJ"): 3},
    "ONI": {("BR-116", "RJ"): 206, ("BR-116", "MG"): 144, ("BR-465", "RJ"): 40, ("BR-493", "RJ"): 72},
    "CIC": {("BR-116", "RJ"): 1.630},
    "DIV": {("BR-116", "RJ"): 0.270},
}
# O Resumo (p.88) traz 3 passagens inferiores no MG e 3 trombetas no MG; a tabela de retornos X do MG da p.71-73
# é a mais longa: o script confere tudo e imprime as diferenças.

# A tabela de faixas adicionais da BR-116/RJ (p.54-55) soma 125,693 km (conferido linha a linha); o Resumo (p.88) traz
# 124,693 km, 1,000 km a menos: erro de soma do próprio PER. Vale a tabela; a divergência fica registrada.
DIVERGENCIAS_CONHECIDAS = {("FAD", "BR-116", "RJ"): 125.693}

num = lambda s: float(s.replace(".", "").replace(",", ".")) if s.count(",") and s.count(".") else float(s.replace(",", "."))
R_BR = r"(BR-\d{3})(\*{0,2}) (RJ|MG)"
R_FAIXA = re.compile(R_BR + r" (\d+,\d+) (\d+,\d+) (\d+,\d+) .*?(?:(Crescente|Decrescente) )?(\d)º$")
R_PONTO = re.compile(R_BR + r" (\d+,\d+) .*?(?:(Vão \d+ m) )?(\d)º$")
R_BARR = re.compile(R_BR + r" (\d+,\d+) (\d+,\d+) .* (\d) (\d)º$")
R_ESC = re.compile(r"^4-116-RJ-8 RJ (\d+,\d+) (\d+,\d+) .* Áreas de Escape (\d)º$")
R_SEG = re.compile(r"^SEGMENTO (\d+'?) - (RJ|MG) (BR-\d{3}) (RJ|MG) (\d+) (\d)?[º-]")
R_SEC = re.compile(r"^3\.2\.(1|2|3) ")
R_LET = re.compile(r"^([A-S])\. ")

linhas = []
contadores = defaultdict(int)


def add(sigla, rod, uf, pag, ki=None, kf=None, ext=None, qtd=1, un="un", sent="", ano="", obs="", extra=""):
    _, tipo, nome = next(v for v in SECOES.values() if v[0] == sigla)
    contadores[sigla] += 1
    sec = next(k for k, v in SECOES.items() if v[0] == sigla)
    desc = f"{nome}{(' ' + extra) if extra else ''} - {rod}/{uf}"
    if ki is not None:
        desc += f" - km {ki:.3f}".replace(".", ",") + (f" ao km {kf:.3f}".replace(".", ",") if kf is not None else "")
    if sent:
        desc += f" ({sent.lower()})"
    linhas.append(dict(
        per_id=f"ERM-PER-{sigla}-{contadores[sigla]:02d}", secao_per=f"3.2.{sec[0]}.{sec[1]}", bloco="obrigatoria",
        tipo_intervencao=tipo, descricao=desc, rodovia=rod, uf=uf,
        km_inicial="" if ki is None else round(ki, 3), km_final="" if kf is None else round(kf, 3),
        extensao_km="" if ext is None else round(ext, 3), quantidade=qtd, unidade=un, sentido=sent, ano_concessao=ano,
        observacao_per=obs, pagina=pag, documento_fonte=DOC))


def ler_paginas():
    inv = pd.read_csv(PROJETO / "dados" / "pesquisa_financeiro" / "inventario.csv", encoding="utf-8-sig")
    sel = inv[(inv["concessao"] == "ecoriominas") & (inv["titulo"] == "PER Atualizado")]
    assert len(sel) == 1, "PER Atualizado da Rio Minas não encontrado no inventario.csv"
    pdf = PROJETO / sel.iloc[0]["arquivo_local"]
    with pdfplumber.open(longo(pdf)) as f:
        return {p: (f.pages[p - 1].extract_text() or "") for p in range(PAG_INI, PAG_FIM + 1)}


# Alças de conexão (p.74-75): o texto da coluna "Complemento (Tipo)" quebra em duas linhas, então vai à mão
ALCAS = [("BR-116", "RJ", 161.8, "OAE expressa (Av. Brasil - BR-116), marginal", 4, 74, ""),
         ("BR-116", "RJ", 161.8, "OAE expressa (Av. Brasil - BR-116), expressa", 4, 74, ""),
         ("BR-116", "RJ", 166.122, "Melhoria de raio de curva no acesso à BR-116 Dutra/RJ", 4, 74,
          "(*) sentido RJ, aumento do raio de curva para acesso à BR-116 sentido Rio de Janeiro (Rua Trevo)"),
         ("BR-116", "RJ", 165.0, "OAE expressa (BR-116 expressa - Linha Vermelha)", 4, 74, ""),
         ("BR-116", "RJ", 165.0, "OAE expressa (Linha Vermelha - BR-116 expressa)", 4, 74, ""),
         ("BR-465", "RJ", 2.5, "Alça em mão dupla entre a BR-465 e a BR-493", 8, 75,
          "(*) a alça deverá ser construída ao sul do entroncamento BR-465 x BR-493 (FLONA Mário Xavier)"),
         ("BR-493", "RJ", 0.0, "BR-493 x BR-101", 4, 75, "")]

paginas = ler_paginas()
tmp = []  # (ordem_rod, ordem_aparicao, sigla, kwargs)
sec, let = "1", None  # a p.52 já está dentro de 3.2.1 (o título está na p.51)
ordem = 0
for pag in range(PAG_INI, PAG_FIM):  # a p.88 é o Resumo
    for ln in paginas[pag].splitlines():
        ln = ln.strip()
        m = R_SEC.match(ln)
        if m:
            sec, let = m.group(1), None
            continue
        m = R_LET.match(ln)
        if m and sec in ("1", "2"):
            let = m.group(1)
            continue
        if sec not in ("1", "2") or let is None or (sec, let) not in SECOES:
            continue
        sigla = SECOES[(sec, let)][0]
        if sigla == "ALC":
            continue
        ordem += 1
        if sigla == "ESC":
            m = R_ESC.match(ln)
            if m:
                tmp.append((("BR-116", "RJ"), ordem, sigla, dict(rod="BR-116", uf="RJ", pag=pag, ki=num(m[1]),
                            ext=num(m[2]), qtd=1, ano=m[3] + "º", obs="extensão mínima de 0,18 km por área")))
            continue
        if sigla in ("ACE", "ONI"):
            m = R_SEG.match(ln)
            if m:
                seg, rod, uf, qtd = m[1], m[3], m[4], int(m[5])
                if qtd == 0:
                    continue  # segmento sem previsão (ano "-")
                tmp.append(((rod, uf), ordem, sigla, dict(rod=rod, uf=uf, pag=pag, qtd=qtd, ano=(m[6] or "") + "º",
                            extra=f"(segmento homogêneo {seg})",
                            obs=f"PER dá só a quantidade por segmento homogêneo (SEGMENTO {seg} - {uf} {rod}), sem km")))
            continue
        if sigla in ("DUP", "FAD", "MAR", "CIC", "DIV"):
            m = R_FAIXA.match(ln)
            if not m:
                continue
            rod, ast, uf = m[1], m[2], m[3]
            obs = {"*": "(*) solução projetada: acostamento usado como faixa de rolamento (3,60 m)",
                   "**": "(**) duas faixas adicionais por sentido"}.get(ast, "")
            tmp.append(((rod, uf), ordem, sigla, dict(rod=rod, uf=uf, pag=pag, ki=num(m[4]), kf=num(m[5]),
                        ext=num(m[6]), qtd=num(m[6]), un="km", sent=m[7] or "", ano=m[8] + "º", obs=obs)))
            continue
        if sigla == "BRU":
            m = R_BARR.match(ln)
            if m:
                tmp.append(((m[1], m[3]), ordem, sigla, dict(rod=m[1], uf=m[3], pag=pag, ki=num(m[4]), ext=num(m[5]),
                            qtd=num(m[5]), un="km", ano=m[7] + "º", obs=f"altura {m[6]} m")))
            continue
        m = R_PONTO.match(ln)
        if m:
            obs = {"RTU": "*Retorno sob o dispositivo do km 107,5 para atender à RJ-122" if m[4].startswith("107,5") else ""}.get(sigla, "")
            tmp.append(((m[1], m[3]), ordem, sigla, dict(rod=m[1], uf=m[3], pag=pag, ki=num(m[4]), ano=m[6] + "º",
                        extra=f"({m[5]})" if m[5] else "", obs=obs)))

for rod, uf, km, tipo, ano, pag, obs in ALCAS:
    tmp.append(((rod, uf), 0, "ALC", dict(rod=rod, uf=uf, pag=pag, ki=km, ano=f"{ano}º", extra=f"({tipo})", obs=obs)))

ordem_sigla = [v[0] for v in SECOES.values()]
tmp.sort(key=lambda t: (ordem_sigla.index(t[2]), ORDEM_ROD[t[0]], t[1]))
for _, _, sigla, kw in tmp:
    add(sigla, **kw)

with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, COLS, delimiter=";")
    w.writeheader()
    w.writerows(linhas)

# --- conferência com o Resumo (p.88)
somas = defaultdict(float)
for l in linhas:
    sigla = l["per_id"].split("-")[2]
    somas[(sigla, l["rodovia"], l["uf"])] += float(l["quantidade"])
erros = []
for sigla, d in RESUMO.items():
    for (rod, uf), esperado in d.items():
        obtido = somas.get((sigla, rod, uf), 0.0)
        ok = abs(obtido - esperado) < 0.0015
        if not ok and (sigla, rod, uf) in DIVERGENCIAS_CONHECIDAS and abs(obtido - DIVERGENCIAS_CONHECIDAS[(sigla, rod, uf)]) < 0.0015:
            print(f"  aviso: {sigla} {rod}/{uf}: Resumo {esperado} x tabela {round(obtido, 3)} (divergência conhecida do PER)")
            ok = True
        if not ok:
            erros.append(f"{sigla} {rod}/{uf}: PER Resumo {esperado} x lido {round(obtido, 3)}")
    for (s, rod, uf), v in somas.items():
        if s == sigla and (rod, uf) not in d:
            erros.append(f"{sigla} {rod}/{uf}: lido {round(v, 3)}, ausente do Resumo")

print(f"{len(linhas)} linhas em {SAIDA}")
for sigla, n in Counter(l["per_id"].split("-")[2] for l in linhas).items():
    print(f"  {sigla}: {n} linhas, quantidade total {round(sum(float(l['quantidade']) for l in linhas if l['per_id'].split('-')[2] == sigla), 3)}")
if erros:
    print("DIFERENÇAS EM RELAÇÃO AO RESUMO DA p.88:")
    for e in erros:
        print("  ", e)
    sys.exit(1)
print("Conferência com o Resumo da p.88: OK")
