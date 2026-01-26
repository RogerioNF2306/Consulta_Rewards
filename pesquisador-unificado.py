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
pyautogui.FAILSAFE = True
# ==============================================================================

def obter_identidade_perfil(id_perfil):
    """
    Define uma impressão digital ÚNICA e FIXA para cada perfil.
    Evita que o sistema detecte mudanças de hardware na mesma conta.
    """
    lista_ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
    ]
    
    # Seleção baseada no ID para ser persistente
    idx = (int(id_perfil) - 1) % len(lista_ua)
    ua = lista_ua[idx]
    
    # Hardware fixo por perfil (para não parecer que você troca de PC toda hora)
    hardware_configs = {
        "1": {"cores": 8, "ram": 16},
        "2": {"cores": 4, "ram": 8},
        "3": {"cores": 12, "ram": 32},
        "4": {"cores": 8, "ram": 16}
    }
    config = hardware_configs.get(id_perfil, {"cores": 8, "ram": 16})
    
    return ua, config["cores"], config["ram"]

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
            pausa = random.randint(15, 25)
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
        time.sleep(random.uniform(5, 10))

        if random.choice([True, False]):
            for _ in range(random.randint(3, 6)):
                pyautogui.scroll(random.randint(-500, -200))
                time.sleep(random.uniform(0.8, 1.8))
            pyautogui.moveRel(random.randint(-30, 30), random.randint(-30, 30), duration=1)
            time.sleep(1)
            pyautogui.press('home')
            time.sleep(1.5)

def modo_manual_edge_externo():
    X_INICIAL, Y_INICIAL = 1114, 362
    X_LIMPAR, Y_LIMPAR = 898, 197
    print("\n" + "="*50)
    print(f"MODO MANUAL (EDGE) | TERMO: {TERMO_BASE}")
    input("👉 Prepare o Edge no Bing e pressione [ENTER]...")
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

    print("\n=== GERENCIADOR DE PERFIS ===")
    for id_p, nome in perfis.items():
        print(f"[{id_p}] Perfil: {nome}")
    
    escolha = input("\nEscolha o perfil: ").strip()
    if escolha not in perfis: return

    nome_perfil = perfis[escolha]
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")
    
    # BUSCA IDENTIDADE STEALTH DO NAVEGADOR.PY
    ua_ativo, cpu_cores, ram_gb = obter_identidade_perfil(escolha)

    with sync_playwright() as p:
        print(f"\n🚀 Lançando instância: {nome_perfil}")
        print(f"🎭 UA: {ua_ativo[:50]}... | Hardware: {cpu_cores} Cores / {ram_gb}GB")

        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars",
                f"--user-agent={ua_ativo}",
                "--lang=pt-BR"
            ],
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )
        
        page = context.pages[0]

        # INJEÇÃO DE STEALTH PROFUNDO (DNV DO NAVEGADOR.PY)
        page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu_cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram_gb}}});
            Object.defineProperty(navigator, 'languages', {{get: () => ['pt-BR', 'pt', 'en-US', 'en']}});
            window.chrome = {{ 
                runtime: {{}},
                app: {{}},
                csi: function() {{}},
                loadTimes: function() {{}}
            }};
        """)

        try:
            page.goto("https://www.bing.com", wait_until="networkidle")
            time.sleep(random.uniform(4, 6))
            executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR)
            print(f"\n[SUCESSO] Perfil {nome_perfil} finalizado.")
            time.sleep(5)
        finally:
            context.close()

if __name__ == "__main__":
    while True:
        print("\n" + "#"*45)
        print("Gerenciador de Pesquisas Unificado")
        print("#"*45)
        print(f" TERMO: {TERMO_BASE} | BUSCAS: {QUANTIDADE_BUSCAS}")
        print("-" * 45)
        print("[1] Modo Manual (Edge)")
        print("[2] Modo Automático (Playwright)")
        print("[0] Sair")
        
        opcao = input("\nSelecione uma opção: ").strip()
        if opcao == "1":
            modo_manual_edge_externo()
        elif opcao == "2":
            modo_automatico_playwright()
        elif opcao == "0":
            break