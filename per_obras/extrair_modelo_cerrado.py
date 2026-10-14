"""
Extrai o item 4 (Obras de ampliação da capacidade e outras melhorias) da aba PER do modelo econômico-financeiro
do leilão da Ecovias do Cerrado (fonte_id ecc_leilao_modelo) e grava os valores de cada subitem por ano de concessão.

Uso:
    python per_obras/extrair_modelo_cerrado.py

Fonte: Modelo Econômico-Financeiro - ECOVIAS DO CERRADO.xlsb (dentro de modelo-economico-financeiro-ecovias-do-cerrado.zip,
edital e anexos). O script procura o .xlsb em dados/valores_obras/fontes/ecc_leilao_modelo/extraido/ (baixado por
valores_obras/organizar.py) e, se não houver, extrai do ZIP já baixado em dados/pesquisa_financeiro/. Confere, célula a
célula, as linhas 41-46 com a cópia REV8 do mesmo modelo (BR_364_365_MODELO_ECONÔMICO_FINANCEIRO_REV8.xlsb, dentro de
modelagem-financeira-planilhas.zip, fonte ecc_evtea_modelagem).

Aba PER: linha 5 "DATA-BASE DOS EVTEs: julho/2016"; linha 8 = ano de concessão; coluna E = total; colunas F..AI = anos
1..30 (F = ano 1, G = ano 2, ..., AI = ano 30); coluna AJ = soma de conferência. Linha 41 = 4.0 (subtotal), linhas 42-46
= 4.1 a 4.5 (folhas, coluna B = 'INV'). Diferente da ECO050, o ano 1 é uma coluna só.

Saída em dados/per_obras/intermediario/ (caminhos em per_obras/caminhos.py):
    modelo_item4_cerrado_anual.csv    1 linha por item (4.0 a 4.5) x ano de concessão (1..30)
    modelo_item4_cerrado_grupos.csv   1 linha por folha x bloco (valor do grupo usado no rateio)
Bloco (rótulo do grupo de rateio): 4.1 obrigatoria, 4.2 condicionada (nome do subitem no modelo: "obras condicionadas
ao volume de tráfego"), 4.3 edificacoes_operacionais, 4.4 desapropriacoes (zero), 4.5 complementacao_dnit.
"""
import sys
import warnings
import zipfile
from pathlib import Path

import pandas as pd
from pyxlsb import open_workbook

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI.parent
sys.path.insert(0, str(PROJETO / "acompanhamento_obras"))
sys.path.insert(0, str(AQUI))
from caminhos import caminho_modelo  # noqa: E402
from portal_antt import longo  # noqa: E402

warnings.filterwarnings("ignore")

FONTE_ID = "ecc_leilao_modelo"
PASTA = PROJETO / "dados" / "valores_obras" / "fontes" / FONTE_ID / "extraido"
ZIP_PESQUISA = (PROJETO / "dados" / "pesquisa_financeiro" / "ecovias-do-cerrado" / "processo-de-licitacao"
                / "edital-e-anexos" / "modelo-economico-financeiro-ecovias-do-cerrado.zip")
REV8 = (PROJETO / "dados" / "valores_obras" / "fontes" / "ecc_evtea_modelagem" / "extraido"
        / "BR_364_365_MODELO_ECONÔMICO_FINANCEIRO_REV8.xlsb")
DATA_BASE = "2016-07"
TOTAL_ITEM4 = 717702925.02
L_INI, L_FIM = 41, 46          # linhas (1-based) da aba PER
COL_TOTAL, COL_ANO1, COL_AJ = 4, 5, 35  # índices 0-based: E, F (ano 1), AJ
BLOCO = {"4.1": "obrigatoria", "4.2": "condicionada", "4.3": "edificacoes_operacionais", "4.4": "desapropriacoes",
         "4.5": "complementacao_dnit"}


def letra(c0):
    c, s = c0 + 1, ""
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


def arquivo_modelo():
    achados = sorted(PASTA.glob("*.xlsb")) if PASTA.exists() else []
    if achados:
        return achados[0]
    if not Path(longo(ZIP_PESQUISA)).exists():
        sys.exit(f"Modelo não encontrado: rode valores_obras/organizar.py (baixa {FONTE_ID}) ou baixe {ZIP_PESQUISA}")
    PASTA.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(longo(ZIP_PESQUISA)) as z:
        membro = [n for n in z.namelist() if n.lower().endswith(".xlsb")]
        assert len(membro) == 1, membro
        destino = PASTA / "modelo-economico-financeiro-ecovias-do-cerrado.xlsb"
        destino.write_bytes(z.read(membro[0]))
    print(f"Extraído do ZIP da pesquisa: {destino}")
    return destino


def ler_linhas(arq):
    """{linha (1-based): [valores por coluna 0-based]} das linhas 1..L_FIM da aba PER."""
    out = {}
    with open_workbook(longo(arq)) as wb, wb.get_sheet("PER") as sh:
        for k, row in enumerate(sh.rows(), 1):
            if k > L_FIM:
                break
            linha = [None] * 40
            for c in row:
                if c.c < 40:
                    linha[c.c] = c.v
            out[k] = linha
    return out


def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def main():
    arq = arquivo_modelo()
    L = ler_linhas(arq)
    db_txt = str(L[5][3])
    assert "julho/2016" in db_txt, db_txt
    anos_cab = [int(num(L[8][COL_ANO1 + a])) for a in range(30)]
    assert anos_cab == list(range(1, 31)), anos_cab

    anual, grupos, resumo = [], [], []
    for r in range(L_INI, L_FIM + 1):
        ln = L[r]
        folha = ln[1] == "INV"
        item = "4.0" if r == L_INI else str(ln[2]).strip()
        desc = str(ln[3]).strip()
        for a in range(1, 31):
            c = COL_ANO1 + a - 1
            anual.append(dict(item=item, descricao=desc, nivel="folha" if folha else "subtotal", ano_concessao=a,
                              celula=f"PER!{letra(c)}{r}", fonte_id=FONTE_ID, data_base=DATA_BASE, linha_planilha=r,
                              valor=num(ln[c]), bloco=BLOCO.get(item, ""), parcela=""))
        soma = sum(num(ln[COL_ANO1 + a]) for a in range(30))
        resumo.append((r, item, folha, num(ln[COL_TOTAL]), soma, num(ln[COL_AJ])))
        if folha:
            anos = [a for a in range(1, 31) if abs(num(ln[COL_ANO1 + a - 1])) > 0]
            grupos.append(dict(linha_planilha=r, item=item, descricao=desc, bloco=BLOCO[item], valor_bloco=soma,
                               anos=",".join(map(str, anos)), n_celulas=30, soma_folha=soma, fonte_id=FONTE_ID,
                               data_base=DATA_BASE, celula_total=f"PER!E{r}"))
    df, g = pd.DataFrame(anual), pd.DataFrame(grupos)
    df.to_csv(caminho_modelo("cerrado", "anual"), sep=";", index=False, encoding="utf-8-sig", decimal=".")
    g.to_csv(caminho_modelo("cerrado", "grupos"), sep=";", index=False, encoding="utf-8-sig", decimal=".")

    # ---- conferências
    TOL = 0.01
    print(f"Modelo: {arq.name} | {db_txt.strip()} (PER!D5)")
    tot = next(x for x in resumo if x[0] == L_INI)
    print(f"4.0 (E{L_INI}) = {tot[3]:,.2f} (esperado {TOTAL_ITEM4:,.2f}): {'ok' if abs(tot[3] - TOTAL_ITEM4) < TOL else 'DIVERGENTE'}")
    folhas = [x for x in resumo if x[2]]
    sf = sum(x[3] for x in folhas)
    print(f"Soma das folhas 4.1-4.5 = {sf:,.2f} x E41: {'ok' if abs(sf - tot[3]) < TOL else 'DIVERGENTE'}")
    for r, item, _, e, s, aj in resumo:
        print(f"  L{r} {item}: E={e:,.2f} soma anos={s:,.2f} AJ={aj:,.2f} "
              f"{'ok' if abs(e - s) < TOL and abs(e - aj) < TOL else 'DIVERGENTE'}")
    print("Anos com valor por subitem: " + "; ".join(f"{x.item}: {x.anos or '-'}" for x in g.itertuples()))
    # ---- cópia REV8 (modelagem-financeira-planilhas.zip)
    if Path(longo(REV8)).exists():
        L8 = ler_linhas(REV8)
        dif = [(r, letra(c)) for r in range(L_INI, L_FIM + 1) for c in range(COL_TOTAL, COL_AJ + 1)
               if abs(num(L[r][c]) - num(L8[r][c])) > 1e-6]
        print(f"Cópia REV8 ({REV8.name}): linhas {L_INI}-{L_FIM}, colunas E-AJ: "
              + ("idênticas" if not dif else f"{len(dif)} células diferentes: {dif[:10]}"))
    else:
        print(f"Cópia REV8 não encontrada ({REV8}); rode valores_obras/organizar.py para baixá-la")
    print(f"Arquivos em {caminho_modelo('cerrado', 'anual').parent}")
    if abs(tot[3] - TOTAL_ITEM4) >= TOL or abs(sf - tot[3]) >= TOL:
        sys.exit("Conferência do item 4 DIVERGENTE")


if __name__ == "__main__":
    main()
