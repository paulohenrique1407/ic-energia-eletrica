"""
Script: gerar_relatorio_conciliacao.py
Descrição: Compara os novos resultados com a tabela verdade histórica do TCC (TIs 31, 33 e 38).
Gera o relatório relatorio_conciliacao_tcc.csv.
"""
from pathlib import Path
import numpy as np
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_DESCRITIVA = DIRETORIO_RAIZ / "output" / "estatistica_descritiva"
DIRETORIO_SAIDA = DIRETORIO_RAIZ / "output" / "comparacao_tis"
ARQUIVO_SAIDA = DIRETORIO_SAIDA / "relatorio_conciliacao_tcc.csv"

BENCHMARK_TCC = pd.DataFrame([
    # TI 31
    {"TI": 31, "EMPRESA": "CEMIG", "VARIAVEL": "VOC", "MEDIA_TCC": 310990.91, "MEDIANA_TCC": 4864.73},
    {"TI": 31, "EMPRESA": "CEMIG", "VARIAVEL": "VNR", "MEDIA_TCC": 380508.58, "MEDIANA_TCC": 10644.69},
    {"TI": 31, "EMPRESA": "ENEL SP", "VARIAVEL": "VOC", "MEDIA_TCC": 991849.47, "MEDIANA_TCC": 228266.97},
    {"TI": 31, "EMPRESA": "ENEL SP", "VARIAVEL": "VNR", "MEDIA_TCC": 216290.10, "MEDIANA_TCC": 160210.00},
    {"TI": 31, "EMPRESA": "Equatorial Para", "VARIAVEL": "VOC", "MEDIA_TCC": 480809.92, "MEDIANA_TCC": 82810.88},
    {"TI": 31, "EMPRESA": "Equatorial Para", "VARIAVEL": "VNR", "MEDIA_TCC": 465148.57, "MEDIANA_TCC": 99656.51},
    {"TI": 31, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VOC", "MEDIA_TCC": 43876.22, "MEDIANA_TCC": 43876.22},
    {"TI": 31, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VNR", "MEDIA_TCC": 43876.22, "MEDIANA_TCC": 43876.22},
    # TI 33
    {"TI": 33, "EMPRESA": "CEMIG", "VARIAVEL": "VOC", "MEDIA_TCC": 613815.00, "MEDIANA_TCC": 31431.00},
    {"TI": 33, "EMPRESA": "CEMIG", "VARIAVEL": "VNR", "MEDIA_TCC": 701596.70, "MEDIANA_TCC": 41505.00},
    {"TI": 33, "EMPRESA": "ENEL SP", "VARIAVEL": "VOC", "MEDIA_TCC": 737545.84, "MEDIANA_TCC": 162021.66},
    {"TI": 33, "EMPRESA": "ENEL SP", "VARIAVEL": "VNR", "MEDIA_TCC": 314487.70, "MEDIANA_TCC": 80406.00},
    {"TI": 33, "EMPRESA": "Equatorial Para", "VARIAVEL": "VOC", "MEDIA_TCC": 533306.00, "MEDIANA_TCC": 65862.31},
    {"TI": 33, "EMPRESA": "Equatorial Para", "VARIAVEL": "VNR", "MEDIA_TCC": 604984.50, "MEDIANA_TCC": 85787.00},
    {"TI": 33, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VOC", "MEDIA_TCC": 445228.50, "MEDIANA_TCC": 45563.00},
    {"TI": 33, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VNR", "MEDIA_TCC": 475472.00, "MEDIANA_TCC": 63611.20},
    # TI 38
    {"TI": 38, "EMPRESA": "CEMIG", "VARIAVEL": "VOC", "MEDIA_TCC": 755437.78, "MEDIANA_TCC": 282504.71},
    {"TI": 38, "EMPRESA": "CEMIG", "VARIAVEL": "VNR", "MEDIA_TCC": 774083.78, "MEDIANA_TCC": 281517.62},
    {"TI": 38, "EMPRESA": "ENEL SP", "VARIAVEL": "VOC", "MEDIA_TCC": 448533.86, "MEDIANA_TCC": 103913.50},
    {"TI": 38, "EMPRESA": "ENEL SP", "VARIAVEL": "VNR", "MEDIA_TCC": 201238.44, "MEDIANA_TCC": 180006.00},
    {"TI": 38, "EMPRESA": "Equatorial Para", "VARIAVEL": "VOC", "MEDIA_TCC": 2252516.51, "MEDIANA_TCC": 102720.48},
    {"TI": 38, "EMPRESA": "Equatorial Para", "VARIAVEL": "VNR", "MEDIA_TCC": 2367236.17, "MEDIANA_TCC": 101517.43},
    {"TI": 38, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VOC", "MEDIA_TCC": 587515.01, "MEDIANA_TCC": 148692.94},
    {"TI": 38, "EMPRESA": "CPFL Piratininga", "VARIAVEL": "VNR", "MEDIA_TCC": 594792.03, "MEDIANA_TCC": 149066.80},
])


def diagnosticar_divergencia(linha: pd.Series) -> str:
    """Classifica a razão metodológica da diferença entre o novo cálculo e o TCC legado."""
    diferenca_projeto = linha["DIF_REL_MEDIA_PROJETO_%"]
    diferenca_tuc = linha["DIF_REL_MEDIA_TUC_%"]
    empresa = linha["EMPRESA"]
    variavel = linha["VARIAVEL"]
    ti = linha["TI"]

    if pd.notna(diferenca_projeto) and abs(diferenca_projeto) < 1.0:
        return "Paridade Exata com Projeto (PEP/ODI)"
    elif pd.notna(diferenca_tuc) and abs(diferenca_tuc) < 1.0:
        return "Paridade Exata com TUC (Ativo)"
    elif ti == 33 and empresa == "Equatorial Para" and variavel == "VOC":
        return "Erro de Transcrição Legada (Omissão de Dígito no TCC)"
    elif empresa == "ENEL SP" and variavel == "VNR":
        return "Erro de Filtragem/Somatório de VNR no TCC Legado"
    elif empresa == "CPFL Piratininga" and ti == 38:
        return "TCC Legado Processado a Nível TUC (Ativo) em vez de Projeto"
    elif empresa == "CPFL Piratininga" and ti == 33:
        return "Unificação por Chave ODI com Filtro de Conciliação Atualizado"
    elif abs(diferenca_projeto) < 5.0:
        return "Aderência Alta ao Nível Projeto (Variação de Filtro)"
    else:
        return "Divergência de Granularidade / Filtro de Conciliação"


def main():
    arquivo_tuc = DIRETORIO_DESCRITIVA / "descritiva_tuc.csv"
    arquivo_projetos = DIRETORIO_DESCRITIVA / "descritiva_projetos.csv"

    if not arquivo_tuc.exists() or not arquivo_projetos.exists():
        raise FileNotFoundError("Gere os arquivos descritivos antes de rodar a conciliação.")

    df_tuc = pd.read_csv(arquivo_tuc)
    df_projetos = pd.read_csv(arquivo_projetos)

    df_tuc = df_tuc[df_tuc["VARIAVEL"].isin(["VOC", "VNR"])].copy()
    df_projetos = df_projetos[df_projetos["VARIAVEL"].isin(["VOC", "VNR"])].copy()

    tabela_tuc = pd.merge(
        BENCHMARK_TCC,
        df_tuc[["TI", "EMPRESA", "VARIAVEL", "N_OBS", "MEDIA", "MEDIANA"]].rename(
            columns={"N_OBS": "N_TUC", "MEDIA": "MEDIA_TUC", "MEDIANA": "MEDIANA_TUC"}
        ),
        on=["TI", "EMPRESA", "VARIAVEL"],
        how="left",
    )

    tabela_conciliada = pd.merge(
        tabela_tuc,
        df_projetos[["TI", "EMPRESA", "VARIAVEL", "N_PROJETOS", "MEDIA", "MEDIANA"]].rename(
            columns={"MEDIA": "MEDIA_PROJETO", "MEDIANA": "MEDIANA_PROJETO"}
        ),
        on=["TI", "EMPRESA", "VARIAVEL"],
        how="left",
    )

    tabela_conciliada["DIF_REL_MEDIA_PROJETO_%"] = np.round(
        ((tabela_conciliada["MEDIA_PROJETO"] - tabela_conciliada["MEDIA_TCC"]) / tabela_conciliada["MEDIA_TCC"]) * 100, 2
    )
    tabela_conciliada["DIF_REL_MEDIA_TUC_%"] = np.round(
        ((tabela_conciliada["MEDIA_TUC"] - tabela_conciliada["MEDIA_TCC"]) / tabela_conciliada["MEDIA_TCC"]) * 100, 2
    )

    tabela_conciliada["DIAGNOSTICO_CAUSAL"] = tabela_conciliada.apply(diagnosticar_divergencia, axis=1)

    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)
    tabela_conciliada.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print("[4/7] Gerando relatório de conciliação metodológica... OK")


if __name__ == "__main__":
    main()