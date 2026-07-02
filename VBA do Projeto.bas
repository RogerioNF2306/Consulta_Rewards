Attribute VB_Name = "M�dulo3"

Private Function DataValorParaDate(ByVal dataValor As Variant) As Date
    Dim partesData As Variant
    Dim dataTexto As String

    If IsDate(dataValor) Then
        DataValorParaDate = DateValue(CDate(dataValor))
        Exit Function
    End If

    dataTexto = Trim$(CStr(dataValor))
    If Len(dataTexto) = 0 Then
        DataValorParaDate = Date
        Exit Function
    End If

    partesData = Split(Trim$(dataTexto), "/")
    If UBound(partesData) = 2 Then
        DataValorParaDate = DateSerial(CInt(partesData(2)), CInt(partesData(1)), CInt(partesData(0)))
        Exit Function
    End If

    partesData = Split(Trim$(dataTexto), "-")
    If UBound(partesData) = 2 Then
        If Len(partesData(0)) = 4 Then
            DataValorParaDate = DateSerial(CInt(partesData(0)), CInt(partesData(1)), CInt(partesData(2)))
        Else
            DataValorParaDate = DateSerial(CInt(partesData(2)), CInt(partesData(1)), CInt(partesData(0)))
        End If
        Exit Function
    End If

    DataValorParaDate = DateValue(CDate(dataTexto))
End Function

Public Function RegistrarPontosEFormatar(ByVal nomeAba As String, ByVal dataAtual As Variant, ByVal pesquisa As Long, ByVal ofertas As Long, ByVal mes As Long, ByVal ano As Long, ByVal totais As Long) As Boolean
    On Error GoTo ErrHandler
    Dim ws As Worksheet
    Dim row As Long
    Dim linhaExistente As Long
    Dim UltimaLinhaComDados As Long
    Dim maxRow As Long
    Dim temDado As Boolean
    Dim cols As Variant
    Dim c As Variant
    Dim dataRegistro As Date
    Dim dataTextoNormalizada As String
    Dim linhaAlvo As Long
    RegistrarPontosEFormatar = False

    ' Configura a planilha de destino dinamicamente com base no .env mapeado pelo Python
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets(nomeAba)
    On Error GoTo 0

    ' Se a aba n�o existir, ela � criada com o layout padr�o e cabe�alhos estruturados
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Sheets.Add(Before:=ThisWorkbook.Sheets(1))
        ws.Name = nomeAba

        ' --- MAPEAMENTO COMPLETO DE COLUNAS ---
        ws.Cells(1, 1).Value = "Data"          ' Coluna 1 (A) - Data do registro (DD/MM/AAAA)
        ws.Cells(1, 2).Value = "Pesquisa Bing" ' Coluna 2 (B) - Pontos di�rios acumulados em buscas
        ws.Cells(1, 3).Value = "Ofertas"       ' Coluna 3 (C) - Pontos de cards e atividades di�rias
        ws.Cells(1, 4).Value = "Soma"          ' Coluna 4 (D) - RESERVADA: Coluna com f�rmulas manuais (Ignorada pelo Python)
        ws.Cells(1, 5).Value = "Pontos no M�s" ' Coluna 5 (E) - Progresso total do m�s atual
        ws.Cells(1, 6).Value = "Pontos no Ano" ' Coluna 6 (F) - Progresso total do ano corrente
        ws.Cells(1, 7).Value = "Pontos Totais" ' Coluna 7 (G) - Saldo l�quido atual da conta Microsoft

        ' Estiliza��o do Cabe�alho
        With ws.Range("A1:G1")
            .Font.Bold = True
            .Interior.Color = RGB(31, 78, 121)
            .Font.Color = RGB(255, 255, 255)
            .HorizontalAlignment = xlCenter
        End With
    End If

    ' Converte o texto dd/mm/aaaa recebido do Python em uma data real, evitando
    ' que o Excel interprete a string pela localidade errada.
    dataRegistro = DataValorParaDate(dataAtual)
    dataTextoNormalizada = Format$(dataRegistro, "dd/mm/yyyy")

    ' --- VERIFICAÇÃO DE DATA EXISTENTE (Evita duplicados) ---
    linhaExistente = 0
    maxRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).row
    If maxRow < 1 Then maxRow = 1

    For row = 2 To maxRow
        If Format$(ws.Cells(row, 1).Value, "dd/mm/yyyy") = dataTextoNormalizada Or Trim$(ws.Cells(row, 1).Text) = dataTextoNormalizada Then
            linhaExistente = row
            Exit For
        End If
    Next row

    ' Define a linha alvo com base na exist�ncia da data
    If linhaExistente > 0 Then
        linhaAlvo = linhaExistente
    Else
        ' Executa a varredura id�ntica ao openpyxl para encontrar a �ltima linha �til ignorando a coluna 4 (D)
        UltimaLinhaComDados = 1
        maxRow = ws.UsedRange.Rows.Count
        If maxRow < 1 Then maxRow = 1

        cols = Array(1, 2, 3, 5, 6, 7) ' Mapeamento das colunas de dados reais (Ignora a coluna 4/D)

        For row = 2 To maxRow + 1
            temDado = False
            For Each c In cols
                If Not IsEmpty(ws.Cells(row, c).Value) And ws.Cells(row, c).Value <> "" Then
                    temDado = True
                    Exit For
                End If
            Next c
            If temDado Then
                UltimaLinhaComDados = row
            End If
        Next row
        linhaAlvo = UltimaLinhaComDados + 1
    End If

    ' --- INSERÇÃO DOS DADOS NAS COLUNAS COMENTADAS ---
    ws.Cells(linhaAlvo, 1).Value = dataRegistro ' Coluna 1 (A) -> Data
    ws.Cells(linhaAlvo, 2).Value = pesquisa     ' Coluna 2 (B) -> Pesquisa Bing
    ws.Cells(linhaAlvo, 3).Value = ofertas      ' Coluna 3 (C) -> Ofertas
    ' Coluna 4 (D) -> "Soma (Pula)" � intencionalmente ignorada para preservar suas f�rmulas nativas.
    ws.Cells(linhaAlvo, 5).Value = mes          ' Coluna 5 (E) -> Pontos M�s
    ws.Cells(linhaAlvo, 6).Value = ano          ' Coluna 6 (F) -> Pontos Ano
    ws.Cells(linhaAlvo, 7).Value = totais       ' Coluna 7 (G) -> Pontos Totais

    ' --- FORMATAÇÃO VISUAL ---
    ' Aplica separadores de milhar normatizados
    ws.Range(ws.Cells(linhaAlvo, 2), ws.Cells(linhaAlvo, 3)).NumberFormat = "#,##0"
    ws.Range(ws.Cells(linhaAlvo, 5), ws.Cells(linhaAlvo, 7)).NumberFormat = "#,##0"
    ws.Cells(linhaAlvo, 1).NumberFormat = "dd/mm/yyyy"
    ws.Cells(linhaAlvo, 1).HorizontalAlignment = xlCenter

    ' Autoajuste de colunas autom�tico para evitar o erro "###"
    ws.Columns("A:G").AutoFit

    ' For�a o salvamento seguro do arquivo em background
    ThisWorkbook.Save
    RegistrarPontosEFormatar = True
    Exit Function

ErrHandler:
    On Error Resume Next
    If Not ws Is Nothing Then
        ws.Range("Z1").Value = "Erro RegistrarPontosEFormatar: " & Err.Number & " - " & Err.Description
    End If
    RegistrarPontosEFormatar = False
End Function
