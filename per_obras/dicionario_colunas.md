# Dicionário de dados: cadastro de obras da ECO050 (id 104, EMG)

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
| 7 | `dados/per_obras/modelo_item4_eco050_anual.csv` | saída | `extrair_modelo_eco050.py` | conferências |
| 8 | `dados/per_obras/modelo_item4_eco050_grupos.csv` | saída | `extrair_modelo_eco050.py` | `montar_cadastro` |
| 9 | `dados/per_obras/cadastro_obras_eco050.csv` (+ `.xlsx`) | saída final | `montar_cadastro_eco050.py` | carga no banco, ligação com o financeiro |

Ordem: `baixar.py` → `consolidar.py` → `valores_obras/organizar.py` (baixa o modelo) → `per_obras/gerar_per_eco050_manuais.py` (só se o PER for retranscrito) → `per_obras/extrair_modelo_eco050.py` → `per_obras/montar_cadastro_eco050.py` (para com erro se o rateio não fechar). `dados/` é gerado e fica fora do git.

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
| situacao | categ. | estado atual | concluida (53), sem_local_definido (14), em_andamento (14), condicionada_nao_acionada (7), nao_iniciada (1) |
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
