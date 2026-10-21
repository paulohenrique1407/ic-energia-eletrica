from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import BASE_CONSOLIDADA, OUT_FIGURAS, OUT_TABELAS
from src.utils.checagens import conferir_soma
from src.utils.formatacao import nome_base
from src.utils.graficos import estilo, salvar_figura
from src.utils.tabelas import salvar_tabela

SCRIPT = Path(__file__).name