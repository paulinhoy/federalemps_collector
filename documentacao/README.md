# Coleta de dados de avanço físico de obras — concessões rodoviárias (ANTT)

_Gerado em 05/10/2026 a partir de `dados/resumo.json`._

## 1. Objetivo

Baixar, descompactar e organizar por concessão os arquivos de **acompanhamento do avanço físico das obras** publicados pela ANTT, usando sempre o **último ano que tenha dados** em cada concessão.

## 2. Fonte dos dados (links usados no download)

Todos os arquivos vêm do portal da ANTT em gov.br. Nenhum outro site foi usado.

- **Lista das concessões (de onde saem os nomes/slugs):**  
  <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes>
- **Padrão da página de acompanhamento de cada concessão** (basta trocar `<slug>`):  
  `https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/<slug>/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual`
- **Padrão da pasta de cada ano:**  
  `https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/<slug>/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/<ano>`
- **Padrão do arquivo baixado:**  
  `https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/<slug>/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/<ano>/<nome-do-arquivo>`  
  É a URL **sem** o sufixo `/view`: com `/view` o portal devolve uma página HTML; sem ele, devolve o arquivo em si.

Exemplo real (ECO050 / Ecovias Minas Goiás, 2026):

- Página: <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual>
- Arquivo: <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/02_04_2026_acompanhamento_fisico_mensal_emg.xlsx>
- Arquivo: <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___01-2026-minas-goias.zip>
- Arquivo: <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___04-2026minasgoias.zip>
- Arquivo: <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/i___execucao_mensal___02-2026-minas-goias.zip>

O nome da subpasta varia entre concessões (`...dos-cronogramas-de-obras...` ou `...de-obras...`); o script descobre o nome real listando a pasta `acompanhamento-de-obras` de cada uma. A lista completa de URLs baixadas está na seção 6.

## 3. O que foi feito

1. **Validação inicial (ECO050).** O script `baixar_antt_2026.py` baixou e descompactou os 3 ZIPs de 2026 (jan, fev, abr) da Ecovias Minas Goiás. Funcionou, mas a lista de arquivos era fixa (março e os meses após abril não estavam).
2. **Análise do `Acompanhamento_fisico_mensal`.** Comparados os 3 meses: a estrutura é igual (1 aba, 244 linhas, 58 colunas). Muda o preenchimento dos meses novos; o **previsto de períodos passados é reescrito** (cerca de 78 valores de 2025 entre fev e abr, só na linha `previsto`); e o status de 14 obras passou de `ATRASADA` para `CONFORME PLANEJAMENTO`.
3. **Mapeamento contra `20260917_Atributos_rev01.xlsx`.** Para ECO050, a melhor fonte cadastral é a planilha `EMG_Acompanhamento de Obras_ABRIL_26.xlsx` (17 obras, 5 grupos). Campos financeiros (valor medido, aditivo, reajuste, desapropriação, supervisão), data de término real e SRE **não existem** nas fontes.
4. **Generalização para todas as concessões.** Dois scripts novos:
   - `listar_concessoes.py`: lê a lista da ANTT e grava `concessoes.json` (41 concessões).
   - `baixar_ultimo_ano.py`: para cada concessão encontra a pasta de acompanhamento, identifica o último ano com arquivos, baixa tudo e extrai os `.zip`.
5. **Correções feitas durante os testes:**
   - Nome da subpasta varia entre concessões: passou a ser descoberto dinamicamente.
   - Caminhos longos no Windows (limite de 260 caracteres) quebravam a extração de alguns ZIPs: passou a usar o prefixo `\\?\`.
   - Arquivos `.xlsx`/`.xlsm` eram extraídos por engano (são ZIPs por dentro) e geravam pastas de XML: agora só `.zip` de verdade é extraído.

## 4. Como reproduzir

```
pip install requests
python listar_concessoes.py          # gera concessoes.json
python baixar_ultimo_ano.py          # baixa todas as concessões
python baixar_ultimo_ano.py eco050 via-040   # opcional: só algumas
```

O script pula arquivos já baixados, então pode ser rodado de novo para atualizar.

## 5. Resultados

| Status | Concessões |
|---|---|
| Baixadas e organizadas | 26 |
| Pasta existe, mas está vazia no site | 14 |
| Sem a pasta de percentuais de avanço físico | 1 |
| **Total** | **41** |

- **92 arquivos** baixados (108 MB) nas 26 concessões com dados.
- **Nenhum erro** de download, de integridade (ZIPs íntegros, nenhum arquivo vazio, nenhum HTML disfarçado de arquivo) ou de extração na execução final.
- Anos escolhidos: **2026** (17 concessões), **2025** (6 concessões), **2024** (3 concessões).

### Formatos encontrados

| Formato | Qtd baixada | Observação |
|---|---|---|
| `.xlsx` | 47 | Planilhas soltas; em várias concessões não há ZIP |
| `.zip` | 42 | Contêm `.xlsx`, `.xlsm` e `.pdf`; extraídos automaticamente |
| `.pdf` | 2 | Portarias e relatórios, não são dados tabulares |
| `.xls` | 1 | Formato antigo (Motiva Pantanal): precisa de `xlrd`, não de `openpyxl` |
| `.csv` | 0 | Nenhuma concessão publicou CSV |

Dentro dos ZIPs foram extraídos 47 `.xlsx`, 1 `.xlsm` e 3 `.pdf`. Não há ZIP dentro de ZIP nem `.rar`/`.7z`.

### Concessões baixadas

| Concessão | Slug | Ano | Arquivos baixados |
|---|---|---|---|
| Autopista Fluminense | `autopista-fluminense` | 2024 | 2 pdf, 1 xlsx |
| Autopista Litoral Sul | `autopista-litoral-sul` | 2026 | 3 zip |
| Autopista Planalto Sul | `autopista-planalto-sul` | 2026 | 3 zip |
| Autopista Régis Bittencourt | `autopista-regis-bittencourt` | 2026 | 3 zip |
| CONCER (Contrato Encerrado) | `concer` | 2024 | 1 xlsx |
| Ecovias Araguaia | `ecovias-araguaia` | 2026 | 1 xlsx, 3 zip |
| Ecovias Capixaba | `ecovias-capixaba` | 2025 | 8 xlsx |
| Ecovias Cerrado | `ecovias-do-cerrado` | 2026 | 1 xlsx, 3 zip |
| Ecovias Minas Goiás | `eco050` | 2026 | 1 xlsx, 3 zip |
| Ecovias Ponte | `ecoponte` | 2025 | 7 xlsx |
| Ecovias Rio Minas | `ecoriominas` | 2026 | 1 xlsx, 3 zip |
| Ecovias Sul (Contrato Encerrado) | `ecosul-contrato-encerrado` | 2025 | 9 xlsx, 3 zip |
| EPR Litoral Pioneiro | `epr-litoral-pioneiro` | 2026 | 2 zip |
| EPR Via Mineira | `epr-via-mineira` | 2026 | 2 xlsx, 2 zip |
| Motiva Minas SP | `motiva-minas-sp` | 2025 | 3 xlsx |
| Motiva Pantanal | `motiva-pantanal` | 2025 | 1 xls, 1 xlsx |
| Nova Rota do Oeste | `rota-do-oeste` | 2026 | 3 xlsx |
| RioSP | `ccr-rio-sp` | 2026 | 2 zip |
| Transbrasiliana | `Transbrasiliana` | 2026 | 3 zip |
| VIA 040 (Contrato Encerrado) | `via-040` | 2024 | 1 xlsx |
| Via Araucária | `via-araucaria` | 2026 | 2 zip |
| Via Bahia (Contrato Encerrado) Via Bahia | `via-bahia` | 2025 | 4 xlsx |
| Via Brasil BR-163 | `via-brasil` | 2026 | 1 xlsx, 2 zip |
| Via Cristais | `via-cristais` | 2026 | 1 zip |
| ViaCosteira | `ccr-viacosteira` | 2026 | 1 xlsx, 2 zip |
| ViaSul | `viasul` | 2026 | 1 xlsx, 2 zip |

### Concessões sem dados

**Pasta vazia no site** ("Atualmente não existem itens nessa pasta"). Não é falha do script; ao rodar de novo, serão baixadas se a ANTT publicar:

- CONCEBRA (`concebra`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/concebra/documentos-de-gestao/acompanhamento-de-obras>
- Ecovias das Gerais (`ecovias-das-gerais`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-das-gerais/documentos-de-gestao/acompanhamento-de-obras>
- Elovias (`elovias`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/elovias/documentos-de-gestao/acompanhamento-de-obras>
- EPR Iguaçu (`epr-iguacu`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-iguacu/documentos-de-gestao/acompanhamento-de-obras>
- EPR Paraná (`epr-parana`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-parana/documentos-de-gestao/acompanhamento-de-obras>
- Motiva Paraná (`pr-vias`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/pr-vias/documentos-de-gestao/acompanhamento-de-obras>
- Nova 364 (`nova-364`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/nova-364/documentos-de-gestao/acompanhamento-de-obras>
- Nova 381 (`nova-381`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/nova-381/documentos-de-gestao/acompanhamento-de-obras>
- Rodovia do Aço (Caducidade Declarada) (`rodovia-do-aco-caducidade-declarada`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rodovia-do-aco-caducidade-declarada/documentos-de-gestao/acompanhamento-de-obras>
- Rota Verde Goiás (`rota-verde-goias`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-verde-goias/documentos-de-gestao/acompanhamento-de-obras>
- Via Campo (`via-campos`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-campos/documentos-de-gestao/acompanhamento-de-obras>
- Way-153 (`rota-sertaneja`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-sertaneja/documentos-de-gestao/acompanhamento-de-obras>
- Way-262 (`way-262`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/way-262/documentos-de-gestao/acompanhamento-de-obras>
- Way-364 (`rota-agro`): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-agro/documentos-de-gestao/acompanhamento-de-obras>

**Sem a pasta de percentuais de avanço físico:**

- Nova Dutra (Contrato Encerrado) (`nova-dutra`): só existe "Execução acumulada de obras de ampliação de capacidade e melhorias": <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/nova-dutra/documentos-de-gestao/acompanhamento-de-obras/execucao-acumulada-de-obras-de-ampliacao-de-capacidade-e-melhorias>

## 6. Estrutura em disco e URLs de cada arquivo

```
dados/<slug>/<ano>/arquivos/<arquivo>              arquivos originais
dados/<slug>/<ano>/extraido/<nome-do-zip>/         conteúdo de cada ZIP
dados/resumo.json                                  status, ano e URLs por concessão
```

**Autopista Fluminense** (`autopista-fluminense`, 2024)

- `acompanhamento_fisico_mensal_fluminense.xlsx` (0.07 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-fluminense/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2024/acompanhamento_fisico_mensal_fluminense.xlsx>
- `fluminense-janeiro-2024-16o-ano-fonte-50500-0767062023-84-21832519-pdf.pdf` (0.21 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-fluminense/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2024/fluminense-janeiro-2024-16o-ano-fonte-50500-0767062023-84-21832519-pdf.pdf>
- `portaria_216_2019_jan24___afl.pdf` (0.45 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-fluminense/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2024/portaria_216_2019_jan24___afl.pdf>

**Autopista Litoral Sul** (`autopista-litoral-sul`, 2026)

- `acompanhamento_fisico_mensal_litoral_sul___dezembro_25.zip` (0.17 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_litoral_sul___dezembro_25.zip>
- `acompanhamento_fisico_mensal_litoral_sul___fevereiro_25.zip` (0.17 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_litoral_sul___fevereiro_25.zip>
- `acompanhamento_fisico_mensal_litoral_sul___mes_02___ano_19.zip` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_litoral_sul___mes_02___ano_19.zip>

**Autopista Planalto Sul** (`autopista-planalto-sul`, 2026)

- `acompanhamento_fisico_mensal_planalto_sul___19_ano___mes_02.zip` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-planalto-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_planalto_sul___19_ano___mes_02.zip>
- `acompanhamento_fisico_mensal_planalto_sul___dezembro_25.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-planalto-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_planalto_sul___dezembro_25.zip>
- `acompanhamento_fisico_mensal_planalto_sul___fevereiro_26_2.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-planalto-sul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_planalto_sul___fevereiro_26_2.zip>

**Autopista Régis Bittencourt** (`autopista-regis-bittencourt`, 2026)

- `acompanhamento_fisico_mensal_regis_bittencourt_01_2026.zip` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-regis-bittencourt/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_regis_bittencourt_01_2026.zip>
- `acompanhamento_fisico_mensal_regis_bittencourt___04_2026.zip` (0.15 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-regis-bittencourt/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_regis_bittencourt___04_2026.zip>
- `autopista-regis-bittencourt-fevereiro-2026-sei-41636045.zip` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-regis-bittencourt/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/autopista-regis-bittencourt-fevereiro-2026-sei-41636045.zip>

**CONCER (Contrato Encerrado)** (`concer`, 2024)

- `acompanhamento_fisico_mensal_concer.xlsx` (0.04 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/concer/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2024/acompanhamento_fisico_mensal_concer.xlsx>

**Ecovias Araguaia** (`ecovias-araguaia`, 2026)

- `2025-11-19___acompanhamento_fisico_mensal_ecovias_araguaia___janeiro-2026_rev01.zip` (0.08 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-araguaia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/2025-11-19___acompanhamento_fisico_mensal_ecovias_araguaia___janeiro-2026_rev01.zip>
- `acompanhamento-fisico-mensal-de-obras-e-servicos-ecovias-araguaia-marco-2026.xlsx` (0.21 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-araguaia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento-fisico-mensal-de-obras-e-servicos-ecovias-araguaia-marco-2026.xlsx>
- `acompanhamento_fisico_mensal_de_obras_e_servicos___ecovias_araguaia__abril-2026_.zip` (0.20 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-araguaia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_de_obras_e_servicos___ecovias_araguaia__abril-2026_.zip>
- `acompanhamento_fisico_mensal_de_obras_e_servicos___ecovias_araguaia__fevereiro-2026_-xlsx.zip` (0.19 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-araguaia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_de_obras_e_servicos___ecovias_araguaia__fevereiro-2026_-xlsx.zip>

**Ecovias Capixaba** (`ecovias-capixaba`, 2025)

- `acompanhamento_fisico_mensal_eco101_abril25.xlsx` (0.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_abril25.xlsx>
- `acompanhamento_fisico_mensal_eco101_agosto25.xlsx` (0.34 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_agosto25.xlsx>
- `acompanhamento_fisico_mensal_eco101_fevereiro25.xlsx` (0.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_fevereiro25.xlsx>
- `acompanhamento_fisico_mensal_eco101_janeiro25.xlsx` (0.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_janeiro25.xlsx>
- `acompanhamento_fisico_mensal_eco101_julho25.xlsx` (0.34 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_julho25.xlsx>
- `acompanhamento_fisico_mensal_eco101_junho25.xlsx` (0.33 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_junho25.xlsx>
- `acompanhamento_fisico_mensal_eco101_maio25.xlsx` (0.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_maio25.xlsx>
- `acompanhamento_fisico_mensal_eco101_marco25.xlsx` (0.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-capixaba/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_eco101_marco25.xlsx>

**Ecovias Cerrado** (`ecovias-do-cerrado`, 2026)

- `02_04_2026_acompanhamento_fisico_mensal_ecc.xlsx` (0.14 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-do-cerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/02_04_2026_acompanhamento_fisico_mensal_ecc.xlsx>
- `03_03_2026_ecc_avanco_obras_fev_2026.zip` (1.90 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-do-cerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/03_03_2026_ecc_avanco_obras_fev_2026.zip>
- `execucao_mensal___01-2026-ccerrado.zip` (1.83 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-do-cerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___01-2026-ccerrado.zip>
- `execucao_mensal___04-2026cerrado.zip` (3.84 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecovias-do-cerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___04-2026cerrado.zip>

**Ecovias Minas Goiás** (`eco050`, 2026)

- `02_04_2026_acompanhamento_fisico_mensal_emg.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/02_04_2026_acompanhamento_fisico_mensal_emg.xlsx>
- `execucao_mensal___01-2026-minas-goias.zip` (11.58 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___01-2026-minas-goias.zip>
- `execucao_mensal___04-2026minasgoias.zip` (14.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/execucao_mensal___04-2026minasgoias.zip>
- `i___execucao_mensal___02-2026-minas-goias.zip` (11.29 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/eco050/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/i___execucao_mensal___02-2026-minas-goias.zip>

**Ecovias Ponte** (`ecoponte`, 2025)

- `acompanhamento_fisico_mensal_ecoponte-fevereiro-2025.xlsx` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-fevereiro-2025.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-janeiro-2025.xlsx` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-janeiro-2025.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-junho-2025.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-junho-2025.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-maio-2025.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-maio-2025.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-marco-2025-1.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-marco-2025-1.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-marco-2025.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-marco-2025.xlsx>
- `acompanhamento_fisico_mensal_ecoponte-versao-julho-2025-1.xlsx` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoponte/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecoponte-versao-julho-2025-1.xlsx>

**Ecovias Rio Minas** (`ecoriominas`, 2026)

- `acompanhamento_fisico_mensal_ecoriominas_anos_04_capex-rev00-com-pesos-sigicor-_mar-26.xlsx` (2.40 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoriominas/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ecoriominas_anos_04_capex-rev00-com-pesos-sigicor-_mar-26.xlsx>
- `acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor_-riominas.zip` (1.77 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoriominas/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor_-riominas.zip>
- `acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor__abr_26_rev0_.zip` (1.91 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoriominas/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor__abr_26_rev0_.zip>
- `acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor__fev_26.zip` (1.78 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecoriominas/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ecoriominas_anos_04_capex_rev00__com_pesos_sigicor__fev_26.zip>

**Ecovias Sul (Contrato Encerrado)** (`ecosul-contrato-encerrado`, 2025)

- `acompanhamento_fisico_mensal_ecosul-34457323.xlsx` (0.13 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecosul-34457323.xlsx>
- `acompanhamento_fisico_mensal_ecosul-setembro-25.xlsx` (0.13 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ecosul-setembro-25.xlsx>
- `copia-de-abril-acompanhamento_fisico_mensal_ecosul-31755644.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-abril-acompanhamento_fisico_mensal_ecosul-31755644.xlsx>
- `copia-de-abril-acompanhamento_fisico_mensal_ecosul-agosto-25.xlsx` (0.13 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-abril-acompanhamento_fisico_mensal_ecosul-agosto-25.xlsx>
- `copia-de-abril-acompanhamento_fisico_mensal_ecosul-junho-25.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-abril-acompanhamento_fisico_mensal_ecosul-junho-25.xlsx>
- `copia-de-abril-acompanhamento_fisico_mensal_ecosul-maio-25.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-abril-acompanhamento_fisico_mensal_ecosul-maio-25.xlsx>
- `copia-de-janeiro-copia-de-acompanhamento_fisico_mensal_ecosul-29456947.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-janeiro-copia-de-acompanhamento_fisico_mensal_ecosul-29456947.xlsx>
- `copia-de-janeiro-copia-de-acompanhamento_fisico_mensal_ecosul-30185843.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-janeiro-copia-de-acompanhamento_fisico_mensal_ecosul-30185843.xlsx>
- `copia-de-marco-acompanhamento_fisico_mensal_ecosul-31077041.xlsx` (0.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-marco-acompanhamento_fisico_mensal_ecosul-31077041.xlsx>
- `copia_de_abril_acompanhamento_fisico_mensal_ecosul_dezembro_25.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia_de_abril_acompanhamento_fisico_mensal_ecosul_dezembro_25.zip>
- `copia_de_abril_acompanhamento_fisico_mensal_ecosul_novembro_25.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia_de_abril_acompanhamento_fisico_mensal_ecosul_novembro_25.zip>
- `copia_de_abril_acompanhamento_fisico_mensal_ecosul_outubro_25.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ecosul-contrato-encerrado/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia_de_abril_acompanhamento_fisico_mensal_ecosul_outubro_25.zip>

**EPR Litoral Pioneiro** (`epr-litoral-pioneiro`, 2026)

- `01-_acompanhamento_fisico_mensal_litoral_pioneiro_janeiro-2026.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-litoral-pioneiro/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/01-_acompanhamento_fisico_mensal_litoral_pioneiro_janeiro-2026.zip>
- `02-_acompanhamento_fisico_mensal_liitoral_pioneiro_fevereiro-2026.zip` (0.11 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-litoral-pioneiro/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/02-_acompanhamento_fisico_mensal_liitoral_pioneiro_fevereiro-2026.zip>

**EPR Via Mineira** (`epr-via-mineira`, 2026)

- `acompanhamento_fisico_mensal_via-mineira_fevereiro-26_errata.xlsx` (0.18 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-via-mineira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_via-mineira_fevereiro-26_errata.xlsx>
- `acompanhamento_fisico_mensal_via_mineira_abril_26.zip` (0.15 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-via-mineira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_via_mineira_abril_26.zip>
- `i-_acompanhamento_fisico_mensal_via_mineira_janeiro_26.zip` (0.15 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-via-mineira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/i-_acompanhamento_fisico_mensal_via_mineira_janeiro_26.zip>
- `reenvio-acompanhamento_fisico_mensal_via-mineira_mar-26.xlsx` (0.18 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/epr-via-mineira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/reenvio-acompanhamento_fisico_mensal_via-mineira_mar-26.xlsx>

**Motiva Minas SP** (`motiva-minas-sp`, 2025)

- `acompanhamento_fisico_mensal_fernao_dias-02-2025.xlsx` (0.17 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/motiva-minas-sp/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_fernao_dias-02-2025.xlsx>
- `acompanhamento_fisico_mensal_fernao_dias-08-2025.xlsx` (0.18 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/motiva-minas-sp/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_fernao_dias-08-2025.xlsx>
- `acompanhamento_fisico_mensal_fernao_dias-xlsx-01-2025.xlsx` (0.17 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/motiva-minas-sp/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_fernao_dias-xlsx-01-2025.xlsx>

**Motiva Pantanal** (`motiva-pantanal`, 2025)

- `00-planejamento-anual-obras_ano-1-a-3_antt-2.xls` (16.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/motiva-pantanal/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/00-planejamento-anual-obras_ano-1-a-3_antt-2.xls>
- `acompanhamento_fisico_mensal_ms-via-1.xlsx` (0.04 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/motiva-pantanal/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_ms-via-1.xlsx>

**Nova Rota do Oeste** (`rota-do-oeste`, 2026)

- `3o-tri-acompanhamento-trimestral-de-obras-3degano-janeiro-26.xlsx` (0.08 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-do-oeste/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/3o-tri-acompanhamento-trimestral-de-obras-3degano-janeiro-26.xlsx>
- `acompanhamento_fisico_mensal_nova_rota_do_oeste-02-2026_rev01.xlsx` (0.25 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-do-oeste/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_nova_rota_do_oeste-02-2026_rev01.xlsx>
- `acompanhamento_fisico_mensal_nova_rota_do_oeste-03-2026_rev00.xlsx` (0.26 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/rota-do-oeste/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_nova_rota_do_oeste-03-2026_rev00.xlsx>

**RioSP** (`ccr-rio-sp`, 2026)

- `2026-01_ficha_mensal_de_acompanhamento_do_ano_04_r00_antt-riosp.zip` (2.32 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-rio-sp/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/2026-01_ficha_mensal_de_acompanhamento_do_ano_04_r00_antt-riosp.zip>
- `2026-02_ficha_mensal_de_acompanhamento_do_ano_04_r00-riosp.zip` (1.91 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-rio-sp/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/2026-02_ficha_mensal_de_acompanhamento_do_ano_04_r00-riosp.zip>

**Transbrasiliana** (`Transbrasiliana`, 2026)

- `acompanhamento_fisico_mensal_transbrasiliana-1-fev.zip` (0.14 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/Transbrasiliana/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_transbrasiliana-1-fev.zip>
- `acompanhamento_fisico_mensal_transbrasiliana.zip` (0.14 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/Transbrasiliana/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_transbrasiliana.zip>
- `doc-_01transb.zip` (1.24 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/Transbrasiliana/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/doc-_01transb.zip>

**VIA 040 (Contrato Encerrado)** (`via-040`, 2024)

- `acompanhamento_fisico_mensal_via-040.xlsx` (0.04 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-040/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2024/acompanhamento_fisico_mensal_via-040.xlsx>

**Via Araucária** (`via-araucaria`, 2026)

- `acompanhamento_mensal__fev-26__rev00-araucaria.zip` (2.12 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-araucaria/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_mensal__fev-26__rev00-araucaria.zip>
- `acompanhamento_mensal__jan-26__rev00-araucaria.zip` (0.17 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-araucaria/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_mensal__jan-26__rev00-araucaria.zip>

**Via Bahia (Contrato Encerrado) Via Bahia** (`via-bahia`, 2025)

- `acompanhamento_fisico_mensal_viabahia-janeiro-25.xlsx` (0.22 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-bahia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/acompanhamento_fisico_mensal_viabahia-janeiro-25.xlsx>
- `copia-de-acompanhamento_fisico_mensal_viabahia-abril-25.xlsx` (0.22 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-bahia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-acompanhamento_fisico_mensal_viabahia-abril-25.xlsx>
- `copia-de-acompanhamento_fisico_mensal_viabahia-fevereiro-25.xlsx` (0.22 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-bahia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-acompanhamento_fisico_mensal_viabahia-fevereiro-25.xlsx>
- `copia-de-acompanhamento_fisico_mensal_viabahia-marco-25.xlsx` (0.22 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-bahia/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2025/copia-de-acompanhamento_fisico_mensal_viabahia-marco-25.xlsx>

**Via Brasil BR-163** (`via-brasil`, 2026)

- `2___acompanhamento_fisico_mensal_de_obras_e_servicos-rev01-brasil-fev.zip` (0.43 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-brasil/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/2___acompanhamento_fisico_mensal_de_obras_e_servicos-rev01-brasil-fev.zip>
- `acompanhamento-fisico-mensal-de-obras-e-servicos-rev01-via-brasil.xlsx` (0.47 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-brasil/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento-fisico-mensal-de-obras-e-servicos-rev01-via-brasil.xlsx>
- `acompanhamento_fisico_mensal_de_obras_e_servicos-rev01-via-brasil.zip` (0.43 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-brasil/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_de_obras_e_servicos-rev01-via-brasil.zip>

**Via Cristais** (`via-cristais`, 2026)

- `programacao_mensal-via-cristais.zip` (16.33 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/via-cristais/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/programacao_mensal-via-cristais.zip>

**ViaCosteira** (`ccr-viacosteira`, 2026)

- `acompanhamento-fisico-mensal-ano-06-mes-08-2025-via-costeira.xlsx` (0.41 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-viacosteira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento-fisico-mensal-ano-06-mes-08-2025-via-costeira.xlsx>
- `acompanhamento_fisico_mensal_ano_06_mes_06_2025_via_costeira.zip` (0.27 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-viacosteira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ano_06_mes_06_2025_via_costeira.zip>
- `acompanhamento_fisico_mensal_ano_06_mes_07_2025_via_costeira.zip` (0.27 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-viacosteira/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_ano_06_mes_07_2025_via_costeira.zip>

**ViaSul** (`viasul`, 2026)

- `acompanhamento_fisico_mensal_viasul-marco-26-despacho-41751472-esregrod-poa.xlsx` (0.78 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/viasul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_viasul-marco-26-despacho-41751472-esregrod-poa.xlsx>
- `acompanhamento_fisico_mensal_viasul_fevereiro_26__despacho_40375798_.zip` (0.64 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/viasul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_viasul_fevereiro_26__despacho_40375798_.zip>
- `acompanhamento_fisico_mensal_viasul_janeiro_26__despacho_39466821_.zip` (0.64 MB): <https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/viasul/documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual/2026/acompanhamento_fisico_mensal_viasul_janeiro_26__despacho_39466821_.zip>

## 7. Limitações e pontos de atenção

- **Cada concessão usa um layout próprio** de planilha. A conferência dos campos de `20260917_Atributos_rev01.xlsx` por concessão **ainda não foi feita** (só para ECO050).
- Algumas concessões têm **vários arquivos no mesmo ano** (um por mês); o script baixa todos, sem consolidar.
- O "último ano com dados" é o último ano com **algum** arquivo na pasta, não necessariamente o mês mais recente. Alguns anos trazem só PDFs de portaria.
- Motiva Pantanal publica `.xls` (formato antigo) e Via Cristais um `.xlsm` (com macro).
- Sobraram em `dados/zips/` e `dados/extraido/` arquivos da primeira versão do script (ECO050 duplicada); podem ser apagados.
- O link da lista de concessões informado inicialmente era uma página de proteção de links do Teams; a lista foi obtida diretamente do portal da ANTT.

## 8. Próximos passos sugeridos

1. Levantar, por concessão, quais colunas das planilhas correspondem aos campos do arquivo de atributos (Empreendimento e Obras).
2. Definir se o histórico mensal (previsto × executado) será guardado como snapshot ou só o último valor.
3. Tratar `.xls` e `.xlsm` no leitor e consolidar os arquivos mensais de cada concessão.
