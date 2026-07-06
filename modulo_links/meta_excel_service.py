import os

import win32com.client


def coluna_para_indice(coluna):
    if isinstance(coluna, int):
        return coluna

    texto = str(coluna).strip().upper()
    if not texto:
        raise ValueError("Coluna do Excel vazia no .env")

    if texto.isdigit():
        return int(texto)

    indice = 0
    for char in texto:
        if not ("A" <= char <= "Z"):
            raise ValueError(f"Coluna invalida no .env: {coluna}")
        indice = indice * 26 + (ord(char) - ord("A") + 1)
    return indice


def proxima_linha_vazia(ws, linha_inicial, coluna_indice):
    linha = linha_inicial
    while True:
        valor = ws.Cells(linha, coluna_indice).Value
        if valor is None or str(valor).strip() == "":
            return linha
        linha += 1


def preco_texto_para_float(preco_texto):
    if not preco_texto:
        return None

    texto = str(preco_texto).strip().replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def gravar_meta_excel(root_dir, cfg, link_escolhido, titulo_final, preco_formatado):
    col_link = coluna_para_indice(cfg["col_link"])
    col_valor = coluna_para_indice(cfg["col_value"])
    row_link_start = int(cfg["row_link_start"])
    row_value_start = int(cfg["row_value_start"])

    if row_link_start < 1 or row_value_start < 1:
        return {"ok": False, "mensagem": "As linhas iniciais no .env devem ser maiores ou iguais a 1."}
    if col_link < 1 or col_valor < 1:
        return {"ok": False, "mensagem": "As colunas no .env devem ser maiores ou iguais a 1."}

    excel_path_cfg = cfg["excel_path"]
    caminho_excel = (
        os.path.join(root_dir, excel_path_cfg)
        if not os.path.isabs(excel_path_cfg)
        else excel_path_cfg
    )
    caminho_excel = os.path.abspath(caminho_excel)

    if not os.path.exists(caminho_excel):
        return {"ok": False, "mensagem": f"Arquivo Excel não encontrado: {caminho_excel}"}

    titulo_excel = str(titulo_final).replace('"', '""')
    formula_hiperlink = f'=HIPERLINK("{link_escolhido}";"{titulo_excel}")'

    print("\n⏳ Conectando à API do Excel via Win32COM (Proteção ativa para Macros)...")

    excel_vinculado_aqui = False
    excel = None
    wb = None
    wb_aberto_aqui = False
    visible_original = None
    display_alerts_original = None

    try:
        try:
            excel = win32com.client.GetActiveObject("Excel.Application")
        except Exception:
            excel = win32com.client.Dispatch("Excel.Application")
            excel_vinculado_aqui = True

        visible_original = excel.Visible
        display_alerts_original = excel.DisplayAlerts
        if excel_vinculado_aqui:
            excel.Visible = False
        excel.DisplayAlerts = False

        caminho_excel_real = os.path.normcase(os.path.abspath(caminho_excel))
        for aberto in excel.Workbooks:
            try:
                aberto_path = os.path.normcase(os.path.abspath(aberto.FullName))
                if aberto_path == caminho_excel_real:
                    wb = aberto
                    break
            except Exception:
                continue

        if wb is None:
            wb = excel.Workbooks.Open(caminho_excel)
            wb_aberto_aqui = True

        try:
            ws = wb.Sheets(cfg["sheet_name"])
        except Exception:
            print(f"ℹ️ Aba '{cfg['sheet_name']}' não encontrada. Criando nova aba...")
            ws = wb.Sheets.Add(After=wb.Sheets(wb.Sheets.Count))
            ws.Name = cfg["sheet_name"]
            ws.Cells(1, col_link).Value = "Jogo (Link)"
            ws.Cells(1, col_valor).Value = "Preco (R$)"

        linha_link = proxima_linha_vazia(ws, row_link_start, col_link)
        linha_valor = proxima_linha_vazia(ws, row_value_start, col_valor)

        ws.Cells(linha_link, col_link).FormulaLocal = formula_hiperlink

        preco_numerico = preco_texto_para_float(preco_formatado)
        if preco_numerico is not None:
            ws.Cells(linha_valor, col_valor).Value = preco_numerico
            ws.Cells(linha_valor, col_valor).NumberFormatLocal = "R$ #.##0,00"
            preco_exibicao = f"{preco_numerico:.2f}".replace(".", ",")
        else:
            ws.Cells(linha_valor, col_valor).Value = preco_formatado
            preco_exibicao = str(preco_formatado)

        print("\n⚙️ Dados estruturados com sucesso:")
        print(f" ├─ Celula {cfg['col_link']}{linha_link}: {formula_hiperlink}")
        print(f" └─ Celula {cfg['col_value']}{linha_valor}: {preco_exibicao}")

        wb.Save()
        print(f"\n✅ SUCESSO! '{titulo_final}' foi catalogado sem risco de corrupção no seu .xlsm!")

        return {
            "ok": True,
            "mensagem": "Meta adicionada com sucesso.",
            "titulo": titulo_final,
            "preco": preco_exibicao,
            "linha_link": linha_link,
            "linha_valor": linha_valor,
        }

    except Exception as e:
        msg = f"Erro crítico ao manipular o Excel via Win32COM: {e}"
        print(f"\n❌ {msg}")
        return {"ok": False, "mensagem": msg}

    finally:
        if wb and wb_aberto_aqui and not cfg["manter_excel_aberto"]:
            wb.Close(SaveChanges=True)
        if excel and not excel_vinculado_aqui:
            if display_alerts_original is not None:
                excel.DisplayAlerts = display_alerts_original
            if visible_original is not None:
                excel.Visible = visible_original
        if excel and excel_vinculado_aqui and not cfg["manter_excel_aberto"]:
            excel.Quit()
