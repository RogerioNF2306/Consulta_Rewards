import os
import subprocess
import sys
import random
import time
import pyautogui
import tkinter as tk
from threading import Thread
from playwright.sync_api import sync_playwright

# Importar configurações do .env / config
from config.config import (
    TERMO_BASE, QUANTIDADE_BUSCAS, 
    DELAY_ENTRE_BUSCAS_MIN, DELAY_ENTRE_BUSCAS_MAX,
    DELAY_LEITURA_MIN, DELAY_LEITURA_MAX,
    DELAY_PAUSA_MIN, DELAY_PAUSA_MAX,
    DELAY_CLICK_MIN, DELAY_CLICK_MAX,
    MOUSE_OFFSET_X, MOUSE_OFFSET_Y,
    LOCALE, TIMEZONE, URL_BING,
    obter_user_agent_por_perfil, obter_hardware_perfil,
    X_INICIAL_MANUAL, Y_INICIAL_MANUAL,
    X_LIMPAR_MANUAL, Y_LIMPAR_MANUAL,
    X_CAIXA_AUTOMATICO, Y_CAIXA_AUTOMATICO,
    X_REPETIR_AUTOMATICO, Y_REPETIR_AUTOMATICO
)

# ==============================================================================
# CONFIGURAÇÕES DE SEGURANÇA MÁXIMA
# ==============================================================================
pyautogui.FAILSAFE = True
# ==============================================================================

class StatusHUD:
    """Cria uma interface HUD refinada, moderna e proporcional no canto superior direito."""
    def __init__(self, modo="Manual", conta="N/A"):
        self.root = tk.Tk()
        self.root.title("HUD Rewards")
        self.root.attributes("-topmost", True)      
        self.root.overrideredirect(True)            
        self.root.attributes("-alpha", 0.95)         
        
        largura_hud = 340
        altura_hud = 175
        largura_tela = self.root.winfo_screenwidth()
        
        self.root.geometry(f"{largura_hud}x{altura_hud}+{largura_tela - largura_hud - 25}+25")
        self.root.configure(bg='#1A1A1A')

        self.frame_interno = tk.Frame(self.root, bg='#0D0D0D', bd=1, relief="solid", highlightbackground="#333333", highlightthickness=1)
        self.frame_interno.pack(fill="both", expand=True, padx=4, pady=4)

        self.label_identidade = tk.Label(
            self.frame_interno, 
            text=f"⚙️ {modo.upper()}\n👤 {conta}", 
            font=("Consolas", 9, "bold"), 
            fg="#FF00FF", bg="#0D0D0D", 
            justify="center", bd=0
        )
        self.label_identidade.pack(fill="x", pady=(8, 4))

        divisor = tk.Frame(self.frame_interno, height=1, bg="#262626")
        divisor.pack(fill="x", padx=15, pady=4)

        self.label_progresso = tk.Label(
            self.frame_interno, 
            text="Pesquisa: 0 / 0", 
            font=("Segoe UI", 10, "bold"), 
            fg="#FFFFFF", bg="#0D0D0D"
        )
        self.label_progresso.pack(pady=1)
        
        self.label_barra = tk.Label(
            self.frame_interno,
            text="[----------]",
            font=("Consolas", 10, "bold"),
            fg="#444444", bg="#0D0D0D"
        )
        self.label_barra.pack(pady=1)

        self.label_termo = tk.Label(
            self.frame_interno, 
            text="Aguardando inicialização...", 
            font=("Segoe UI", 9), 
            fg="#00FF00", bg="#0D0D0D", 
            wraplength=310, justify="center"
        )
        self.label_termo.pack(pady=2, fill="x", padx=10)

        self.label_falta = tk.Label(
            self.frame_interno, 
            text="Calculando rota...", 
            font=("Segoe UI", 8), 
            fg="#BBBBBB", bg="#0D0D0D"
        )
        self.label_falta.pack(pady=1)

        self.label_status_tempo = tk.Label(
            self.frame_interno, 
            text="Status: Pronto", 
            font=("Segoe UI", 9, "bold"), 
            fg="#00FFFF", bg="#0D0D0D"
        )
        self.label_status_tempo.pack(pady=(2, 8))

    def actualizar(self, atual, total, termo, status_tempo=""):
        faltam_busca = total - atual
        faltam_pausa = 5 - (atual % 5) if atual % 5 != 0 else 5
        
        proporcao = int((atual / total) * 10) if total > 0 else 0
        barra_texto = f"[{'■' * proporcao}{'-' * (10 - proporcao)}]"
        
        self.label_progresso.config(text=f"Pesquisa: {atual} / {total}")
        self.label_barra.config(text=barra_texto, fg="#00FF00" if proporcao > 0 else "#444444")
        self.label_termo.config(text=f"🔎 {termo}")
        self.label_falta.config(text=f"Restam: {faltam_busca} buscas | Próxima Pausa em: {faltam_pausa}")
        
        if status_tempo:
            if "PAUSA" in status_tempo or "⚠️" in status_tempo:
                cor_status = "#FF5555"
                self.label_barra.config(fg="#FF5555")
            else:
                cor_status = "#00FFFF"
            self.label_status_tempo.config(text=status_tempo, fg=cor_status)
        
        self.root.update()

    def fechar(self):
        self.root.destroy()


def mover_mouse_humano(x, y):
    offset_x = random.randint(-MOUSE_OFFSET_X, MOUSE_OFFSET_X)
    offset_y = random.randint(-MOUSE_OFFSET_Y, MOUSE_OFFSET_Y)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.4, 0.7))
    pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.2))

def clicar_humano():
    pyautogui.mouseDown()
    time.sleep(random.uniform(DELAY_CLICK_MIN, DELAY_CLICK_MAX))
    pyautogui.mouseUp()

def digitar_humano(texto):
    for char in texto:
        pyautogui.write(char)
        time.sleep(random.uniform(0.04, 0.14) if char != " " else random.uniform(0.18, 0.32))

def gerar_termo_organico(termo_base):
    conectores = ["como funciona", "exemplos de", "documentacao", "tutorial passo a passo", "melhores praticas", "sintaxe", "erro resolvido", "guia completo"]
    complementos = ["em desenvolvimento", "avancado", "com exemplos", "clean code", "na prática", "com api", "no github", "arquitetura moderna"]
    
    if random.choice([True, False]):
        return f"{random.choice(conectores)} {termo_base} {random.choice(complementos)}"
    else:
        return f"{termo_base} {random.choice(complementos)} {random.randint(2024, 2026)}"


def execucao_manual_worker(quantidade, termo, x_ini, y_ini, x_limp, y_limp, hud_obj):
    """Controla o navegador manual aberto externamente pelo usuário"""
    try:
        time.sleep(2) 
        for i in range(1, quantidade + 1):
            termo_final = gerar_termo_organico(termo)
            hud_obj.actualizar(i, quantidade, termo_final, "Status: Digitando...")

            if i > 1 and (i - 1) % 5 == 0:
                tempo_pausa = random.randint(DELAY_PAUSA_MIN, DELAY_PAUSA_MAX)
                for seg in range(tempo_pausa, 0, -1):
                    hud_obj.actualizar(i-1, quantidade, "---", f"⚠️ PAUSA SEGURANÇA: {seg}s")
                    time.sleep(1)
                hud_obj.actualizar(i, quantidade, termo_final, "Status: Retomando...")

            pyautogui.press('home')
            time.sleep(random.uniform(DELAY_ENTRE_BUSCAS_MIN, DELAY_ENTRE_BUSCAS_MAX))

            if i == 1:
                mover_mouse_humano(x_ini, y_ini)
            else:
                mover_mouse_humano(x_limp, y_limp)
            
            clicar_humano()
            time.sleep(random.uniform(1.0, 1.8))
            
            digitar_humano(termo_final)
            pyautogui.press('enter')
            
            espera_leitura = random.randint(DELAY_LEITURA_MIN, DELAY_LEITURA_MAX)
            for seg in range(espera_leitura, 0, -1):
                hud_obj.actualizar(i, quantidade, termo_final, f"Status: Lendo página ({seg}s)")
                time.sleep(1)

            if random.choice([True, False]):
                pyautogui.scroll(random.randint(-500, -200))
                time.sleep(random.uniform(0.8, 1.5))
                pyautogui.press('home')

    finally:
        hud_obj.fechar()


def execucao_hibrida_playwright_worker(quantidade, termo, nome_perfil, user_data_dir, ua_ativo, cpu_cores, ram_gb, hud_obj):
    """ABRE o perfil limpo via Playwright e OPERA a digitação e cliques físicos com PyAutoGUI"""
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
            locale=LOCALE,
            timezone_id=TIMEZONE
        )
        
        page = context.pages[0]
        page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu_cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram_gb}}});
            window.chrome = {{ runtime: {{}}, app: {{}}, csi: function() {{}}, loadTimes: function() {{}} }};
        """)

        try:
            page.goto(URL_BING, wait_until="networkidle")
            time.sleep(3)

            # Carrega posições salvas do ambiente de configuração
            box_inicial_x = X_CAIXA_AUTOMATICO
            box_inicial_y = Y_CAIXA_AUTOMATICO
            box_repetir_x = X_REPETIR_AUTOMATICO
            box_repetir_y = Y_REPETIR_AUTOMATICO

            # Contingência dinâmica do DOM para o primeiro clique caso o .env esteja zerado
            if box_inicial_x == 0 or box_inicial_y == 0:
                print("⚠️ Coordenadas iniciais do .env ausentes. Executando varredura dinâmica no DOM...")
                try:
                    search_box = page.locator("input[name='q'], #sb_form_q").first
                    search_box.wait_for(state="visible", timeout=5000)
                    box_bounding = search_box.bounding_box()
                    if box_bounding:
                        box_inicial_x = int(box_bounding["x"] + (box_bounding["width"] / 2))
                        box_inicial_y = int(box_bounding["y"] + (box_bounding["height"] / 2))
                except Exception as dom_err:
                    print(f"❌ Falha crítica de varredura na tela inicial: {dom_err}")
                    return

            for i in range(1, quantidade + 1):
                termo_final = gerar_termo_organico(termo)
                hud_obj.actualizar(i, quantidade, termo_final, "Status: Movendo Mouse...")

                # Pausa de Segurança Estrutural a cada 5 iterações
                if i > 1 and (i - 1) % 5 == 0:
                    tempo_pausa = random.randint(DELAY_PAUSA_MIN, DELAY_PAUSA_MAX)
                    for seg in range(tempo_pausa, 0, -1):
                        hud_obj.actualizar(i-1, quantidade, "---", f"⚠️ PAUSA SEGURANÇA: {seg}s")
                        time.sleep(1)
                    hud_obj.actualizar(i, quantidade, termo_final, "Status: Retomando...")

                # 1. Determina dinamicamente o alvo com base no ciclo de buscas
                if i == 1:
                    target_x, target_y = box_inicial_x, box_inicial_y
                else:
                    # Se houver coordenada consecutiva mapeada, utiliza ela prioritariamente
                    if box_repetir_x != 0 and box_repetir_y != 0:
                        target_x, target_y = box_repetir_x, box_repetir_y
                    else:
                        # Fallback dinâmico para a barra superior na tela de resultados caso o .env consecutivo não esteja calibrado
                        try:
                            search_box = page.locator("input[name='q'], #sb_form_q").first
                            box_bounding = search_box.bounding_box()
                            if box_bounding:
                                target_x = int(box_bounding["x"] + (box_bounding["width"] / 2))
                                target_y = int(box_bounding["y"] + (box_bounding["height"] / 2))
                            else:
                                target_x, target_y = box_inicial_x, box_inicial_y
                        except Exception:
                            target_x, target_y = box_inicial_x, box_inicial_y

                # Executa o deslocamento físico do hardware simulado e clica
                mover_mouse_humano(target_x, target_y)
                clicar_humano()
                time.sleep(random.uniform(0.5, 1.0))

                # 2. Executa comando de teclado via OS para limpar o campo de busca
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.4, 0.8))

                # 3. Digitação Humana via PyAutoGUI (Teclado Físico do OS)
                hud_obj.actualizar(i, quantidade, termo_final, "Status: Digitando...")
                digitar_humano(termo_final)
                time.sleep(random.uniform(0.3, 0.7))
                pyautogui.press('enter')
                
                # 4. Aguarda carregar os resultados da pesquisa
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=5000)
                except Exception:
                    pass  # Avança se houver lentidão na resposta do servidor da Microsoft
                
                # 5. Tempo de leitura simulado com rolagem de página via hardware externo
                espera_leitura = random.randint(DELAY_LEITURA_MIN, DELAY_LEITURA_MAX)
                for seg in range(espera_leitura, 0, -1):
                    hud_obj.actualizar(i, quantidade, termo_final, f"Status: Lendo página ({seg}s)")
                    if seg == espera_leitura - 2:  # Efetua scroll orgânico na metade do ciclo de leitura
                        pyautogui.scroll(random.randint(-400, -150))
                    time.sleep(1)

                # Retorna ao topo preparando a página para a próxima iteração
                pyautogui.press('home')
                time.sleep(random.uniform(DELAY_ENTRE_BUSCAS_MIN, DELAY_ENTRE_BUSCAS_MAX))

        except Exception as e:
            print(f"❌ Ocorreu um erro na automação híbrida do perfil {nome_perfil}: {e}")
        finally:
            context.close()
            hud_obj.fechar()


def modo_manual_edge_externo():
    print("\n" + "="*50)
    print(f"MODO MANUAL (EDGE) | TERMO: {TERMO_BASE}")
    print(f"📍 Coordenadas Injetadas: Inicial({X_INICIAL_MANUAL},{Y_INICIAL_MANUAL}) | Limpar({X_LIMPAR_MANUAL},{Y_LIMPAR_MANUAL})")
    input("👉 Prepare o Edge no Bing e pressione [ENTER]...")
    
    hud_main = StatusHUD(modo="Manual (Edge)", conta="Perfil Local")
    t = Thread(target=execucao_manual_worker, args=(QUANTIDADE_BUSCAS, TERMO_BASE, X_INICIAL_MANUAL, Y_INICIAL_MANUAL, X_LIMPAR_MANUAL, Y_LIMPAR_MANUAL, hud_main))
    t.start()
    hud_main.root.mainloop()


def modo_automatico_playwright_hibrido():
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
    ua_ativo = obter_user_agent_por_perfil(escolha)
    cpu_cores, ram_gb = obter_hardware_perfil(escolha)

    hud_main = StatusHUD(modo="Híbrido (Core + OS)", conta=nome_perfil)
    
    # Executa o worker híbrido em Thread apartada para manter o HUD fluído
    t = Thread(target=execucao_hibrida_playwright_worker, args=(
        QUANTIDADE_BUSCAS, TERMO_BASE, nome_perfil, user_data_dir, ua_ativo, cpu_cores, ram_gb, hud_main
    ))
    t.start()
    
    hud_main.root.mainloop()


if __name__ == "__main__":
    while True:
        print("\n" + "#"*45)
        print("      SISTEMA REWARDS 2026 - MODO HÍBRIDO")
        print("#"*45)
        print(f" TERMO: {TERMO_BASE} | BUSCAS: {QUANTIDADE_BUSCAS}")
        print("-" * 45)
        print("[1] Modo Manual (Edge Externo - PyAutoGUI)")
        print("[2] Modo Híbrido Automático (Playwright + PyAutoGUI)")
        print("[0] Sair")
        
        opcao = input("\nSelecione uma opção: ").strip()
        if opcao == "1":
            modo_manual_edge_externo()
        elif opcao == "2":
            modo_automatico_playwright_hibrido()
        elif opcao == "0":
            break