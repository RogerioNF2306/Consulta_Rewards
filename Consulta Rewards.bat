@echo off
:: Configura o prompt de comando para UTF-8 (corrige os blocos de cores e emojis)
chcp 65001 >nul

title Microsoft Rewards Automação

:: Garante o posicionamento na pasta real deste .bat
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo   🤖 INICIANDO INTEGRADOR MICROSOFT REWARDS
echo ============================================================
echo.

:: Rastreamento inteligente do Ambiente Virtual (VENV)
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Ambiente virtual localizado na pasta atual. Ativando...
    call ".venv\Scripts\activate.bat"
) else if exist "..\.venv\Scripts\activate.bat" (
    echo [OK] Ambiente virtual localizado na raiz de Projetos. Ativando...
    call "..\.venv\Scripts\activate.bat"
) else (
    echo [AVISO] Nenhum .venv encontrado. Tentando rodar via Python Global...
)

echo.
echo 🚀 Executando: python consulta-rewards.py
echo ------------------------------------------------------------
echo.

:: Executa o arquivo correto
python consulta-rewards.py

echo.
echo ------------------------------------------------------------
echo 🏁 Script encerrado.
echo ============================================================
pause