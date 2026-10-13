"""
Documentos do portal da ANTT de onde saem os valores. `baixar=True` = planilha lida pelo script (baixada para
dados/valores_obras/fontes/<fonte_id>/); os demais são PDFs/páginas cujos valores foram transcritos à mão em
valores_manuais.csv / totais_manuais.csv (com página), e ficam aqui só como referência do link.
"""
BASE = "https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes"
ACOMP = "documentos-de-gestao/acompanhamento-de-obras/percentuais-de-avanco-fisico-dos-cronogramas-de-obras-e-servicos-do-planejamento-anual"
EVTEA_ECC = f"{BASE}/ecovias-do-cerrado/documentos-de-gestao/processo-de-licitacao/edital-de-concessao-no-01-2019-1/arquivos/estudos-de-viabilidade"

FONTES = {
    # ---- planilhas lidas pelo script
    "ecc_evtea_fator_d": dict(
        id_empreendimento=103, baixar=True, documento="EVTEA do leilão - fator-d.xlsx (abas Ampliação, OAEs_novas, PER 364-365)",
        url=f"{EVTEA_ECC}/fator-d.xlsx"),
    "ecc_evtea_modelagem": dict(
        id_empreendimento=103, baixar=True, membros=["*RESUMO_OBRAS_MELHORIAS*.xlsb"],
        documento="EVTEA do leilão - modelagem-financeira-planilhas.zip (BR_364_365_RESUMO_OBRAS_MELHORIAS_REV8.xlsb: localização das obras)",
        url=f"{EVTEA_ECC}/modelagem-financeira-planilhas.zip"),
    "ecc_planilha_base_2026_04": dict(
        id_empreendimento=103, baixar=True, membros=["*Acompanhamento de Obras*.xlsx"],
        documento="Acompanhamento abr/2026 - ECC_Acompanhamento de Obras_ABRIL_26.xlsx, aba Planilha base",
        url=f"{BASE}/ecovias-do-cerrado/{ACOMP}/2026/execucao_mensal___04-2026cerrado.zip"),
    "eco050_evtea_modelo": dict(
        id_empreendimento=104, baixar=True, documento="Estudos indicativos do leilão - modelo-economico-financeiro-eco-050.xlsx (aba PER)",
        url=f"{BASE}/eco050/documentos-de-gestao/processo-de-licitacao/modelo-economico-financeiro-eco-050.xlsx"),
    "eco050_planilha_base_2026_04": dict(
        id_empreendimento=104, baixar=True, membros=["*Acompanhamento de Obras*.xlsx"],
        documento="Acompanhamento abr/2026 - EMG_Acompanhamento de Obras_ABRIL_26.xlsx, aba Planilha base",
        url=f"{BASE}/eco050/{ACOMP}/2026/execucao_mensal___04-2026minasgoias.zip"),
    # ---- PDFs e páginas (valores transcritos à mão, com página)
    "eco050_per_original": dict(
        id_empreendimento=104, documento="PER original do contrato (Programa de Exploração da Rodovia), per-original.pdf: itens 3.2.1, 3.2.3 e Apêndices A e B",
        url=f"{BASE}/eco050/documentos-de-gestao/contrato-e-anexos/anexos-do-contrato/per-original.pdf"),
    "eco050_nt_gegir_2023": dict(
        id_empreendimento=104, documento="Nota Técnica GEGIR complementar pós-manifestação (8ª Revisão Ordinária, 2023)",
        url=f"{BASE}/eco050/revisao-e-reajuste-da-tarifa-de-pedagio/2023/nota-tecnica-gegir-complementar-pos-manifestacao.pdf"),
    "eco050_nt145_2019": dict(
        id_empreendimento=104, documento="Nota Técnica SEI nº 145/2019/GEFIR/SUINF/DIR (4ª Revisão Ordinária)",
        url=f"{BASE}/eco050/revisao-e-reajuste-da-tarifa-de-pedagio/2019/nota-tecnica-sei-n-145-2019-gefir-suinf-dir.pdf"),
    "eco050_edital": dict(
        id_empreendimento=104, documento="Edital de Concessão nº 001/2013",
        url=f"{BASE}/eco050/documentos-de-gestao/processo-de-licitacao/edital-antt-l2-e-4.pdf"),
    "erm_noticia_edital": dict(
        id_empreendimento=105, documento="Notícia ANTT: ANTT aprova edital para concessão da BR-116/465/493/RJ/MG",
        url="https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/antt-aprova-edital-para-concessao-da-br-116-465-493-rj-mg"),
    "eco050_df2019": dict(id_empreendimento=104, documento="Demonstração financeira anual 2019",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/demonstracao-financeira-anual-2019.pdf"),
    "eco050_df2020": dict(id_empreendimento=104, documento="Demonstração financeira anual 2020",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/demonstracao-financeira-anual-2020.pdf"),
    "eco050_df2021": dict(id_empreendimento=104, documento="Demonstração financeira anual 2021",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/demonstracao-financeira-anual-2021"),
    "eco050_df2022": dict(id_empreendimento=104, documento="Demonstrações financeiras 4º tri 2022",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/4tri22-df-eco050.pdf"),
    "eco050_df2023": dict(id_empreendimento=104, documento="Demonstrações financeiras 4º tri 2023",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/df-4tri2023-eco050.pdf"),
    "eco050_df2024": dict(id_empreendimento=104, documento="Demonstrações financeiras 2024",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/eco050-4df-2024-assinada.pdf"),
    "eco050_df2025": dict(id_empreendimento=104, documento="Demonstrações financeiras 2025",
                          url=f"{BASE}/eco050/relatorios/relatorios-financeiros/eco050-2025.pdf"),
    "ecc_df2021": dict(id_empreendimento=103, documento="Demonstração financeira anual 2021",
                       url=f"{BASE}/ecovias-do-cerrado/relatorios/relatorios-financeiros/demonstracao-financeira-anual-2021"),
    "ecc_df2022": dict(id_empreendimento=103, documento="Demonstrações financeiras 4º tri 2022",
                       url=f"{BASE}/ecovias-do-cerrado/relatorios/relatorios-financeiros/ecovias-do-cerrado_4tri2022.pdf"),
    "ecc_df2023": dict(id_empreendimento=103, documento="Demonstrações financeiras 4º tri 2023",
                       url=f"{BASE}/ecovias-do-cerrado/relatorios/relatorios-financeiros/df-4tri2023-ecovias-do-cerrado.pdf"),
    "ecc_df2024": dict(id_empreendimento=103, documento="Demonstrações financeiras 4º tri 2024",
                       url=f"{BASE}/ecovias-do-cerrado/relatorios/relatorios-financeiros/df-4tri2024-ecovias-do-cerrado.pdf"),
    "ecc_df2025": dict(id_empreendimento=103, documento="Demonstrações financeiras 2025",
                       url=f"{BASE}/ecovias-do-cerrado/relatorios/relatorios-financeiros/cerrado-2025.pdf"),
    "erm_df2022": dict(id_empreendimento=105, documento="Demonstrações financeiras anuais completas 2022",
                       url=f"{BASE}/ecoriominas/relatorios/relatorios-financeiros/demonstracoes-financeiras-anuais-completas-2022-ecoriominas.pdf"),
    "erm_df2023": dict(id_empreendimento=105, documento="Demonstrações financeiras 4º tri 2023",
                       url=f"{BASE}/ecoriominas/relatorios/relatorios-financeiros/df-4tri-2023-ecoriominas-assinada.pdf"),
    "erm_df2024": dict(id_empreendimento=105, documento="Demonstrações financeiras 4º tri 2024",
                       url=f"{BASE}/ecoriominas/relatorios/relatorios-financeiros/df-4tri2024-ecoriominas-assinada-1.pdf"),
    "erm_df2025": dict(id_empreendimento=105, documento="Demonstrações financeiras 2025",
                       url=f"{BASE}/ecoriominas/relatorios/relatorios-financeiros/ecoriominas2025.pdf"),
}
