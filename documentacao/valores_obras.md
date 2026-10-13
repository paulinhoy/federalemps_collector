# Valores financeiros das obras (ANTT)

Organiza os valores encontrados no portal da ANTT (ver [`pesquisa_financeiro_antt.md`](pesquisa_financeiro_antt.md)) e liga cada valor às obras da [`lista_obras`](acompanhamento_obras.md). Todo valor traz **data-base** e **onde foi encontrado** (documento, link, página ou aba/linha/coluna).

## 1. Como rodar

```
pip install requests pandas openpyxl pyxlsb
python acompanhamento_obras/consolidar.py     # gera a lista_obras
python valores_obras/organizar.py             # baixa as planilhas-fonte, extrai, liga e gera as tabelas
```

Arquivos de código e insumos (`valores_obras/`):

| Arquivo | Conteúdo |
|---|---|
| `organizar.py` | Extração das planilhas, ligação com as obras e geração das tabelas |
| `fontes.py` | Cadastro das fontes: documento e link. As planilhas são baixadas para `dados/valores_obras/fontes/` |
| `valores_manuais.csv` | Valores transcritos de PDFs, com página: orçamentos dos retornos em nível da ECO050 (NT GEGIR 2023) e trecho DNIT (NT 145/2019) |
| `totais_manuais.csv` | Totais transcritos de PDFs e páginas: valor do contrato ECO050, Capex/Opex Rio Minas (notícia), realizado anual das DFs |
| `correspondencias_manuais.csv` | Ligações obra ↔ valor que a regra automática não alcança, com a referência que justifica (ex.: passarelas que mudaram de km pelo 6º Termo Aditivo) |

## 2. Tipos de valor (não somar tipos diferentes)

| `tipo_valor` | Significado | Fonte |
|---|---|---|
| `inicial_leilao` | Orçamento do estudo de viabilidade do leilão (EVTEA), a preços da data-base | Planilhas do EVTEA |
| `inicial_inclusao` | Valor previsto quando a obra foi **incluída** no contrato depois do leilão | Notas técnicas (revisões) |
| `aprovado_revisao` | Orçamento aprovado pela ANTT na revisão (após projeto executivo) | Notas técnicas (revisões) |
| `estimativa_concessionaria` | Capex estimado hoje pela concessionária, **sem data-base informada** | Aba "Planilha base" do acompanhamento (abr/2026) |
| `realizado` | Investimento efetivamente feito (só total anual da concessão) | Demonstrações Financeiras |

## 3. Hierarquia de ligação valor → obra (`forma`)

| `forma` | Quando | Como ler |
|---|---|---|
| `direto` | O valor é da própria obra (ou de um trecho que coincide só com ela). Também quando várias obras da lista são **versões da mesma obra** (nunca aparecem no mesmo mês) | O valor é da obra |
| `unitario_tipo` | A fonte só tem custo por unidade de um tipo de dispositivo (ex.: rotatória alongada tipo 1 em GO = R$ 2,43 mi cada) | Valor de referência da obra; não é exclusivo dela |
| `grupo` | O valor é de um grupo ou trecho que contém várias obras (ou os dois lados de uma marginal) | O valor é **dividido** entre `n_obras_no_grupo` obras da lista. Com `grupo_maior_que_lista`, também entre obras fora da lista (ex.: grupo "Duplicações" do leilão da ECO050, que cobre a concessão toda) |
| (sem linha) | Nenhum valor encontrado | `resumo_por_obra.sem_valor = True` |

Regras da ligação automática:
- **Tipo da obra:** vem da descrição (marginal, acostamento, rotatória, passarela, interseção, acesso, retorno, duplicação, faixa adicional, OAE…).
- **Rodovia:**
  - pega a BR da coluna ou da descrição;
  - na ECO050, é sempre a BR-050;
  - na Cerrado, o km separa: BR-364/GO abaixo de 400, BR-365/MG acima.
- **Ligação por km:**
  - intervalos que se sobrepõem;
  - pontos a até 0,6 km.
  - O EVTEA usa uma versão antiga do SNV; sobreposições pequenas entram com `confianca = baixa`.
- **Nome próprio:** Trevão, Xapetuba e Tejuco ligam pelo nome, mesmo com km diferente.
- **Item PER:** quando a fonte informa o item PER (Planilha base), a obra com o mesmo item tem prioridade.
- **Dispositivos da Cerrado:** o subtipo vem do local de cada dispositivo na planilha `RESUMO_OBRAS_MELHORIAS` do EVTEA. Exemplos: rotatória RA-1A/RA-2A, passarela em pista simples (PPS) ou dupla (PPD), acesso em pista simples (APS) ou dupla (APD).
- **Valor coberto:** se a obra tem valor `direto` de um tipo, as ligações `grupo`/`unitario_tipo` do mesmo tipo ficam com `coberto_por_valor_direto = True`.

## 4. Tabelas geradas (`dados/valores_obras/`)

| Arquivo | 1 linha por | Colunas principais |
|---|---|---|
| `resumo_por_obra.csv` | obra | Para cada tipo de valor: `*_valor`, `*_forma`, `*_data_base`, `*_fonte` (documento + página/célula), `*_valor_ids`, `*_outros_valores`. Mais `n_fontes`, `fontes`, **`fontes_concorrentes`** (obra com valor de mais de uma fonte) e `sem_valor` |
| `obras_valores.csv` | ligação obra × valor | `forma`, `metodo`, `confianca`, `n_obras_no_grupo`, `grupo_maior_que_lista`, `coberto_por_valor_direto`, `observacao` |
| `valores_encontrados.csv` | valor achado | `tipo_valor`, `natureza`, `nivel`, `descricao_fonte`, km, `valor`, **`data_base`**, `valor_precos_iniciais`, `fonte_id`, `documento`, `url`, **`localizacao`**, `conferido_por`, `n_obras_ligadas`, `fontes_concorrentes` |
| `valor_total_empreendimento.csv` | total | Capex, Opex, ampliação e valor do contrato do leilão, além do realizado por ano (DFs). Com `data_base`, `precisao`, `localizacao` e `fontes_concorrentes` |
| `valores_obras.xlsx` | — | As 4 tabelas em abas |

### Como achar o documento de um `fonte_id`

`fonte_id` não é uma tabela, é o código de um **documento** do portal da ANTT. O cadastro fica em `valores_obras/fontes.py`, e as tabelas já trazem `documento`, `url` e `localizacao` (página, aba, linha, coluna) ao lado de cada `fonte_id`. Exemplo: `eco050_df2025` corresponde às "Demonstrações financeiras 2025" da ECO050, em `.../eco050/relatorios/relatorios-financeiros/eco050-2025.pdf`, p.10.

Onde fica a cópia local:
- **Planilhas** (`baixar=True` em `fontes.py`): `dados/valores_obras/fontes/<fonte_id>/`, baixadas pelo `organizar.py`.
- **PDFs e páginas:** não são baixados pelo script. Os valores deles foram transcritos para `valores_manuais.csv` ou `totais_manuais.csv`. Quando existe cópia, ela está em `dados/pesquisa_financeiro/<concessão>/<seção do portal>/`, com as mesmas pastas do site, e o índice dessas cópias é `dados/pesquisa_financeiro/inventario.csv`.

`conferido_por` diz quem conferiu o valor:
- `extração automática`: lido da célula pelo script;
- `revisão manual`: transcrito e conferido na página do PDF;
- `agente de pesquisa`: valores das DFs, ainda não reconferidos por nós.

## 5. Resultado (obras presentes em abr/2026)

| | ECO050 (104) | Cerrado (103) | Rio Minas (105) |
|---|---|---|---|
| Obras | 24 | 71 | 699 |
| Com algum valor | 24 | 53 | 0 |
| Valor do leilão `direto` / `unitario_tipo` / `grupo` | 0 / 0 / 24 | 4 / 19 / 27 | — |
| Estimativa da concessionária (Planilha base) | 12 | 26 | — |
| Com fontes concorrentes | 12 | 23 | — |

**Totais por empreendimento:**

| Empreendimento | Total | Valor | Data-base | Fonte |
|---|---|---|---|---|
| ECO050 | Capex, estudo do leilão | R$ 3,03 bi | não informada | aba PER, linha 263 |
| ECO050 | Opex, estudo do leilão | R$ 1,97 bi | não informada | aba PER, linha 264 |
| ECO050 | Ampliação | R$ 1,15 bi | não informada | aba PER |
| ECO050 | Valor estimado do contrato | R$ 10,14 bi | mai/2012 | Edital, p.9 |
| Cerrado | Capex | R$ 2,06 bi | jul/2016 | EVTEA |
| Cerrado | Opex | R$ 2,53 bi | jul/2016 | EVTEA |
| Cerrado | Melhorias e ampliação | R$ 743 mi | jul/2016 | EVTEA |
| Rio Minas | Capex (precisão baixa) | R$ 8,8 bi | jan/2021 | Notícia da ANTT |
| Rio Minas | Opex (precisão baixa) | R$ 8,5 bi | jan/2021 | Notícia da ANTT |

Também entra o realizado por ano das três concessões, com dados das DFs.

Exemplo de fontes concorrentes (`EMG-0031`, retorno em nível km 196,5):
- **Inicial da inclusão (2015):** R$ 1,89 mi por retorno, a preços de mai/2012.
- **Aprovado pela ANTT:** R$ 9,51 mi (obra + projeto), a preços de abr/2022 (NT GEGIR 2023, p.15).
- **Estimativa atual da concessionária:** R$ 13,37 mi, sem data-base.

## 6. Limitações e pendências

- **Rio Minas:** o portal da ANTT não tem valor por obra. Ficam só os totais.
- **ECO050:** o leilão só tem valores **por grupo**, e os grupos cobrem a concessão inteira (`grupo_maior_que_lista`). O valor por obra vem só das revisões (retornos) e da estimativa da concessionária.
- **Data-base ausente:** a Planilha base e o modelo do leilão da ECO050 não informam data-base. O edital e o contrato da ECO050 usam mai/2012. Os valores não foram corrigidos por índice de preços: para comparar valores de datas diferentes, é preciso corrigi-los pelo IPCA antes.
- **43 valores sem obra ligada.** Na maioria, são obras que não estão na lista de acompanhamento:
  - retornos da ECO050 executados antes de 2024;
  - trecho DNIT;
  - duplicação dos subtrechos ST-13/14 da Cerrado e suas OAEs;
  - faixas adicionais ST-1 a ST-4.
- **Pendentes de correspondência manual:** OAEs da Cerrado na Planilha base com km ~0,9 diferente das obras da lista. Exemplos: km 847,8 × ECC-0093 km 848,7; km 787,7 × ECC-0258 km 788,6. Provavelmente são a mesma OAE, mas falta confirmar antes de incluir em `correspondencias_manuais.csv`.
- **Iluminação:** as obras de iluminação da Cerrado ficam sem valor porque o EVTEA a considera dentro da recuperação e dos trabalhos iniciais (valor 0 na aba Ampliação).
- **OAEs novas da Cerrado:** podem estar contidas no valor da duplicação do subtrecho. Por isso estão marcadas para não somar.
