"""
Caminhos das tabelas geradas pelos scripts de per_obras/ (tudo em dados/, fora do git).

    dados/per_obras/intermediario/        extrações do modelo (modelo_item4_<conc>_anual.csv, _grupos.csv)
    dados/finais/<tabela>/<prefixo>_<conc>.<ext>
        cadastro_obras/        cadastro_obras_<conc>.csv e .xlsx
        financeiro_mensal/     fin_mensal_<conc>.csv
        financeiro_acumulado/  fin_acumulado_<conc>.csv
        financeiro_resumo/     fin_resumo_<conc>.csv
        xlsx/                  fin_<conc>.xlsx (planilha combinada da concessão)

<conc> = eco050, cerrado, riominas. Exemplo: caminho_final('cadastro_obras', 'eco050', 'csv').
"""
from pathlib import Path

PROJETO = Path(__file__).resolve().parent.parent
DADOS = PROJETO / "dados"
INTERMEDIARIO = DADOS / "per_obras" / "intermediario"
FINAIS = DADOS / "finais"
CONSOLIDADO = DADOS / "acompanhamento_obras" / "consolidado"

CONCESSOES = ("eco050", "cerrado", "riominas")
PREFIXO = {
    "cadastro_obras": "cadastro_obras",
    "financeiro_mensal": "fin_mensal",
    "financeiro_acumulado": "fin_acumulado",
    "financeiro_resumo": "fin_resumo",
    "xlsx": "fin",
}


def caminho_final(tabela, conc, ext="csv"):
    """dados/finais/<tabela>/<prefixo>_<conc>.<ext>; cria a pasta."""
    if tabela not in PREFIXO:
        raise ValueError(f"tabela desconhecida: {tabela} (use {sorted(PREFIXO)})")
    if conc not in CONCESSOES:
        raise ValueError(f"concessão desconhecida: {conc}")
    pasta = FINAIS / tabela
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / f"{PREFIXO[tabela]}_{conc}.{ext}"


def caminho_modelo(conc, parte):
    """dados/per_obras/intermediario/modelo_item4_<conc>_<parte>.csv (parte = 'anual' ou 'grupos'); cria a pasta."""
    if parte not in ("anual", "grupos"):
        raise ValueError(parte)
    INTERMEDIARIO.mkdir(parents=True, exist_ok=True)
    return INTERMEDIARIO / f"modelo_item4_{conc}_{parte}.csv"
