# Cadastro de obras da ECO050 (id 104, EMG)

**Objetivo:** ter uma linha por obra esperada na concessão, na versão mais atual (km corrigido), com o valor do item 4 do modelo econômico-financeiro rateado por obra, para carregar no banco de dados. O histórico das mudanças fica em `per_obras/alteracoes_eco050.md` e `.csv`.

## Como rodar

```
python per_obras/extrair_modelo_eco050.py     # item 4 do modelo -> dados/per_obras/modelo_item4_eco050_*.csv
python per_obras/montar_cadastro_eco050.py    # -> dados/per_obras/cadastro_obras_eco050.csv e .xlsx
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

`per_obras/acompanhamento_financeiro_eco050.py` cruza o cadastro com o acompanhamento mensal da ANTT (obra × mês) e gera `fin_mensal_eco050.csv`, `fin_acumulado_eco050.csv` e `fin_resumo_eco050.csv` (mais `fin_eco050.xlsx`) em `dados/per_obras/`. Colunas em `per_obras/dicionario_colunas.md` (tabelas 10 a 12).

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
