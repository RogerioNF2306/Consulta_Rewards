# consulta-rewards.py
import asyncio
from playwright.async_api import async_playwright

# Importação direta e limpa da estrutura funcional do utils
from utils import (
    inicializar_e_atualizar_seletores,
    obter_user_data_dir,
    capturar_dados_pagina,
    consultar_valor_customizado,
    renderizar_interface,
    GREEN, YELLOW, RED, BLUE, RESET
)

async def main():
    # Executa a criação/atualização em tempo real do arquivo 'seletores.js'
    inicializar_e_atualizar_seletores()
    
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
                # Realiza a captação utilizando os dados estruturados
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