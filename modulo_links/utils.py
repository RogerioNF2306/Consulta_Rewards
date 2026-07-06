import asyncio
import json
import os
from playwright.async_api import async_playwright

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(os.path.dirname(__file__), 'seletors.json')
SEARCH_URL = "https://www.xbox.com/pt-BR/Search/Results?q="


def resolve_user_data_dir():
    """Resolve caminho da sessão persistente com prioridade e fallback seguro."""
    env_dir = os.getenv("REWARDS_SESSION_DIR", "").strip()

    if env_dir:
        if not os.path.isabs(env_dir):
            env_dir = os.path.abspath(os.path.join(ROOT_DIR, env_dir))
        os.makedirs(env_dir, exist_ok=True)
        return env_dir

    preferred = os.path.join(MODULE_DIR, "perfil_oh")
    os.makedirs(preferred, exist_ok=True)
    return preferred


USER_DATA_DIR = resolve_user_data_dir()


def load_all_selectors():
    default_config = {
        "XboxTool": {
            "search_url_base": "https://www.xbox.com/pt-BR/Search/Results?q=",
            "product_card_link": "div[class*='ProductCard-module__cardWrapper'] a",
            "price_selector": "[class*='Price-module__boldText']",
            "product_title_h1": "h1[data-testid='ProductDetailsHeaderProductTitle']",
            "valid_link_pattern": "xbox\\.com/pt-BR/games/store/"
        }
    }

    if not os.path.exists(FILE_PATH):
        return default_config

    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, value in default_config.items():
                if key not in data:
                    data[key] = value
                else:
                    for sub_key, sub_value in value.items():
                        if sub_key not in data[key]:
                            data[key][sub_key] = sub_value
            return data
    except Exception:
        return default_config


def load_xbox_selectors():
    data = load_all_selectors()
    return data['XboxTool']


def save_all_selectors(data):
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")
        return False


def save_xbox_selectors(xbox_config):
    data = load_all_selectors()
    data['XboxTool'] = xbox_config
    return save_all_selectors(data)


async def diagnostic_xbox(page, config):
    print("\n🔎 Investigando e Atualizando seletores da Xbox Store...")
    try:
        search_url = config['XboxTool'].get('search_url_base', SEARCH_URL)
        await page.goto(f"{search_url}Hollow+Knight", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(4)

        card_element = await page.query_selector("div[class*='ProductCard-module__cardWrapper']")
        if not card_element:
            card_element = await page.query_selector(config['XboxTool']['product_card_link'])

        if card_element:
            raw_card_class = await card_element.evaluate("node => node.className")
            classes = raw_card_class.split()
            target_class = next((c for c in classes if "ProductCard-module__cardWrapper" in c), None)
            if target_class:
                config['XboxTool']['product_card_link'] = f"div.{target_class} a"
                print(f"✅ Seletor do Card atualizado dinamicamente: div.{target_class} a")

            price_el = await card_element.query_selector(config['XboxTool']['price_selector'])
            if price_el:
                config['XboxTool']['price_selector'] = config['XboxTool']['price_selector']
                print(f"✅ Seletor de preço verificado: {config['XboxTool']['price_selector']}")

            link_el = await card_element.query_selector("a")
            if link_el:
                href = await link_el.get_attribute("href")
                if href:
                    url_produto = f"https://www.xbox.com{href}" if href.startswith("/") else href
                    print("🔗 Entrando na página do produto para testar H1...")
                    await page.goto(url_produto, wait_until="domcontentloaded", timeout=60000)

                    h1_el = await page.query_selector("h1")
                    if h1_el:
                        testid = await h1_el.get_attribute("data-testid")
                        if testid:
                            config['XboxTool']['product_title_h1'] = f"h1[data-testid='{testid}']"
                        else:
                            raw_h1_class = await h1_el.evaluate("node => node.className")
                            if raw_h1_class:
                                first_class = raw_h1_class.split()[0]
                                config['XboxTool']['product_title_h1'] = f"h1.{first_class}"
                        print(f"✅ Seletor do Título H1 validado: {config['XboxTool']['product_title_h1']}")

    except Exception as e:
        print(f"⚠️ Alerta no diagnóstico Xbox: {e}")

    return config


async def run_diagnostic():
    print("\n" + "═" * 60 + "\n🤖 AUTÔNATO DE DIAGNÓSTICO DE XBOX TOOL\n" + "═" * 60)
    config = load_all_selectors()

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            USER_DATA_DIR, headless=True, no_viewport=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0]
        config = await diagnostic_xbox(page, config)
        await asyncio.sleep(1)
        await context.close()

    if save_all_selectors(config):
        print("\n✨ [SUCESSO] O arquivo 'selectors.json' foi calibrado e atualizado para XboxTool!")


def sync_xbox_selectors():
    xbox_config = load_xbox_selectors()
    if save_xbox_selectors(xbox_config):
        print("✅ Seletores de XboxTool sincronizados e salvos.")
    else:
        print("⚠️ Não foi possível salvar os seletores de XboxTool.")
    return xbox_config
