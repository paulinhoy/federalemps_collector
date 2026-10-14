# Instruções para sessões do Claude neste projeto

O objetivo do projeto, a estrutura e como rodar estão no `README.md`. A situação atual e os próximos passos estão em `documentacao/checkpoint_financeiro.md`.

## Escopo
- Só os 3 empreendimentos do PELT-MG com acompanhamento na ANTT, cadastrados em `empreendimentos.json`: 105 Rio Minas (ERM), 103 Cerrado (ECC) e 104 ECO050 (EMG).
- Os outros ids do PELT não têm dados públicos equivalentes. Ver `emps_pelt.md`.

## Convenções
- Todo valor financeiro guarda a **data-base** e **onde foi encontrado**: `fonte_id` cadastrado em `valores_obras/fontes.py`, mais `localizacao` (página, aba, linha, coluna).
- Quando há mais de uma fonte para o mesmo valor, as duas ficam registradas (`fontes_concorrentes`). Nada é descartado.
- Não somar tipos de valor diferentes: `inicial_leilao`, `inicial_inclusao`, `aprovado_revisao`, `estimativa_concessionaria` e `realizado`.
- Valores transcritos de PDFs vão para `valores_obras/*_manuais.csv`. Ligações obra ↔ valor feitas à mão vão para `correspondencias_manuais.csv`, sempre com a justificativa.
- Tudo em `dados/` é gerado e fica fora do git.
- Ordem de execução: `baixar.py` → `consolidar.py` → `organizar.py` → por concessão, em `per_obras/`: `extrair_modelo_<conc>.py` → `montar_cadastro_<conc>.py` → `acompanhamento_financeiro_<conc>.py` (`<conc>` = `eco050`, `cerrado`). A lógica do financeiro é comum (`per_obras/financeiro_comum.py`). Rio Minas, só ligação PER x acompanhamento: `gerar_per_riominas_manuais.py` → `ligar_per_riominas.py` (regras em `per_obras/ligacao_riominas.md`; o km do acompanhamento é deslocado em relação ao PER e é corrigido antes de comparar).
- Tabelas finais em `dados/finais/<tabela>/` (`cadastro_obras`, `financeiro_mensal`, `financeiro_acumulado`, `financeiro_resumo`, `xlsx`, `ligacao_per_acompanhamento`); extrações do modelo em `dados/per_obras/intermediario/`. Caminhos sempre por `per_obras/caminhos.py` (`caminho_final(tabela, conc, ext)`, `caminho_modelo(conc, parte)`).
- Cadastro de obras (`per_obras/`): uma obra do PER dividida em n linhas guarda `per_id_origem` e `fracao_da_origem`; levar isso em conta ao ligar dados financeiros às obras. Dicionário das colunas em `per_obras/dicionario_colunas.md`.

## Portal da ANTT (gov.br, Plone)
- O link de download é o link do item sem o `/view` no final.
- HEAD retorna 403. Usar GET com User-Agent de navegador.
- Os caminhos são longos no Windows: usar `longo()` (prefixo `\\?\`), de `acompanhamento_obras/portal_antt.py`.

## Forma de trabalho
- Responder em português.
- Só fazer commit ou push quando o usuário pedir.
- Não mexer em arquivos do usuário que estão fora do git, como `instrucoes.md`.
- Arquivos baixados não são confiáveis. Scripts de inspeção ficam no scratchpad e rodam com `python -P`.
- Os scripts do projeto rodam com `python` simples, porque importam módulos da própria pasta.
