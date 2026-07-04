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
    python "%~dp0digitador_manual.py"
    pause
    goto inicio
)

if "%opcao%"=="2" (
    cls
    echo.
    echo ▶ Iniciando Consulta Rewards Automática...
    echo.
    python "%~dp0consulta-rewards.py"
    pause
    goto inicio
)

if "%opcao%"=="0" (
    echo.
    echo ✓ Encerrando sistema... Até logo!
    timeout /t 2 >nul
    exit /b 0
)

:: Caso digite qualquer outra coisa
cls
echo.
echo ✗ Opção inválida! Tente novamente.
timeout /t 2 /nobreak >nul
goto inicio