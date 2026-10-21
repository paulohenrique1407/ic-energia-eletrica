"""Etapa 5 - Estatística multivariada / correlação (seções 5.3 e 5.4 do relatório).

EXEMPLO implementado: correlação VOC x VNR por TI (Pearson, Spearman e Pearson em log)
+ gráfico de dispersão em escala log. VOC/VNR são valores monetários assimétricos;
por isso comparar Pearson com Spearman e com a correlação em log é uma boa prática.

    python -m src.multivariada
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.config import (BASE_CONSOLIDADA, CORES_EMPRESAS, MIN_OBS_CORRELACAO,
                        OUT_MULTIVARIADA)
from src.utils.formatacao import nome_base
from src.utils.graficos import estilo, salvar_figura
from src.utils.tabelas import salvar_tabela

SCRIPT = Path(__file__).name


def correlacoes(df_ti: pd.DataFrame) -> dict:
    pos = df_ti[(df_ti["voc"] > 0) & (df_ti["vnr"] > 0)]
    return {
        "n": len(df_ti),
        "pearson": stats.pearsonr(df_ti["voc"], df_ti["vnr"])[0],
        "spearman": stats.spearmanr(df_ti["voc"], df_ti["vnr"])[0],
        "pearson_log": stats.pearsonr(np.log(pos["voc"]), np.log(pos["vnr"]))[0],
    }


def dispersao(df_ti: pd.DataFrame, ti: int):
    fig, ax = plt.subplots()
    for empresa, g in df_ti.groupby("empresa"):
        ax.scatter(g["voc"], g["vnr"], s=12, alpha=0.6, label=empresa,
                   color=CORES_EMPRESAS.get(empresa, "gray"))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("VOC (R$, escala log)")
    ax.set_ylabel("VNR (R$, escala log)")
    ax.set_title(f"VOC x VNR - TI {ti}")
    ax.legend(frameon=False)
    return fig


def analise_componentes_principais(df: pd.DataFrame):
    """PLACEHOLDER: espaço para PCA / agrupamento / regressão.

    Dica: use random_state=SEED (de src.config) em qualquer método aleatório e
    registre os parâmetros no CHANGELOG.md.
    """
    raise NotImplementedError


def main() -> None:
    estilo()
    df = pd.read_csv(BASE_CONSOLIDADA)

    linhas = []
    for ti, df_ti in df.groupby("ti"):
        if len(df_ti) < MIN_OBS_CORRELACAO:
            print(f"   TI {ti}: n={len(df_ti)} < {MIN_OBS_CORRELACAO}, ignorada")
            continue
        linhas.append({"ti": ti, **correlacoes(df_ti)})
        salvar_figura(dispersao(df_ti, ti), OUT_MULTIVARIADA / f"ti_{ti}",
                      nome_base("fig", "dispersao", "voc-vnr", ti), SCRIPT)

    salvar_tabela(pd.DataFrame(linhas), OUT_MULTIVARIADA,
                  nome_base("tab", "correlacao", "voc-vnr"),
                  "Correlação entre VOC e VNR por TI.", "tab:correlacao", SCRIPT)
    print("   multivariada: ok")


if __name__ == "__main__":
    main()
