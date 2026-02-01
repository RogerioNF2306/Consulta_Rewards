import os
import subprocess
import sys
import random
import time
import pyautogui
import tkinter as tk
from threading import Thread
from playwright.sync_api import sync_playwright

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA MÁXIMA (REWARDS 2026)
# ==============================================================================
TERMO_BASE = "flask"       
QUANTIDADE_BUSCAS = 30     
pyautogui.FAILSAFE = True
# ==============================================================================

class StatusHUD:
    """Cria uma pequena janela no canto superior direito para monitoramento detalhado."""
    def __init__(self, modo="Manual", conta="N/A"):
        self.root = tk.Tk()
        self.root.title("HUD Rewards")
        self.root.attributes("-topmost", True)      
        self.root.overrideredirect(True)            
        self.root.attributes("-alpha", 0.85)         
        
        largura_tela = self.root.winfo_screenwidth()
        # Altura ajustada para 140 para caber todas as labels confortavelmente
        self.root.geometry(f"300x140+{largura_tela - 320}+30")
        self.root.configure(bg='black')

        # Label de Modo e Conta (Novidade)
        self.label_identidade = tk.Label(self.root, text=f"Modo: {modo} | {conta}", font=("Arial", 9, "bold"), fg="#FF00FF", bg="black")
        self.label_identidade.pack(pady=2)

        self.label_progresso = tk.Label(self.root, text="Iniciando...", font=("Arial", 10, "bold"), fg="white", bg="black")
        self.label_progresso.pack(pady=2)

        self.label_termo = tk.Label(self.root, text="Aguardando...", font=("Arial", 9), fg="#00FF00", bg="black", wraplength=280)
        self.label_termo.pack(pady=1)

        self.label_falta = tk.Label(self.root, text="", font=("Arial", 9), fg="yellow", bg="black")
        self.label_falta.pack(pady=1)

        self.label_status_tempo = tk.Label(self.root, text="Status: Pronto", font=("Arial", 9, "italic"), fg="#00FFFF", bg="black")
        self.label_status_tempo.pack(pady=2)

    def atualizar(self, atual, total, termo, status_tempo=""):
        faltam_busca = total - atual
        # Lógica de cálculo para próxima pausa
        faltam_pausa = 5 - (atual % 5) if atual % 5 != 0 else 5
        
        self.label_progresso.config(text=f"Pesquisa: {atual} / {total}")
        self.label_termo.config(text=f"Termo: {termo}")
        self.label_falta.config(text=f"Restam: {faltam_busca} | Prox. Pausa em: {faltam_pausa}")
        
        if status_tempo:
            self.label_status_tempo.config(text=status_tempo, fg="#FF6666" if "PAUSA" in status_tempo else "#00FFFF")
        
        self.root.update()

    def fechar(self):
        self.root.destroy()

hud = None

def obter_identidade_perfil(id_perfil):
    lista_ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
    ]
    idx = (int(id_perfil) - 1) % len(lista_ua)
    ua = lista_ua[idx]
    hardware_configs = {
        "1": {"cores": 8, "ram": 16}, "2": {"cores": 4, "ram": 8},
        "3": {"cores": 12, "ram": 32}, "4": {"cores": 8, "ram": 16}
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

def executar_logica_pesquisa(quantidade, termo, x_ini, y_ini, x_limp, y_limp, modo, conta):
    global hud
    complementos = ["python", "flask", "tutorial", "code", "github", "api", "framework", 
                    "documentation", "news", "examples", "structure", "database", "security"]
    
    hud = StatusHUD(modo=modo, conta=conta)

    for i in range(1, quantidade + 1):
        termo_final = f"{termo} {random.choice(complementos)} {random.randint(1, 9999)}"
        hud.atualizar(i, quantidade, termo_final, "Status: Digitando...")

        if i > 1 and (i - 1) % 5 == 0:
            tempo_pausa = random.randint(15, 25)
            for seg in range(tempo_pausa, 0, -1):
                hud.atualizar(i-1, quantidade, "---", f"⚠️ PAUSA SEGURANÇA: {seg}s")
                time.sleep(1)
            hud.atualizar(i, quantidade, termo_final, "Status: Retomando...")

        pyautogui.press('home')
        time.sleep(random.uniform(1.2, 2.2))

        if i == 1:
            mover_mouse_humano(x_ini, y_ini)
        else:
            mover_mouse_humano(x_limp, y_limp)
        
        clicar_humano()
        time.sleep(random.uniform(1.5, 3.0))
        
        print(f"[{i}/{quantidade}] Pesquisando: {termo_final}")
        for char in termo_final:
            pyautogui.write(char)
            time.sleep(random.uniform(0.06, 0.22) if char != " " else random.uniform(0.25, 0.45))
        
        pyautogui.press('enter')
        
        espera_leitura = random.randint(18, 25)
        for seg in range(espera_leitura, 0, -1):
            hud.atualizar(i, quantidade, termo_final, f"Status: Lendo página ({seg}s)")
            time.sleep(1)

        if random.choice([True, False]):
            pyautogui.scroll(random.randint(-400, -100))
            time.sleep(1)
            pyautogui.press('home')

    hud.fechar()

def modo_manual_edge_externo():
    X_INICIAL, Y_INICIAL = 1114, 362
    X_LIMPAR, Y_LIMPAR = 898, 197
    print("\n" + "="*50)
    print(f"MODO MANUAL (EDGE) | TERMO: {TERMO_BASE}")
    input("👉 Prepare o Edge no Bing e pressione [ENTER]...")
    time.sleep(3)
    # Passando os dados de modo e conta
    executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR, "Manual (Edge)", "Perfil Local")

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
    ua_ativo, cpu_cores, ram_gb = obter_identidade_perfil(escolha)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                f"--user-agent={ua_ativo}"
            ],
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )
        
        page = context.pages[0]
        page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu_cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram_gb}}});
            window.chrome = {{ runtime: {{}}, app: {{}}, csi: function() {{}}, loadTimes: function() {{}} }};
        """)

        try:
            page.goto("https://www.bing.com", wait_until="networkidle")
            time.sleep(5)
            # Passando os dados de modo e conta
            executar_logica_pesquisa(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL, Y_INICIAL, X_LIMPAR, Y_LIMPAR, "Automático", nome_perfil)
        finally:
            context.close()

if __name__ == "__main__":
    while True:
        print("\n" + "#"*45)
        print("      SISTEMA REWARDS 2026 - HUD ATIVO")
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