# Análise de Infraestrutura do Setor Elétrico (ANEEL)

Este repositório contém a infraestrutura de código e a metodologia desenvolvida para a padronização, consolidação e análise estatística +*multivariada e figuras. dos ativos de distribuição de energia elétrica das concessionárias **CEMIG**, **ENEL SP**, **CPFL Piratininga** e **Equatorial Pará**, cobrindo os Tipos de Instalação de $0$ a $99$ ($\text{TIs } 0\text{--}99$).

---

## 1. Visão Geral e Contexto

No ambiente regulatório da ANEEL, a valoração da infraestrutura de distribuição é fundamentada em dois indicadores principais:

* **VOC (Valor Original Contábil):** Custo histórico efetivo de aquisição e instalação imobilizado pela distribuidora.
* **VNR (Valor Novo de Reposição):** Valoração regulatória de reposição do ativo padronizada pela ANEEL.

---

## 2. Metodologia de Dupla Camada

Para eliminar a ambiguidade observada em trabalhos anteriores, que alternavam sem aviso prévio entre a análise por item unitário e a análise por obra consolidada, o pipeline processa os dados em duas etapas:

```
                            Base Bruta de Dados (ANEEL)
                                         │
                                         ▼
              Consolidação, Expurgo (/Sobra Contabil, /Sobra Fisica) e Filtros
                             (VOC > 0, VNR > 0, TI 0..99)
                                         │
               ┌─────────────────────────┴─────────────────────────┐
               ▼                                                   ▼
     CAMADA 1: Nível TUC                                 CAMADA 2: Nível Projeto
 (Unidade de Cadastro / Ativo)                         (Obra Consolidada PEP/ODI)
               │                                                   │
               ├─ Sem Agrupamento por Obra                         ├─ Agrupamento PROJETO_UNIFICADO
```

### 🔹 Camada 1 — Nível TUC (Unidade de Cadastro / Ativo Individual)

Analisa cada componente físico unitário instalado

* **Objetivo:** Avaliar o comportamento contábil e regulatório de itens individuais.

### 🔹 Camada 2 — Nível Projeto (Obra Consolidada / PEP e ODI)

Agrupa as linhas de ativos utilizando a chave unificada `PROJETO_UNIFICADO = PEP.fillna(ODI)` para calcular o investimento total de cada empreendimento.

* **Objetivo:** Avaliar o custo total e a escala financeira de obras concluídas por distribuidora.

---

## 3. Estrutura do Repositório

```text
ic-energia-eletrica/
├── data/
│   ├── raw/                           # Planilhas brutas (.xlsx e .xlsb) das 4 concessionárias
│   └── processed/
│       └── base_consolidada.csv       # Base unificada com filtros e chave PROJETO_UNIFICADO
│
├── output/
│   ├── estatistica_descritiva/        # Relatórios descritivos e testes de hipóteses (TUC e Projeto)
│   │   ├── descritiva_tuc.csv
│   │   ├── descritiva_projetos.csv
│   │   ├── levene_tuc.csv
│   │   └── levene_projetos.csv
│   └── comparacao_tis/                # Relatórios de conciliação e presença de TIs
│       ├── relatorio_conciliacao_tcc.csv
│       ├── output_tis_comuns.csv
│       ├── output_projetos_tis.csv
│       └── output_validar_tis.csv
│
├── src/
│   ├── referencia_tcc.py              # Dicionário de configuração de cabeçalhos e abas (FONTES)
│   ├── consolidar_base.py             # Filtros, expurgos (/Sobra contabil, /Sobra fisica) e consolidação
│   ├── estatistica_descritiva.py      # Cálculo de métricas de posição, dispersão e forma
│   ├── teste_levene.py                # Teste de homogeneidade de variâncias (Levene pela mediana)
│   ├── gerar_relatorio_conciliacao.py # valida os novos levantamentos com os levantamentos do tcc
│   ├── comparar_tis_comuns.py         # Mapeamento de presença/ausência das TIs 0-99
│   ├── comparar_tis_numerico.py       # Contagem de projetos únicos por TI e concessionária
│   ├── validar_tis.py                 # Agrupamento por famílias de TIs de 10 em 10 para validar com o tcc
│   └── executar_pipeline.py           # facilitar execução
│
├── README.md                          # Documentação principal do projeto
├── CHANGELOG.md                       # Mudanças feitas no projeto
```

---


## 4. Descrição das Saídas Geradas (`output/`)

Ao final da execução, os seguintes arquivos estruturados estarão disponíveis:

| Diretório                         | Arquivo                           | Descrição                                                                                             |
| :--------------------------------- | :-------------------------------- | :------------------------------------------------------------------------------------------------------ |
| `output/estatistica_descritiva/` | `descritiva_tuc.csv`            | Métricas de posição, dispersão e forma no **nível de Ativo Unitário (TUC)**.                |
| `output/estatistica_descritiva/` | `descritiva_projetos.csv`       | Métricas de posição, dispersão e forma no **nível de Obra Consolidada (PEP/ODI)**.           |
| `output/estatistica_descritiva/` | `levene_tuc.csv`                | Teste de Levene de variâncias entre distribuidoras no **nível de Ativo Unitário (TUC)**.      |
| `output/estatistica_descritiva/` | `levene_projetos.csv`           | Teste de Levene de variâncias entre distribuidoras no **nível de Obra Consolidada (PEP/ODI)**. |
| `output/comparacao_tis/`         | `relatorio_conciliacao_tcc.csv` | Validação entre os novos levantamentos e os levantamentos do tcc                                      |
| `output/comparacao_tis/`         | `output_tis_comuns.csv`         | Matriz binária ($\text{X} / -$) indicando a presença de cada TI por distribuidora.                  |
| `output/comparacao_tis/`         | `output_projetos_tis.csv`       | Contagem total de projetos únicos por TI e concessionária.                                            |
| `output/comparacao_tis/`         | `output_validar_tis.csv`        | Distribuição de frequência agregada por famílias de TI em familias de 10 em 10.                     |
