from playwright.async_api import async_playwright

async def criar_contexto(playwright, user_data_dir):
    return await playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        no_viewport=True,
        args=["--disable-blink-features=AutomationControlled"]
    )


async def _get_text(element):
    if not element:
        return None
    try:
        text = await element.inner_text()
        return text.strip() if text else None
    except Exception:
        return None


async def buscar_no_xbox(page, termo_busca, config):
    url_busca = f"{config['search_url_base']}{termo_busca}"
    await page.goto(url_busca, wait_until="networkidle", timeout=60000)

    for _ in range(3):
        await page.mouse.wheel(0, 1000)
        await page.wait_for_timeout(600)

    await page.wait_for_selector(config['product_card_link'], timeout=10000)
    cards = await page.query_selector_all(config['product_card_link'])
    opcoes = []
    for card in cards:
        titulo = await card.get_attribute('title') or await card.get_attribute('aria-label') or await _get_text(card)
        titulo = titulo.strip() if titulo else None
        href = await card.get_attribute('href')
        if not href:
            link_el = await card.query_selector('a')
            href = await link_el.get_attribute('href') if link_el else None
        href = href.strip() if href else None
        preco_elem = await card.query_selector(config['price_selector'])
        preco = await preco_elem.inner_text() if preco_elem else 'Consultar'

        if titulo and href:
            if href.startswith('/'):
                link_full = f"https://www.xbox.com{href}"
            else:
                link_full = href

            if not any(o['link'] == link_full for o in opcoes):
                opcoes.append({"titulo": titulo, "link": link_full, "preco": preco})
    return opcoes


async def interacao_selecao(page, nome_original, link_atual=None, config=None):
    termo_atual = nome_original
    while True:
        opcoes = await buscar_no_xbox(page, termo_atual, config)
        print("\n" + "═"*75)
        print(f"🎮 JOGO: {nome_original}")
        if link_atual:
            print(f"🔗 LINK NA PLANILHA: {link_atual}")
        print("═"*75)

        if not opcoes:
            print("❌ Nenhum resultado encontrado no Xbox.")
        else:
            for i, opt in enumerate(opcoes):
                mark = " ⭐ (IGUAL AO ATUAL)" if opt['link'] == link_atual else ""
                print(f"[{i+1}] {opt['titulo']}{mark}")
                print(f"    💰 {opt['preco']} | 🔗 {opt['link']}")

        print("\n" + "─"*75)
        print("[R] Refinar busca | [P] Pular | [M] Manter atual | [0] Sair")
        print("─"*75)
        escolha = input("👉 Ação: ").strip().lower()
        if escolha == '0':
            return 'SAIR'
        if escolha == 'p':
            return None
        if escolha == 'm':
            return link_atual
        if escolha == 'r':
            termo_atual = input("🔎 Novo termo: ").strip()
            continue
        if escolha.isdigit() and 1 <= int(escolha) <= len(opcoes):
            return opcoes[int(escolha)-1]['link']
        print("⚠️ Opção inválida. Tente novamente.")
