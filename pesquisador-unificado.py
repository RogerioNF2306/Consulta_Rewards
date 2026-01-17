import os
import subprocess
import sys
import random
import time
import pyautogui
from playwright.sync_api import sync_playwright

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA MÁXIMA (REWARDS 2026)
# ==============================================================================
TERMO_BASE = "flask"       # Assunto principal
QUANTIDADE_BUSCAS = 30     # Qtd de buscas
# ==============================================================================

pyautogui.FAILSAFE = True

def mover_mouse_humano(x, y):
    """Move o mouse com tremores e desvios leves para parecer humano"""
    # Cria um alvo levemente fora do centro e depois corrige (simula erro humano)
    offset_x = random.randint(-4, 4)
    offset_y = random.randint(-4, 4)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.6, 1.1))
    pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))

def clicar_humano():
    """Simula o tempo de pressão física do dedo no botão"""
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.06, 0.16))
    pyautogui.mouseUp()

def executar_logica_pesquisa(quantidade, termo, x_ini, y_ini, x_limp, y_limp):
    """Lógica blindada contra análise de integridade"""
    complementos = ["python", "flask", "tutorial", "code", "github", "api", "framework", 
                    "documentation", "news", "examples", "structure", "database", "security"]
    
    for i in range(1, quantidade + 1):
        # PAUSA LONGA ALEATÓRIA: Fundamental para quebrar análise de cadência (a cada 5 buscas)
        if i % 5 == 0:
            pausa = random.randint(1, 10)
            print(f"   -- [SEGURANÇA] Pausa de {pausa}s para despistar algoritmos...")
            time.sleep(pausa)

        # 1. VOLTAR AO TOPO E LIMPAR
        pyautogui.press('home')
        time.sleep(random.uniform(1.2, 2.2))

        if i == 1:
            mover_mouse_humano(x_ini, y_ini)
        else:
            mover_mouse_humano(x_limp, y_limp)
        
        clicar_humano()
        time.sleep(random.uniform(2.0, 4.0))
        
        # 2. GERAÇÃO E DIGITAÇÃO HUMANA
        termo_final = f"{termo} {random.choice(complementos)} {random.randint(1, 9999)}"
        print(f"[{i}/{quantidade}] Pesquisando: {termo_final}")

        for char in termo_final:
            pyautogui.write(char)
            # Simula pausas de 'pensamento' maiores no espaço
            if char == " ":
                time.sleep(random.uniform(0.25, 0.5))
            else:
                time.sleep(random.uniform(0.06, 0.22))
        
        pyautogui.press('enter')

        # 3. ESPERA EXTENDIDA (Indispensável para validar os pontos)
        time.sleep(random.uniform(3, 5))

        # 4. INTERAÇÃO REAL NA PÁGINA (SCROLL)
        if random.choice([True, False]):
            print("   -- Simulando leitura humana...")
            for _ in range(random.randint(3, 6)):
                pyautogui.scroll(random.randint(-500, -200))
                time.sleep(random.uniform(0.8, 1.8))
            
            # Pequeno movimento aleatório do mouse após o scroll
            pyautogui.moveRel(random.randint(-50, 50), random.randint(-50, 50), duration=0.5)
            
            time.sleep(1)
            pyautogui.press('home')
            print("   -- Retornando ao topo.")
            time.sleep(2)

def modo_manual_edge_externo():
    X_INICIAL, Y_INICIAL = 1114, 362
    X_LIMPAR, Y_LIMPAR = 898, 197
    print("\n" + "="*50)
    print(f"MODO MANUAL (EDGE) | TERMO: {TERMO_BASE}")
    input("Prepare o Edge no Bing e pressione [ENTER]...")
    time.sleep(3)
    executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR)

def modo_automatico_playwright():
    X_INICIAL, Y_INICIAL = 1329, 327
    X_LIMPAR, Y_LIMPAR = 890, 163
    perfis = {
        "1": "rogeriofelixrj@gmail.com",
        "2": "rogeriofelix2306@gmail.com",
        "3": "familiafelix58b@gmail.com",
        "4": "raphaelfelixrj2306@gmail.com"
    }

    print("\n=== GERENCIADOR DE PERFIS (STEALTH ATIVO) ===")
    for id, nome in perfis.items():
        print(f"[{id}] Perfil: {nome}")
    
    escolha = input("\nEscolha o perfil: ").strip()
    if escolha not in perfis: return

    nome_perfil = perfis[escolha]
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")

    with sync_playwright() as p:
        print(f"\nAbrindo navegador blindado para: {nome_perfil}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0]
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)

        try:
            page.goto("https://www.bing.com", wait_until="networkidle")
            time.sleep(5)
            executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR)
            print(f"\n[SUCESSO] Perfil {nome_perfil} finalizado.")
            time.sleep(5)
        finally:
            context.close()

if __name__ == "__main__":
    while True:
        print("\n" + "#"*45)
        print("      SISTEMA REWARDS 2026 - BLINDAGEM TOTAL")
        print("#"*45)
        print(f" TERMO: {TERMO_BASE} | BUSCAS: {QUANTIDADE_BUSCAS}")
        print("-" * 45)
        print("[1] Modo Manual (Edge Externo)")
        print("[2] Modo Automático (Playwright Blindado)")
        print("[0] Sair")
        
        opcao = input("\nSelecione uma opção: ").strip()
        if opcao == "1": modo_manual_edge_externo()
        elif opcao == "2": modo_automatico_playwright()
        elif opcao == "0": break