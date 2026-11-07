"""
Script: teste_levene.py
Descrição: Aplica o Teste de Levene para verificar igualdade de variâncias entre distribuidoras:
1. levene_tuc.csv (Ativo Individual)
2. levene_projetos.csv (Obra Consolidada)
"""
from pathlib import Path
import pandas as pd
from scipy import stats

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_DADOS = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"
DIRETORIO_SAIDA = DIRETORIO_RAIZ / "output" / "estatistica_descritiva"


def executar_teste_levene(df_input: pd.DataFrame, nome_camada: str, minimo_observacoes: int) -> list:
    """Executa o teste de Levene entre distribuidoras por TI e variável."""
    resultados = []
    grupos_ti = df_input.groupby("TI")

    for ti, dados_ti in grupos_ti:
        for variavel in ["VOC", "VNR"]:
            amostras_empresas = []
            empresas_avaliadas = []

            for empresa, dados_empresa in dados_ti.groupby("EMPRESA"):
                valores = dados_empresa[variavel].dropna().values
                if len(valores) >= minimo_observacoes:
                    amostras_empresas.append(valores)
                    empresas_avaliadas.append(empresa)

            if len(amostras_empresas) >= 2:
                estatistica_levene, p_valor = stats.levene(*amostras_empresas, center="median")
                resultados.append({
                    "CAMADA": nome_camada,
                    "TI": int(ti),
                    "VARIAVEL": variavel,
                    "N_EMPRESAS_TESTADAS": len(amostras_empresas),
                    "EMPRESAS": ", ".join(empresas_avaliadas),
                    "ESTATISTICA_LEVENE": estatistica_levene,
                    "P_VALOR": p_valor,
                    "VARIANCE_HOMOGENEO": p_valor > 0.05,
                })

    return resultados


def main():
    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_DADOS.resolve()}")

    df_base = pd.read_csv(ARQUIVO_DADOS)
    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)

    # 1. Levene Nível TUC
    resultados_tuc = executar_teste_levene(df_base, "TUC_ATIVO", minimo_observacoes=5)
    pd.DataFrame(resultados_tuc).to_csv(DIRETORIO_SAIDA / "levene_tuc.csv", index=False, encoding="utf-8-sig")

    # 2. Levene Nível Projetos
    df_validos_projeto = df_base[df_base["PROJETO_UNIFICADO"].notna()].copy()
    df_projetos = (
        df_validos_projeto.groupby(["TI", "EMPRESA", "PROJETO_UNIFICADO"], as_index=False)[["VOC", "VNR"]]
        .sum()
    )
    resultados_projetos = executar_teste_levene(df_projetos, "PROJETO_PEP_ODI", minimo_observacoes=3)
    pd.DataFrame(resultados_projetos).to_csv(DIRETORIO_SAIDA / "levene_projetos.csv", index=False, encoding="utf-8-sig")

    print("[3/7] Aplicando Teste de Levene... OK")


if __name__ == "__main__":
    main()