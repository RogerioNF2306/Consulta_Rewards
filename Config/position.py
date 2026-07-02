import os
import sys
import time
import pyautogui
from playwright.sync_api import sync_playwright

# Importa as configurações do ecossistema para alinhar o Modo 2 (Playwright)
try:
    from config.config import (
        LOCALE, TIMEZONE, URL_BING,
        obter_user_agent_por_perfil, obter_hardware_perfil
    )
except ImportError:
    LOCALE, TIMEZONE, URL_BING = "pt-BR", "America/Sao_Paulo", "https://www.bing.com"
    def obter_user_agent_por_perfil(id): return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    def obter_hardware_perfil(id): return 8, 16

def salvar_no_env(chave_x, valor_x, chave_y, valor_y):
    """Grava ou atualiza as chaves de coordenadas de forma limpa no arquivo .env"""
    env_path = os.path.join(os.getcwd(), '.env')
    linhas_atualizadas = []
    chaves_modificadas = {chave_x: str(valor_x), chave_y: str(valor_y)}
    encontradas = {chave_x: False, chave_y: False}

    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        for linha in linhas:
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith('#'):
                linhas_atualizadas.append(linha)
                continue
            
            partes = linha_limpa.split('=', 1)
            chave = partes[0].strip()
            
            if chave in chaves_modificadas:
                linhas_atualizadas.append(f"{chave}={chaves_modificadas[chave]}\n")
                encontradas[chave] = True
            else:
                linhas_atualizadas.append(linha)
    
    for chave, modificado in encontradas.items():
        if not modificado:
            linhas_atualizadas.append(f"{chave}={chaves_modificadas[chave]}\n")

    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(linhas_atualizadas)
    
    print(f"💾 Dados salvos com sucesso no .env -> {chave_x}={valor_x} | {chave_y}={valor_y}")

def realizar_contagem_e_captura(modo_selecionado, tempo_espera=3):
    """Executa a contagem regressiva visual e delega o salvamento de chaves específicas"""
    print(f"\n🚀 Prepare o mouse sobre o elemento desejado! Captura em {tempo_espera} segundos...")
    for i in range(tempo_espera, 0, -1):
        print(f"Capturando em: {i}...  ", end="\r")
        time.sleep(1)
    
    x, y = pyautogui.position()
    
    try:
        cor = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
    except Exception:
        cor = "Não foi possível mapear a cor RGB"

    print("\n\n" + "="*50)
    print("🎯 [GRAVAÇÃO DE COORDENADAS CONCLUÍDA]")
    print("="*50)
    print(f"📌 Coordenadas Obtidas: X={x}, Y={y} | RGB={cor}")
    print("="*50)

    if modo_selecionado == "1_INI":
        salvar_no_env("X_INICIAL_MANUAL", x, "Y_INICIAL_MANUAL", y)
    elif modo_selecionado == "1_LIMP":
        salvar_no_env("X_LIMPAR_MANUAL", x, "Y_LIMPAR_MANUAL", y)
    elif modo_selecionado == "2_AUTO_INI":
        salvar_no_env("X_CAIXA_AUTOMATICO", x, "Y_CAIXA_AUTOMATICO", y)
    elif modo_selecionado == "2_AUTO_REP":
        salvar_no_env("X_REPETIR_AUTOMATICO", x, "Y_REPETIR_AUTOMATICO", y)

def capturar_modo_manual():
    while True:
        print("\n--- SUBMENU: CALIBRAÇÃO MANUAL (EDGE EXTERNO) ---")
        print("[1] Mapear Ponto INICIAL (Clique Inicial da Barra do Bing)")
        print("[2] Mapear Ponto de LIMPEZA (Botão de Limpar/X da Barra)")
        print("[0] Voltar ao Menu Principal")
        
        sub_opcao = input("Selecione o ponto de calibração: ").strip()
        if sub_opcao == "1":
            print("\n👉 Posicione o mouse em cima do campo de texto do Bing no Edge.")
            input("Pressione [ENTER] para iniciar a contagem...")
            realizar_contagem_e_captura("1_INI", tempo_espera=4)
        elif sub_opcao == "2":
            print("\n👉 Posicione o mouse em cima do botão de 'Limpar Texto' (X) do Bing no Edge.")
            input("Pressione [ENTER] para iniciar a contagem...")
            realizar_contagem_e_captura("1_LIMP", tempo_espera=4)
        elif sub_opcao == "0":
            break

def capturar_modo_playwright():
    """Modo 2: Injeta ambiente para pegar posições da janela do modo automático"""
    perfis = {
        "1": "rogeriofelixrj@gmail.com",
        "2": "rogeriofelix2306@gmail.com",
        "3": "familiafelix58b@gmail.com",
        "4": "raphaelfelixrj2306@gmail.com"
    }

    print("\n=== SELEÇÃO DE AMBIENTE PLAYWRIGHT ===")
    for id_p, nome in perfis.items():
        print(f"[{id_p}] Perfil: {nome}")
    
    escolha = input("\nSelecione um perfil para injetar o navegador de testes: ").strip()
    if escolha not in perfis: return

    nome_perfil = perfis[escolha]
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")
    ua_ativo = obter_user_agent_por_perfil(escolha)
    cpu_cores, ram_gb = obter_hardware_perfil(escolha)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir, headless=False, no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled", "--start-maximized", f"--user-agent={ua_ativo}"],
            locale=LOCALE, timezone_id=TIMEZONE
        )
        page = context.pages[0]
        page.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu_cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram_gb}}});
        """)

        try:
            page.goto(URL_BING, wait_until="networkidle")
            
            while True:
                print("\n--- SUBMENU: CALIBRAÇÃO AUTOMÁTICA (PLAYWRIGHT) ---")
                print("[1] Mapear Ponto INICIAL (Página inicial limpa do Bing)")
                print("[2] Mapear Ponto CONSECUTIVO (Página de resultados/topo após buscar)")
                print("[0] Voltar ao Menu Principal")
                
                sub_op = input("Selecione o ponto de calibração automática: ").strip()
                if sub_op == "1":
                    print("\n👉 Coloque o mouse sobre a caixa de pesquisa CENTRAL do Bing.")
                    input("Pressione [ENTER] no terminal para iniciar a contagem...")
                    realizar_contagem_e_captura("2_AUTO_INI", tempo_espera=4)
                elif sub_op == "2":
                    print("\n👉 Faça uma busca manual na janela ativa para ir à tela de resultados.")
                    print("👉 Em seguida, posicione o mouse na barra de pesquisa que ficou no TOPO.")
                    input("Pressione [ENTER] no terminal para iniciar a contagem...")
                    realizar_contagem_e_captura("2_AUTO_REP", tempo_espera=4)
                elif sub_op == "0":
                    break
                    
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            context.close()

if __name__ == "__main__":
    while True:
        print("\n" + "#"*50)
        print("    GERENCIADOR DE POSIÇÕES E COORDENADAS REWARDS")
        print("#"*50)
        print("[1] Mapear Posições para Modo Manual (Edge Externo)")
        print("[2] Mapear Posições para Modo Automático (Playwright)")
        print("[0] Sair do Capturador")
        print("-" * 50)
        
        opcao = input("Selecione qual cenário deseja calibrar: ").strip()
        if opcao == "1":
            capturar_modo_manual()
        elif opcao == "2":
            capturar_modo_playwright()
        elif opcao == "0":
            break