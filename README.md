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
valores_obras/                valores financeiros (Capex, orçamentos, estimativas) ligados às obras
  organizar.py                extrai das planilhas da ANTT, liga às obras e gera as tabelas
  fontes.py                   documentos-fonte (link)
  valores_manuais.csv         valores transcritos de PDFs (com página)
  totais_manuais.csv          totais do empreendimento transcritos de PDFs/páginas
  correspondencias_manuais.csv  ligações obra x valor feitas à mão, com justificativa
per_obras/                    cadastro de todas as obras do PER, com valor do item 4 rateado (por enquanto só ECO050)
  gerar_per_eco050_manuais.py   gera per_eco050_manuais.csv (obras do PER original, com página)
  extrair_modelo_eco050.py      item 4 da aba "PER" do modelo econômico-financeiro, por ano e bloco
  montar_cadastro_eco050.py     cadastro: PER + alterações + acompanhamento + valor rateado
  alteracoes_eco050.md/.csv     o que mudou desde o PER original (km, realocações, inclusões), com fonte
  dicionario_colunas.md         dicionário das colunas das tabelas desta pasta
documentacao/
  acompanhamento_obras.md     regras, tabelas, colunas, resultados, limitações
  valores_obras.md            hierarquia dos valores, tipos de valor, tabelas, resultados
  pesquisa_financeiro_antt.md onde estão os dados financeiros no portal da ANTT
  checkpoint_financeiro.md    resumo do que existe de valores por empreendimento
dados/                        (fora do git) gerado pelos scripts
  acompanhamento_obras/
    brutos/                   arquivos do portal por concessão e ano
    consolidado/              tabelas CSV + consolidado.xlsx
  valores_obras/              fontes baixadas + tabelas de valores + valores_obras.xlsx
  pesquisa_financeiro/        documentos baixados pelo agente de pesquisa (mesmas pastas do portal) + inventario.csv
```

Novas fontes (contratos, valores) entram como novas pastas ao lado de `acompanhamento_obras/`, tanto no código quanto em `dados/`.

## Como rodar

```
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python acompanhamento_obras/baixar.py
python acompanhamento_obras/consolidar.py
python valores_obras/organizar.py
python per_obras/extrair_modelo_eco050.py
python per_obras/montar_cadastro_eco050.py
```

O pandas está fixado em 2.3.2: com o pandas 3.0 os scripts quebram por causa da mudança no tipo de string.

`consolidar.py` precisa rodar antes de `organizar.py`, porque gera a `lista_obras` em que os valores são ligados.

Detalhes:
- [`documentacao/acompanhamento_obras.md`](documentacao/acompanhamento_obras.md): avanço físico;
- [`documentacao/valores_obras.md`](documentacao/valores_obras.md): valores financeiros;
- [`documentacao/cadastro_obras.md`](documentacao/cadastro_obras.md): cadastro de obras da ECO050 e rateio do item 4;
- [`documentacao/checkpoint_financeiro.md`](documentacao/checkpoint_financeiro.md): situação atual e próximos passos.
