@echo off
chcp 65001 > nul
cls

:inicio
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║         SISTEMA REWARDS 2026 - LAUNCHER            ║
echo ║     Automação de Pesquisas com Stealth Mode       ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo [1] Pesquisador Unificado (Modo Manual + Automático)
echo [2] Navegador Stealth (Sessão Interativa)
echo [3] Consulta Rewards (Informações da Conta)
echo [4] Exibir Configurações Ativas
echo [0] Sair
echo.
set /p opcao="Escolha uma opção (0-4): "

if "%opcao%"=="1" (
    cls
    echo.
    echo ▶ Iniciando Pesquisador Unificado...
    echo.
    python "%~dp0pesquisador-unificado.py"
    pause
    cls
    goto inicio
) else if "%opcao%"=="2" (
    cls
    echo.
    echo ▶ Iniciando Navegador Stealth...
    echo.
    python "%~dp0navegador.py"
    pause
    cls
    goto inicio
) else if "%opcao%"=="3" (
    cls
    echo.
    echo ▶ Iniciando Consulta Rewards...
    echo.
    python "%~dp0consulta-rewards.py"
    pause
    cls
    goto inicio
) else if "%opcao%"=="4" (
    cls
    echo.
    echo ▶ Exibindo Configurações...
    echo.
    python "%~dp0config.py"
    pause
    cls
    goto inicio
) else if "%opcao%"=="0" (
    echo.
    echo ✓ Encerrando sistema... Até logo!
    echo.
    exit /b 0
) else (
    cls
    echo.
    echo ✗ Opção inválida! Tente novamente.
    echo.
    timeout /t 2 /nobreak > nul
    cls
    goto inicio
)

echo.
pause
exit /b 0
