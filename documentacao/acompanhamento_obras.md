# Acompanhamento de obras: histórico consolidado (ANTT, Acompanhamento Físico Mensal)

Escopo (empreendimentos do PELT-MG, ver `empreendimentos.json`):

| id_empreendimento | Empreendimento | slug ANTT | Prefixo do `obra_id` |
|---|---|---|---|
| 105 | Ecovias Rio Minas | `ecoriominas` | `ERM-` |
| 103 | Ecovias do Cerrado | `ecovias-do-cerrado` | `ECC-` |
| 104 | ECO050 (Ecovias Minas Goiás) | `eco050` | `EMG-` |

Fonte: portal da ANTT, pasta "Percentuais de Avanço Físico dos Cronogramas de Obras e Serviços do Planejamento Anual" de cada concessão, **todos os anos**:
`https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/<slug>/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-.../<ano>/`

## 1. Como rodar

```
pip install requests pandas openpyxl
python acompanhamento_obras/baixar.py        # baixa/atualiza todos os anos (só o que é novo ou mudou)
python acompanhamento_obras/consolidar.py    # gera dados/acompanhamento_obras/consolidado/ (≈ 2 min)
```

Estrutura dos dados (fora do git):
```
dados/acompanhamento_obras/
  brutos/<slug>/<ano>/arquivos/      arquivos originais do portal (versões antigas em arquivos/_versoes/)
  brutos/<slug>/<ano>/extraido/      conteúdo dos ZIPs
  consolidado/                       tabelas geradas (seção 3)
  manifesto.json                     url, tamanho, sha256 e datas de cada arquivo baixado
  alteracoes.jsonl                   log do que apareceu ou mudou a cada execução do download
  historico_resumo.json              arquivos encontrados por empreendimento e ano
```

## 2. O que existe na fonte

| Concessão | Arquivos baixados | Tabela física mensal disponível | Meses consolidados | Meses faltando |
|---|---|---|---|---|
| ECO050 | 36 (2023–2026) | **mar/2024 → abr/2026** | 24 | mai/2024, jul/2024 |
| Ecovias do Cerrado | 38 (2023–2026) | **abr/2024 → abr/2026** | 21 | jun, jul, out/2024; fev/2025 |
| Ecovias Rio Minas | 24 (2024–2026) | **mai/2024 → abr/2026** | 24 | nenhum |

- **Antes de 2024**, ECO050 e Cerrado publicavam outro modelo ("Avanço de Obras": índice % por obra e detalhe por atividade), que **não entrou** nesta consolidação. Rio Minas só tem dados a partir de 2024.
- Cada arquivo publicado vira um **snapshot**: a "foto" da tabela naquele mês. São 71 snapshots, dos quais 69 são "principais" (um por mês).

## 3. Tabelas geradas (`dados/acompanhamento_obras/consolidado/`)

Todas trazem `id_empreendimento` (PELT) e `concessao` (slug), exceto `serie_mensal`, `etapas_por_snapshot`, `evolucao` e `mudancas_por_obra`, que se ligam pelo `snapshot`/`obra_id`.

| Arquivo | Uma linha por… | Para quê |
|---|---|---|
| `marcos_por_obra.csv` | obra | **Marcos e histórico resumido de cada obra** (seção 3.2): quando surgiu, 1º avanço, conclusão, última variação, revisões, mais um texto explicando a trajetória |
| `obras_por_snapshot.csv` | obra × mês de referência | **Tabela limpa principal**: campos da obra repetidos + mês de referência + situação + % previsto e executado |
| `obras.csv` | obra | Catálogo: `obra_id` estável, código PER, descrição, local, 1ª e última aparição, situação e % no último mês |
| `evolucao.csv` | concessão × mês | Quantas obras entraram/saíram, quantas tiveram o plano reescrito, o executado revisado, a situação alterada |
| `mudancas_por_obra.csv` | obra × transição de mês | O que mudou em cada obra de um mês para o seguinte (de → para) |
| `etapas_por_snapshot.csv` | etapa × mês | Etapas do eventograma da Rio Minas (Pavimentação, Drenagem…), com peso, ligadas à obra-mãe |
| `serie_mensal.csv` | obra × mês × previsto/executado × snapshot | Valores mensais exatamente como na fonte, para auditoria ou gráficos |
| `snapshots.csv` | arquivo | Mês de referência, como foi definido, data de publicação, aba e linha do cabeçalho, alertas |
| `consolidado.xlsx` | — | snapshots, obras, marcos_por_obra, obras_por_snapshot, evolucao e mudancas_por_obra em abas |

### Colunas principais de `obras_por_snapshot`

| Coluna | Significado |
|---|---|
| `obra_id` | Código estável da obra, criado por nós (`EMG-0001`, `ECC-0001`, `ERM-0001`) |
| `vinculo` | Como a obra foi reconhecida em relação ao mês anterior: `exata`, `km`, `similaridade`, `item_per_alterado` ou `nova` (ver seção 4.4) |
| `item_per`, `id_sigicor` | Códigos da fonte. O item PER **não identifica a obra sozinho**: várias obras compartilham o mesmo item |
| `mes_referencia` | Mês a que os dados se referem (seção 4.1) |
| `data_publicacao` | Data de publicação, quando consta no nome do arquivo ou no texto "Atualizado - dd/mm/aaaa" |
| `situacao` | Situação até o mês, como informada (CONCLUÍDA, ATRASADA, CONFORME PLANEJAMENTO, ADIANTADA, NÃO INICIADA) |
| `pct_executado_acum_ate_ref` | % executado acumulado até o mês de referência (0 a 1) |
| `pct_previsto_acum_ate_ref` | % que deveria estar executado até o mês de referência, segundo o plano do ano (seção 4.3) |
| `pct_meta_fim_ano_concessao` | % previsto para o fim do ano de concessão corrente |
| `pct_*_no_mes_ref` | Avanço previsto e executado **no próprio mês** |
| `ano_concessao_ref` | Ano de concessão do mês de referência (ex.: "Ano concessão: 13º (jan/26-dez/26)") |
| `principal` | `True` se este arquivo é o que vale para o mês (quando há mais de um) |
| `alerta` | Soma acima de 100% (seção 6) |
| `pct_executado_anos_anteriores` | Executado acumulado antes do 1º mês da planilha (coluna "Anos anteriores"/"Acumulado até o Nº ano") |

### 3.2 `marcos_por_obra`: quando a obra surgiu, começou, terminou e mudou

Cada pergunta tem **duas respostas**, porque a concessionária reescreve o passado:
- **relatado**: o que foi dito em cada mês (vem de `obras_por_snapshot`);
- **último arquivo**: o que a planilha mais recente da obra diz sobre os meses passados (vem de `serie_mensal`).

Quando as duas divergem, houve revisão retroativa.

| Coluna | Significado |
|---|---|
| `surgiu_em`, `situacao_ao_surgir`, `pct_exec_ao_surgir` | 1º mês em que a obra aparece e como estava |
| `ja_iniciada_ao_surgir` | Já tinha execução ao aparecer: o início real é anterior à série |
| `primeiro_avanco_relatado_em`, `pct_no_primeiro_avanco` | 1º mês em que o executado acumulado ficou > 0 |
| `inicio_execucao_ultimo_arquivo` | 1º mês com execução segundo a planilha mais recente (ou "antes de aaaa-mm" se havia acumulado de anos anteriores) |
| `inicio_revisado_retroativamente` | As duas datas de início divergem por revisão (não por falta de publicação) |
| `atingiu_100_em` | 1º mês com executado ≥ 99,5% |
| `situacao_concluida_em` | 1º mês com situação "CONCLUÍDA". Pode não existir mesmo com 100% |
| `caiu_abaixo_100_em`, `queda_na_virada_do_ano_concessao` | Voltou a < 100% depois de concluir. Na virada do ano de concessão, é um **serviço recorrente** (sinalização, conservação) que recomeça o ciclo anual |
| `ultima_variacao_exec_em`, `ultima_variacao_exec_pp`, `meses_com_variacao_exec` | Última mudança do executado acumulado (em pontos percentuais) e em quantos meses ele mudou |
| `revisoes_exec_retroativas`, `ultima_revisao_exec_retroativa_em` | Quantas vezes o executado de meses passados foi alterado |
| `reprogramacoes_previsto_passado` | Quantas vezes o previsto de meses passados foi reescrito |
| `mudancas_situacao` | Quantas vezes a situação mudou |
| `ultima_ref`, `situacao_ultima`, `pct_exec_ultimo`, `pct_prev_ultimo` | Último dado disponível |
| `presente_no_ultimo_snapshot`, `meses_ausente` | Se a obra saiu da tabela, e meses publicados em que ela não apareceu |
| `vinculo_aproximado` | A obra foi ligada entre meses por km/similaridade/troca de item PER: conferir |
| `alerta_acima_100` | Algum mês com soma > 100% |
| `historico` | Texto com a trajetória da obra |

Exemplo (`EMG-0016`, Trevo Tipo Diamante km 280,3):

> Surgiu em 2024-03 (NÃO INICIADA, 0,0% executado). 1º avanço relatado em 2024-04 (14,5%). Na planilha mais recente o início da execução está em 2024-05 (revisão retroativa). Executado de meses passados revisado 3x (última em 2025-04). Previsto de meses passados reescrito 6x (última em 2026-04). Atingiu 100% em 2025-11. Situação nunca foi 'CONCLUÍDA' (última: CONFORME PLANEJAMENTO). Última variação do executado em 2026-04 (+0,03 p.p.). Último dado (2026-04): 100,0% executado, 100,0% previsto, CONFORME PLANEJAMENTO.

Para ver o detalhe mês a mês de uma obra: filtre `obras_por_snapshot` pelo `obra_id` (com `principal = True`) e `mudancas_por_obra` para o que mudou em cada transição.

Números (abr/2026):

| | ECO050 (104) | Cerrado (103) | Rio Minas (105) |
|---|---|---|---|
| Obras | 32 | 267 | 795 |
| Com algum avanço relatado | 26 | 241 | 237 |
| Atingiram 100% | 17 | 225 | 115 |
| Situação "CONCLUÍDA" | 9 | 222 | 115 |
| Início revisado retroativamente | 3 | 7 | 89 |
| Caíram abaixo de 100% depois (na virada do ano) | 0 | 6 (0) | 79 (73) |

## 4. Regras de tratamento

### 4.1 Mês de referência
O nome do arquivo segue padrões diferentes (`emg-abril`, `05_05_2026_…`, `ecoriominas-set24`, `-1.xlsx`). A regra, por ordem de confiança:
1. mês escrito no nome do arquivo ou do ZIP (ex.: `abril`, `set24`, `04-2026`);
2. data de publicação (`dd_mm_aaaa` no nome ou "Atualizado - dd/mm/aaaa" na planilha) **menos 1 mês**, porque o arquivo publicado em 05/05 traz os dados de abril;
3. se não houver nenhum dos dois, o mês é deduzido dos dados: último mês com executado preenchido, ou último mês com avanço > 0 quando o ano todo vem preenchido com zeros. Isso aconteceu em 13 arquivos, marcados em `snapshots.alerta`.

Quando dois arquivos caem no mesmo mês, vale o publicado por último (2 casos na Cerrado: mai/2024 e nov/2024, versões com pequenas diferenças).

### 4.2 Estrutura da planilha
- O cabeçalho e as colunas mensais são localizados pelo **conteúdo** ("Item PER", "Comparativo", datas), não pela posição. A linha do cabeçalho varia (5ª, 6ª…) e a ordem das colunas também.
- Cada obra ocupa 2 linhas (previsto/executado). Os campos da obra ficam na linha "previsto" e são repetidos na "executado".
- Os meses são agrupados em blocos "Ano concessão: Nº". Quando um mês aparece em dois blocos (Cerrado: jan/2025 em dois anos de concessão; Rio Minas: bloco "3º ano" duplicado), vale o primeiro valor preenchido.
- Valores em texto (`"0,00%"`, `"-"`) e km em estaca (`298+660`) são convertidos.
- **Eventograma (Rio Minas, a partir de out/2025):** a linha "Eventograma" é a obra, e as linhas seguintes com peso numérico são suas etapas. A obra vai para `obras_por_snapshot` e as etapas para `etapas_por_snapshot`.

### 4.3 Previsto acumulado
O previsto de cada ano de concessão é um **plano novo** que reprograma o que faltou do ano anterior. Somar os previstos de anos diferentes passa de 100%. Por isso:
- **executado acumulado** = acumulado dos anos anteriores + avanços mensais até o mês de referência;
- **previsto acumulado** = executado real até o início do ano de concessão + previsto desse ano até o mês de referência.

### 4.4 Identidade da obra entre meses
Não existe um código único e estável na fonte. O item PER se repete entre obras, e a descrição é reescrita com frequência. A ECO050, por exemplo, alterna entre "Duplicação - km 95,700 ao 99,440" e "Duplicação da Travessia Urbana de Cristalina do km 95,700 ao km 99,440", e às vezes troca o item PER (3.2.1.2 → 3.2.3 → 3.2.1.2).

O `obra_id` é atribuído percorrendo os meses em ordem, ligando cada linha a uma obra já conhecida por:
1. mesma chave (item PER + descrição normalizada);
2. mesmo item PER e mesmo km inicial/final (±50 m);
3. mesmo item PER e descrição ≥ 85% parecida;
4. outro item PER, descrição ≥ 93% parecida e km compatível;
5. senão, obra nova.

O método usado fica na coluna `vinculo` para conferência.

## 5. Resultados: como os dados evoluíram

| | ECO050 | Ecovias do Cerrado | Ecovias Rio Minas |
|---|---|---|---|
| Obras distintas no período | 32 | 267 | 795 |
| Presentes em todos os meses | 23 | 18 | 0 |
| Obras no 1º → último mês | 27 → 24 | 89 → 71 | 14 → 699 |
| % executado médio, 1º → último mês | 24% → **83%** | 90% → 72%* | 15% → 12%* |
| Situação no último mês (abr/2026) | 13 conforme, 9 concluídas, 2 não iniciadas | 48 concluídas, 17 não iniciadas, 5 atrasadas | 530 não iniciadas, 61 atrasadas, 52 conforme, 51 adiantadas |
| Previsto do passado reescrito (obra × mês) | 94, em 8 meses | 181, em 9 meses | 523, em 10 meses |
| Executado do passado revisado (obra × mês) | 43 | 109 | 234 |

\* A média cai porque **entraram obras novas com 0%**, não porque o avanço regrediu.

Principais achados:
- **O escopo muda muito.** A Rio Minas foi de 14 obras (mai/2024) para 186 (set/2024), 246 (set/2025), 539 (out/2025, plano do 4º ano com CAPEX completo) e 699 (abr/2026, revisão "rev0"). A Cerrado alternou entre arquivos de ~60–90 obras e versões detalhadas de 186 trechos (set–dez/2024).
- **O plano é reescrito retroativamente.** Em vários meses, o previsto de meses já passados foi alterado: 18 obras da ECO050 em abr/2024, ago/2024 e abr/2025, e 340 obras da Rio Minas em abr/2026. Com isso, o status "atrasada/conforme" muda sem avanço real: a comparação é feita contra um plano que mudou.
- **O executado também é revisado.** Valores já informados são corrigidos em meses seguintes (para cima e para baixo). Exemplo: em jun/2025 a Rio Minas corrigiu abril e maio de 84 obras. A coluna `executado_passado_alterado` de `mudancas_por_obra` mostra cada caso.
- **Campos quase vazios na fonte:** Município (36% das linhas na ECO050, 28% na Cerrado, 2% na Rio Minas), Data de Início e Previsão de Término (≈ 0% nas 3 concessões; só algumas datas na Rio Minas em 2024). Km inicial está bem preenchido em ECO050 (96%) e Cerrado (90%), mas não na Rio Minas (2%), onde o km vem dentro da descrição. **Marcos de data não estão disponíveis** nesta tabela.

## 6. Limitações

- **52 linhas** somam mais de 100% (coluna `alerta`). Na fonte, alguns meses vêm como % acumulado em vez de incremento mensal. Por exemplo, a OAE km 848+700 da Cerrado tem 100% em todos os meses de 2024. Não corrigimos automaticamente.
- O vínculo de obras é heurístico. Revisar as linhas com `vinculo` = `similaridade`/`item_per_alterado`, e as "novas" nos meses de mudança de escopo.
- 13 arquivos não têm mês no nome nem data de publicação. O mês foi deduzido dos dados, e a sequência resultante preenche exatamente as lacunas, o que dá boa confiança.
- O modelo "Avanço de Obras" (2023 e paralelo) e a "Planilha base" (abr/2026, com Capex) não estão nesta consolidação.
- Marcos ficam presos aos meses publicados: com mês faltando (ex.: Cerrado), o marco pode cair no mês seguinte ao real. 302 obras já tinham execução ao aparecer pela 1ª vez; para elas o início real é anterior à série.
- 12 obras caíram abaixo de 100% fora da virada do ano de concessão: podem ser correções da fonte ou vínculo de identidade errado. Vale conferir.

## 7. Desafios para automatizar a atualização

Ordenados do mais crítico ao menos crítico:

1. **O mês de referência não é declarado de forma estruturada.** Depende do nome do arquivo, que muda de padrão a cada publicação ("-1", "-hsr-2", "antt_…", ZIP sem mês). Mitigação já implementada: cascata nome → data de publicação → dados, com alerta. Recomendado: **revisão humana do `snapshots.csv` a cada carga**, que é rápida (1 linha por arquivo novo).
2. **Identidade das obras.** Sem código estável, cada nova publicação pode renomear, reclassificar o item PER, dividir ou juntar obras. A heurística liga a maioria, mas mudanças de escopo geram "novas" obras que podem ser renomeações. Recomendado: manter uma **tabela de correspondência manual** (`obra_id` ↔ chave) que o script respeite, para corrigir casos pontuais sem mexer no código. Hoje os IDs são recalculados a cada execução e podem mudar se um arquivo antigo for incluído ou removido. Para produção, os IDs precisam ser **persistidos** (gerados uma vez e só acrescentados).
3. **O modelo da planilha muda sem aviso.** Já vimos: colunas de km/município removidas, linha do cabeçalho mudando, blocos duplicados, "ITEM DO PER", "REALIZADO", eventograma com pesos, grupo "anos anteriores" com 2 colunas. O leitor detecta pelo conteúdo, mas um modelo novo pode passar despercebido e gerar números errados **sem erro de execução** (foi assim com o "Acumulado até o 10º Ano"). Recomendado: **testes de sanidade a cada carga**, bloqueando a carga se falharem:
   - obra CONCLUÍDA com executado < 95%;
   - soma > 100%;
   - queda de executado;
   - número de obras muito diferente do mês anterior;
   - mês de referência fora da sequência.
4. **Dados retroativos são reescritos.** Como o previsto e o executado do passado mudam, o histórico correto é **guardar cada snapshot**, sem sobrescrever. O desenho atual já faz isso (`snapshot` + `mes_referencia`). A "verdade" de um mês depende de qual publicação você usa.
5. **Arquivos duplicados ou concorrentes para o mesmo mês** (republicações com pequenas diferenças), sem data de publicação para desempatar. O site da ANTT não informa data de modificação nem ETag. Hoje a regra de desempate é heurística.
6. **Infraestrutura:**
   - caminhos longos no Windows (resolvido com `\\?\`);
   - downloads grandes que caem no meio (18 MB; o download agora tenta 3 vezes);
   - leitura lenta das planilhas com 16 mil colunas formatadas (resolvido limitando a largura);
   - a consolidação completa leva ≈ 2 min e cresce com o histórico. Para incremental, processar só os snapshots novos e acrescentar.
7. **Novo ano de concessão.** Cada concessão vira o ano em um mês diferente (Cerrado e ECO050 em janeiro, Rio Minas em outubro), e o plano do ano novo costuma vir com escopo e descrições reorganizados. É justamente quando o vínculo de obras mais falha, então esses meses merecem revisão.

### Fluxo sugerido para a automação
```
baixar.py  ->  consolidar (só snapshots novos)  ->  testes de sanidade  ->  [falhou? revisão manual]
                                                                                   ->  publicar tabelas
```
Com IDs persistidos, uma tabela manual de correspondência de obras e revisão do `snapshots.csv` nas viradas de ano, o processo fica estável.
