# federalemps_collector

Coleta de dados públicos para acompanhar a evolução dos empreendimentos do **PELT-MG**.

## Empreendimentos acompanhados

A relação completa entre o PELT e o que foi encontrado em dados públicos está em [`emps_pelt.md`](emps_pelt.md). No momento só 3 empreendimentos têm acompanhamento de obras público (ANTT). Eles estão configurados em [`empreendimentos.json`](empreendimentos.json):

| id_empreendimento | Empreendimento | Fonte |
|---|---|---|
| 105 | Ecovias Rio Minas | ANTT, `ecoriominas` |
| 103 | Ecovias do Cerrado | ANTT, `ecovias-do-cerrado` |
| 104 | ECO050 (Ecovias Minas Goiás) | ANTT, `eco050` |

Outros órgãos pesquisados (DNIT, ANAC, CODEBA, MT) não publicam acompanhamento de obras equivalente ao da ANTT.

## Estrutura

```
empreendimentos.json          empreendimentos do escopo (id PELT, slug e URL na ANTT, prefixo do obra_id)
acompanhamento_obras/         % de avanço físico das obras (ANTT)
  portal_antt.py              acesso ao portal e caminhos
  baixar.py                   baixa o histórico completo (incremental)
  consolidar.py               gera as tabelas consolidadas e os marcos por obra
documentacao/
  acompanhamento_obras.md     regras, tabelas, colunas, resultados, limitações
dados/                        (fora do git) gerado pelos scripts
  acompanhamento_obras/
    brutos/                   arquivos do portal por concessão e ano
    consolidado/              tabelas CSV + consolidado.xlsx
```

Novas fontes (contratos, valores) entram como novas pastas ao lado de `acompanhamento_obras/`, tanto no código quanto em `dados/`.

## Como rodar

```
pip install requests pandas openpyxl
python acompanhamento_obras/baixar.py
python acompanhamento_obras/consolidar.py
```

Detalhes em [`documentacao/acompanhamento_obras.md`](documentacao/acompanhamento_obras.md).
