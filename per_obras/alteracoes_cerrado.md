# Mudanças desde o PER: Ecovias do Cerrado (id 103, ECC)

Fontes usadas (só estas): PER original × PER atualizado (fontes `ecc_per_original` e `ecc_per_atualizado`) e a ligação do cadastro com o acompanhamento da ANTT. Não foram lidos aditivos, notas técnicas, atas nem planejamentos. Tabela completa em `alteracoes_cerrado.csv`.

## PER original × PER atualizado

O item 3.2 só muda nas **passarelas** (redação do 2º TA, Deliberação 353/2024, nota 3 da p.43):
- os prazos passam a ser por ID (no original eram por ano, sem dizer qual passarela). PPS: Aparecida do Rio Doce no 2º ano, Cachoeira Alta e Ituiutaba (ID 7) no 4º ano, Naveslândia e Ituiutaba (ID 6) no 5º ano. As 2 PPD de Monte Alegre de Minas ficam no 3º ano;
- a passarela 7 de Ituiutaba passa do TH 15 para o TH 16 (Resumo de melhorias, p.45: TH 15 de 2 para 1 passarela; TH 16 de 0 para 1).

O resto do texto e das tabelas (duplicação, faixas adicionais, complementação, marginais, acostamentos, correção de traçado, acessos, interseções, rotatórias, retornos, iluminação e obras condicionadas) é igual nas duas versões.

## O que a ligação com o acompanhamento mostrou

- **km diferente** do km do estudo (> 1 km): interseção de Paranaiguara (16,0 → 21,9, `a_confirmar`), 2º trevo de Ituiutaba (758,9 → 757,3), rotatória da GO-180 (174,8 → 173,5), passarelas de Monte Alegre (689/690 → 688,6/687,7). Marginais deslocadas: TH 2 (5,0–8,5 → 6,0–9,13), TH 4 (57–58 → 57,8–59,25), TH 6 (113,8–114,6 → 114,5–115,3).
- **obras a mais** (sem valor, `ECC-EXT-MAR-01` a `06`): marginais em Cachoeira Alta (112,31–113,53), Uberlândia (628,9–631,16, TH 10, sem marginal no PER) e Ituiutaba (755,53–758,54, além da marginal do PER no TH 16). Podem ser do estoque de melhorias (3.2.1.5) ou inclusões. `a_confirmar`.
- **obras a menos** (prazo vencido e sem série): 84 dos 145 acessos (TH 7, 13, 14 e 15 sem nenhum), marginal de Monte Alegre de Minas (TH 11, 3º ano), passarela de Aparecida do Rio Doce, iluminação de 2 retornos e 2 interseções existentes. Ficam como `sem_acompanhamento`: podem ter sido concluídas antes de abr/2024 ou não estar no acompanhamento.
- **acostamento fora do TH**: km 160,1–160,66 está no TH 8, que não tem acostamento no PER; ligado ao TH 7 (`a_confirmar`).
- **duplicação do TH 14**: a única série é a ponte sobre o Rio Tejuco (km 749,35); o % é da ponte (`a_confirmar`).

## Divergências PER × estudo (sem forçar)

- O estudo (RESUMO_OBRAS, Fator D e modelo) tem a complementação para pista dupla das 2 passarelas de Ituiutaba (2 × 50% de PPD, 13º/14º ano; R$ 964.127,28 no Fator D e R$ 928.936,64 no 4.1 do modelo, anos 13–14). O PER não tem essa obra: o valor ficou rateado entre as demais obras do 4.1.
- Retornos km 743 e 748: o PER diz TH 15, mas pelos limites da Tabela 3 eles estão no TH 14. Mantido o TH 15.
- Iluminação de interseções existentes: o PER grafa a rodovia errada (BR-365/MG no TH 2; BR-364/MG nos TH 10–12).
