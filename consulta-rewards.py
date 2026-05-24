import re
import os
import asyncio
from playwright.async_api import async_playwright

# Configurações de UI
GREEN, YELLOW, RED, RESET, BOLD, BLUE = "\033[92m", "\033[93m", "\033[91m", "\033[0m", "\033[1m", "\033[94m"

def obter_user_data_dir():
    base_dir = os.path.join(os.getcwd(), "microsoft_session")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def limpar_pontos(texto):
    if not texto: return 0
    nums = "".join(re.findall(r'\d+', str(texto)))
    return int(nums) if nums else 0

async def extrair_pontos_com_js(page):
    try:
        return await page.evaluate("""
            () => {
                const btn = document.querySelector('button[aria-label="Exibir perfil"] p');
                return btn ? parseInt(btn.textContent.replace(/\\D/g, '')) : 0;
            }
        """)
    except:
        return 0

async def capturar_dados_pagina(page):
    """Varre o saldo e as opções de cards fixos diretamente pelo HTML."""
    saldo = 0
    cards_fixos = {}
    
    # 1. Captura do Saldo
    try:
        seletor_perfil = 'button[aria-label="Exibir perfil"] p'
        await page.wait_for_selector(seletor_perfil, timeout=3000)
        saldo_texto = await page.locator(seletor_perfil).first.inner_text()
        saldo = limpar_pontos(saldo_texto)
    except:
        saldo = await extrair_pontos_com_js(page)

    # 2. Varredura dos Cards Fixos (.text-pageHeader do HTML)
    try:
        elementos_pts = await page.locator('.text-pageHeader').all()
        valores_reais = [5, 15, 30]
        idx = 0
        for elemento in elementos_pts:
            texto = await elemento.inner_text()
            if texto and "—" not in texto and idx < len(valores_reais):
                pts = limpar_pontos(texto)
                if 500 <= pts <= 10000:
                    cards_fixos[valores_reais[idx]] = pts
                    idx += 1
    except:
        pass

    if not cards_fixos:
        cards_fixos = {5: 1005, 15: 2580, 30: 5165}

    return saldo, cards_fixos

async def consultar_valor_customizado(page, valor_reais):
    """Injeta o valor diretamente no input e captura o retorno real do site."""
    try:
        seletor_input = 'input[type="text"]'
        await page.wait_for_selector(seletor_input, timeout=2000)
        
        # Interage com o campo de texto fornecido no HTML
        await page.locator(seletor_input).click()
        await page.locator(seletor_input).fill("")
        await page.locator(seletor_input).type(str(valor_reais), delay=30)
        
        await asyncio.sleep(1.2) # Aguarda processamento do site
        
        elementos_resultado = await page.locator('p.text-pageHeader').all()
        for item in elementos_resultado:
            texto_pts = await item.inner_text()
            if texto_pts and "—" not in texto_pts:
                pts_validados = limpar_pontos(texto_pts)
                if pts_validados > 100:
                    return pts_validados
    except:
        pass
    return 0

def renderizar_interface(saldo, cards_fixos, meta_usuario=None, pontos_meta=0):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{BLUE}{'='*75}{RESET}")
    print(f"{BOLD}📊 PAINEL DE CONSULTA DIRETA MICROSOFT REWARDS 2026{RESET}")
    print(f"{BLUE}{'='*75}{RESET}\n")

    print(f"{BOLD}💰 SALDO ATUAL:{RESET} {GREEN}{saldo:,.0f}{RESET} pts\n")
    
    print(f"{BOLD}🎁 CARDS FIXOS ATUAIS:{RESET}")
    for valor, pts in cards_fixos.items():
        status = f"{GREEN}DISPONÍVEL ✅{RESET}" if saldo >= pts else f"{RED}Faltam {(pts - saldo):,.0f} pts ❌{RESET}"
        print(f"├─ R$ {valor:<2} ({pts:,.0f} pts) ──> {status}")
    
    print(f"\n{BOLD}🔍 RESULTADO DA ÚLTIMA CONSULTA:{RESET}")
    if meta_usuario and pontos_meta > 0:
        print(f"├─ Solicitado: R$ {meta_usuario} ── Custo Real: {YELLOW}{pontos_meta:,.0f}{RESET} pts")
        if saldo >= pontos_meta:
            print(f"└─ STATUS: {GREEN}SALDO SUFICIENTE PARA O RESGATE! ✅{RESET}")
        else:
            print(f"└─ STATUS: {RED}REPROVADO! Faltam exatos {(pontos_meta - saldo):,.0f} pontos. ❌{RESET}")
    elif meta_usuario:
        print(f"└─ {RED}Valor R$ {meta_usuario} fora do limite permitido pelo site (25 a 500).{RESET}")
    else:
        print(f"└─ {YELLOW}Nenhuma consulta realizada ainda.{RESET}")

    print(f"\n{BLUE}{'='*75}{RESET}")
    print(f"{BOLD}Digite o VALOR EM REAIS, [R] para Recarregar ou [S] para Sair.{RESET}")

async def main():
    user_data_dir = obter_user_data_dir()
    url_resgate_alvo = "https://rewards.bing.com/redeem/sku/001409000021"
    meta_usuario = None
    pontos_meta = 0
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir, headless=False, args=["--start-maximized", "--no-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print(f"{YELLOW}⏳ Conectando à página de resgate...{RESET}")
        await page.goto(url_resgate_alvo, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(1)

        if "login.live.com" in page.url:
            print(f"{RED}🔒 Conta deslogada! Faça o login no navegador para liberar o terminal.{RESET}")
            await page.wait_for_selector('button[aria-label="Exibir perfil"]', timeout=180000)

        while True:
            try:
                # Realiza a varredura automática inicial pronta
                saldo, cards_fixos = await capturar_dados_pagina(page)
                
                if meta_usuario:
                    pontos_meta = await consultar_valor_customizado(page, meta_usuario)
                
                renderizar_interface(saldo, cards_fixos, meta_usuario, pontos_meta)
                
                entrada = input("\n[Valor (R$25 a R$500), (R)ecarregar ou (S)air] > ").strip().lower()
                
                if entrada == 's':
                    print(f"\n{GREEN}Encerrando automação com segurança...{RESET}")
                    break
                elif entrada == 'r':
                    meta_usuario = None
                    pontos_meta = 0
                    print(f"{YELLOW}🔄 Atualizando página...{RESET}")
                    await page.reload(wait_until="networkidle")
                elif entrada:
                    # Se for número, joga direto na consulta do input
                    if entrada.isdigit():
                        meta_usuario = int(entrada)
                    else:
                        print(f"{RED}Entrada inválida. Digite um número inteiro, 'r' ou 's'.{RESET}")
                        await asyncio.sleep(1)
            
            except Exception as e:
                print(f"{RED}Erro no fluxo de execução: {e}{RESET}")
                await asyncio.sleep(2)

        await context.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Programa finalizado pelo teclado.{RESET}")