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

# BANCO DE USER-AGENTS REAIS E ATUALIZADOS
LISTA_UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
]

def mover_mouse_humano(x, y):
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.6, 1.1))
    pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))

def clicar_humano():
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.07, 0.17))
    pyautogui.mouseUp()

def executar_logica_pesquisa(quantidade, termo, x_ini, y_ini, x_limp, y_limp):
    complementos = ["python", "flask", "tutorial", "code", "github", "api", "framework", 
                    "documentation", "news", "examples", "structure", "database", "security"]
    
    for i in range(1, quantidade + 1):
        if i % 5 == 0:
            pausa = random.randint(9,10)
            print(f"   -- [SEGURANÇA] Pausa anti-detecção: {pausa}s...")
            time.sleep(pausa)

        pyautogui.press('home')
        time.sleep(random.uniform(1.2, 2.2))

        if i == 1:
            mover_mouse_humano(x_ini, y_ini)
        else:
            mover_mouse_humano(x_limp, y_limp)
        
        clicar_humano()
        time.sleep(random.uniform(1.5, 3.0))
        
        termo_final = f"{termo} {random.choice(complementos)} {random.randint(1, 9999)}"
        print(f"[{i}/{quantidade}] Pesquisando: {termo_final}")

        for char in termo_final:
            pyautogui.write(char)
            time.sleep(random.uniform(0.06, 0.22) if char != " " else random.uniform(0.25, 0.45))
        
        pyautogui.press('enter')
        time.sleep(random.uniform(3, 5))

        if random.choice([True, False]):
            for _ in range(random.randint(3, 6)):
                pyautogui.scroll(random.randint(-500, -200))
                time.sleep(random.uniform(0.8, 1.8))
            pyautogui.moveRel(random.randint(-30, 30), random.randint(-30, 30), duration=1)
            time.sleep(1)
            pyautogui.press('home')
            time.sleep(1.5)

# --- CORREÇÃO: MODO MANUAL REINSERIDO ---
def modo_manual_edge_externo():
    # AJUSTE AS COORDENADAS ABAIXO SE NECESSÁRIO
    X_INICIAL, Y_INICIAL = 1114, 362
    X_LIMPAR, Y_LIMPAR = 898, 197
    
    print("\n" + "="*50)
    print(f"MODO MANUAL (EDGE) | TERMO: {TERMO_BASE} | QTD: {QUANTIDADE_BUSCAS}")
    input("👉 Abra o Edge no Bing e pressione [ENTER] aqui para começar...")
    
    print("\nIniciando em 3 segundos... FOQUE NA JANELA DO EDGE!")
    time.sleep(3)
    
    executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR)
    print("\n[OK] Tarefas concluídas no Modo Manual.")

def modo_automatico_playwright():
    X_INICIAL, Y_INICIAL = 1329, 327
    X_LIMPAR, Y_LIMPAR = 890, 163
    
    perfis = {
        "1": "rogeriofelixrj@gmail.com",
        "2": "rogeriofelix2306@gmail.com",
        "3": "familiafelix58b@gmail.com",
        "4": "raphaelfelixrj2306@gmail.com"
    }

    print("\n=== GERENCIADOR DE PERFIS ELITE (UA DINÂMICO) ===")
    for id, nome in perfis.items():
        print(f"[{id}] Perfil: {nome}")
    
    escolha = input("\nEscolha o perfil: ").strip()
    if escolha not in perfis: return

    nome_perfil = perfis[escolha]
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")
    ua_perfil = LISTA_UA[int(escolha) % len(LISTA_UA)]

    with sync_playwright() as p:
        print(f"\nAbrindo navegador blindado: {nome_perfil}")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars",
                f"--user-agent={ua_perfil}"
            ]
        )
        
        page = context.pages[0]
        cores = random.choice([4, 8, 12])
        ram = random.choice([8, 16])
        page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram}}});
            window.chrome = {{ runtime: {{}} }};
        """)

        try:
            page.goto("https://www.bing.com", wait_until="networkidle")
            time.sleep(5)
            executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR)
            print(f"\n[SUCESSO] Perfil {nome_perfil} concluído.")
            time.sleep(5)
        finally:
            context.close()

if __name__ == "__main__":
    while True:
        print("\n" + "#"*45)
        print("      SISTEMA REWARDS 2026 - FINAL FIX")
        print("#"*45)
        print(f" TERMO: {TERMO_BASE} | BUSCAS: {QUANTIDADE_BUSCAS}")
        print("-" * 45)
        print("[1] Modo Manual (Usar seu Edge aberto)")
        print("[2] Modo Automático (Playwright Blindado)")
        print("[0] Sair")
        
        opcao = input("\nSelecione uma opção: ").strip()
        if opcao == "1":
            modo_manual_edge_externo() # <-- FUNÇÃO AGORA DEFINIDA E ATIVA
        elif opcao == "2":
            modo_automatico_playwright()
        elif opcao == "0":
            break