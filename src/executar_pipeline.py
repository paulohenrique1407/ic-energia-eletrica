"""
Script: executar_pipeline.py
Descrição: Apaga o diretório output/ e executa a sequência completa de scripts do pipeline.
"""
import shutil
import time
from pathlib import Path

import consolidar_base
import estatistica_descritiva
import teste_levene
import gerar_relatorio_conciliacao
import comparar_tis_comuns
import comparar_tis_numerico
import validar_tis

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_SAIDA = DIRETORIO_RAIZ / "output"


def limpar_diretorio_saida():
    """Remove todo o conteúdo prévio do diretório output/."""
    if DIRETORIO_SAIDA.exists():
        shutil.rmtree(DIRETORIO_SAIDA)
        print(f"[OK] Diretório limpo: {DIRETORIO_SAIDA.resolve()}")

    (DIRETORIO_SAIDA / "estatistica_descritiva").mkdir(parents=True, exist_ok=True)
    (DIRETORIO_SAIDA / "comparacao_tis").mkdir(parents=True, exist_ok=True)


def main():
    tempo_inicio = time.time()
    print("==================================================")
    print("     INICIANDO PIPELINE DE ESTATÍSTICA DESCRITIVA ")
    print("==================================================")

    limpar_diretorio_saida()

    consolidar_base.main()
    estatistica_descritiva.main()
    teste_levene.main()
    gerar_relatorio_conciliacao.main()
    comparar_tis_comuns.main()
    comparar_tis_numerico.main()
    validar_tis.main()

    tempo_total = time.time() - tempo_inicio
    print("==================================================")
    print(f" PIPELINE CONCLUÍDO COM SUCESSO EM {tempo_total:.2f}s! ")
    print("==================================================")


if __name__ == "__main__":
    main()