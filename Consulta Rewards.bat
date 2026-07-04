@echo off
:: Configura o prompt de comando para UTF-8 (corrige os blocos de cores e emojis)
chcp 65001 >nul

title Microsoft Rewards - Integrador Excel

:: Garante o posicionamento na pasta real deste .bat
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:inicio
cls
echo ============================================================
echo    🤖 INICIANDO INTEGRADOR MICROSOFT REWARDS - Excel
echo ============================================================
echo.
echo [1] Modo Manual (Salvamento de Dados no Excel Manual)
echo [2] Modo Automático (Informações da Conta e Resgate)
echo [0] Sair
echo.

set /p opcao="Escolha uma opção (0-2): "

if "%opcao%"=="1" (
    cls
    echo.
    echo ▶ Iniciando Painel de Entrada Manual...
    echo.
    echo Site do Rewards Earn: "https://rewards.bing.com/earn"
    echo.
    python "%~dp0digitador_manual.py"
    
    :: Se o Python retornar código 2 (Cancelou com 'S'), volta direto pro menu sem travar a tela
    if errorlevel 2 goto inicio
    
    :: Se foi sucesso (código 0), dá a pausa para você ver a confirmação verde antes de voltar
    echo.
    pause
    goto inicio
)

if "%opcao%"=="2" (
    cls
    echo.
    echo ▶ Iniciando Consulta Rewards Automática...
    echo.
    python "%~dp0consulta-rewards.py"
    echo.
    pause
    goto inicio
)

if "%opcao%"=="0" (
    echo.
    echo ✓ Encerrando sistema... Até logo!
    timeout /t 2 >nul
    exit /b 0
)

:: Caso digite qualquer outra coisa no menu principal
cls
echo.
echo ✗ Opção inválida! Tente novamente.
timeout /t 2 /nobreak >nul
goto inicio