# Cadastro de obras

Seções: ECO050 (abaixo) e Ecovias do Cerrado (no fim). Tabelas finais em `dados/finais/<tabela>/` (caminhos em `per_obras/caminhos.py`).

# Cadastro de obras da ECO050 (id 104, EMG)

**Objetivo:** ter uma linha por obra esperada na concessão, na versão mais atual (km corrigido), com o valor do item 4 do modelo econômico-financeiro rateado por obra, para carregar no banco de dados. O histórico das mudanças fica em `per_obras/alteracoes_eco050.md` e `.csv`.

## Como rodar

```
python per_obras/extrair_modelo_eco050.py     # item 4 do modelo -> dados/per_obras/intermediario/modelo_item4_eco050_*.csv
python per_obras/montar_cadastro_eco050.py    # -> dados/finais/cadastro_obras/cadastro_obras_eco050.csv e .xlsx
```

Antes disso, o modelo já precisa ter sido baixado por `valores_obras/organizar.py`, e o acompanhamento consolidado por `consolidar.py`. O script imprime as conferências e para com erro se o rateio não fechar.

## Insumos

| Arquivo | Conteúdo |
|---|---|
| `per_obras/per_eco050_manuais.csv` | Obras do PER original (`per_id`, km, página) |
| `per_obras/alteracoes_eco050.csv` | km atual e data de conclusão já compilados (chave `obra_per_ref`) |
| `per_obras/correspondencias_cadastro_eco050.csv` | Ligações feitas à mão: `id_obra` ↔ `per_id_origem` / `ref_alteracoes` / `obra_id_acompanhamento`, com UF, município e km quando mudam, `a_confirmar` e `justificativa`. Uma linha com justificativa iniciada por `EXCLUIDA` tira a obra do PER do cadastro |
| `per_obras/obras_extra_per_eco050.csv` | Obras fora do PER (por enquanto só os 3 retornos em nível do acompanhamento), com fonte e página |
| `per_obras/marcos_liberacao_eco050.csv` | Liberação ao tráfego (Relatório mensal 12/2025) |
| `per_obras/cronograma_planejamento_anual_2026_eco050.csv` | Datas previstas e executadas, ID SIGICOR (PA2026 Rev02) |
| `dados/acompanhamento_obras/consolidado/obras.csv` | Obras do acompanhamento (EMG-0001 a EMG-0031) |

## Colunas principais

- `id_obra`: o `per_id` para obras do PER; sufixo `-a`, `-b` quando a obra do PER foi dividida; `EMG-EXT-<SIGLA>-nn` para obras fora do PER.
- `tipo_intervencao`: duplicacao, via_marginal, passarela, interconexao_diamante, interconexao_trevo, interconexao_trombeta, retorno_desnivel, retorno_nivel, melhoria_acesso, faixa_adicional, ponte, recuperacao, iluminacao, outro. O "retorno operacional" do estoque 3.2.3.3 fica como `outro`.
- `bloco`: obrigatoria (PER 3.2.1), manutencao_nivel_servico (estoque 3.2.3.3, sem local), condicionada (faixas adicionais 3.2.3.1), extra_per.
- `km_inicial`, `km_final`: km atual. `km_final` fica vazio em obra pontual. O km do PER fica em `km_per_original`.
- Datas: `data_*_prevista` vêm do PA2026 Rev02 (ligação por tipo + UF + km). `data_inicio_real` vem do executado do PA2026. `data_conclusao_real` é a liberação ao tráfego: na duplicação, a data mais recente dos marcos que cobrem o trecho. Nas demais obras, vem de `alteracoes_eco050.csv` ou de um marco com o mesmo tipo e km. As datas podem ser só ano ou ano-mês. `prazo_contratual` = 07/01/2019 nas obras obrigatórias do 3.2.1, que é a meta final de duplicação. As metas anuais são 07/01/2016 a 2019, mas o PER não diz qual segmento vence em qual ano.
- `situacao`: condicionada_nao_acionada; concluida (tem data de conclusão, ou o acompanhamento/PA2026 diz 100%); em_andamento (% > 0); sem_local_definido (estoque ou "localização a definir"); nao_iniciada.
- `origem`: per_original, per_realocada (km mudou ou houve reconfiguração), inclusao_revisao, inclusao_aditivo. A fonte da mudança fica em `fonte_alteracao`.
- `obra_id_acompanhamento`: uma ou mais obras do acompanhamento, separadas por `|`. A mesma obra do acompanhamento pode aparecer em duas linhas. Exemplo: Catalão 275,4–286,8 cruza dois segmentos PNV.
- Valor: `item_modelo`, `valor_grupo_bloco`, `soma_pesos_grupo`, `peso`, `valor`, `metodo_valor`, `data_base`, `fonte_id`, `localizacao_valor` (células da aba PER).

## Regras de rateio

- Grupo = `item_modelo` × `bloco` do modelo (`modelo_item4_eco050_grupos.csv`): 4.1.1.1 passarelas; 4.1.1.2 vias laterais (marginais); 4.1.2.3.1 acessos; 4.1.2.3.2 interseções (diamante, trevo, trombeta, retorno em desnível e retorno operacional do estoque); 4.1.2.4.2 duplicação; 4.2.2 faixas adicionais. Bloco obrigatoria (anos 1–5) → obras do PER 3.2.1. Bloco manutencao_nivel_servico (anos 6–30) → linhas de estoque `EMG-PER-EST-*`. Bloco condicionada → faixas adicionais.
- `peso` = 1 por unidade (`rateio_igual_por_unidade`). Para marginais, duplicação e faixas adicionais, `peso` = km da linha (`rateio_por_km`). Nas marginais é o km **atual**, que já inclui os saldos remanejados.
- `valor = valor_grupo_bloco × peso / soma_pesos_grupo`. A data-base não é informada no modelo. O contrato é de mai/2012.
- 4.3 Elaboração de projetos não é obra e não é rateado. O excedente dos anos 20–22 (R$ 8,89 mi, igual a 5% do 4.2.2 de cada ano) foi reclassificado como bloco `condicionada` em `extrair_modelo_eco050.py`.
- Obras fora do item 4 (retornos em nível Extra-PER) ficam sem `item_modelo` e sem valor.
- Conferências impressas: por grupo, a soma rateada é igual ao valor do grupo; soma rateada + 4.3 = R$ 1.145.919.554,57 (total do item 4); duplicação = 218,5 km; obras do acompanhamento não ligadas.

## Obra do PER dividida em n linhas

Quando uma obra do PER vira mais de uma linha, todas guardam o mesmo `per_id_origem` e uma `fracao_da_origem`:

- duplicação: segmentos PNV quebrados nos trechos do acompanhamento (Cristalina 95,7–99,44; Catalão 275,4–286,8). Fração = km da linha / km do segmento;
- marginal ID-2: virou duas linhas, Sul e Norte. Fração = extensão útil do sentido no PER.

**Ao ligar o financeiro ao cadastro, lembre que um valor dado "por obra do PER" precisa ser repartido pela `fracao_da_origem`, ou agregado por `per_id_origem`.**

## Pendências

- Passarelas 171/175: o cadastro segue `alteracoes_eco050.csv`, que se baseia no PA2025: ID-7 (279,5) → 171 = EMG-0025 e ID-1 (40,5) → 175 = EMG-0026. O 6º TA, cl. 3.1, lido diretamente, diz o contrário (ID-1 → 171). Por isso as duas linhas estão com `a_confirmar`. O valor é o mesmo nas duas.
- Passarela 277,5: mantida no km oficial; `alteracoes` indica 278,9 por inferência.
- Retornos em nível Extra-PER: só os 3 do acompanhamento. Os 9 já executados (Res. 4.652/2015) e o km 286,5 ficam para depois. A contagem 10 × 9 × 12 não fecha. A UF do km 196,5 diverge entre as fontes.
- Ainda não entraram: pontes, trecho DNIT (1º TA), segmento km 178,35–179,5 (3º TA), duplicação km 77+600 e iluminação (1ª Revisão Quinquenal), acesso Extra-PER km 245,8.
- Diamante 4 (151,5) e marginal 1 (40–41): localização a definir. Marginais 3, 4 e 6 ficaram fora do cadastro (saldos remanejados), sem aditivo localizado.
- Catalão: a conclusão de 2026 vem da ata de 14/05/2026, sem o dia. Os dispositivos de Catalão seguem `em_andamento` (PA2026/acompanhamento abr/2026).

## Acompanhamento financeiro (cadastro × % físico mensal)

`per_obras/acompanhamento_financeiro_eco050.py` cruza o cadastro com o acompanhamento mensal da ANTT (obra × mês) e gera `dados/finais/financeiro_mensal/fin_mensal_eco050.csv`, `dados/finais/financeiro_acumulado/fin_acumulado_eco050.csv` e `dados/finais/financeiro_resumo/fin_resumo_eco050.csv` (mais `dados/finais/xlsx/fin_eco050.xlsx`). A lógica fica em `per_obras/financeiro_comum.py`, usada também pela Cerrado; o script da ECO050 só tem a configuração. Colunas em `per_obras/dicionario_colunas.md` (tabelas 10 a 12).

```
python per_obras/acompanhamento_financeiro_eco050.py    # depois de montar_cadastro_eco050.py
```

Regras:
- Valores nominais, sem correção por índice: cada linha guarda `valor_nominal`, `tipo_valor` e `data_base` (item 4 = `inicial_leilao`, data-base "não informada (contrato: mai/2012)"; retornos Extra-PER = `aprovado_revisao`, 2022-04, só a parcela de obra). Tipos diferentes nunca se somam.
- O % executado da fonte é da obra inteira e contínuo na virada do ano de concessão (o script imprime a checagem). Valor no mês = valor × Δ%; acumulado = valor × % acumulado.
- Previsto de cada mês = o do arquivo daquele mês; o do arquivo mais recente fica em `pct_previsto_acum_ultimo_arquivo`.
- Série principal por linha do cadastro (`serie_principal`, `criterio_serie_principal`): a da própria obra (duplicação EMG-0003, EMG-0001); em duplicatas, a de dados mais recentes. As outras ficam em `series_ligadas` e não geram valor. Uma série para várias linhas (DUP-11-b e DUP-12-a): cada uma aplica o mesmo % ao seu valor.
- Datas reais: início = 1º mês com executado > 0; término = 1º mês com executado >= 0,99 (`TERMINO_MIN` no topo do script); `data_conclusao_real` do cadastro prevalece. Obra com avanço no 1º mês em que aparece: `inicio_antes_da_serie` = True e início vazio.
- Obras do cadastro sem série (`fin_acumulado`): concluídas antes da série (100% executadas), sem local a alocar, condicionadas não acionadas.
- Conferência em `fin_resumo`: executado + a executar + 4.3 projetos = R$ 1.145.919.554,57 em todo mês de `inicial_leilao`; o script termina com erro se divergir.
- Séries ligadas ao cadastro e sem uso (não principais): EMG-0002, 0004, 0018, 0027, 0028.

## Pontos para discutir depois (ECO050)

1. **Regra das datas reais.** Hoje o início é o 1º mês com executado > 0 e o término é o 1º mês com executado >= 99% (ou a data oficial, quando existe). As 15 obras que já tinham avanço em mar/2024 ficam com o início vazio (`inicio_antes_da_serie`). Falta decidir o limiar do término e o que fazer com o início anterior à série.
2. **Correção monetária.** Os valores estão nominais, cada um na sua data-base (item 4: mai/2012; retornos: abr/2022). A correção pelo IPCA fica para as operações nas tabelas principais.
3. **Peso do rateio.** Hoje o peso é igual dentro do grupo (ou km). A coluna `peso` já existe para receber outro critério, por exemplo o custo unitário por tipo.
4. **Obras com `a_confirmar` (7)**, entre elas o diamante 4 e a marginal 1, que estão como "não iniciadas" e sem local definido.
5. **Quedas no executado (`revisao_negativa`, 9 linhas em 7 obras).** Decidir se mantemos o valor negativo do mês ou se suavizamos a série.
6. **Obras fora do PER** ainda não incluídas (lista em "Pendências").

---

# Cadastro de obras da Ecovias do Cerrado (id 103, ECC)

**Objetivo:** o mesmo da ECO050: uma linha por obra esperada no PER, na versão mais atual (PER atualizado, com a redação do 2º TA), ligada ao acompanhamento da ANTT, com km atual e o valor do item 4 do modelo econômico-financeiro rateado por obra. Mudanças desde o PER em `per_obras/alteracoes_cerrado.md` e `.csv`.

## Como rodar

```
python per_obras/gerar_per_cerrado_manuais.py         # só se o PER for retranscrito -> per_obras/per_cerrado_manuais.csv
python per_obras/extrair_modelo_cerrado.py            # item 4 do modelo -> dados/per_obras/intermediario/modelo_item4_cerrado_*.csv
python per_obras/montar_cadastro_cerrado.py           # -> dados/finais/cadastro_obras/cadastro_obras_cerrado.csv e .xlsx
python per_obras/acompanhamento_financeiro_cerrado.py # -> dados/finais/financeiro_*/fin_*_cerrado.csv e xlsx/fin_cerrado.xlsx
```

Antes: `consolidar.py` (acompanhamento) e `valores_obras/organizar.py` (baixa `fator-d.xlsx`, a modelagem REV8 e, a partir de agora, o modelo do edital, fonte `ecc_leilao_modelo`). Se o modelo ainda não foi baixado, `extrair_modelo_cerrado.py` o tira do ZIP já baixado em `dados/pesquisa_financeiro/`. Os scripts param com erro se o rateio ou a conferência não fecharem.

## Insumos (só estes)

| Insumo | Uso |
|---|---|
| PER atualizado (`ecc_per_atualizado`, pp.36–48) | base do cadastro: obras, TH, km, quantidades e prazos, transcritos em `per_obras/gerar_per_cerrado_manuais.py` (com página) |
| PER original (`ecc_per_original`) | só para registrar o que mudou (só as passarelas) |
| Acompanhamento ANTT (`obras.csv`, `obras_por_snapshot.csv`, `serie_mensal.csv`, obras ECC-nnnn) | ligação, km atual, situação e % mensal |
| Modelo econômico-financeiro do edital, aba PER (`ecc_leilao_modelo`), linhas 41–46 | valor do item 4 por subitem e ano (data-base jul/2016). A cópia REV8 (`modelagem-financeira-planilhas.zip`) é idêntica nas linhas 41–46 (conferido célula a célula pelo script) |
| `fator-d.xlsx`, aba Ampliação, colunas I/J (`ecc_evtea_fator_d`, jul/2016) | peso do rateio: custo de cada obra no estudo |
| `BR_364_365_RESUMO_OBRAS_MELHORIAS_REV8.xlsb` (`ecc_evtea_modelagem`) | km dos dispositivos que o PER não localiza (rotatórias, interseções, passarelas), só para ligar ao acompanhamento |
| `per_obras/correspondencias_cadastro_cerrado.csv` | ligações feitas à mão, com justificativa (marginais, iluminação, Trevão, passarelas de Ituiutaba, pesagem, fibra, duplicação) |

## Modelo: item 4 por subitem

Aba PER: coluna E = total; F..AI = anos 1..30 (o ano 1 é uma coluna só, diferente da ECO050); AJ = soma de conferência. 4.0 = R$ 717.702.925,02.

| Subitem | Valor (R$) | Anos | Bloco (grupo do rateio) | O que é no estudo (Fator D) |
|---|---|---|---|---|
| 4.1 Obras de melhorias | 194.720.004,91 | 2–5, 13–14 | obrigatoria | 1.2: marginais, acostamentos, dispositivos (passarelas, interseções, rotatórias, acessos) |
| 4.2 Obras condicionadas ao volume de tráfego | 379.324.801,15 | 2–5, 7, 13–16, 22–24 | condicionada | 1.3: faixas adicionais (3.2.1.2), duplicação TH 13–15 (3.2.1.1), retornos, correção de traçado |
| 4.3 Edificações e instalações operacionais | 123.735.514,55 | 1–3 | edificacoes_operacionais | 2: praças, PRF, BSO, pesagem, fibra, CCO, sede |
| 4.4 Desapropriações | 0 | – | – | – |
| 4.5 Complementação das obras do DNIT | 19.922.604,41 | 1–2 | complementacao_dnit | 1.1: Trevão e Xapetuba |

Fator D × modelo: o modelo é o Fator D vezes o fator REIDI da linha 3 da aba PER (0,98175 no ano 1; 0,9635 nos demais). 4.1 e 4.2 = Fator D × 0,9635 (−3,65%); 4.3 fica −2,64% e 4.5 −2,92% (têm valor no ano 1). Nada foi forçado: o custo do Fator D é usado só como peso.

## Regras

- **Linhas do PER → linhas do cadastro** (todas guardam `per_id_origem` e `fracao_da_origem`):
  - marginal: uma linha por TH e lado (LD/LE), fração = extensão do lado / extensão do TH;
  - faixa adicional (Tabela 3): uma linha por TH e ano de implantação, fração = km do ano / km do TH;
  - acostamento e faixa adicional: a linha é quebrada nos trechos do acompanhamento que caem no TH (`-s01`, `-s02`...) e o que sobra vira `-saldo` (sem km). Os trechos preenchem os anos em ordem. Se os trechos somam mais que o PER, a fração é km do trecho / soma dos trechos (sem saldo);
  - quantidade em unidades (acessos, praças, BSO, PRF, pesagem) vira uma linha por unidade (`-01`, `-02`...), fração = 1/n;
  - edificações (4.3): o PER não as lista por obra; as linhas vêm do Fator D (aba Ampliação, item 2, por tipo × UF), `origem` = `evtea_fator_d`.
- **Ligação com o acompanhamento.** As séries ECC são agrupadas em obras físicas: mesmo tipo e mesmo km (0,6 km em dispositivos, 0,1 km em acessos, extremos a 0,35 km em obras lineares), desde que não apareçam no mesmo mês (o arquivo muda de formato em mai/2024 e set/2024 e a mesma obra ganha outro `obra_id`). Depois: (1) correspondências manuais; (2) dispositivos com km do EVTEA: o par mais próximo primeiro, até 6 km, com `a_confirmar` acima de 3 km; (3) acessos: pelo TH, em ordem de km; (4) acostamentos e faixas: pelo TH. Séries de obras do item 4 que sobram viram `ECC-EXT-<SIGLA>-nn` (sem valor). Séries fora do item 4 (OAE do 3.1.3, sistemas do 3.4.3, desvio emergencial, foto) ficam fora do cadastro; o script lista todas com o motivo.
- **km atual** (`fonte_km`): série mais recente do acompanhamento > km do PER > km do EVTEA > vazio (acessos e saldos: o PER só dá o TH, que fica em `trecho_homogeneo`). A duplicação fica com o km da Tabela 1.
- **Situação:** com série, o último mês da série mais recente (≥ 0,99 concluida; > 0 em_andamento; 0 nao_iniciada). Sem série: `condicionada_nao_acionada` no 4.2 e no 3.2.3; `sem_acompanhamento` nas demais (prazo vencido; pode ter sido concluída antes de abr/2024).
- **Prazo:** `prazo_per` (texto do PER) e `ano_prazo` (ano de concessão). `prazo_contratual` = ano civil, supondo ano 1 = 2020 (a concessão vira o ano em janeiro). O cadastro não tem datas previstas nem datas reais, porque não foram usados planejamentos; o financeiro calcula as datas reais pela série.
- **Valor:** grupo = `item_modelo` × `bloco`. `peso` = `valor_estudo_obra` = custo da obra no Fator D (jul/2016): coluna J × fração da linha (marginais, acostamentos, faixas, duplicação, correção de traçado, Trevão, Xapetuba, fibra) ou coluna I (unitário por tipo × UF) × quantidade (dispositivos, acessos, retornos, edificações). `valor = valor_grupo_bloco × peso / soma_pesos_grupo`; a soma por grupo bate com o modelo e o total com R$ 717.702.925,02. Hoje todas as 298 linhas com valor têm custo do estudo. A regra de peso igual (`peso_igual_sem_custo_no_estudo`) fica no script para o caso de obra sem custo.
- **Sem valor:** iluminação (o Fator D diz "considerado na Recuperação", item 2.7 do modelo), obras condicionadas do 3.2.3 (fora do modelo; custeio pelo Anexo 9) e obras do acompanhamento fora do PER.

## Acompanhamento financeiro

`per_obras/acompanhamento_financeiro_cerrado.py` usa a mesma lógica da ECO050 (`financeiro_comum.py`): `fin_mensal` com `revisao_negativa`, `fin_acumulado`, `fin_resumo` com conferência mensal que termina com erro se não fechar, mesmas regras de datas reais. Diferenças:
- todo o item 4 é rateado; a parte não rateada é o 4.4, que é zero (coluna `valor_nao_rateado_4_4`);
- a data-base é jul/2016;
- linhas sem valor entram em `fin_mensal` com valor vazio e ficam fora do resumo;
- `sem_acompanhamento` vira `tipo_registro` = `sem_serie_sem_informacao`, com 0% executado.

A fonte tem 21 meses (abr/2024 a abr/2026). O Trevão (ECC-0001) aparece com 130,9% executado em set–dez/2024; foi mantido como na fonte.

## Pendências e pontos a discutir (Cerrado)

1. **Obras sem série.** 84 dos 145 acessos, a marginal de Monte Alegre (TH 11), a passarela de Aparecida do Rio Doce, as edificações (exceto pesagem e fibra) e algumas iluminações estão com prazo vencido e sem série. Hoje contam como 0% executado (`sem_acompanhamento`). Decidir se tratamos como concluídas antes da série.
2. **Lado das marginais.** Leste/Oeste do acompanhamento foi convertido em LD/LE sem verificar o sentido (LD = sentido Uberlândia–Jataí). Só muda o valor no TH 6 (0,7 × 0,8 km).
3. **Complementação das passarelas de Ituiutaba para pista dupla** (estudo, 13º/14º ano, R$ 0,93 mi no 4.1 do modelo): não está no PER; o valor foi rateado entre as demais obras do 4.1.
4. **4.2 sem série = `condicionada_nao_acionada`**, como pedido. No PER atualizado, porém, a duplicação dos TH 13–15 (13º/14º ano), as faixas adicionais (Tabela 3) e os retornos têm prazo fixo; o gatilho só antecipa.
5. **Edificações (4.3)** entram como linhas do Fator D por tipo × UF, sem km, porque o PER não as lista. Validar se devem ficar no cadastro ou como valor não rateado (como o 4.3 de projetos da ECO050).
6. **Marginais fora do PER** (`ECC-EXT-MAR-01` a `06`) e interseção de Paranaiguara (5,9 km do km do estudo) estão com `a_confirmar`.
7. **Ano 1 = 2020** para converter prazos em ano civil: a confirmar no contrato.

### Decisões e pontos em aberto (discussão de out/2026)

1. **Obras do 4.2 com prazo fixo no PER e sem série** (hoje `condicionada_nao_acionada`): em aberto, o usuário vai definir a solução.
2. **Obras com prazo vencido e sem nenhuma série** (`sem_acompanhamento`, contadas como 0% executadas): ficam como estão até aparecerem no acompanhamento de obras.
3. **Obras condicionadas ao gatilho de tráfego** (16 linhas DCO/FCO, sem `valor`): nenhuma aparece no acompanhamento (nenhum gatilho acionado). Há custo estimado no estudo: `BR_364_365_CAPEX_ORÇAMENTO_REV8.xlsb` (zip "Modelagem Financeira – Planilhas"), aba "Duplicações", linha 799 "TOTAL DAS DUPLICAÇÕES + PROJETOS", colunas ST-1 a ST-19 (TH16 = ST-16A + ST-16B), e aba "Faixas Adicionais Pista Dupla", linha 799, ST-10D a ST-12D. Soma ≈ R$ 1,38 bi (jul/2016, sem REIDI). Conferido: ST-13/14/15 da mesma aba = custos do Fator D usados no item 4. Ideia inicial do usuário, ainda não decidida: atribuir o valor do estudo a essas obras e, se forem executadas, distribuir o valor da mesma forma que as demais. Fonte concorrente: aba "comparativo" do Fator D traz o 4.2 com R$ 421,3 mi (o modelo final usa R$ 379,3 mi).
4. **Rio Minas**: só a ligação PER × acompanhamento está feita (`per_obras/ligacao_riominas.md`); série de % mensal e valor ficam para discussão posterior.
