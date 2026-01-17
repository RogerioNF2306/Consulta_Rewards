import os
import subprocess
import sys
from playwright.sync_api import sync_playwright

def garantir_navegadores():
    # Verifica se o diretório de instalação do Playwright existe, se não, instala o Chromium
    # Usamos o Chromium pois ele permite maior manipulação de flags de stealth
    try:
        print("Verificando ambiente Playwright...")
        # Tenta rodar um comando simples para ver se o browser está lá
    except:
        print("Instalando dependências necessárias...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])

def iniciar_sessao_rewards():
    garantir_navegadores()

    # --- CONFIGURAÇÃO DE PERFIS ---
    # Você pode renomear os perfis abaixo como desejar
    perfis = {
        "1": "rogeriofelixrj@gmail.com",
        "2": "rogeriofelix2306@gmail.com",
        "3": "familiafelix58b@gmail.com",
        "4": "raphaelfelixrj2306@gmail.com"
    }

    print("\n=== GERENCIADOR DE PERFIS MICROSOFT REWARDS ===")
    for id, nome in perfis.items():
        print(f"[{id}] Perfil: {nome}")
    
    escolha = input("\nEscolha o número do perfil que deseja abrir: ").strip()
    nome_perfil = perfis.get(escolha, "Padrao")
    
    # Define a pasta onde os dados (cookies/login) de cada perfil serão salvos
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")

    with sync_playwright() as p:
        print(f"\nIniciando navegador com Perfil: {nome_perfil}...")

        # --- STEALTH AVANÇADO: CONFIGURAÇÕES DE LANÇAMENTO ---
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            # Argumentos para parecer um navegador real instalado
            args=[
                "--disable-blink-features=AutomationControlled", # Principal flag anti-bot
                "--disable-features=IsolateOrigins,site-per-process",
                "--start-maximized",
                "--no-default-browser-check",
                "--disable-infobars",
                "--lang=pt-BR",
                "--use-fake-ui-for-media-stream",
                "--disable-web-security"
            ],
            no_viewport=True, # Força a usar o tamanho real da tela (mais humano)
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.pages[0]

        # --- INJEÇÃO DE STEALTH (SOBRESCREVE PROPRIEDADES DE SOFTWARE) ---
        # Este script roda antes de qualquer site carregar, limpando pegadas de automação
        page.add_init_script("""
            # Removendo a propriedade webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            # Simulando plugins comuns de navegadores reais
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            
            # Simulando idiomas e hardware
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        """)

        print(f"Acessando Microsoft Rewards...")
        
        try:
            # Navega com um pequeno atraso aleatório para simular comportamento humano
            page.goto("https://rewards.bing.com", wait_until="domcontentloaded")
            
            print("\n" + "="*60)
            print(f"PRONTO! Você está usando o perfil: {nome_perfil.upper()}")
            print("Pressione Ctrl+C no terminal quando terminar para fechar.")
            print("="*60 + "\n")

            # Mantém o navegador aberto e funcional
            while True:
                if not context.pages: # Se você fechar a aba manualmente, o script encerra
                    break
                page.wait_for_timeout(2000)
                
        except KeyboardInterrupt:
            print(f"\nFechando perfil {nome_perfil} com segurança...")
        except Exception as e:
            print(f"\nOcorreu um erro inesperado: {e}")
        finally:
            context.close()

if __name__ == "__main__":
    iniciar_sessao_rewards()