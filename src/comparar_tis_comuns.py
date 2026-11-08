"""
Mapeia presença/ausência das TIs (0 a 99) entre as distribuidoras,
gera output/comparacao_tis/output_tis_comuns.csv.
"""
from pathlib import Path
import numpy as np
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"
ARQUIVO_SAIDA = DIRETORIO_RAIZ / "output" / "comparacao_tis" / "output_tis_comuns.csv"


def main():
    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_DADOS.resolve()}")

    df_base = pd.read_csv(ARQUIVO_DADOS)
    lista_tis = list(range(0, 100))
    lista_empresas = ["CEMIG", "ENEL SP", "Equatorial Para", "CPFL Piratininga"]

    matriz_presenca = (
        pd.crosstab(df_base["TI"], df_base["EMPRESA"])
        .reindex(index=lista_tis, columns=lista_empresas, fill_value=0)
    )

    tabela_resultado = pd.DataFrame(
        np.where(matriz_presenca > 0, "X", "-"),
        index=matriz_presenca.index,
        columns=matriz_presenca.columns,
    )
    tabela_resultado = tabela_resultado.rename(columns={"Equatorial Para": "Equatorial Pará"})

    tabela_resultado["Comum a Todas"] = (matriz_presenca > 0).all(axis=1).map({True: "VERDADEIRO", False: "FALSO"})
    tabela_resultado.index.name = "TI"

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela_resultado.to_csv(ARQUIVO_SAIDA, encoding="utf-8-sig")
    print("[5/7] Mapeando TIs comuns entre distribuidoras... OK")


if __name__ == "__main__":
    main()