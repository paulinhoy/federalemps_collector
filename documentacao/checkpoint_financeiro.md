# Checkpoint: valores financeiros das obras (out/2026)

Situação da busca por valores e cronogramas das obras dos 3 empreendimentos, **só no portal da ANTT**. O detalhe completo, com link, página e célula de cada fonte, está em [`pesquisa_financeiro_antt.md`](pesquisa_financeiro_antt.md). Os documentos baixados estão em `dados/pesquisa_financeiro/` (fora do git), com o inventário em `dados/pesquisa_financeiro/inventario.csv` (887 arquivos mapeados, 255 baixados).

## 1. Conclusão em uma frase

Há **valor inicial previsto por obra** só na Ecovias do Cerrado. Na ECO050 ele existe só para algumas obras incluídas depois do contrato. Na Rio Minas ele **não é publicado**. **Valor gasto por obra não existe** para nenhuma das três.

## 2. Tipos de valor (não misturar)

| Tipo | Significado | Fonte típica |
|---|---|---|
| **Inicial (leilão)** | Orçamento do estudo de viabilidade, a preços da data-base do contrato | Planilhas do estudo de viabilidade (EVTEA) |
| **Aprovado em revisão** | Orçamento aceito pela ANTT para obra incluída depois do contrato | Notas técnicas das revisões |
| **Estimativa atual da concessionária** | Quanto a concessionária diz hoje que a obra custa | Aba "Planilha base" do acompanhamento (abr/2026) |
| **Realizado** | Custo efetivo | Só total anual nas demonstrações financeiras; **não há por obra** |

## 3. O que existe por empreendimento

| | ECO050 (104) | Ecovias do Cerrado (103) | Ecovias Rio Minas (105) |
|---|---|---|---|
| **Valor inicial por obra** | ⚠️ Não. O estudo de 2013 (`modelo-economico-financeiro-eco-050.xlsx`, aba "PER") está só **por grupo do PER × ano** (ex.: Duplicações R$ 647,6 mi, linha 78) | ✅ `fator-d.xlsx`, aba "Ampliação", coluna J, preços de **jul/2016**. Obras com km (marginais VM-1 a VM-6, duplicações ST-13 a ST-15, Trevão, Xapetuba, correções de traçado, faixas adicionais) e obras por **tipo × quantidade** (passarelas, rotatórias, acessos: só valor unitário) | ❌ Não publicado. Só o total: Capex R$ 8,8 bi e Opex R$ 8,5 bi (notícia da ANTT, data-base jan/2021) |
| **Aprovado em revisão, por obra** | ✅ 12 retornos em nível (NT GEGIR 2023, p.11–15) e recuperação do trecho DNIT por segmento, R$ 150,5 mi a preços de mai/2012 (NT 145/2019, p.13) | Nenhuma obra incluída por revisão até a 4ª Revisão Ordinária | Nenhuma obra incluída por revisão (tarifa do FCM = 0) |
| **Estimativa atual da concessionária** | "Planilha base" abr/2026: 17 obras, R$ 248,6 mi, sem data-base | "Planilha base" abr/2026: 31 obras, R$ 210,0 mi, sem data-base | ❌ Os arquivos "CAPEX" só têm pesos em % |
| **Capex/Opex total do leilão** | Investimentos R$ 3.027,9 mi; custos operacionais R$ 1.965,6 mi | Capex R$ 2.062,0 mi; Opex R$ 2.531,9 mi | Capex R$ 8,8 bi; Opex R$ 8,5 bi |
| **Realizado (total por ano, DFs)** | 2025: R$ 262,9 mi | 2025: R$ 278,8 mi | 2025: R$ 1.532,6 mi |
| **Data-base contratual / índice** | mai/2012, IPCA (divergência: mar/2012 em quadros da 13ª revisão) | jul/2016, IPCA (o edital diz set/2016) | out/2021, IPCA (a notícia de Capex usa jan/2021) |
| **Cronograma por obra** | Planilha base (início, entrega estimada); planejamentos anual e quinquenal (com ID SIGICOR a partir de 2026) | PER atualizado p.37–44 (ano de concessão por obra); Planilha base (12 com entrega real) | Planejamento global rev. 04: **início e fim de 845 obras** (jun/2024 a set/2030); PER p.52–54 |
| **Reajustes e revisões** | Completo 2015–2026 (seção 4.1 da pesquisa) | 2020–2024; 2025/2026 não publicados | 2022–2026 |

## 4. Verificações feitas por nós (além do agente de pesquisa)

- ECO050, Planilha base: coluna AC soma **R$ 248.597.000**, igual ao relatório.
- Cerrado, `fator-d.xlsx` aba "Ampliação": conferidas as linhas 4–120 (cabeçalho na linha 4, valores na coluna J). Ex.: linha 17 VM-1 km 5–8,5 = R$ 8.874.507,74; linha 22 VM-4 km 688–691,5 = R$ 17.972.952,51; linha 12 Trevão = R$ 17.525.784,62.

## 5. Cuidados conhecidos

- **Não usar** os R$ da planilha "Execução acumulada" da ECO050: são de outra concessão (Autopista Litoral Sul).
- Os valores iniciais estão a preços antigos (2012/2016). Para comparar com valores atuais, corrigir pelo IPCA (o IRT da ECO050 em 2026 é 2,22).
- A lista do leilão não bate um a um com a lista do acompanhamento (nomes e agrupamentos diferentes). Ligar por **rodovia + km**.
- Planilha base: datas em texto inválidas na Cerrado ("31/09/2025"); Capex repetido em linhas da ECO050 (km 286,5 = km 196,5).
- Pendências de leitura: arquivos `.xlsb` do Cerrado (precisa do pacote `pyxlsb`) e cerca de 50 PDFs escaneados sem texto (lista na seção 6.1 da pesquisa).

## 6. Opções de próximos passos (a decidir)

1. Tabela `valor_inicial_por_obra` (valor, data-base, tipo do valor, fonte com link/linha, `obra_id` ligado por rodovia + km): Cerrado completa, ECO050 com retornos, trecho DNIT e Planilha base, Rio Minas marcada como "não publicado".
2. Ler os `.xlsb` do Cerrado para localizar as obras que hoje só têm valor por tipo × quantidade.
3. Incluir a aba "Planilha base" no `consolidar.py`, porque deve se repetir nos próximos meses (estimativa atual + datas de início e entrega).
4. Preencher `id_sigicor` da ECO050 a partir dos planejamentos anual e quinquenal.
5. Para a Rio Minas, decidir se vale buscar fora da ANTT (ex.: estudo do leilão em BNDES/PPI).
