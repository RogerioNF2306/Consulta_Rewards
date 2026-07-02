import json
import re
import os
import config

# Cores importadas do config
GREEN, YELLOW, RED, RESET, BOLD, BLUE = (
    config.GREEN, config.YELLOW, config.RED,
    config.RESET, config.BOLD, config.BLUE
)

SELETORES_ATUAIS = None
SELETORES_JS_SINCRONIZADO = False


def inicializar_e_atualizar_seletores():
    """
    Garante que o arquivo 'seletores.js' exista e carrega os seletores em memória.
    O arquivo só é criado com o fallback estático quando ainda não existe.
    """
    global SELETORES_JS_SINCRONIZADO
    if SELETORES_JS_SINCRONIZADO:
        return

    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_js = os.path.join(diretorio_atual, "seletores.js")

    if os.path.exists(caminho_js):
        carregar_seletores_do_js(caminho_js)
        SELETORES_JS_SINCRONIZADO = True
        return
    
    try:
        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(config.CONTEUDO_SELETORES_JS)
        SELETORES_JS_SINCRONIZADO = True
        carregar_seletores_do_js(caminho_js)
        print(f"{GREEN}✅ Arquivo 'seletores.js' sincronizado com sucesso!{RESET}")
    except Exception as e:
        print(f"{RED}⚠️ Falha ao atualizar o arquivo de seletores: {e}{RESET}")


def salvar_seletores_no_js(seletores, caminho_js=None):
    """Persiste um conjunto plano de seletores em seletores.js e atualiza o cache em memória."""
    global SELETORES_ATUAIS, SELETORES_JS_SINCRONIZADO
    if caminho_js is None:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_js = os.path.join(diretorio_atual, "seletores.js")

    with open(caminho_js, "w", encoding="utf-8") as f:
        json.dump(seletores, f, ensure_ascii=False, indent=4)

    SELETORES_ATUAIS = seletores
    SELETORES_JS_SINCRONIZADO = True


async def descobrir_seletores_da_pagina(page, contexto="auto", salvar=True):
    """Valida e ajusta os seletores com base na página atualmente aberta.

    O retorno segue o formato plano usado pelo scraper.
    """
    seletores = dict(obter_seletores())

    try:
        if contexto in ("auto", "earn"):
            if await page.locator('div.grid:has(div:has-text("Atividade de hoje"))').count() > 0:
                seletores["grid_earn"] = 'div.grid:has(div:has-text("Atividade de hoje"))'
            if await page.locator('div.grid:has(div:has-text("Histórico"))').count() > 0:
                seletores["grid_historico"] = 'div.grid:has(div:has-text("Histórico"))'
            if await page.locator('div.wrap-anywhere').count() > 0:
                seletores["wrap_anywhere"] = 'div.wrap-anywhere'

        if contexto in ("auto", "redeem"):
            if await page.locator('button[aria-label="Exibir perfil"] p').count() > 0:
                seletores["perfil_botao"] = 'button[aria-label="Exibir perfil"] p'
            if await page.locator('button:has-text("Personalizado")').count() > 0:
                seletores["botao_personalizado"] = 'button:has-text("Personalizado")'
            if await page.locator('input[type="text"]').count() > 0:
                seletores["input_valor"] = 'input[type="text"]'
            if await page.locator('p.text-pageHeader.text-fgCtrlNeutralSecondaryRest').count() > 0:
                seletores["campo_pontos_resultado"] = 'p.text-pageHeader.text-fgCtrlNeutralSecondaryRest'
            elif await page.locator('p.text-pageHeader').count() > 0:
                seletores["campo_pontos_resultado"] = 'p.text-pageHeader'

        if salvar:
            salvar_seletores_no_js(seletores)
        else:
            global SELETORES_ATUAIS
            SELETORES_ATUAIS = seletores

        return seletores
    except Exception:
        return seletores


def obter_user_data_dir():
    """
    Retorna o caminho do diretório do perfil persistente do navegador.
    Prioriza o caminho estático definido em config; se não existir, cria uma pasta local.
    """
    if os.path.exists(config.CAMINHO_ESTATICO_SESSAO):
        return config.CAMINHO_ESTATICO_SESSAO
        
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(diretorio_atual, config.NOME_PASTA_SESSAO_LOCAL)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    return base_dir

def inicializar_seletores(verbose=False):
    """Garante que os seletores estejam carregados e retorna o dicionario ativo."""
    global SELETORES_ATUAIS
    inicializar_e_atualizar_seletores()
    seletores = carregar_seletores_do_js()

    fonte = "seletores.js"
    if seletores is None:
        seletores = config.SELETORES
        SELETORES_ATUAIS = seletores
        fonte = "config.SELETORES"

    if verbose:
        total = len(seletores) if isinstance(seletores, dict) else 0
        print(f"{GREEN}✅ Seletores carregados de {fonte} ({total} itens).{RESET}")

    return seletores


async def aplicar_configuracao_de_contexto(page):
    """Aplica apenas configuracoes de compatibilidade e localidade, sem spoofing de navegador."""
    try:
        await page.set_extra_http_headers({
            'accept-language': config.ACCEPT_LANGUAGE
        })
    except Exception:
        pass


async def abrir_contexto_inteligente(playwright, headless=None, user_data_dir=None):
    """Cria um contexto persistente com configuracao conservadora e perfil reutilizavel."""
    if user_data_dir is None:
        user_data_dir = obter_user_data_dir()
    if headless is None:
        headless = config.HEADLESS

    launch_kwargs = {
        'headless': headless,
        'args': ['--start-maximized'],
        'viewport': {'width': 1366, 'height': 768},
        'locale': 'pt-BR',
        'timezone_id': 'America/Sao_Paulo',
    }

    if config.USER_AGENT:
        launch_kwargs['user_agent'] = config.USER_AGENT

    context = await playwright.chromium.launch_persistent_context(user_data_dir, **launch_kwargs)
    context.set_default_navigation_timeout(config.TIMEOUT_MS)
    context.set_default_timeout(config.TIMEOUT_MS)

    page = context.pages[0] if context.pages else await context.new_page()
    await aplicar_configuracao_de_contexto(page)
    return context, page


def carregar_seletores_do_js(caminho_js=None):
    """Carrega o objeto SELETORES de seletores.js para uso pelo scraper."""
    global SELETORES_ATUAIS
    if caminho_js is None:
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_js = os.path.join(diretorio_atual, "seletores.js")

    if not os.path.exists(caminho_js):
        return None

    try:
        with open(caminho_js, "r", encoding="utf-8") as f:
            conteudo = f.read()

        SELETORES_ATUAIS = json.loads(conteudo)
        return SELETORES_ATUAIS
    except Exception as e:
        print(f"{RED}⚠️ Falha ao carregar seletores do JS: {e}{RESET}")
        return None


def obter_seletores():
    """Retorna o dicionário de seletores carregado do JS ou do config como fallback."""
    if SELETORES_ATUAIS is not None:
        return SELETORES_ATUAIS
    carregado = carregar_seletores_do_js()
    if carregado is not None:
        return carregado
    return config.SELETORES


def limpar_pontos(texto):
    """
    Extrai o valor numérico inteiro de uma string que representa pontos.
    Remove separadores de milhar (pontos) e vírgulas decimais (se houver).
    Exemplos:
        "9.478"  -> 9478
        "42.687" -> 42687
        "3/60"   -> 3 (se passado apenas a parte antes da barra)
    """
    if not texto:
        return 0
    numeros = re.sub(r'[^\d]', '', str(texto))
    return int(numeros) if numeros else 0


def extract_correlation_id(error_message: str) -> str | None:
    """
    Extrai o correlationId de mensagens de erro da Microsoft/Azure.
    Útil para depuração de falhas de rota.
    """
    match = re.search(r'correlationId[:\s]+([a-f0-9\-]+)', error_message, re.I)
    return match.group(1) if match else None


def format_points_report(data: dict) -> str:
    """
    Formata um relatório amigável dos pontos coletados.
    Espera um dicionário com as chaves: search, offers, month, year.
    """
    return f"""
{BOLD}📊 RELATÓRIO MICROSOFT REWARDS{RESET}
{BLUE}─{RESET * 30}
🔍 Pesquisas:  {data.get('search', 0):>6,} pts
🎯 Ofertas:    {data.get('offers', 0):>6,} pts
📅 Este Mês:   {data.get('month', 0):>6,} pts
📆 Este Ano:   {data.get('year', 0):>6,} pts
{BLUE}─{RESET * 30}
"""


def renderizar_interface(saldo, cards_fixos, meta_usuario=None, pontos_meta=0):
    """
    Desenha o painel CLI formatado no console.
    (Função legada, mantida para compatibilidade)
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{BLUE}{'='*75}{RESET}")
    print(f"{BOLD}📊 Painel de Consulta de Resgate-Rewards 2026{RESET}")
    print(f"{BLUE}{'='*75}{RESET}\n")
    print(f"{BOLD}💰 SALDO ATUAL:{RESET} {GREEN}{saldo:,.0f}{RESET} pts🏅\n")
    
    if cards_fixos:
        print(f"{BOLD}📌 CARDS DISPONÍVEIS:{RESET}")
        for nome, valor in cards_fixos.items():
            print(f"   {nome}: {valor} pts")
        print()
    
    if meta_usuario:
        print(f"{BOLD}🎯 META: {meta_usuario}{RESET} (faltam {max(0, pontos_meta - saldo):,} pts)")