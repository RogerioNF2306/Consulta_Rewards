Attribute VB_Name = "Modulo4"
Option Explicit

Private Function MontarComandoPython(ByVal pythonExe As String, ByVal scriptPath As String, ByVal nomeJogo As String) As String
    Dim jogoSeguro As String

    ' Evita quebrar o parser de linha de comando em caso de aspas no nome.
    jogoSeguro = Replace(nomeJogo, """", "'")

    MontarComandoPython = "cmd /c """"" & pythonExe & """ """" & scriptPath & """ --from-vba --jogo """" & jogoSeguro & """"""
End Function

Private Function ExtrairLinhaResultado(ByVal saida As String) As String
    Dim linhas() As String
    Dim i As Long

    linhas = Split(saida, vbCrLf)
    For i = LBound(linhas) To UBound(linhas)
        If Left$(Trim$(linhas(i)), 15) = "RESULTADO_META|" Then
            ExtrairLinhaResultado = Trim$(linhas(i))
            Exit Function
        End If
    Next i

    ExtrairLinhaResultado = ""
End Function

Public Sub Modulo4_AdicionarMetaRewards()
    On Error GoTo ErrHandler

    Dim nomeJogo As String
    Dim pythonExe As String
    Dim scriptPath As String
    Dim comando As String

    Dim shellObj As Object
    Dim execObj As Object
    Dim saida As String
    Dim saidaErro As String
    Dim linhaResultado As String
    Dim partes() As String

    nomeJogo = InputBox("Digite o nome do jogo para adicionar nas metas:", "Modulo 4 - Adicionar Meta")
    nomeJogo = Trim$(nomeJogo)

    If Len(nomeJogo) = 0 Then
        MsgBox "Operacao cancelada pelo usuario.", vbInformation, "Modulo 4"
        Exit Sub
    End If

    pythonExe = ThisWorkbook.Path & "\.venv\Scripts\python.exe"
    scriptPath = ThisWorkbook.Path & "\adicionar_meta.py"

    If Len(Dir$(scriptPath)) = 0 Then
        MsgBox "Arquivo nao encontrado: " & scriptPath, vbCritical, "Modulo 4"
        Exit Sub
    End If

    If Len(Dir$(pythonExe)) = 0 Then
        MsgBox "Python da venv nao encontrado em: " & pythonExe & vbCrLf & _
               "Crie/ative a venv antes de usar o Modulo 4.", vbCritical, "Modulo 4"
        Exit Sub
    End If

    comando = MontarComandoPython(pythonExe, scriptPath, nomeJogo)

    Set shellObj = CreateObject("WScript.Shell")
    Set execObj = shellObj.Exec(comando)

    Application.StatusBar = "Modulo 4: consultando jogo e gravando na planilha..."
    Do While execObj.Status = 0
        DoEvents
    Loop
    Application.StatusBar = False

    saida = execObj.StdOut.ReadAll
    saidaErro = execObj.StdErr.ReadAll
    If Len(saidaErro) > 0 Then
        saida = saida & vbCrLf & saidaErro
    End If

    linhaResultado = ExtrairLinhaResultado(saida)

    If Len(linhaResultado) = 0 Then
        MsgBox "Nao foi possivel interpretar o retorno do Python." & vbCrLf & vbCrLf & saida, vbExclamation, "Modulo 4"
        Exit Sub
    End If

    partes = Split(linhaResultado, "|")
    If UBound(partes) < 2 Then
        MsgBox "Retorno invalido: " & linhaResultado, vbExclamation, "Modulo 4"
        Exit Sub
    End If

    If partes(1) = "OK" Then
        Dim titulo As String
        Dim preco As String
        Dim linhaLink As String
        Dim linhaValor As String

        titulo = IIf(UBound(partes) >= 2, partes(2), "")
        preco = IIf(UBound(partes) >= 3, partes(3), "")
        linhaLink = IIf(UBound(partes) >= 4, partes(4), "")
        linhaValor = IIf(UBound(partes) >= 5, partes(5), "")

        MsgBox "Meta adicionada com sucesso!" & vbCrLf & _
               "Jogo: " & titulo & vbCrLf & _
               "Preco: R$ " & preco & vbCrLf & _
               "Linha Link: " & linhaLink & " | Linha Valor: " & linhaValor, vbInformation, "Modulo 4"
    Else
        Dim erroTexto As String
        erroTexto = IIf(UBound(partes) >= 2, partes(2), "Falha nao identificada")
        MsgBox "Falha ao adicionar meta:" & vbCrLf & erroTexto, vbCritical, "Modulo 4"
    End If

    Exit Sub

ErrHandler:
    Application.StatusBar = False
    MsgBox "Erro no Modulo 4: " & Err.Number & " - " & Err.Description, vbCritical, "Modulo 4"
End Sub
