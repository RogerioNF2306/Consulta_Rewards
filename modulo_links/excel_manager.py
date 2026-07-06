import os
import time

import openpyxl


def carregar_planilha(path):
    try:
        wb = openpyxl.load_workbook(path, keep_vba=True)
        return wb
    except PermissionError:
        print(f"\n⚠️ Permissão Negada: O arquivo '{os.path.basename(path)}' está aberto ou bloqueado.")
        return None
    except Exception as e:
        print(f"❌ Erro ao abrir o arquivo Excel: {type(e).__name__}: {e}")
        return None


def salvar_planilha(wb, path):
    tentativas = 5
    for i in range(tentativas):
        try:
            wb.save(path)
            wb.close()
            time.sleep(1.5)
            return True
        except PermissionError as e:
            if i < tentativas - 1:
                print(f"⚠️ Arquivo bloqueado. Re-tentando em 3 segundos... ({i+1}/{tentativas})")
                time.sleep(3)
            else:
                print(f"\n❌ Falha definitiva ao salvar: permissão negada.\n{e}")
        except Exception as e:
            print(f"\n❌ Falha ao salvar planilha: {type(e).__name__}: {e}")
            break
    return False


def fechar_excel_forcado():
    try:
        print("\n⏳ Solicitando encerramento forçado do Excel...")
        os.system("taskkill /f /im excel.exe >nul 2>&1")
        time.sleep(1.5)
        print("✅ Processo do Excel encerrado com sucesso.")
    except Exception as e:
        print(f"⚠️ Não foi possível fechar o Excel automaticamente: {e}")
