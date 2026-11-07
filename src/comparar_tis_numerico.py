"""
Script: comparar_tis_numerico.py
Descrição: Conta os projetos únicos (PROJETO_UNIFICADO) por TI (0 a 99) nas distribuidoras.
Gera output/comparacao_tis/output_projetos_tis.csv.
"""
from pathlib import Path
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"
ARQUIVO_SAIDA = DIRETORIO_RAIZ / "output" / "comparacao_tis" / "output_projetos_tis.csv"


def main():
    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_DADOS.resolve()}")

    df_base = pd.read_csv(ARQUIVO_DADOS)
    lista_tis = list(range(0, 100))
    lista_empresas = ["CEMIG", "ENEL SP", "Equatorial Para", "CPFL Piratininga"]

    df_unicos = df_base.dropna(subset=["PROJETO_UNIFICADO"]).drop_duplicates(
        subset=["TI", "EMPRESA", "PROJETO_UNIFICADO"]
    )

    tabela_contagem = (
        pd.crosstab(df_unicos["TI"], df_unicos["EMPRESA"])
        .reindex(index=lista_tis, columns=lista_empresas, fill_value=0)
    )
    tabela_contagem = tabela_contagem.rename(columns={"Equatorial Para": "Equatorial Pará"})

    tabela_contagem["GLOBAL"] = tabela_contagem.sum(axis=1)

    total_geral = pd.DataFrame(tabela_contagem.sum(axis=0)).T
    total_geral.index = ["Total Geral"]

    tabela_final = pd.concat([tabela_contagem, total_geral])
    tabela_final.index.name = "TI"

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tabela_final.to_csv(ARQUIVO_SAIDA, encoding="utf-8-sig")
    print("[6/7] Contabilizando projetos por TI... OK")


if __name__ == "__main__":
    main()