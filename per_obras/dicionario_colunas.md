# Dicionário de dados: cadastro de obras (ECO050 e Ecovias do Cerrado)

Primeiro a ECO050 (id 104, EMG; tabelas 1 a 12); a Ecovias do Cerrado (id 103, ECC; tabelas C1 a C9) está no fim. Caminhos das tabelas geradas: `per_obras/caminhos.py`.

# ECO050 (id 104, EMG)

Convenções gerais: CSVs com `;` e UTF-8 com BOM. Datas em ISO, às vezes só `AAAA` ou `AAAA-MM` (precisão da fonte). Valores em R$ (reais, sem separador de milhar). Frações de 0 a 1. Km em número decimal com ponto (nos insumos copiados de planilhas, alguns campos trazem vírgula e texto). **Data-base dos valores do modelo: não informada na planilha; o contrato é de mai/2012.** Contexto e regras de rateio: `documentacao/cadastro_obras.md`.

## Índice e fluxo de geração

| # | Tabela | Tipo | Gerada por | Usada por |
|---|---|---|---|---|
| 1 | `per_obras/per_eco050_manuais.csv` | insumo | `gerar_per_eco050_manuais.py` | `montar_cadastro` |
| 2 | `per_obras/alteracoes_eco050.csv` | insumo (à mão) | compilação manual (histórico em `alteracoes_eco050.md`) | `montar_cadastro` |
| 3 | `per_obras/correspondencias_cadastro_eco050.csv` | insumo (à mão) | manual | `montar_cadastro` |
| 4 | `per_obras/obras_extra_per_eco050.csv` | insumo (à mão) | manual | `montar_cadastro` |
| 5 | `per_obras/marcos_liberacao_eco050.csv` | insumo (transcrito) | manual | `montar_cadastro` |
| 6 | `per_obras/cronograma_planejamento_anual_2026_eco050.csv` | insumo (transcrito) | manual | `montar_cadastro` |
| 7 | `dados/per_obras/intermediario/modelo_item4_eco050_anual.csv` | saída | `extrair_modelo_eco050.py` | conferências |
| 8 | `dados/per_obras/intermediario/modelo_item4_eco050_grupos.csv` | saída | `extrair_modelo_eco050.py` | `montar_cadastro` |
| 9 | `dados/finais/cadastro_obras/cadastro_obras_eco050.csv` (+ `.xlsx`) | saída final | `montar_cadastro_eco050.py` | carga no banco, ligação com o financeiro |
| 10 | `dados/finais/financeiro_mensal/fin_mensal_eco050.csv` | saída | `acompanhamento_financeiro_eco050.py` | análises mensais, correção por índice |
| 11 | `dados/finais/financeiro_acumulado/fin_acumulado_eco050.csv` | saída | `acompanhamento_financeiro_eco050.py` | obras sem série mensal |
| 12 | `dados/finais/financeiro_resumo/fin_resumo_eco050.csv` | saída | `acompanhamento_financeiro_eco050.py` | totais e conferência por mês |

Ordem: `baixar.py` → `consolidar.py` → `valores_obras/organizar.py` (baixa o modelo) → `per_obras/gerar_per_eco050_manuais.py` (só se o PER for retranscrito) → `per_obras/extrair_modelo_eco050.py` → `per_obras/montar_cadastro_eco050.py` (para com erro se o rateio não fechar) → `per_obras/acompanhamento_financeiro_eco050.py` (tabelas 10 a 12; gera também `dados/finais/xlsx/fin_eco050.xlsx`, uma aba por tabela; a lógica está em `financeiro_comum.py`). `dados/` é gerado e fica fora do git.

---

## 9. `cadastro_obras_eco050.csv` (tabela final)

1 linha por obra esperada na concessão, na versão mais atual (km corrigido): 89 linhas (86 com valor; 3 Extra-PER sem valor). Gerada por `montar_cadastro_eco050.py`; usada na carga do banco e na ligação com valores financeiros.

### Regras de uso

- **Obra dividida em n linhas:** `per_id_origem` é o `per_id` da obra no PER e `fracao_da_origem` é a parte dela que a linha representa. Hoje há 82 `per_id_origem` distintos nas 86 linhas; 4 deles têm mais de uma linha: EMG-PER-DUP-01 (Cristalina), EMG-PER-DUP-11 e EMG-PER-DUP-12 (Catalão) e EMG-PER-MAR-02 (marginal de Cristalina, Sul/Norte). `fracao_da_origem` só vem preenchida nas duplicações e na marginal ID-2 (18 linhas; 1.0 = obra inteira); nas demais, a linha é a obra inteira. Um valor dado "por obra do PER" deve ser repartido por `fracao_da_origem` ou agregado por `per_id_origem`. Não conte linhas como obras do PER sem olhar `per_id_origem`.
- **`peso` e `valor`:** `valor` é rateio do valor do grupo do modelo: `valor = valor_grupo_bloco × peso / soma_pesos_grupo`. Não é custo de obra nem valor realizado. Peso = 1 por unidade (`rateio_igual_por_unidade`) ou km da linha (`rateio_por_km`; nas marginais, o km atual).
- **Valores de tipos diferentes não se somam:** `valor` é só o previsto do modelo (EVTEA, item 4). Não somar com `inicial_leilao`, `inicial_inclusao`, `aprovado_revisao`, `estimativa_concessionaria` ou `realizado` de `valores_obras/`. Somar `valor` dentro do cadastro é válido (total das 86 linhas: R$ 1.091.351.956,74; com o 4.3, que não é rateado, fecha R$ 1.145.919.554,57).
- **`km_per_original` x `km_inicial`:** `km_per_original` é o km do PER original (texto `ini-fim`); `km_inicial`/`km_final` são o km atual, corrigido por aditivo/revisão. `km_inicial` vazio em obra sem local (estoque, "a definir") ou condicionada.
- **`prazo_contratual` x `data_termino_prevista`:** `prazo_contratual` é a meta do contrato/PER (2019-01-07, final da duplicação, só nas obrigatórias 3.2.1). `data_termino_prevista` é o planejamento anual (PA2026 Rev02), que muda e pode passar do contrato. Atraso se mede entre `data_conclusao_real` e `prazo_contratual`.
- **`a_confirmar`:** True em 7 linhas; a ligação ou o dado depende de conferência (passarelas 171/175, onde o 6º TA e o PA2025 divergem; retornos Extra-PER com UF divergente). Ver `observacao`.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| id_obra | texto | chave da linha. `per_id`, com sufixo `-a`/`-b` se dividida; `EMG-EXT-<SIGLA>-nn` fora do PER | `EMG-PER-DUP-01-a`, `EMG-EXT-RNV-01` |
| id_empreendimento | inteiro | id PELT do empreendimento | 104 |
| nome | texto | descrição da obra | `Duplicação km 99,44-106,7 (segmento 050BGO0070)` |
| tipo_intervencao | categ. | tipo da obra | interconexao_diamante (19), duplicacao (16), interconexao_trombeta (10), melhoria_acesso (10), passarela (9), faixa_adicional (7), via_marginal (7), retorno_desnivel (5), retorno_nivel (3), interconexao_trevo (2), outro (1, retorno operacional do estoque) |
| bloco | categ. | grupo no PER/modelo | obrigatoria (67), manutencao_nivel_servico (12, estoque anos 6-30), condicionada (7, faixas adicionais), extra_per (3) |
| item_per | texto | seção do PER | 3.2.1.1, 3.2.1.2, 3.2.3.1, 3.2.3.3, `Extra PER - 3.2.1.2` |
| rodovia | texto | rodovia | BR-050 |
| uf | texto | UF; vazio se sem local | GO, MG, GO/MG |
| municipio | texto | município; vazio se não identificado | Cristalina, Catalão, Uberaba |
| km_inicial | km | km atual (início, ou ponto em obra pontual) | 95.7 |
| km_final | km | km atual final; vazio em obra pontual | 99.44 |
| extensao_km | km | extensão da linha; só obras lineares (30 linhas) | 3.74 |
| quantidade | número | quantidade, na `unidade` | 3.74; 1 |
| unidade | categ. | unidade de `quantidade` | km (30), un (59) |
| km_per_original | texto | trecho no PER original, `ini-fim` | `95.7-106.7` |
| data_inicio_prevista | data | início previsto, PA2026 Rev02 (AAAA ou AAAA-MM) | 2016-07 |
| data_termino_prevista | data | término previsto, PA2026 Rev02 | 2024-09 |
| fonte_datas_previstas | texto | linha(s) do PA2026 usadas | `PA2026 Rev02 L35` |
| prazo_contratual | data | meta do contrato/PER (ver regra) | 2019-01-07 |
| data_inicio_real | data | início executado (PA2026) | 2022-09 |
| data_conclusao_real | data | liberação ao tráfego (marcos, alteracoes ou PA2026); pode ser só ano | 2024-07-30; 2026 |
| fonte_datas_reais | texto | documento, página e marco usados | `Relatório mensal 12/2025 p.14,18 (...)` |
| situacao | categ. | estado atual | concluida (61), sem_local_definido (12), condicionada_nao_acionada (7), em_andamento (6), nao_iniciada (3) |
| fonte_situacao | categ. | de onde veio a `situacao`: com série no acompanhamento, o último mês da série principal (executado ≥ 0,99 = concluida; > 0 = em_andamento; 0 = nao_iniciada); sem série, a regra de PA2026/marcos | `acompanhamento 2026-04`, `PA2026/marcos` |
| item_modelo | texto | item do modelo (item 4); vazio nas Extra-PER | 4.1.1.1 passarelas (9), 4.1.1.2 marginais (7), 4.1.2.3.1 acessos (10), 4.1.2.3.2 interseções (37), 4.1.2.4.2 duplicação (16), 4.2.2 faixas adicionais (7) |
| valor_grupo_bloco | R$ | valor do grupo (item × bloco) no modelo, soma dos anos | 647559986.56 |
| soma_pesos_grupo | número | soma dos `peso` do grupo (km ou unidades) | 218.5 |
| peso | número | peso da linha no rateio | 3.74 |
| valor | R$ | valor rateado da linha (data-base mai/2012) | 11084093.13 |
| metodo_valor | categ. | critério do peso | rateio_por_km (30), rateio_igual_por_unidade (56) |
| data_base | texto | data-base do valor | `não informada (contrato: mai/2012)` |
| fonte_id | texto | fonte cadastrada em `valores_obras/fontes.py` | eco050_evtea_modelo |
| localizacao_valor | texto | células da aba PER do modelo | `PER!F80+G80 a K80 (linha 80, anos 1-5)` |
| per_id_origem | texto | `per_id` da obra no PER (ver regra); vazio nas Extra-PER | EMG-PER-DUP-01 |
| fracao_da_origem | fração 0-1 | parte da obra do PER que a linha cobre (ver regra) | 0.34, 0.66, 1.0 |
| origem | categ. | origem do dado | per_original (44), per_realocada (42, km mudou ou reconfigurada), inclusao_revisao (3) |
| fonte_alteracao | texto | documentos que justificam a mudança; vazio em per_original | `NT 145/2019 pp.16...` |
| obra_id_acompanhamento | texto | obras do acompanhamento ANTT (EMG-00nn), separadas por `\|`; a mesma pode repetir em 2 linhas | `EMG-0001\|EMG-0002` |
| id_sigicor | texto | ID SIGICOR no PA2026 | 13165 |
| a_confirmar | booleano | ver regra | False (82), True (7) |
| observacao | texto | notas e divergências entre fontes | texto livre |

---

## 7. `modelo_item4_eco050_anual.csv`

1 linha por item do item 4 (folha ou subtotal) × ano de concessão (1 a 30; ano 1 = colunas F+G da aba PER) × bloco: 1.773 linhas. Gerada por `extrair_modelo_eco050.py`; usada para conferir totais.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| item | texto | código do item; `sem_codigo_L<linha>` quando a planilha não traz código | 4.1.1.1, `sem_codigo_L49` |
| descricao | texto | descrição na planilha (vazia em parte das linhas) | Passarelas |
| nivel | categ. | folha (1.413) ou subtotal (360). Não somar folha com subtotal | folha, subtotal |
| ano_concessao | inteiro | ano da concessão | 1 a 30 |
| celula | texto | célula(s) de origem na aba PER | `PER!H44` |
| fonte_id | texto | fonte | eco050_evtea_modelo |
| data_base | texto | data-base | não informada (contrato: mai/2012) |
| linha_planilha | inteiro | linha na aba PER | 44 |
| valor | R$ | valor do item no ano | 145809101.30 |
| bloco | categ. | obrigatoria (anos 1-5), manutencao_nivel_servico (anos 6-30), condicionada (4.2.2 e excedente de projetos nos anos 20-22) | |
| parcela | texto | só nas 6 linhas do 4.3 nos anos 20-22: `valor-base dos anos 6-30` ou `excedente: projetos das faixas adicionais (4.2.2)`. A célula de origem é a mesma nas duas; o valor foi dividido entre os blocos | |

## 8. `modelo_item4_eco050_grupos.csv`

1 linha por folha × bloco do modelo: 85 linhas. Gerada por `extrair_modelo_eco050.py`; dela `montar_cadastro` tira `valor_grupo_bloco`.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| linha_planilha | inteiro | linha na aba PER | 48 |
| item | texto | código do item (ou `sem_codigo_L<n>`) | 4.1.1.1 |
| descricao | texto | descrição | Passarelas |
| bloco | categ. | grupo | obrigatoria, manutencao_nivel_servico, condicionada |
| valor_bloco | R$ | soma dos anos do bloco (valor do grupo) | 13802696.60 |
| anos | texto | faixa de anos somada | 1-5, 6-30, 1-30, 20-22 |
| n_celulas | inteiro | células somadas | 5, 25, 30, 3 |
| soma_folha | R$ | soma de conferência da folha, todos os anos (não é o valor do bloco) | 17746324.19 |
| fonte_id | texto | fonte | eco050_evtea_modelo |
| data_base | texto | data-base | não informada (contrato: mai/2012) |

---

## 1. `per_eco050_manuais.csv`

1 linha por obra prevista no PER original (`per_id`): 85 linhas, transcritas à mão do PDF (fonte `eco050_per_original`). Gerada por `gerar_per_eco050_manuais.py`; usada por `montar_cadastro`. Km aqui é o do PER original, sem correção.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| per_id | texto | chave da obra no PER | EMG-PER-DUP-01 |
| secao_per | categ. | seção do PER | 3.2.1.1, 3.2.1.2, 3.2.3.1, 3.2.3.3 |
| bloco | categ. | grupo | obrigatoria, condicionada, manutencao_nivel_servico |
| tipo_intervencao | categ. | tipo (grafia do PER, diferente do cadastro) | duplicacao, via_marginal, melhoria_acesso, interconexao_diamante, passarela, interconexao_trevo_completo, interconexao_trevo, interconexao_trombeta, retorno_em_desnivel, faixa_adicional, retorno_operacional |
| descricao | texto | descrição | Duplicação do segmento 050BGO0070 |
| pnv | texto | segmento do PNV (lineares) | 050BGO0070 |
| rodovia | texto | rodovia | BR-050 |
| uf | texto | UF | GO, MG, GO/MG |
| municipio | texto | município | Araguari |
| km_inicial / km_final | km | km no PER | 95.7 / 106.7 |
| extensao_km | km | extensão (lineares) | 11.0 |
| quantidade | número | quantidade, em `unidade` | 11.0; 1 |
| unidade | categ. | km, un | |
| sentido | categ. | sentido da marginal | Sul e Norte, Sul, Norte, Ambos |
| observacao_per | texto | observação do PER | metas anuais de pista dupla |
| pagina | texto | página do PDF | `32 e 84` |
| documento_fonte | texto | fonte_id | eco050_per_original |

## 2. `alteracoes_eco050.csv`

1 linha por alteração documentada de uma obra (realocação, prazo, reconfiguração, exclusão, inclusão): 99 linhas, compiladas à mão. Usada por `montar_cadastro` via `ref_alteracoes` para km atual e data de conclusão.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| obra_per_ref | texto | chave textual da obra (tipo, número, km, cidade); vazia em parte das inclusões | `Passarela 1 km 40,5 (Araguari/MG)` |
| tipo_alteracao | categ. | natureza | realocacao_km, prazo, reconfiguracao, exclusao, inclusao |
| tipo_intervencao | texto | tipo em texto livre | Passarela, Retorno em nível |
| descricao_atual | texto | descrição após a alteração | Passarela Uberaba |
| km_inicial_atual / km_final_atual | texto | km atual, com vírgula | 171 |
| data_inicio_prevista / data_termino_prevista | texto | datas previstas com anotação do documento | `2024-09 (Rev02)` |
| data_conclusao_real | texto | conclusão (dd/mm/aaaa, pode ter anotação de inferência) | 30/07/2024 |
| obra_id_acompanhamento | texto | obra do acompanhamento | EMG-0025 |
| documento / url | texto | documentos e links, separados por `\|` | 6º Termo Aditivo (22/04/2025) |
| localizacao | texto | página/linha em cada documento | `6º TA cl. 2.1 p.2; PA2025 L198` |
| observacao | texto | notas e divergências | |

## 3. `correspondencias_cadastro_eco050.csv`

1 linha por linha do cadastro que precisa de ligação manual: 59 linhas. Liga `id_obra` a PER, alterações e acompanhamento. Justificativa iniciada por `EXCLUIDA` tira a obra do PER do cadastro.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| id_obra | texto | id da linha no cadastro | EMG-PER-PAS-01 |
| per_id_origem | texto | obra do PER de origem; vazio em 3 linhas | EMG-PER-PAS-01 |
| fracao_da_origem | fração 0-1 | parte da obra do PER (obra dividida); só 2 linhas | 0.509091, 0.490909 |
| ref_alteracoes | texto | `obra_per_ref` em `alteracoes_eco050.csv` | |
| km_inicial / km_final | km | sobrescreve o km quando mudou (km_final vazio em todas) | 171 |
| uf / municipio | texto | sobrescreve quando mudou (7 linhas) | MG / Uberaba |
| obra_id_acompanhamento | texto | obras EMG-00nn, separadas por `\|` | EMG-0025 |
| a_confirmar | booleano | ligação não confirmada | False, True |
| justificativa | texto | motivo da ligação; obrigatório | |

## 4. `obras_extra_per_eco050.csv`

1 linha por obra fora do PER (por ora, 3 retornos em nível do acompanhamento). Entram no cadastro sem `item_modelo` e sem valor.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| id_obra | texto | chave | EMG-EXT-RNV-01 |
| nome | texto | descrição | Retorno em nível km 107,2 (Extra-PER) |
| tipo_intervencao / bloco / item_per | texto | iguais ao cadastro | retorno_nivel / extra_per / `Extra PER - 3.2.1.2` |
| rodovia, uf, municipio | texto | local | Cristalina, Ipameri, Delta |
| km_inicial / km_final | km | km (final vazio) | 107.2 |
| quantidade / unidade | número / texto | 1 / un | |
| origem | categ. | inclusao_revisao | |
| fonte / localizacao | texto | documento e página/linha | `NT GEGIR compl. 2023 p.11 Tab. 11` |
| a_confirmar | booleano | True nas 3 (UF divergente entre fontes) | True |
| observacao | texto | divergências | |

## 5. `marcos_liberacao_eco050.csv`

1 linha por marco de liberação ao tráfego do Relatório mensal 12/2025 (pp. 14-19): 132 linhas; inclui praças e BSOs, que não são obras do cadastro. Usada para `data_conclusao_real`.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| pagina_pdf | inteiro | página do relatório | 14 a 19 |
| descricao | texto | marco | Duplicação - inclusive adequação da pista existente |
| rodovia | texto | trecho | BR050/GO, BR050/MG, CT, CT - MG |
| km_inicial / km_final | km (texto, vírgula) | km do marco; final vazio se pontual | 99,4 / 110,7 |
| liberada_ao_trafego | data dd/mm/aaaa | data de liberação (vazia em 5 marcos) | 02/02/2015 |
| protocolo_antt | texto | protocolo | MGO-GEC-0017-2015 |

## 6. `cronograma_planejamento_anual_2026_eco050.csv`

1 linha por item do Planejamento Anual 2026 Rev02 (PA2026): 143 linhas. Usada para datas previstas/executadas e `id_sigicor`.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| row | inteiro | linha na planilha PA2026 | 13 |
| item | texto | item do PER/contrato | 3.2.1.1, 3.4.4 |
| sigicor | texto | ID SIGICOR (`-` se não há) | 13165 |
| desc | texto | descrição | Duplicação - Trecho de Cristalina |
| rod | texto | rodovia/UF | BR 050/GO, GO, MG, GO/MG |
| kmi / kmf | km | km inicial/final (final vazio em pontual) | 134.9 / 140.6 |
| prev_ini / prev_fim | data | previsto (AAAA-MM; `2018-(mes n/d)`; `<=2015`) | 2016-05 |
| prev_cum_final | fração 0-1 | % previsto acumulado ao fim do período | 1.0, 0.0 |
| exec_ini / exec_fim | data | executado, mesmo formato | 2022-09 |
| exec_cum_final | fração 0-1 | % executado acumulado | 0.9895 |

---

## 10. `fin_mensal_eco050.csv`

1 linha por obra do cadastro com série no acompanhamento × mês de referência: 600 linhas (28 linhas do cadastro × 24 meses; 25 do item 4 e os 3 retornos Extra-PER). Gerada por `acompanhamento_financeiro_eco050.py`. Valores **nominais**, sem correção por índice. Chave: `id_obra` + `mes_ref`. Meses: mar/2024 a abr/2026, sem mai/2024 e jul/2024 (sem arquivo na ANTT). Os retornos Extra-PER só aparecem de jan a mar/2025.

### Regras de uso

- **O % é da obra inteira.** O executado acumulado da fonte é contínuo na virada do ano de concessão (conferido em EMG-0003, 0007, 0013, 0014 e 0019); não há rebase. Os desvios entre o delta do acumulado e o `no_mes` são revisões retroativas da fonte.
- **Previsto oficial do mês** é o do arquivo daquele mês (visão da época). É um plano por ano de concessão: reprograma o que faltou e pode cair de um mês para o outro (ex.: jun/2025). O previsto do arquivo mais recente vai em `pct_previsto_acum_ultimo_arquivo`.
- **Valor no mês** = `valor_nominal` × `pct_*_mes`. **Acumulado** = `valor_nominal` × `pct_*_acum`. Nunca somar `tipo_valor` diferentes.
- **`pct_previsto_mes` vazio** em jan a mar/2026: a fonte não traz o plano mensal de 2026. O valor correspondente também fica vazio.
- **Série principal.** Uma linha do cadastro pode ligar a várias séries; só a principal gera valor. Duplicação: a série "Duplicação" da própria obra (EMG-0001, EMG-0003). Em duplicatas: a de dados mais recentes. As demais ficam em `series_ligadas`. Uma série para várias linhas (DUP-11-b e DUP-12-a, EMG-0003): cada linha aplica o mesmo % ao seu valor.
- **Datas reais** são da obra (iguais em todas as linhas dela). Início = 1º mês de referência com executado > 0. Se já havia avanço no 1º mês em que a obra aparece, `inicio_antes_da_serie` = True e a data fica vazia (o início do cadastro não é usado aqui). Término = 1º mês com executado >= 0,99; `data_conclusao_real` do cadastro prevalece (pode ser só o ano).
- **Acumulado que cai.** Algumas séries têm executado acumulado menor que o do mês anterior (EMG-0019 e EMG-0020 em ago/2025). Mantido como na fonte.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| id_obra | texto | chave da linha do cadastro (tabela 9) | `EMG-PER-DUP-11-b` |
| obra_id_acompanhamento | texto | série principal usada (uma só) | EMG-0003 |
| serie_principal | booleano | sempre True; as outras séries não geram linha | True |
| mes_ref | texto | mês de referência `AAAA-MM` | 2025-03 |
| snapshot | texto | arquivo da ANTT daquele mês | EMG-2025-03-14 |
| pct_previsto_acum | fração 0-1 | previsto acumulado, visão do arquivo do mês | 0.8494 |
| pct_executado_acum | fração 0-1 | executado acumulado, obra inteira | 0.7881 |
| pct_previsto_mes | fração 0-1 | previsto no próprio mês; vazio em jan a mar/2026 | 0.0415 |
| pct_executado_mes | fração 0-1 | executado no próprio mês | 0.0274 |
| pct_previsto_acum_ultimo_arquivo | fração 0-1 | previsto acumulado do mês segundo o arquivo mais recente em que a obra aparece: anos anteriores + soma dos previstos mensais dele até o mês | 0.7881 |
| valor_nominal | R$ | valor da linha, nominal. Item 4: `valor` do cadastro. Extra-PER: `aprovado_revisao`, só a obra (sem a parcela de projetos) | 11084093.13 |
| tipo_valor | categ. | tipo do `valor_nominal` | inicial_leilao (25 linhas do cadastro), aprovado_revisao (3) |
| data_base | texto | data-base do valor | `não informada (contrato: mai/2012)`, `2022-04` |
| valor_previsto_mes | R$ | `valor_nominal` × `pct_previsto_mes` | |
| valor_executado_mes | R$ | `valor_nominal` × `pct_executado_mes` | |
| valor_previsto_acum | R$ | `valor_nominal` × `pct_previsto_acum` | |
| valor_executado_acum | R$ | `valor_nominal` × `pct_executado_acum` | |
| situacao_fonte | categ. | situação no arquivo do mês | ATRASADA, ADIANTADA, CONFORME PLANEJAMENTO, NÃO INICIADA, CONCLUÍDA |
| revisao_negativa | bool | True quando o executado acumulado do mês é menor que o do mês anterior (executado no mês negativo); o valor fica como na fonte | True/False |
| data_inicio_prevista / data_termino_prevista | data | do cadastro (PA2026 Rev02; `AAAA` ou `AAAA-MM`); vazias nos Extra-PER | 2016-07 |
| data_inicio_real | data | início segundo a série (ver regra); vazia se `inicio_antes_da_serie` ou não iniciada | 2024-04 |
| data_termino_real | data | término (ver regra); vazia se não concluída | 2024-07-30; 2026 |
| metodo_data_inicio | categ. | origem da data de início | serie_1o_mes_exec_positivo, serie_1o_mes_exec_positivo_apos_lacuna (mês anterior sem arquivo), nao_observado_antes_da_serie, nao_iniciada_na_serie |
| metodo_data_termino | categ. | origem da data de término | cadastro_data_conclusao_real, serie_1o_mes_exec_ge_0.99, nao_concluida_na_serie |
| inicio_antes_da_serie | booleano | já havia avanço > 0 no 1º mês em que a obra aparece | False |
| fonte_id | texto | fonte do valor, cadastrada em `valores_obras/fontes.py` | eco050_evtea_modelo, eco050_nt_gegir_2023 |
| localizacao_valor | texto | onde está o valor (aba/célula, ou `valor_id` e página) | `EMG-NT2023-T25-OBRA: p.15, Tabela 25` |
| series_ligadas | texto | todas as séries ligadas à linha no cadastro, separadas por `\|` | `EMG-0003\|EMG-0004\|EMG-0027\|EMG-0028` |
| criterio_serie_principal | categ. | por que esta série é a principal | unica, duplicacao_propria_obra, dados_mais_recentes |

---

## 11. `fin_acumulado_eco050.csv`

1 linha por obra do cadastro **sem** série no acompanhamento: 61 linhas. Gerada por `acompanhamento_financeiro_eco050.py`. Sem evolução mensal: concluída antes de mar/2024 conta como 100% executada; as demais, 0%. Todas são do item 4 (`inicial_leilao`).

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| id_obra | texto | chave (tabela 9) | EMG-PER-DUP-02 |
| nome | texto | descrição da obra | |
| tipo_registro | categ. | motivo de não ter série | concluida_antes_serie (42), sem_local_a_alocar (12), condicionada_nao_acionada (7), nao_iniciada_sem_serie (0) |
| situacao | categ. | situação no cadastro | concluida, sem_local_definido, condicionada_nao_acionada |
| data_inicio_real / data_termino_real | data | do cadastro (`data_inicio_real`, `data_conclusao_real`); podem vir só com o ano ou vazias | 2018; 2017-06-30 |
| data_inicio_prevista / data_termino_prevista | data | do cadastro (PA2026 Rev02) | |
| pct_executado | fração 0-1 | 1 se concluída, 0 se não | 1.0 |
| valor_nominal | R$ | `valor` do cadastro | 37045774.81 |
| valor_executado | R$ | `valor_nominal` se concluída, senão 0 | |
| valor_a_executar | R$ | 0 se concluída, senão `valor_nominal` | |
| tipo_valor | categ. | tipo do valor | inicial_leilao |
| data_base | texto | data-base | `não informada (contrato: mai/2012)` |
| fonte_id / localizacao_valor | texto | fonte e células da aba PER do modelo | eco050_evtea_modelo |

---

## 12. `fin_resumo_eco050.csv`

1 linha por mês de referência × `tipo_valor`: 48 linhas (24 meses × inicial_leilao e aprovado_revisao). Gerada por `acompanhamento_financeiro_eco050.py`. Cada tipo é somado isoladamente.

- Executado das obras com série = soma de `valor_executado_acum` no mês. Obra sem linha no mês (ainda não apareceu: conta 0; já saiu da fonte: mantém o último executado) entra em `n_linhas_serie_sem_dado_no_mes`.
- Conferência de `inicial_leilao`: executado com série + executado das concluídas antes da série + a executar + 4.3 projetos (não rateado) = R$ 1.145.919.554,57 em todo mês, com `valor_a_executar` >= 0. Se divergir, o script termina com erro.

| coluna | tipo | descrição | exemplo / valores possíveis |
|---|---|---|---|
| mes_ref | texto | mês de referência | 2026-04 |
| snapshot | texto | arquivo da ANTT do mês | EMG-2026-04-23 |
| tipo_valor | categ. | tipo somado | inicial_leilao, aprovado_revisao |
| n_linhas_com_serie | inteiro | linhas do cadastro com série deste tipo | 25 |
| n_linhas_serie_sem_dado_no_mes | inteiro | dessas, as sem linha no mês | 0 |
| valor_total_tipo | R$ | soma de `valor_nominal` do tipo (com e sem série) | 1091351956.74 |
| valor_executado_acum_com_serie | R$ | executado acumulado das obras com série | |
| valor_executado_concluidas_antes_serie | R$ | executado das concluídas antes da série (100%) | |
| valor_a_executar | R$ | `valor_total_tipo` menos os dois executados | |
| valor_projetos_4_3_nao_rateado | R$ | item 4.3 do modelo; só em `inicial_leilao` | 54567597.84 |
| soma_conferencia | R$ | executado + concluídas + a executar + 4.3 | |
| valor_esperado | R$ | 1.145.919.554,57 em `inicial_leilao`; `valor_total_tipo` nos demais | |
| conferencia | categ. | ok ou divergência (tolerância R$ 0,01) | ok |

---

# Ecovias do Cerrado (id 103, ECC)

Mesmas convenções. **Data-base dos valores do modelo e do Fator D: jul/2016** (aba PER do modelo, D5: "DATA-BASE DOS EVTEs: julho/2016"). Regras em `documentacao/cadastro_obras.md` (seção Cerrado).

## Índice e fluxo de geração

| # | Tabela | Tipo | Gerada por | Usada por |
|---|---|---|---|---|
| C1 | `per_obras/per_cerrado_manuais.csv` | insumo (transcrito, com página) | `gerar_per_cerrado_manuais.py` | `montar_cadastro_cerrado` |
| C2 | `per_obras/correspondencias_cadastro_cerrado.csv` | insumo (à mão) | manual | `montar_cadastro_cerrado` |
| C3 | `per_obras/alteracoes_cerrado.csv` (+ `.md`) | registro (à mão) | manual | consulta (não é lida por script) |
| C4 | `dados/per_obras/intermediario/modelo_item4_cerrado_anual.csv` | saída | `extrair_modelo_cerrado.py` | conferências |
| C5 | `dados/per_obras/intermediario/modelo_item4_cerrado_grupos.csv` | saída | `extrair_modelo_cerrado.py` | `montar_cadastro_cerrado`, financeiro |
| C6 | `dados/finais/cadastro_obras/cadastro_obras_cerrado.csv` (+ `.xlsx`) | saída final | `montar_cadastro_cerrado.py` | carga no banco, financeiro |
| C7 | `dados/finais/financeiro_mensal/fin_mensal_cerrado.csv` | saída | `acompanhamento_financeiro_cerrado.py` | análises mensais |
| C8 | `dados/finais/financeiro_acumulado/fin_acumulado_cerrado.csv` | saída | `acompanhamento_financeiro_cerrado.py` | obras sem série |
| C9 | `dados/finais/financeiro_resumo/fin_resumo_cerrado.csv` | saída | `acompanhamento_financeiro_cerrado.py` | totais e conferência por mês |

Ordem: `consolidar.py` → `valores_obras/organizar.py` → `extrair_modelo_cerrado.py` → `montar_cadastro_cerrado.py` → `acompanhamento_financeiro_cerrado.py` (gera também `dados/finais/xlsx/fin_cerrado.xlsx`).

## C6. `cadastro_obras_cerrado.csv`

332 linhas: 326 de 132 `per_id` (118 obras do PER atualizado + 14 itens de edificações do Fator D, em 28 linhas) e 6 obras do acompanhamento fora do PER (`ECC-EXT-*`). 298 linhas com valor. **Tem as mesmas colunas da ECO050 (tabela 9)**, com estas diferenças de conteúdo:

| coluna | na Cerrado |
|---|---|
| id_obra | `ECC-PER-<SIGLA>-nn` (obra do PER), com sufixo `-LD`/`-LE` (lado da marginal), `-a`/`-b` (ano da faixa adicional), `-s01`... (trecho do acompanhamento), `-saldo` (parte sem trecho), `-01`... (unidade). `ECC-EXT-<SIGLA>-nn` = obra do acompanhamento fora do PER. Siglas: DUP, FXA, CMP, MAR, ACO, CTR, ACE, INT, ROT, PAS, RET, ILT, ILM, ILR, ILI (iluminação), DCO e FCO (condicionadas do 3.2.3), EDI (edificações) |
| tipo_intervencao | duplicacao, faixa_adicional, interconexao_trevo, interconexao_trombeta, via_marginal, acostamento, correcao_tracado, melhoria_acesso, intersecao, rotatoria, passarela, retorno_nivel, iluminacao, praca_pedagio, posto_prf, base_operacional, posto_pesagem, fibra_optica, centro_controle, edificio_sede |
| bloco | obrigatoria (4.1), condicionada (4.2 e 3.2.3), edificacoes_operacionais (4.3), complementacao_dnit (4.5), iluminacao_recuperacao (sem valor no item 4), extra_per |
| item_per | 3.2.1.1 a 3.2.1.4, 3.2.3.1, 3.2.3.2; nas edificações, a seção do PER pelo sumário (3.1.7, 3.4.x) |
| km_inicial / km_final | km atual; a origem está em `fonte_km` |
| km_per_original | km do PER (`ini-fim`); para acessos, acostamentos e faixas, `TH n: ini-fim` (o PER só dá o trecho homogêneo) |
| data_*_prevista, data_inicio_real, data_conclusao_real, fonte_datas_* , id_sigicor | vazias (não foram usados planejamentos) |
| prazo_contratual | ano civil do prazo do PER, supondo ano de concessão 1 = 2020 |
| situacao | concluida, em_andamento, nao_iniciada (pela série); condicionada_nao_acionada (4.2/3.2.3 sem série); `sem_acompanhamento` (sem série, prazo vencido) |
| item_modelo | 4.1, 4.2, 4.3, 4.5; vazio = sem valor |
| peso | = `valor_estudo_obra` (custo do Fator D) |
| metodo_valor | rateio_por_custo_estudo; peso_igual_sem_custo_no_estudo (não ocorre hoje); vazio sem valor |
| data_base | 2016-07 |
| fonte_id | ecc_leilao_modelo |
| localizacao_valor | linha da aba PER do modelo (`PER!F42:AI42`, total `PER!E42`, anos com valor) |
| origem | per_original, per_realocada (km do acompanhamento a mais de 1 km do PER/EVTEA, ou TH mudado pelo 2º TA), evtea_fator_d (edificações), acompanhamento_extra |
| a_confirmar | ver `observacao` e `per_obras/alteracoes_cerrado.csv` |

Colunas novas (só Cerrado, no fim da tabela):

| coluna | tipo | descrição | exemplo |
|---|---|---|---|
| subtipo | texto | APS/APD (acesso), RA-1A/RA-2A (rotatória), PPS/PPD (passarela), implantação/adequação (acostamento) | APS |
| trecho_homogeneo | texto | TH do PER (1 a 19); `2-6-8` nas travessias urbanas | 16 |
| prazo_per | texto | prazo como escrito no PER | `4º ano` |
| ano_prazo | inteiro | ano de concessão do prazo (o último, quando há vários) | 4 |
| fonte_km | texto | de onde vem o km: `acompanhamento ECC-nnnn (mês)`, `PER atualizado p.n`, `EVTEA (RESUMO_OBRAS... aba, linha)`, ou `sem km` | |
| valor_estudo_obra | R$ | custo da obra no estudo (Fator D), na data-base do estudo. **Não somar com `valor`** (o modelo aplica o REIDI) | 2441722.83 |
| data_base_estudo | texto | data-base do custo do estudo | 2016-07 |
| fonte_estudo | texto | fonte do custo | ecc_evtea_fator_d |
| localizacao_estudo | texto | célula do Fator D e fração/quantidade | `Ampliação!J17 (VM-1 ...) x 1` |

## C1. `per_cerrado_manuais.csv`

143 linhas do PER atualizado (uma por "linha do PER"; 132 `per_id`). Colunas: `per_id`, `id_linha` (id antes de quebrar em unidades/trechos), `fracao_linha` (parte do `per_id`), `secao_per`, `bloco`, `tipo_intervencao`, `subtipo`, `descricao`, `th`, `rodovia`, `uf`, `municipio`, `km_inicial`/`km_final` (km do PER, ou limites do TH), `extensao_km`, `quantidade`, `unidade`, `sentido` (LD/LE), `prazo_per`, `ano_prazo`, `prazo_per_original` (só quando difere do PER original), `km_evtea` e `fonte_km_evtea` (km do RESUMO_OBRAS), `item_modelo`, `fd_linha` (linha da aba Ampliação do Fator D), `fd_modo` (`total` = J × `fd_fracao`; `unitario` = I × quantidade, ou J/H quando não há unitário), `fd_fracao`, `observacao_per`, `pagina` (página do PDF), `documento_fonte` (ecc_per_atualizado; ecc_evtea_fator_d nas edificações).

## C2. `correspondencias_cadastro_cerrado.csv`

1 linha por ligação manual: `id_obra` (linha do cadastro antes da quebra em trechos: o `id_linha`, ou o id da unidade), `obra_id_acompanhamento` (séries ECC separadas por `|`; o grupo inteiro de cada série vai junto), `a_confirmar`, `justificativa`. Numa linha de acostamento ou faixa, a série vira um trecho da linha e o `a_confirmar` vale só para esse trecho.

## C3. `alteracoes_cerrado.csv`

1 linha por mudança ou divergência: `id_obra` (uma ou várias, separadas por `|`), `tipo_alteracao` (prazo, realocacao_th, km_diferente, obra_a_mais, obra_a_menos, inicio_parcial, divergencia_evtea, divergencia_per), `tipo_intervencao`, `descricao`, `km_per`, `km_atual`, `origem_da_informacao` (PER original × atualizado, ou ligação com o acompanhamento), `documento`, `localizacao`, `a_confirmar`, `observacao`.

## C4/C5. `modelo_item4_cerrado_anual.csv` e `_grupos.csv`

Mesmas colunas das tabelas 7 e 8 da ECO050. Diferenças: o ano 1 é uma coluna só (F; anos 1..30 = F..AI); `item` vai de 4.0 (subtotal, linha 41) a 4.5 (linhas 42–46); `parcela` sempre vazia; `bloco` = rótulo do grupo de rateio do subitem (tabela na doc). `_grupos.csv` tem 5 linhas (4.1 a 4.5), `anos` = lista dos anos com valor (ex.: `2,3,4,5,13,14`) e a coluna extra `celula_total` (`PER!E42`).

## C7–C9. Financeiro

Mesmas colunas das tabelas 10 a 12 da ECO050, com estas diferenças:
- `fin_mensal_cerrado`: 1.443 linhas (177 linhas do cadastro com série × até 21 meses, abr/2024 a abr/2026). Linhas sem valor (iluminação, `ECC-EXT-*`) têm `valor_nominal` e `tipo_valor` vazios. `data_base` = 2016-07.
- `fin_acumulado_cerrado`: 155 linhas; `tipo_registro` também pode ser `sem_serie_sem_informacao` (situação `sem_acompanhamento`, conta 0% executado).
- `fin_resumo_cerrado`: 21 linhas (só `inicial_leilao`). A coluna `valor_projetos_4_3_nao_rateado` da ECO050 aqui é `valor_nao_rateado_4_4` (4.4 desapropriações = 0). Conferência: executado + a executar + 4.4 = R$ 717.702.925,02 em todos os meses.


# Ecovias Rio Minas (id 105, ERM)

Por enquanto só a ligação PER x acompanhamento, sem valores: `per_riominas_manuais.csv` (688 obras do PER Atualizado, `ERM-PER-<SIGLA>-nn`) e `dados/finais/ligacao_per_acompanhamento/ligacao_per_acompanhamento_riominas.csv` (uma linha por par `per_id` x `obra_id_acompanhamento`; `tipo_ligacao` = `km`, `manual`, `sem_acompanhamento` ou `fora_do_per`). Colunas, regras e pendências em [`ligacao_riominas.md`](ligacao_riominas.md).
