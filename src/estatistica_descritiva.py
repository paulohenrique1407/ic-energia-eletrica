"""
Processa as estatísticas descritivas das 100 TIs em 2 camadas:
1. descritiva_tuc.csv (Ativo Individual)
2. descritiva_projetos.csv (Obra Consolidada PEP/ODI)
"""
from pathlib import Path
import numpy as np
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"
DIRETORIO_SAIDA = DIRETORIO_RAIZ / "output" / "estatistica_descritiva"


def calcular_estatisticas_grupo(df_dados: pd.DataFrame, nome_camada: str, nome_coluna_obs: str) -> list:
    """Calcula estatísticas de posição, dispersão e forma agrupando por TI e EMPRESA."""
    resultados = []

    grupos = df_dados.groupby(["TI", "EMPRESA"])

    for (ti, empresa), grupo in grupos:
        for variavel in ["VOC", "VNR", "RAZAO_VOC_VNR", "DESVIO_PERCENTUAL"]:
            if variavel not in grupo.columns:
                continue

            valores = grupo[variavel].dropna()
            total_observacoes = len(valores)
            if total_observacoes == 0:
                continue

            media = valores.mean()
            mediana = valores.median()
            desvio_padrao = valores.std(ddof=1) if total_observacoes > 1 else 0.0
            coeficiente_variacao = (desvio_padrao / media * 100) if (media != 0 and not np.isnan(media)) else np.nan
            q1 = valores.quantile(0.25)
            q3 = valores.quantile(0.75)

            resultados.append({
                "CAMADA": nome_camada,
                "TI": int(ti),
                "EMPRESA": empresa,
                "VARIAVEL": variavel,
                nome_coluna_obs: total_observacoes,
                "MEDIA": media,
                "MEDIANA": mediana,
                "DESVIO_PADRAO": desvio_padrao,
                "CV_PERCENT": coeficiente_variacao,
                "AMPLITUDE": valores.max() - valores.min(),
                "MIN": valores.min(),
                "Q1": q1,
                "Q3": q3,
                "MAX": valores.max(),
                "IQR": q3 - q1,
                "SKEWNESS": valores.skew() if total_observacoes > 2 else np.nan,
                "KURTOSIS": valores.kurtosis() if total_observacoes > 3 else np.nan,
            })

    return resultados


def main():
    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_DADOS.resolve()}")

    df_base = pd.read_csv(ARQUIVO_DADOS)
    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)

    # 1. Camada TUC (Ativo Individual)
    df_tuc = df_base.copy()
    df_tuc["RAZAO_VOC_VNR"] = df_tuc["VOC"] / df_tuc["VNR"]
    df_tuc["DESVIO_PERCENTUAL"] = ((df_tuc["VOC"] - df_tuc["VNR"]) / df_tuc["VNR"]) * 100

    resultados_tuc = calcular_estatisticas_grupo(df_tuc, "TUC_ATIVO", "N_OBS")
    pd.DataFrame(resultados_tuc).to_csv(DIRETORIO_SAIDA / "descritiva_tuc.csv", index=False, encoding="utf-8-sig")

    # 2. Camada Projeto (Obra Consolidada)
    df_validos_projeto = df_base[df_base["PROJETO_UNIFICADO"].notna()].copy()
    df_projetos = (
        df_validos_projeto.groupby(["TI", "EMPRESA", "PROJETO_UNIFICADO"], as_index=False)[["VOC", "VNR"]]
        .sum()
    )
    df_projetos["RAZAO_VOC_VNR"] = df_projetos["VOC"] / df_projetos["VNR"]
    df_projetos["DESVIO_PERCENTUAL"] = ((df_projetos["VOC"] - df_projetos["VNR"]) / df_projetos["VNR"]) * 100

    resultados_projetos = calcular_estatisticas_grupo(df_projetos, "PROJETO_PEP_ODI", "N_PROJETOS")
    pd.DataFrame(resultados_projetos).to_csv(DIRETORIO_SAIDA / "descritiva_projetos.csv", index=False, encoding="utf-8-sig")

    print("[2/7] Calculando estatísticas descritivas (TUC e Projetos)... OK")


if __name__ == "__main__":
    main()