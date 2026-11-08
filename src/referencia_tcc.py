"""
Todos os campos utilizam os nomes dos cabeçalhos para
o script consolidar_base.py localizar automaticamente a linha do cabeçalho
e mapear a posição de cada coluna.
"""

FONTES = [
    {
        "empresa": "CEMIG",
        "arquivo": "AIS_INCREMENTAL_CEMIG.xlsb",
        "aba": "INCREMENTAL",
        "ti": ["Tipo de Instalação"],
        "odi": "Código ODI",
        "pep": "PEP",
        "conc": "Status de Conciliação",
        "voc": "Valor de Origem (R$)",
        "vnr": "VNR (R$)",
    },
    {
        "empresa": "ENEL SP",
        "arquivo": "Base_Incremental_EnelSP.xlsb",
        "aba": "Base Incremental",
        "ti": ["Tipo de Instalação (TI)", "TI"],
        "odi": "ODI",
        "pep": "Número de Projeto (PEP)",
        "conc": "Status de Conciliação",
        "voc": "Valor Original Contábil - VOC (R$)",
        "vnr": "VNR (R$)",
    },
    {
        "empresa": "CPFL Piratininga",
        "arquivo": "CPFL_Pira_Base_Incremental_V19.xlsb",
        "aba": "Incremental",
        "ti": ["TI"],
        "odi": "ODI",
        "pep": None,
        "conc": None,
        "voc": "Valor original contábil (Saneado) - VOC (R$)",
        "vnr": "VNR (R$)",
    },
    {
        "empresa": "Equatorial Para",
        "arquivo": "Equatorial-Para_Quadros-Resumos.xlsx",
        "aba": "Incremental",
        "ti": ["TI"],
        "odi": "ODI",
        "pep": "PEP",
        "conc": "Status de conciliação",
        "voc": "Valor original contábil - VOC (R$)",
        "vnr": "VNR (R$)",
    },
]