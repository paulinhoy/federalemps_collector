# ECO050 (id 104, EMG): alterações das obras após o PER original e datas

Pesquisa feita em 13/10/2026 sobre `dados/pesquisa_financeiro/eco050/`. Detalhe linha a linha (99 linhas) em `alteracoes_eco050.csv`. Arquivos de apoio na mesma pasta:
- `marcos_liberacao_eco050.csv`: tabela "Marcos contratuais" (data de liberação ao tráfego por obra) do Relatório Mensal 12/2025, p.14-19, extraída por tabela.
- `cronograma_planejamento_anual_2026_eco050.csv`: início/fim, previsto e executado, por obra (com ID SIGICOR) extraído do Planejamento anual 2026 Rev02.

Siglas: PA = planejamento anual (aba única, "L" = linha da planilha); Relatório 12/2025 = `relatorio_mensal_obras_e_servicos_12-2025.pdf`; NT = nota técnica. Páginas citadas são páginas do PDF.

## (a) Início da concessão e regra ano -> data

- **Assunção = 08/01/2014** (assinatura do Termo de Arrolamento e Transferência de Bens). Fontes: Relatório 12/2025 p.3 e p.10 ("Data de início da concessão 08/01/2014"); NT GEGIR preliminar 2023 p.1 §3; DF 2017 p.27 ("30 anos contados a partir de 08 de janeiro de 2014"). Contrato: "Data da Assunção" = data do TATB (cl. 1.1.1 (xii), p.5); prazo 30 anos desde a assunção (cl. 3.1).
- Contrato assinado em 05/12/2013; início da cobrança de pedágio em 12/04/2015 (Relatório 12/2025 p.10).
- **Regra:** ano N da concessão = de 08/01/(2013+N) a 07/01/(2014+N). Ex.: ano 1 = 08/01/2014 a 07/01/2015; 12º ano = 08/01/2025 a 07/01/2026 (NT 8305/2026 §152); 10º ano = 08/01/2023 a 07/01/2024 (voto DFQ 2024).
- **Metas anuais de duplicação (PER 3.2.1 e 3.2.1.1, p.32):** o PER diz 48 meses a partir da Licença de Instalação. A LI 1045/2015 foi emitida em **23/01/2015** (imagem da p.1 da LI; o Relatório 12/2025 p.7 diz 25/01/2015: divergência). Para o Fator D a ANTT adota o marco "12 meses a contar da assunção, independentemente da LI" (Voto DLL 2023 p.3 §3.17, citando a PGF), logo meta do ano 1 = 07/01/2016 ... ano 4 = **07/01/2019**. A Planilha base abr/2026 confirma: coluna W "Data prevista no PER" = 07/01/2019 para as obras de Catalão e Uberaba. Prazo por ano (INFERÊNCIA a partir das duas fontes): ano k de meta vence em 07/01/(2015+k).
- Marginais: até 12 meses após a duplicação do subtrecho (PER p.32).

## (b) Alterações por obra do PER (resumo; detalhes e fontes no CSV)

Siglas de tipo: R = realocação de km; C = reconfiguração; E = exclusão. O km "PER" vem das listas do PER p.33-35.

| Obra do PER | Tipo | Antes (PER) | Depois | Fonte principal |
|---|---|---|---|---|
| Passarela 1 | R | km 40,5 Araguari | Uberaba km 171 ou 175 | 6º TA cl. 2.1 p.2 (22/04/2025); PA2025 L198 |
| Passarela 7 | R | km 279,5 Catalão | Uberaba km 171 ou 175 | idem; PA2024 L204 ("excluída no anteprojeto") |
| Passarela 2 | R | km 179,0 | km 182 (liberada 05/02/2019) | PA2024 L230; Relatório p.16 |
| Passarelas 3, 4, 5 | R | 101,0; 96,4; 98,7 | 97,9; 96,1; 97,3 (liberadas 30/07/2024) | PA2026 L187-191; Relatório p.18 |
| Passarela 6 | R (inferência) | 277,5 | 278,9 (em obra; prevista mai/2026) | Relatório p.13; Ata 14/05/2026 p.4 |
| Diamante 2 | R | km 131,3 Uberaba | km 98,5 Cristalina | Ofício SEI 9466/2022 CPROJ/GEENG (cit. PA2026 L105) |
| Retorno em desnível 1 | R | km 101,0 | km 102,5 Cristalina | idem (PA2026 L107) |
| Diamante 5 | R | 97,3 | 96,7 | PA2026 L103 |
| Trombeta 1 | R | km 4,0 Araguari | km 280,615 Catalão | PA2025 L214 (GAC-0715-2021) |
| Trombeta 2 | R | km 22,0 Araguari | km 273,45 (concluída) | PA2025 L216 |
| Diamantes 3, 14, 15 | R | 140,3; 273,2; 280,5 | 283,05; 277,95; 280,3 | PA2024 L148-156 |
| Diamante 1 | R | km 124,0 | km 116 (28/06/2019) | PA2026 L203; Relatório p.16 |
| Diamante 4 | R pendente | km 151,5 | sem local definido | PA2024 L158; Quinquenal L32 |
| Diamantes 6-13, 16; trombetas 4-8; retorno desnível 5 | R (ajuste <2,3 km) | ver CSV | km as built | PA2026; Relatório pp.15-17 |
| Marginais 2, 7, 8 | C | 98,0-100,8; 276,5-280,5; 276,9-283,1 | 96,8/98-101,3; 277,3-283,1 (x2) | PA2023 L92-100; PA2026 L89-99 |
| Marginais 3, 4, 6 | E (remanejadas) | 106,7-107,3; 107,3-108,0; 245,4-246,9 | saldos vão para as marginais de Cristalina (ID-3, ID-4, 450 m da ID-6) e Catalão (800 m da ID-6) | PA2023 L92 e L98 obs |
| Marginal 1 | R pendente | km 40-41 Araguari | a definir (km 180 Uberaba ou travessias) | PA2024 L102; Ofício 260/2018 GEINV |
| Duplicação das travessias | C | pista dupla em Cristalina e Catalão | reprojeto via EVTEA (km 95,7-101,3 e 273,4-286,8) | NT 145/2019 pp.15-16; PA2022 L12, L70 |
| Acessos 1, 2, 3, 7, 8 | R (ajuste) | 247,0; 258,0; 264,0; 289,0; 301,0 | 247,3; 258,2; 264,3; 288,8; 301,5 | PA2026; Relatório pp.16-17 |

Não houve alteração localizada em: trevo completo km 276,5, acessos 4-6, retornos em desnível 2-4 (só data). Faixas adicionais (PER 3.2.3.1, gatilho de VDMA): **nenhum registro** de gatilho atingido nos documentos lidos. Manutenção de nível de serviço sem local (3.2.3.3): nenhuma inclusão específica encontrada.

Termos aditivos e efeito nas obras: 1º TA (2017, escaneado) arrolou trecho DNIT; 2º, 4º, 5º, 7º, 8º, 9º TA não tocam obras (Fator C, datas de reajuste, Fator D, tarifa, parâmetros operacionais, pavimento); 3º TA (25/07/2024) assume o km 178,35-179,5 (Uberaba); 6º TA realoca passarelas; 10º TA (20/03/2026) inclui 4G. Não existe PER atualizado ou consolidado no portal (verificado em 13/10/2026: só "PER - Original", contrato e 10 TAs).

## (c) Obras novas fora do PER

- **Retornos em nível:** Res. ANTT 4.652/2015 incluiu 10 retornos (1ª Rev. Extraordinária). Locais (NT 950/2021 p.3): 146,1; 150,6; 171,0->172,5; 195,0; 216,0->216,3; 177,1->248,5; 259,7->260,0; 288,4 (->287,7); 289,1 (->289,9). Liberados 23/05/2016 a 09/11/2020 (Relatório pp.15-16). NT GEGIR compl. 2023 p.11 (Tab. 11) lista 12 itens, 9 executados e 3 não executados: km 131,4, 196,5, 107,2 (os mesmos que o acompanhamento marca "Extra-PER", EMG-0030/31/32). Em 2018 seis retornos foram retirados só do FCM (NT 053/2018 p.36). Contagem 10 x 9 locais x 12 itens: não reconciliada.
- **Retorno km 286,5/"retorno operacional km 286"** (Planilha base linha 17; PA2026 L229): origem não esclarecida.
- **Melhoria de acesso Extra-PER km 245,8** (26/03/2019).
- **Pontes** Paineiras 164,8, Imburuçu 179,8, Capão Dantas 236,2, Marimbondo 310,8, divisa GO-MG 314,2 (30/06/2017 a 21/10/2021): fora das listas do PER; natureza contratual não confirmada.
- **Trecho DNIT** km 0-65,7 (Uberlândia) e 174-180 (Uberaba) via 1º TA (2017); revisão de projeto +R$ 22,4 mi (NT 145/2019 p.13). Segmento **km 178,35-179,5** assumido pelo 3º TA (25/07/2024); a obra de recuperação/adequação aguarda novo TA (ata 14/05/2026 p.5). **Interseção km 180 Uberaba**: 3 alternativas em estudo (ata 14/05/2026 p.4).
- **1ª Revisão Quinquenal** (Deliberação ANTT 25/2025, citada na ata 13/11/2025 p.3, **não baixada**): duplicação km 77+600 em Uberlândia e adequação do trevo completo (obra prevista para 2027, ata 26/06/2025 p.4), iluminação urbana km 77-81 (estimativa 2026), melhorias de acessos, dispositivos/retornos (ata 23/05/2024 p.2). Retorno em nível km 51: proposta sem decisão (ata 14/07/2023).
- Não físicas: 4G (10º TA), elevador PRF km 42, controladores/redutores DNIT, link SIR, passeios em OAEs do contorno de Uberlândia (04/10/2024 a 31/01/2025). Exclusão pendente: passeios em OAEs rurais (NT 5670/2026 p.7).

## (d) Datas

**Previstas.** (1) Metas do PER: ver (a). Total 218,5 km em quatro metas (35,0/52,4/74,3/56,8 km, conforme o checkpoint; o texto do PDF p.32 está embaralhado). (2) PA2026 Rev02 (CSV de cronograma): previsto por obra, replanejado (ex.: Cristalina prev. 2024-09; Catalão 2026-01/02). (3) Quinquenal Rev0 (24/11/2023): Cristalina jan-abr/2024; Catalão jan/2024-ago/2025. (4) Planilha base abr/2026: Catalão início 24/08/2023, entrega estimada 31/10/2025; passarelas 171/175 e 277,5 início 01/08/2025; retornos 196,5 (04/11/2024) e 286,5 (25/11/2025-15/01/2026). (5) 4G: 12º ao 16º ano (08/01/2025 a 07/01/2031). (6) Cristalina: Carta ECO050-GAC-0634-2023 (14/09/2023) repactuou conclusão para abril/2024 (PA2026 obs); a obra só foi liberada em 30/07/2024.

**Realizadas** (liberação ao tráfego, Relatório 12/2025 pp.14-19; lista completa no CSV de marcos). Duplicação acumulada x metas (cálculo nosso, só GO, 218,5 km):

| Marco | Km duplicados e liberados até a data | Meta cumulativa (35,0/87,4/161,7/218,5) |
|---|---|---|
| até 07/01/2016 | 26,3 (02/02/2015 foi antes) | 35,0 |
| até 07/01/2017 | 39,2 (23/05/2016: +12,9) | 87,4 |
| até 07/01/2018 | 91,1 (30/06/2017: +51,9) | 161,7 |
| até 07/01/2019 | 122,1 (30/06/2018: +31,0) | 218,5 |
| restante | 24/05/2019: 53,9 km; 09/11/2020: 22,6 km; 21/10/2021: 4,8 km; 30/07/2024: 3,74 km (Cristalina); Catalão 11,4 km em 2026 | |

Catalão: avanço 58% em dez/2024 (ata 17/12/2024), 97% em nov/2025 (ata 13/11/2025), 98,95% no PA2026; ata 14/05/2026 informa a entrega (dia não informado). Cristalina: tudo liberado em 30/07/2024 (duplicação, marginais, 2 diamantes, retorno em desnível 102,5, 3 passarelas). Passarela 278,9: previsão maio/2026. Passarelas 171/175: 32,5% e 37,5% em abr/2026.

## (e) Documentos lidos e pendências

Lidos com texto: contrato (cl. de assunção, 10.3.2), PER original (pp.32-38), edital (p.6), TAs 2 a 10, Fatores C/D/Q, relatório mensal 12/2025, atas tripartite de 12/2022, 07/2023, 12/2023, 05/2024, 12/2024, 06/2025, 11/2025 e 05/2026, relatório anual tripartite 2025, planejamentos anuais 2015-2026 (extração por script), quinquenal, Planilha base abr/2026, NTs/votos/deliberações 2019-2026 (busca por obras), NT 053/2018 (texto OCR ruim), DFs 2017-2025 (só contexto), LI 1045/2015 (imagem) e LI 1430/2022, 3º aditamento do TATB.

Baixados nesta tarefa (novas pastas): `eco050/termo-de-arrolamento-e-transferencia-de-bens/` (4 PDFs), `eco050/licenciamento-ambiental/` (3 PDFs), `eco050/atas-tripartite/` (7 atas).

**Pendências:**
1. **Escaneados sem texto (não lidos):** 1º TA (26 p.), Termo de Arrolamento original e aditamentos 1 e 2, quase todas as NTs e votos de 2015-2018 (inclui NT 003/2015 GEINV, que fundamenta os 10 retornos; Relatório Técnico 013/2015; NT 001/2019), NTs/votos de 2022 (5ª e 7ª RO), Resolução 5.381/2017, Decisão SUROD 532/2025 (só imagem), autorização de supressão 1052.8.2023.03625 (trechos urbanos Catalão/Cristalina). Podem trazer o reprojeto dos perímetros urbanos, ano a ano.
2. **Documentos citados e não publicados no portal:** Deliberação ANTT 25/2025 (1ª Revisão Quinquenal), Deliberação 124/2024 (Compor), 215/2026 (13ª Rev. Extraordinária), 48/2026; Ofício SEI 9466/2022 CPROJ/GEENG (realocação para Cristalina); ECO050-GAC-0715-2021 (trombeta 280,615); Carta GAC-0634-2023; Ofício 260/2018 GEINV; processo 50500.170570/2024-89.
3. Relatórios mensais 2014-2024 e 2026 (não baixados, 12/2025 já tem o acumulado), relatórios de monitoração, planejamentos anuais 2015 (.xls) e 2025 só por script, "percentuais de avanço" mensais.

## Dúvidas para decisão humana

1. **Passarelas 171 x 175:** o 6º TA (leitura direta) liga ID-1->171 e ID-7->175; o PA2025 liga ID-7(279,5)->171 e ID-1(40,5)->175. Qual adotar? No CSV usei o PA2025.
2. **Passarela 277,5 x 278,9:** tratei como a mesma obra reposicionada (inferência); o acompanhamento ainda usa 277,5.
3. **Contagem de retornos em nível** (10 x 9 locais x 12 itens) e UF de km 196,5 (GO na NT 2023, MG na Planilha base).
4. **Marginais 3, 4 e 6 e diamante 4 (151,5), marginal 1 (40-41):** tratadas como excluídas/pendentes sem aditivo localizado; só o planejamento anual as registra.
5. **Pontes e passeios de OAE:** incluir no cadastro como obras novas ou deixar fora?
6. **Marco da meta anual:** adotar 08/01/2015 (assunção + 12 meses, regra da ANTT para o Fator D) ou 23/01/2015 (LI + 48 meses, texto do PER)?

## Decisões adotadas no cadastro (`montar_cadastro_eco050.py`, 13/10/2026)

Ver `documentacao/cadastro_obras.md`. Resumo:
1. O cadastro usa o km e o local atuais. O km do PER vai para `km_per_original` e a fonte da mudança para `fonte_alteracao`.
2. **Passarelas 171/175 (divergência registrada):** o 6º TA (cl. 2.1 e tabela da cl. 3.1, p.2) liga ID-1 (40,5) → 171 e ID-7 (279,5) → 175. O PA2025 (L196 e L198) e este CSV ligam ID-7 → 171 (EMG-0025) e ID-1 → 175 (EMG-0026). O PA2026 Rev02 (L197 e L199) não traz o "Antigo ID". O cadastro segue este CSV e marca as duas linhas com `a_confirmar=True`. O valor é o mesmo. Atenção: `valores_obras/correspondencias_manuais.csv` liga EMG-0026 ao km 171 e EMG-0025 ao km 175, o inverso deste CSV. A Planilha base abr/2026 dá 32,5% no km 171 e 37,5% no km 175, iguais aos de EMG-0025 e EMG-0026: isso confirma EMG-0025 = km 171.
3. A passarela 277,5 → 278,9 é inferência. O cadastro mantém 277,5 (oficial) com nota.
4. Os retornos em nível Extra-PER entram por enquanto só os 3 do acompanhamento (107,2; 131,4; 196,5), com `a_confirmar=True`. Os demais itens da seção (c) ficam para depois.
5. Obras fora do item 4 ficam sem `item_modelo` e sem valor.
6. Uma obra do PER dividida vira n linhas, com `per_id_origem` e `fracao_da_origem`. Os casos são a duplicação (cortada nos trechos de Cristalina e Catalão do acompanhamento) e a marginal ID-2 (Sul/Norte). As marginais 3, 4 e 6 ficam fora do cadastro, porque os saldos foram remanejados.
7. Prazo contratual das obras do 3.2.1: 07/01/2019. As metas anuais de duplicação vencem em 07/01/2016, 2017, 2018 e 2019, sem segmento definido.
8. O excedente do 4.3 nos anos 20–22 (5% do 4.2.2) foi reclassificado como bloco `condicionada` (projetos das faixas adicionais).
