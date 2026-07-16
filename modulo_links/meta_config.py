import os
from pathlib import Path
from dotenv import load_dotenv

def _get_env_int(var_name, default):
    valor = os.getenv(var_name, str(default))
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        print(f"⚠️ Valor inválido em {var_name}='{valor}'. Usando padrão {default}.")
        return int(default)


def _get_env_bool(var_name, default=True):
    valor_padrao = "1" if default else "0"
    valor = os.getenv(var_name, valor_padrao).strip().lower()
    return valor not in {"0", "false", "nao", "não", "off"}


def load_meta_env(root_dir):
    # O pathlib monta o caminho automaticamente: root_dir / "config" / ".env"
    env_path = Path(root_dir) / "config" / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        print(f"⚠️ Atenção: Arquivo .env não encontrado em: {env_path}")

    return {
        "excel_path": os.getenv("EXCEL_PATH", "Histórico de Compras Xbox-Py.xlsm"),
        "sheet_name": os.getenv("Excel_Metas", "Metas"),
        "col_link": os.getenv("Excel_Metas_Column", "B"),
        "row_link_start": _get_env_int("Excel_Metas_Start_Row", 2),
        "col_value": os.getenv("Excel_Metas_Value", "C"),
        "row_value_start": _get_env_int("Excel_Metas_Value_Start_Row", 2),
        "manter_excel_aberto": _get_env_bool("MANTER_EXCEL_ABERTO", default=True),
    }