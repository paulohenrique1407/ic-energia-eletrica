"""
Agrupa a contagem de observações por famílias de TIs de 10 em 10,
gera output/comparacao_tis/output_validar_tis.csv.
"""
from pathlib import Path
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"
ARQUIVO_SAIDA = DIRETORIO_RAIZ / "output" / "comparacao_tis" / "output_validar_tis.csv"


def main():
    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_DADOS.resolve()}")

    df_base = pd.read_csv(ARQUIVO_DADOS)

    familia_num = (df_base["TI"] // 10) * 10
    df_base["Família de TI"] = familia_num.astype(str) + "-" + (familia_num + 9).astype(str)

    lista_familias = [f"{i}-{i+9}" for i in range(10, 100, 10)]
    lista_empresas = ["CEMIG", "ENEL SP", "Equatorial Para", "CPFL Piratininga"]

    tabela_familias = (
        pd.crosstab(df_base["Família de TI"], df_base["EMPRESA"])
        .reindex(index=lista_familias, columns=lista_empresas, fill_value=0)
    )
    tabela_familias = tabela_familias.rename(columns={"Equatorial Para": "Equatorial Pará"})

    tabela_familias["GLOBAL"] = tabela_familias.sum(axis=1)

    total_geral = pd.DataFrame(tabela_familias.sum(axis=0)).T
    total_geral.index = ["Total Geral"]

    tabela_final = pd.concat([tabela_familias, total_geral])

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela_final.to_csv(ARQUIVO_SAIDA, index_label="Família de TI", encoding="utf-8-sig")
    print("[7/7] Validando famílias de TIs... OK")


if __name__ == "__main__":
    main()