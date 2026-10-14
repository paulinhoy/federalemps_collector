"""
Acompanhamento financeiro da Ecovias do Cerrado (id 103, ECC): cruza o cadastro de obras (valor do item 4 rateado pelo
custo do estudo) com o % físico do acompanhamento mensal da ANTT. A lógica está em per_obras/financeiro_comum.py
(a mesma da ECO050).

Uso (depois de per_obras/montar_cadastro_cerrado.py):
    python per_obras/acompanhamento_financeiro_cerrado.py

Insumos (dados/, gerados): finais/cadastro_obras/cadastro_obras_cerrado.csv,
    per_obras/intermediario/modelo_item4_cerrado_grupos.csv (4.4, não rateado e igual a zero),
    acompanhamento_obras/consolidado/obras_por_snapshot.csv, serie_mensal.csv
Saídas (dados/finais/<tabela>/): fin_mensal_cerrado, fin_acumulado_cerrado, fin_resumo_cerrado e xlsx/fin_cerrado.xlsx.

Diferenças em relação à ECO050: todo o item 4 é rateado (4.4 desapropriações = 0 é a única parte não rateada);
linhas do cadastro sem valor (iluminação, obras condicionadas do 3.2.3, obras do acompanhamento fora do PER) entram em
fin_mensal com valor vazio e não entram no resumo; situação `sem_acompanhamento` (obra do PER sem série) conta como
0% executada em fin_acumulado (tipo_registro `sem_serie_sem_informacao`).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from financeiro_comum import Config, gerar  # noqa: E402

CFG = Config(
    conc="cerrado", conc_fonte="ecovias-do-cerrado", id_emp=103, total_item4=717702925.02, tipo_item4="inicial_leilao",
    db_item4="2016-07",
    passo0_ids=("ECC-0093", "ECC-0095", "ECC-0096", "ECC-0097", "ECC-0002"),
    nao_rateado=lambda grp: float(grp.loc[grp["item"] == "4.4", "valor_bloco"].astype(float).sum()),
    coluna_nao_rateado="valor_nao_rateado_4_4", rotulo_nao_rateado="4.4 desapropriações (não rateado, zero)",
    valor_extra=None, avisar_sem_valor=False, data_base_da_linha=True,
)

if __name__ == "__main__":
    gerar(CFG)
