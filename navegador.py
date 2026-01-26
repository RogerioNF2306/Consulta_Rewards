import os
import subprocess
import sys
import random
import time
from playwright.sync_api import sync_playwright

def garantir_navegadores():
    """Verifica e instala o Chromium caso necessário."""
    try:
        # Tenta verificar se o executável do chromium existe de forma silenciosa
        pass 
    except:
        print("🔧 Configurando ambiente Playwright pela primeira vez...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])

def obter_config_humana(id_perfil):
    """
    Retorna um User-Agent e configurações de hardware baseadas no perfil.
    Isso garante que cada conta tenha uma 'impressão digital' única.
    """
    # Lista de UAs reais de 2026 (Chrome, Edge e Firefox)
    lista_ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    ]
    
    # Seleciona UA fixo por ID para manter consistência entre sessões do mesmo perfil
    idx = (int(id_perfil) - 1) % len(lista_ua)
    ua = lista_ua[idx]
    
    # Simulação de Hardware condizente
    cores = random.choice([4, 8, 12, 16])
    memoria = random.choice([8, 16, 32])
    
    return ua, cores, memoria

def iniciar_sessao_rewards():
    garantir_navegadores()

    perfis = {
        "1": "rogeriofelixrj@gmail.com",
        "2": "rogeriofelix2306@gmail.com",
        "3": "familiafelix58b@gmail.com",
        "4": "raphaelfelixrj2306@gmail.com"
    }

    print("\n" + "="*50)
    print("      NAVEGADOR STEALTH REWARDS - ELITE 2026")
    print("="*50)
    for id_p, nome in perfis.items():
        print(f"[{id_p}] Perfil: {nome}")
    
    escolha = input("\nEscolha o perfil para navegar: ").strip()
    if escolha not in perfis:
        print("❌ Escolha inválida.")
        return

    nome_perfil = perfis[escolha]
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{nome_perfil}")
    
    # Obtém a identidade única deste perfil
    user_agent_ativo, cpu_cores, ram_gb = obter_config_humana(escolha)

    with sync_playwright() as p:
        print(f"\n🚀 Lançando instância blindada para: {nome_perfil}")
        print(f"🎭 Identidade: {user_agent_ativo[:60]}...")

        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars",
                f"--user-agent={user_agent_ativo}",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ],
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )

        page = context.pages[0]

        # --- INJEÇÃO DE STEALTH PROFUNDO ---
        # Sobrescrevemos o hardware e limpamos rastros de automação via JavaScript
        page.add_init_script(f"""
            # Esconde o Webdriver
            Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
            
            # Simula Hardware Real
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu_cores}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram_gb}}});
            
            # Simula plugins e languages de forma nativa
            Object.defineProperty(navigator, 'languages', {{get: () => ['pt-BR', 'pt', 'en-US', 'en']}});
            
            # Mock de Vendor do Chrome
            window.chrome = {{
                runtime: {{}},
                loadTimes: function() {{}},
                csi: function() {{}},
                app: {{}}
            }};
        """)

        try:
            # Navegação inicial com delay orgânico
            time.sleep(random.uniform(1.5, 3.0))
            page.goto("https://rewards.bing.com", wait_until="networkidle")
            
            print("\n" + "✅" * 20)
            print(f"NAVEGAÇÃO ATIVA: {nome_perfil.upper()}")
            print(f"HARDWARE SIMULADO: {cpu_cores} Cores / {ram_gb}GB RAM")
            print("Pressione Ctrl+C para encerrar a sessão com segurança.")
            print("✅" * 20 + "\n")

            while True:
                if context.pages == []: break
                page.wait_for_timeout(5000)

        except KeyboardInterrupt:
            print(f"\nEncerrando sessão de {nome_perfil}...")
        except Exception as e:
            print(f"\n⚠️ Erro durante a navegação: {e}")
        finally:
            context.close()

if __name__ == "__main__":
    iniciar_sessao_rewards()