"""
Lê as planilhas brutas a partir dos nomes dos cabeçalhos definidos em referencia_tcc.py,
localiza a linha do cabeçalho automaticamente, descarta as sobras,
cria a chave PROJETO_UNIFICADO (PEP se existir, senão ODI) e mantém apenas linhas válidas com VOC > 0 e VNR > 0.
Saída: data/processed/base_consolidada.csv
"""
import re
import sys
import unicodedata
from pathlib import Path
import pandas as pd

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_RAW = DIRETORIO_RAIZ / "data" / "raw"
ARQUIVO_SAIDA = DIRETORIO_RAIZ / "data" / "processed" / "base_consolidada.csv"

if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

from referencia_tcc import FONTES

LIMITE_BUSCA_CABECALHO = 40
VALORES_VAZIOS = {"nan", "None", "0", ""}


def normalizar_texto(texto) -> str:
    """Converte o texto para minúsculas, remove acentos, quebras de linha e colapsa espaços."""
    sem_quebra = str(texto).replace("\n", " ").replace("\r", " ")
    sem_acento = unicodedata.normalize("NFKD", sem_quebra)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


def obter_nomes_colunas(configuracao: dict) -> dict:
    """Mapeia os rótulos internos para os nomes reais esperados no cabeçalho."""
    nomes = {f"TI_{i}": nome for i, nome in enumerate(configuracao["ti"])}
    for campo in ("odi", "pep", "conc", "voc", "vnr"):
        if configuracao[campo] is not None:
            nomes[campo.upper()] = configuracao[campo]
    return nomes


def encontrar_linha_cabecalho(df_raw: pd.DataFrame, nomes_colunas: dict, nome_empresa: str) -> int:
    """Procura a primeira linha que contém todos os cabeçalhos esperados."""
    alvo = {chave: normalizar_texto(nome) for chave, nome in nomes_colunas.items()}

    for linha_idx in range(min(len(df_raw), LIMITE_BUSCA_CABECALHO)):
        celulas = {normalizar_texto(c) for c in df_raw.iloc[linha_idx] if isinstance(c, str)}
        faltam = [chave for chave, nome_norm in alvo.items() if nome_norm not in celulas]
        if not faltam:
            return linha_idx

    raise ValueError(f"Não foi possível localizar a linha de cabeçalho para a empresa: {nome_empresa}")


def mapear_posicao_colunas(linha_cabecalho: list, nomes_colunas: dict) -> dict:
    """Retorna o índice numérico 0-based de cada coluna encontrada no cabeçalho."""
    linha_norm = [normalizar_texto(c) if isinstance(c, str) else None for c in linha_cabecalho]
    posicoes = {}
    for chave, nome in nomes_colunas.items():
        alvo = normalizar_texto(nome)
        posicoes[chave] = linha_norm.index(alvo)
    return posicoes


def extrair_coluna_texto(df_dados: pd.DataFrame, posicao: int | None) -> pd.Series:
    """Extrai uma coluna de texto pelo seu índice ou retorna nulos se ausente."""
    if posicao is None:
        return pd.Series(None, index=df_dados.index, dtype=object)
    return df_dados.iloc[:, posicao].astype(str).str.strip()


def extrair_dados_empresa(configuracao: dict) -> pd.DataFrame:
    """Lê a aba da distribuidora e extrai as colunas com busca dinâmica de cabeçalho."""
    caminho_arquivo = DIRETORIO_RAW / configuracao["arquivo"]
    engine_leitura = "pyxlsb" if caminho_arquivo.suffix.lower() == ".xlsb" else None

    df_raw = pd.read_excel(
        caminho_arquivo,
        sheet_name=configuracao["aba"],
        header=None,
        engine=engine_leitura,
    )

    nomes_colunas = obter_nomes_colunas(configuracao)
    linha_cabecalho_idx = encontrar_linha_cabecalho(df_raw, nomes_colunas, configuracao["empresa"])
    posicoes = mapear_posicao_colunas(df_raw.iloc[linha_cabecalho_idx].tolist(), nomes_colunas)

    dados = df_raw.iloc[linha_cabecalho_idx + 1:].copy()

    # Extração de TI (se houver mais de uma coluna, vale o primeiro valor numérico)
    colunas_ti = [pd.to_numeric(dados.iloc[:, posicoes[f"TI_{i}"]], errors="coerce") for i in range(len(configuracao["ti"]))]
    serie_ti = pd.concat(colunas_ti, axis=1).bfill(axis=1).iloc[:, 0]

    return pd.DataFrame({
        "EMPRESA": configuracao["empresa"],
        "TI": serie_ti,
        "VOC": pd.to_numeric(dados.iloc[:, posicoes["VOC"]], errors="coerce"),
        "VNR": pd.to_numeric(dados.iloc[:, posicoes["VNR"]], errors="coerce"),
        "ODI": extrair_coluna_texto(dados, posicoes.get("ODI")),
        "PEP": extrair_coluna_texto(dados, posicoes.get("PEP")),
        "STATUS_CONCILIACAO": extrair_coluna_texto(dados, posicoes.get("CONC")) if "CONC" in posicoes else "CO",
    })


def main():
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    tabelas_empresas = [extrair_dados_empresa(configuracao) for configuracao in FONTES]
    df_consolidado = pd.concat(tabelas_empresas, ignore_index=True)

    for coluna in ("PEP", "ODI", "STATUS_CONCILIACAO"):
        df_consolidado[coluna] = df_consolidado[coluna].mask(df_consolidado[coluna].isin(VALORES_VAZIOS))

    df_consolidado = df_consolidado[df_consolidado["TI"].between(0, 99)].copy()
    df_consolidado["TI"] = df_consolidado["TI"].astype(int)

    mascara_sobras = df_consolidado["STATUS_CONCILIACAO"].fillna("CO").str.upper().str.contains("SC|SF")
    df_consolidado = df_consolidado[~mascara_sobras].copy()

    df_consolidado["PROJETO_UNIFICADO"] = df_consolidado["PEP"].fillna(df_consolidado["ODI"])

    df_consolidado = df_consolidado[(df_consolidado["VOC"] > 0) & (df_consolidado["VNR"] > 0)].copy()

    df_consolidado.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"[1/7] Consolidando bases brutas... OK ({len(df_consolidado):,} linhas)")


if __name__ == "__main__":
    main()