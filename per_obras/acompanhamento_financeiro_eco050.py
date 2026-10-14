"""
Acompanhamento financeiro da ECO050 (id 104, EMG): cruza o cadastro de obras (valor do item 4 rateado, ou valor do
retorno Extra-PER) com o % físico do acompanhamento mensal da ANTT. A lógica está em per_obras/financeiro_comum.py.

Uso (depois de per_obras/montar_cadastro_eco050.py):
    python per_obras/acompanhamento_financeiro_eco050.py

Insumos (dados/, gerados):
    finais/cadastro_obras/cadastro_obras_eco050.csv, per_obras/intermediario/modelo_item4_eco050_grupos.csv (só o 4.3)
    acompanhamento_obras/consolidado/obras_por_snapshot.csv, serie_mensal.csv
    valores_obras/obras_valores.csv (só os 3 retornos Extra-PER)
Saídas (dados/finais/<tabela>/, caminhos em per_obras/caminhos.py; CSV ';' UTF-8 BOM): fin_mensal_eco050,
fin_acumulado_eco050, fin_resumo_eco050 e xlsx/fin_eco050.xlsx.
Regras em documentacao/cadastro_obras.md; colunas em per_obras/dicionario_colunas.md.

Os valores NÃO são corrigidos por índice: ficam nominais, com data-base e tipo. Nunca se somam tipos diferentes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from financeiro_comum import Config, gerar  # noqa: E402

PRIORIDADE_EXTRA = ["aprovado_revisao", "inicial_inclusao"]


def valor_extra(oid, val):
    """Valor de obra fora do item 4 (retornos Extra-PER) em valores_obras/obras_valores.csv."""
    v = val[val.obra_id == oid]
    for t in PRIORIDADE_EXTRA:
        x = v[v.tipo_valor == t]
        if t == "aprovado_revisao":      # a obra, sem a parcela de projetos
            x = x[x.valor_id.str.endswith("-OBRA")]
        if len(x):
            assert len(x) == 1, f"{oid}: mais de um valor {t}"
            r = x.iloc[0]
            return float(r.valor), t, str(r.data_base), r.fonte_id, f"{r.valor_id}: {r.localizacao}"
    return None


CFG = Config(
    conc="eco050", conc_fonte="eco050", id_emp=104, total_item4=1145919554.57, tipo_item4="inicial_leilao",
    db_item4="não informada (contrato: mai/2012)",
    passo0_ids=("EMG-0003", "EMG-0007", "EMG-0013", "EMG-0019", "EMG-0014"),
    nao_rateado=lambda grp: float(grp.loc[grp["item"] == "4.3", "valor_bloco"].sum()),
    coluna_nao_rateado="valor_projetos_4_3_nao_rateado", rotulo_nao_rateado="4.3 projetos (não rateado)",
    valor_extra=valor_extra,
)

if __name__ == "__main__":
    gerar(CFG)
