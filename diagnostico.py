#!/usr/bin/env python3
"""
Script de Diagnóstico - Consulta Rewards
Ajuda a identificar e resolver problemas de conexão
"""

import os
import shutil
import subprocess
import sys

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def main():
    print(f"\n{BOLD}🔧 DIAGNÓSTICO - SISTEMA REWARDS CONSULTATION{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    # 1. Verificar se Chrome está rodando
    print(f"{YELLOW}[1/5] Verificando processos Chrome...{RESET}")
    try:
        resultado = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True
        )
        if "chrome.exe" in resultado.stdout:
            print(f"{RED}❌ Chrome ainda está aberto! Fechando...{RESET}")
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                         capture_output=True)
            print(f"{GREEN}✅ Chrome fechado{RESET}\n")
        else:
            print(f"{GREEN}✅ Nenhum Chrome aberto{RESET}\n")
    except:
        print(f"{YELLOW}⚠️  Não consegui verificar Chrome (OK em Linux/Mac){RESET}\n")
    
    # 2. Verificar diretório microsoft_session
    print(f"{YELLOW}[2/5] Verificando perfil microsoft_session...{RESET}")
    profile_dir = os.path.join(os.getcwd(), "microsoft_session")
    
    if os.path.exists(profile_dir):
        size = sum(f.stat().st_size for f in os.scandir(profile_dir) if f.is_file())
        print(f"├─ Encontrado: {profile_dir}")
        print(f"├─ Tamanho: {size / (1024*1024):.2f} MB")
        
        limpar = input(f"{YELLOW}├─ Deseja limpar esse perfil? (s/n): {RESET}").lower()
        if limpar == 's':
            try:
                shutil.rmtree(profile_dir)
                print(f"{GREEN}✅ Perfil limpo{RESET}\n")
            except Exception as e:
                print(f"{RED}❌ Erro ao limpar: {e}{RESET}\n")
        else:
            print(f"{GREEN}✅ Perfil mantido{RESET}\n")
    else:
        print(f"{GREEN}✅ Perfil novo será criado{RESET}\n")
    
    # 3. Verificar Playwright
    print(f"{YELLOW}[3/5] Verificando Playwright...{RESET}")
    try:
        import playwright
        print(f"{GREEN}✅ Playwright instalado{RESET}\n")
    except ImportError:
        print(f"{RED}❌ Playwright NÃO instalado!{RESET}")
        print(f"Execute: pip install playwright")
        print(f"Depois: playwright install chromium\n")
        return False
    
    # 4. Verificar .env
    print(f"{YELLOW}[4/5] Verificando arquivo .env...{RESET}")
    if os.path.exists(".env"):
        print(f"{GREEN}✅ Arquivo .env encontrado{RESET}\n")
    else:
        print(f"{YELLOW}⚠️  .env não encontrado, será criado automaticamente{RESET}\n")
    
    # 5. Tentar executar
    print(f"{YELLOW}[5/5] Tentando iniciar navegador...{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    input(f"\n{BOLD}Pressione ENTER para iniciar o navegador...{RESET}")
    
    # Executar consulta-rewards.py
    resultado = subprocess.run([sys.executable, "consulta-rewards.py"])
    
    return resultado.returncode == 0

if __name__ == "__main__":
    try:
        sucesso = main()
        if sucesso:
            print(f"\n{GREEN}✅ Tudo funcionou!{RESET}")
        else:
            print(f"\n{RED}❌ Houve um erro{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Cancelado pelo usuário{RESET}")
    except Exception as e:
        print(f"\n{RED}Erro: {e}{RESET}")
