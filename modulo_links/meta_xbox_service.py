import re

from playwright.async_api import async_playwright

from modulo_links.navegador_links import criar_contexto, interacao_selecao


def limpar_preco_xbox(preco_cru):
    if not preco_cru:
        return "0,00"

    texto = str(preco_cru).upper().strip()
    if "GRATUITO" in texto or "INCLUÍDO" in texto or "INCLUIDO" in texto:
        return "0,00"

    texto = texto.replace("R$", " ")
    texto = re.sub(r"\s+", " ", texto)

    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2}|\d+)", texto)
    if match:
        return match.group(1)

    return "0,00"


async def coletar_meta_xbox(nome_jogo_busca, xbox_config, user_data_dir):
    titulo_final = nome_jogo_busca
    preco_cru = "Consultar"

    print(f"\n⏳ Abrindo navegador e pesquisando por '{nome_jogo_busca}'...")

    async with async_playwright() as p:
        context = await criar_contexto(p, user_data_dir)
        try:
            page = context.pages[0] if context.pages else await context.new_page()

            resultado = await interacao_selecao(
                page,
                nome_jogo_busca,
                link_atual=None,
                config=xbox_config,
            )

            if resultado in ["SAIR", "PULAR", "MANTER", None] or not isinstance(resultado, str):
                msg = "Operação cancelada ou nenhum jogo selecionado."
                print(f"\n⚠️ {msg}")
                return {"ok": False, "mensagem": msg}

            link_escolhido = resultado.strip()
            if not link_escolhido:
                msg = "Link selecionado inválido."
                print(f"\n⚠️ {msg}")
                return {"ok": False, "mensagem": msg}

            print("\n⏳ Coletando dados finais da página oficial do produto...")
            try:
                await page.goto(link_escolhido, wait_until="networkidle", timeout=30000)
                titulo_final = await page.inner_text(xbox_config["product_title_h1"])
                titulo_final = titulo_final.strip()
            except Exception:
                titulo_final = nome_jogo_busca

            try:
                preco_elem = await page.query_selector(xbox_config["price_selector"])
                if not preco_elem:
                    preco_elem = await page.query_selector("[class*='Price-module__boldText']")
                preco_cru = await preco_elem.inner_text() if preco_elem else "Consultar"
            except Exception:
                preco_cru = "Consultar"

            return {
                "ok": True,
                "mensagem": "Coleta Xbox concluída.",
                "link": link_escolhido,
                "titulo": titulo_final,
                "preco": limpar_preco_xbox(preco_cru),
            }
        finally:
            await context.close()
