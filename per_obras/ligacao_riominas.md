# Ligação PER x acompanhamento, Ecovias Rio Minas (id 105, ERM)

**Objetivo:** dizer, para cada obra do PER Atualizado da Rio Minas, quais obras (ERM-nnnn) do acompanhamento da ANTT correspondem a ela, e quais obras do acompanhamento não estão no PER. Só a ligação: não há valores financeiros, modelo econômico, aditivos, NTs, atas nem planejamentos.

## Como rodar

```
python per_obras/gerar_per_riominas_manuais.py   # PER Atualizado (seção 3.2, p.52-88) -> per_obras/per_riominas_manuais.csv
python per_obras/ligar_per_riominas.py           # -> dados/finais/ligacao_per_acompanhamento/ligacao_per_acompanhamento_riominas.csv, .xlsx e _resumo.csv
```

O primeiro script lê o PDF (`inventario.csv`, concessão `ecoriominas`, título "PER Atualizado") e confere os totais contra a tabela Resumo da p.88; para com erro se algo não fechar. O segundo precisa de `dados/acompanhamento_obras/consolidado/obras.csv` (`consolidar.py`) e para com erro se alguma obra ERM do acompanhamento ficar de fora da saída.

## Obras do PER (`per_riominas_manuais.csv`)

688 linhas, id `ERM-PER-<SIGLA>-nn`, na ordem das tabelas do PER (BR-116/RJ, BR-116/MG, BR-465/RJ, BR-493/RJ). Colunas como no cadastro da ECO050, mais `ano_concessao` (ano da concessão em que a obra deve ficar pronta, ex. `4º`); sem `pnv`/`municipio`. Faixas adicionais e marginais têm uma linha por sentido, como no PER.

| Sigla | tipo_intervencao | Seção do PER | Linhas | Quantidade (Resumo p.88) |
|---|---|---|---|---|
| DUP | duplicacao | 3.2.1.A (p.52-53) | 30 | 303,228 km |
| FAD | faixa_adicional | 3.2.1.B (p.54-60) | 138 | 256,236 km (ver divergência abaixo) |
| ESC | area_escape | 3.2.1.C (p.60) | 3 | 3 |
| MAR | via_marginal | 3.2.2.B (p.64-67) | 58 | 85,517 km |
| DIA | interconexao_diamante | 3.2.2.C | 10 | 10 |
| PIN | passagem_inferior | 3.2.2.D | 13 | 13 |
| TRB | interconexao_trombeta | 3.2.2.E | 4 | 4 |
| TRV | interconexao_trevo | 3.2.2.F | 1 | 1 |
| RTU / RTX | retorno_em_desnivel (tipo U / tipo X) | 3.2.2.G / H | 15 / 85 | 15 / 85 |
| ROT / ROA | rotatoria (nível / alongada) | 3.2.2.I / J | 9 / 10 | 9 / 10 |
| ALC | alca_conexao | 3.2.2.K (p.74-75, transcrita à mão) | 7 | 7 |
| ACE | melhoria_acesso | 3.2.2.L (p.75-77) | 58 | 775 |
| BRU | barreira_ruido | 3.2.2.M (p.77-78) | 28 | 4,977 km |
| CPP | caixa_produto_perigoso | 3.2.2.N (p.78-80) | 29 | 29 |
| FAU | passagem_fauna | 3.2.2.O (p.80-82) | 57 | 57 |
| PAS | passarela | 3.2.2.P (p.82-84) | 75 | 75 |
| ONI | ponto_onibus | 3.2.2.Q (p.84-86) | 56 | 462 |
| CIC | ciclovia | 3.2.2.R (p.87) | 1 | 1,630 km |
| DIV | divisor_central | 3.2.2.S (p.87) | 1 | 0,270 km |

- Acessos (ACE) e pontos de ônibus (ONI): o PER só dá a quantidade por "segmento homogêneo" (SEGMENTO n, sem km). Cada linha é um segmento (`quantidade` = nº de acessos/pontos) e o número do segmento está na `descricao`. Segmentos com quantidade 0 não geram linha.
- Quantidade: km (extensão) para duplicação, faixa, marginal, barreira de ruído, ciclovia e divisor central; unidade (1) para as demais, exceto ACE/ONI (nº do segmento).
- Barreiras de ruído: a altura (3 m) e a extensão estão em `observacao_per` e `extensao_km`. Faixas com `*` (acostamento usado como faixa) ou `**` (duas faixas por sentido) trazem a nota em `observacao_per`.
- **Fora da lista, de propósito:** 3.2.2.A Travessias urbanas (p.62-64), que é só a relação de trechos urbanos que exigem iluminação e não consta do Resumo; e 3.2.3 Manutenção de nível de serviço (p.89 em diante), que traz só gatilhos volumétricos por trecho homogêneo, sem obra localizada. Na ECO050 o equivalente (estoque de obras condicionadas) entrou no cadastro; aqui não, porque o PER da Rio Minas não define obras discretas.
- **Divergência do próprio PER:** a tabela de faixas adicionais da BR-116/RJ (p.54-55) soma 125,693 km, mas o Resumo (p.88) traz 124,693 km. Vale a tabela (conferida linha a linha); o script avisa e segue.
- **Provável erro de digitação no PER:** o divisor central da p.87 está em km 102,350 a 102,620, mas as coordenadas dele correspondem ao km ~90,4 da própria tabela de faixas da p.54 (ver correspondência manual abaixo).

## Ligação (`ligar_per_riominas.py`)

### O problema da quilometragem

O acompanhamento usa o km do projeto executivo por segmento homogêneo (SH), diferente do km do PER. A diferença (acompanhamento menos PER) foi medida nas obras que casam sem dúvida e é aplicada como correção antes de comparar:

| Trecho | Diferença | Exemplo |
|---|---|---|
| BR-116/RJ, km < 150 (SH 29 a 36) | +2,7 km | duplicação PER 57,000-77,900 x SH 29 59,43-80,53 |
| BR-116/RJ, km >= 150 (SH 49 a 58, Dutra) | +7,02 km | diamante PER 195,500 x SH 56 202,520 |
| BR-116/MG, km < 450 | -0,6 km | duplicação PER 413,315-421,627 x SH 2 412,722-421,210 |
| BR-116/MG, km >= 450 | -0,78 km | duplicação PER 500,111-520,517 x SH 7 499,33-519,73 |
| BR-493/RJ | -0,15 km | duplicação PER 5,300-15,600 x SH 38 5,17-15,48 |

A diferença aplicada fica em `delta_km_acomp_menos_per`; `dif_km_inicial`/`dif_km_final` são as diferenças que sobram depois da correção. As funções estão em `delta_acomp_menos_per()`; para outro trecho da concessão, acrescentar aqui.

### Dados do acompanhamento

Só 12 das 795 obras ERM têm km nas colunas de `obras.csv`. O script extrai rodovia, km, sentido e SH da `descricao`. O SH manda sobre o texto quando divergem (ex. "BR-116/MG - SH 35" é BR-116/RJ; vale o SH, registrado em `observacao`). O tipo vem do `item_per` do acompanhamento (3.2.1.A duplicação, 3.2.1.B faixa adicional, 3.2.2.B marginal etc.).

### Regras (coluna `regra`)

| regra | Como liga |
|---|---|
| `km_trecho` | Duplicação, faixa adicional, marginal, ciclovia, divisor: mesmo tipo e rodovia/UF, mesmo sentido (quando os dois informam), km já corrigido com sobreposição >= 10% da obra do acompanhamento (ou >= 50% do trecho do PER). Uma obra do acompanhamento pode ligar a mais de um trecho do PER, e um trecho do PER a várias obras do acompanhamento. Se o trecho do PER já tem outra obra bem ajustada (extremidades dentro de 0,75 km) e esta não casa, ela é descartada (`fora_do_per`). |
| `km_ponto` | Obras pontuais (área de escape, diamante, passagem inferior, trombeta, trevo, retornos, rotatórias, alças, barreiras, caixas de produto perigoso, passagem de fauna, passarela): alinhamento 1 a 1 em ordem de km, mesmo tipo e rodovia/UF, tolerância de 2,0 km (1,0 km nas barreiras). Diferença corrigida > 0,75 km vai como `a_confirmar`. |
| `segmento_sh` | Acessos e pontos de ônibus: PER por segmento, acompanhamento por SH. Mapa: BR-116/RJ segmentos `n'` (com apóstrofo) = SH 48+n; BR-493/RJ segmentos 1 a 3 = SH 38 a 40; BR-116/MG segmentos 1 e 2 = SH 1 e 2. Conferido pela quantidade: em todos os 15 segmentos de acessos e 14 de pontos a quantidade do PER é igual à do acompanhamento. Liga a linha-resumo do SH ("8 Acessos - SH 49") e cada unidade individual. |
| `subetapa_da_passarela` | As linhas genéricas "Serviços Preliminares / Obras Complementares / Infraestrutura / Mesoestrutura / Superestrutura" (ERM-0476 a 0480, 0482 a 0486, 0488 a 0492, classificadas no acompanhamento como 3.2.1.B) herdam a ligação da passarela imediatamente anterior (ERM-0475, 0481, 0487). |
| `manual` | `correspondencias_cadastro_riominas.csv` (obra do acompanhamento -> `per_id`, `a_confirmar`, `justificativa`); tem precedência sobre as regras automáticas. |

`tipo_ligacao`: `km` (qualquer regra automática; o detalhe está em `regra`), `manual`, `sem_acompanhamento` (obra do PER sem nada no acompanhamento) e `fora_do_per` (obra do acompanhamento sem obra do PER). `a_confirmar` = True quando a ligação é ambígua ou a diferença de km é grande; o motivo está em `observacao`.

### Colunas de `ligacao_per_acompanhamento_riominas.csv`

`per_id`, `tipo_ligacao`, `regra`, `a_confirmar`, `observacao`; dados do PER (`tipo_intervencao`, `rodovia`, `uf`, `per_km_inicial`, `per_km_final`, `per_quantidade`, `per_unidade`, `per_sentido`, `per_ano_concessao`, `per_pagina`); dados do acompanhamento (`obra_id_acompanhamento`, `acomp_descricao`, `acomp_item_per`, `acomp_tipo`, `acomp_km_inicial`, `acomp_km_final`, `acomp_sentido`, `acomp_sh`, `presente_ultimo_snapshot`); medidas (`delta_km_acomp_menos_per`, `dif_km_inicial`, `dif_km_final`, `sobreposicao_km`); `per_id_relacionado` (nas obras `fora_do_per`, o trecho de duplicação/faixa onde fica um OAE). Nas linhas `fora_do_per`, `tipo_intervencao` traz o tipo da obra do acompanhamento.

O `_resumo.csv` (e a aba `resumo_por_per_id` do xlsx) tem uma linha por `per_id` com `n_obras_acompanhamento`, `n_no_ultimo_snapshot`, `obras_acompanhamento`, `regras`, `a_confirmar` e `status` (`ligado`, `a_confirmar`, `sem_acompanhamento`). Como acompanhamento e PER têm granularidades diferentes, a relação normal é 1 obra do PER para n obras do acompanhamento; contar obras do acompanhamento ligadas não dá o valor da obra do PER.

## Números (rodada de 14/10/2026)

- Obras do PER: 688. **171 ligadas** (167 `ligado` + 4 `a_confirmar`) e **517 `sem_acompanhamento`**.
- Pares ligados: 506 (348 `segmento_sh`, 69 `km_trecho`, 73 `km_ponto`, 15 `subetapa_da_passarela`, 1 `manual`), com 506 obras do acompanhamento diferentes.
- Obras ERM do acompanhamento: 795. 506 ligadas e **289 `fora_do_per`**: 205 serviços operacionais (itens 3.1.x e 3.4.x do PER, frente de serviços operacionais, fora da lista da seção 3.2), 66 OAEs (pontes/viadutos de duplicação, faixa adicional e alargamentos que o PER não lista à parte; 60 caem dentro de trecho de duplicação/faixa do PER e ficam em `per_id_relacionado`), 7 vias marginais, 4 passarelas, 4 serviços preliminares (limpeza e supressão vegetal), 2 acessos e 1 caixa de produto perigoso.
- Cobertura por ano de concessão: obras do 4º ano, todas ligadas (137); 5º ano, 11 de 32; 6º, 21 de 191; 7º e 8º ano, praticamente nenhuma (o acompanhamento só traz o ciclo inicial: BR-116/RJ SH 29-36 e 49-58, BR-116/MG SH 1, 2 e 7, BR-493/RJ SH 38-40). A BR-465/RJ não tem nenhuma obra de melhoria no acompanhamento.

## Pendências e pontos a validar

1. **Divisor central (ERM-0001 x ERM-PER-DIV-01)**, ligação manual `a_confirmar`: o PER tem km 102,350 e o acompanhamento km 92,7; pelas coordenadas do PER e pelo deslocamento de 2,7 km, é a mesma obra e o km do PER parece erro de digitação.
2. **Passarelas da BR-116/MG (PAS-52 e PAS-53 x ERM-0447 e 0448)** e **passagem inferior BR-493 km 23,390 (PIN-13 x ERM-0119, km 22,20)**: ligadas por posição, mas com diferença de 1,0 a 1,5 km; `a_confirmar`.
3. **Obras com marcação `(***)` no acompanhamento** (passarelas ERM-0451, 0468, 0470, 0472; marginais da BR-493 ERM-0248, 0353, 0354, 0626 e da BR-116/RJ ERM-0099, 0102): ficaram `fora_do_per` por não terem obra do PER na posição. O significado de `(***)` não foi confirmado (parece obra adicional ao PER); duas delas (ERM-0099 e 0102) sobrepõem marginais do PER mas com extremidades que não casam. A marginal ERM-0106 (BR-493 km 3,014-3,289) também.
4. **Acessos soltos** ERM-0002 (BR-116 km 55) e ERM-0215 (BR-116/RJ km 57,60): o PER dá acessos da BR-116/RJ só por segmento, sem km; não foi possível dizer a qual segmento pertencem.
5. **Acessos e pontos de ônibus fora dos SH 1, 2, 38 a 40, 49 a 58** (demais segmentos do PER): `sem_acompanhamento`, porque o acompanhamento não tem esses SH.
6. **Obras que saíram do cronograma** (`presente_ultimo_snapshot` = False, 79 das `fora_do_per` e boa parte da BR-116/RJ SH 29-31): continuam ligadas; conferir se foram canceladas ou só reorganizadas antes de usá-las como "obra em andamento".
7. **Faixas adicionais e marginais da BR-116/RJ SH 53 a 56**: ERM-0216 a 0219 (limpeza e supressão vegetal) cobrem várias obras do PER de uma vez e por isso ficaram fora da ligação.
8. A correção de km é por faixas grosseiras (acima); em trechos novos do acompanhamento (outros SH) pode ser preciso ajustar `delta_acomp_menos_per()`.
