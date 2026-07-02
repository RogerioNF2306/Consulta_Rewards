import asyncio
import random
import re
from playwright.async_api import async_playwright

try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None

import config
import utils
from excel_manager import salvar_dados_excel

# Cache simples para evitar reaplicar stealth na mesma page a cada navegação.
_stealth_status_por_pagina = {}

# ============================================================
# 🔥 INICIALIZAÇÃO OBRIGATÓRIA DOS SELETORES
# Garante que o arquivo 'seletores.js' seja carregado antes de qualquer operação.
# ============================================================
utils.inicializar_seletores()


async def human_delay(page, min_sec=1.5, max_sec=3.5):
    """Delay natural entre ações."""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def aplicar_stealth_se_disponivel(page):
    """Aplica stealth na page uma única vez, se a biblioteca estiver disponível."""
    page_id = id(page)
    if page_id in _stealth_status_por_pagina:
        return _stealth_status_por_pagina[page_id]

    if stealth_async is None:
        _stealth_status_por_pagina[page_id] = False
        return False

    try:
        await stealth_async(page)
        _stealth_status_por_pagina[page_id] = True
        print(f"{config.GREEN}🕵️ Stealth aplicado na sessão atual.{config.RESET}")
        return True
    except Exception as e:
        _stealth_status_por_pagina[page_id] = False
        print(f"{config.YELLOW}⚠️ Falha ao aplicar stealth: {e}{config.RESET}")
        return False


async def navegar_para_url(page, url, timeout=60000):
    """Navega para uma URL e registra o status de resposta."""
    try:
        await aplicar_stealth_se_disponivel(page)
        resposta = await page.goto(url, wait_until="networkidle", timeout=timeout)
        if resposta and resposta.status >= 400:
            print(f"{config.YELLOW}⚠️ A página retornou status {resposta.status} para {url}{config.RESET}")
        return resposta
    except Exception as e:
        print(f"{config.RED}❌ Falha ao carregar {url}: {e}{config.RESET}")
        return None


async def garantir_login(page, destino_url=None):
    """Verifica se a página de login foi exibida e aguarda a conclusão do acesso."""
    if destino_url is None:
        destino_url = config.URL_DASHBOARD

    hosts_login = ("login.live.com", "login.microsoftonline.com", "signin.live.com")
    if any(host in page.url for host in hosts_login):
        print(f"\n🔒 {config.YELLOW}[SESSÃO EXPIRADA]{config.RESET} Autenticação manual necessária.")
        try:
            # Garante o ponto de login solicitado quando a sessão expirar.
            if "login.live.com" not in page.url:
                await navegar_para_url(page, config.URL_LOGIN, timeout=config.TIMEOUT_LOGIN_MS)

            await page.wait_for_url("**/rewards.bing.com/**", timeout=config.TIMEOUT_LOGIN_MS)
            await page.wait_for_load_state("networkidle", timeout=30000)
            print(f"{config.GREEN}✅ Login detectado!{config.RESET}")

            if destino_url:
                await navegar_para_url(page, destino_url)
                await page.wait_for_load_state("networkidle", timeout=30000)

            return True
        except asyncio.TimeoutError:
            print(f"{config.RED}❌ Tempo de login esgotado. Abortando.{config.RESET}")
            return False
    return True


async def sincronizar_seletores_com_site(page, url_resgate=None):
    """Acessa o site em aba dedicada e atualiza seletores no arquivo seletores.js."""
    if url_resgate is None:
        url_resgate = config.URL_RESGATE_ALVO

    print(f"{config.YELLOW}⏳ Sincronizando seletores com o site (/earn e /redeem)...{config.RESET}")
    print(f"{config.YELLOW}🗂️ Abrindo aba de sincronizacao de seletores...{config.RESET}")

    pagina_sync = None
    try:
        # Usa uma nova aba para tornar a sincronizacao visivel sem afetar a aba principal.
        pagina_sync = await page.context.new_page()
        await pagina_sync.bring_to_front()
        await human_delay(pagina_sync, 0.7, 1.2)

        # 1) Coleta sinais da pagina de earn.
        resposta_earn = await navegar_para_url(pagina_sync, config.URL_EARN)
        if resposta_earn is None:
            print(f"{config.YELLOW}⚠️ Nao foi possivel abrir /earn para sincronizar seletores.{config.RESET}")
        else:
            await human_delay(pagina_sync, 1, 2)
            await utils.descobrir_seletores_da_pagina(pagina_sync, contexto="earn", salvar=True)

        # 2) Coleta sinais da pagina de redeem.
        resposta_redeem = await navegar_para_url(pagina_sync, url_resgate)
        if resposta_redeem and resposta_redeem.status == 404:
            resposta_redeem = await navegar_para_url(pagina_sync, config.URL_RESGATE_ALVO)

        if resposta_redeem is None:
            print(f"{config.YELLOW}⚠️ Nao foi possivel abrir /redeem para sincronizar seletores.{config.RESET}")
        else:
            await human_delay(pagina_sync, 1, 2)
            await utils.descobrir_seletores_da_pagina(pagina_sync, contexto="redeem", salvar=True)

        seletores = utils.inicializar_seletores(verbose=False)
        total = len(seletores) if isinstance(seletores, dict) else 0
        print(f"{config.YELLOW}↩️ Fechando aba de sincronizacao e voltando para a aba principal...{config.RESET}")
        await pagina_sync.close()
        await page.bring_to_front()
        print(f"{config.GREEN}✅ Seletores sincronizados com o site e salvos em seletores.js ({total} itens).{config.RESET}")
        return True
    except Exception as e:
        print(f"{config.YELLOW}⚠️ Nao foi possivel sincronizar seletores com o site: {e}{config.RESET}")
        return False
    finally:
        if pagina_sync is not None and not pagina_sync.is_closed():
            await pagina_sync.close()
        try:
            await page.bring_to_front()
        except Exception:
            pass


async def expandir_detalhamento(page):
    """Abre o flyout de detalhamento de pontos."""
    try:
        seletor_detalhe = 'p.text-metadata:has-text("Detalhamento de pontos")'
        if await page.locator(seletor_detalhe).count() > 0:
            await page.locator(seletor_detalhe).first.click()
            await human_delay(page, 1, 2)
            return True

        seletor_card = 'div.flex.grow.flex-col.p-paddingCardBodyDefaultOutside:has(p:has-text("Pontos de hoje"))'
        if await page.locator(seletor_card).count() > 0:
            await page.locator(seletor_card).first.click()
            await human_delay(page, 1, 2)
            return True

        seletor_icone = 'img[alt="Pontos de hoje"]'
        if await page.locator(seletor_icone).count() > 0:
            await page.locator(seletor_icone).locator('xpath=ancestor::div[contains(@class, "flex")][1]').click()
            await human_delay(page, 1, 2)
            return True

        print("⚠️ Não foi possível encontrar o card de detalhamento.")
        return False
    except Exception as e:
        print(f"⚠️ Erro ao expandir detalhamento: {e}")
        return False


async def extrair_dados_dashboard_excel(page):
    """Extrai métricas da página /earn (pesquisa, ofertas, mês, ano e total de pontos da conta)."""
    await utils.descobrir_seletores_da_pagina(page, contexto="earn", salvar=True)
    resultado = {"pesquisa": "0", "ofertas": "0", "mes": "0", "ano": "0", "totais": "0"}

    # Verifica se os labels já estão visíveis
    tem_conteudo = await page.evaluate('''
        () => {
            const labels = ['Pesquisa do Bing', 'Ofertas', 'Este mês', 'Este ano'];
            return labels.some(label => {
                const el = Array.from(document.querySelectorAll('div.wrap-anywhere'))
                    .find(div => div.textContent.trim() === label);
                return el !== undefined;
            });
        }
    ''')

    if not tem_conteudo:
        print("⏳ Abrindo detalhamento de pontos...")
        await expandir_detalhamento(page)
        try:
            await page.wait_for_function(
                '''() => {
                    const labels = ['Pesquisa do Bing', 'Ofertas', 'Este mês', 'Este ano'];
                    return labels.some(label => {
                        const el = Array.from(document.querySelectorAll('div.wrap-anywhere'))
                            .find(div => div.textContent.trim() === label);
                        return el !== undefined;
                    });
                }''',
                timeout=9000
            )
        except:
            print("⚠️ Nenhum label apareceu após abrir o flyout.")
            return resultado

    dados = await page.evaluate('''
        () => {
            function getValue(labelText) {
                const divs = document.querySelectorAll('div.wrap-anywhere');
                for (let i = 0; i < divs.length; i++) {
                    if (divs[i].textContent.trim() === labelText) {
                        let next = divs[i].nextElementSibling;
                        while (next && !next.classList.contains('wrap-anywhere')) {
                            next = next.nextElementSibling;
                        }
                        if (next) {
                            return next.textContent.trim();
                        }
                    }
                }
                return null;
            }

            let pontosTotais = null;
            const medalDiv = Array.from(document.querySelectorAll('div.flex.items-center.gap-2'))
                .find(div => div.querySelector('img[alt*="Membro"]') || div.querySelector('img[src*="Medals"]'));
            
            if (medalDiv && medalDiv.querySelector('p')) {
                pontosTotais = medalDiv.querySelector('p').textContent.trim();
            }

            return {
                pesquisa: getValue('Pesquisa do Bing'),
                ofertas: getValue('Ofertas'),
                mes: getValue('Este mês'),
                ano: getValue('Este ano'),
                totais: pontosTotais
            };
        }
    ''')

    if dados.get('pesquisa'):
        resultado['pesquisa'] = dados['pesquisa'].split('/')[0].strip()
    if dados.get('ofertas'):
        resultado['ofertas'] = dados['ofertas']
    if dados.get('mes'):
        resultado['mes'] = dados['mes']
    if dados.get('ano'):
        resultado['ano'] = dados['ano']
    if dados.get('totais'):
        resultado['totais'] = dados['totais']

    print(f"🔍 Dados extraídos: pesquisa={resultado['pesquisa']}, ofertas={resultado['ofertas']}, mês={resultado['mes']}, ano={resultado['ano']}, totais={resultado['totais']}")
    return resultado


async def extrair_pontos_resgate(page):
    """Extrai pontos da página de resgate."""
    try:
        pontos_el = await page.evaluate('''
            () => {
                const els = document.querySelectorAll('p.text-pageHeader');
                for (let el of els) {
                    const text = el.textContent.trim();
                    if (text && text !== '—' && /\\d/.test(text)) {
                        let next = el.nextElementSibling;
                        let found = false;
                        while (next && !found) {
                            if (next.textContent.trim().toLowerCase().includes('pontos')) {
                                found = true;
                            }
                            next = next.nextElementSibling;
                        }
                        if (found) {
                            return text;
                        }
                    }
                }
                for (let el of els) {
                    const text = el.textContent.trim();
                    if (text && text !== '—' && /\\d/.test(text)) {
                        return text;
                    }
                }
                return null;
            }
        ''')
        if pontos_el:
            return utils.limpar_pontos(pontos_el)
    except Exception as e:
        print(f"⚠️ Erro ao extrair pontos do resgate: {e}")
    return 0


async def extrair_saldo_perfil(page):
    """Retorna o saldo atual de pontos (ex: 10.000) a partir do ícone de perfil."""
    try:
        seletor = utils.obter_seletores().get("perfil_botao", 'button[aria-label="Exibir perfil"] p')
        saldo_text = await page.locator(seletor).first.inner_text()
        return utils.limpar_pontos(saldo_text)
    except:
        return 0


async def extrair_falta_resgate(page):
    """
    Extrai o texto 'Falta X' da página de resgate, indicando quantos pontos faltam.
    Retorna o número de pontos faltantes, ou 0 se não houver (significa que é suficiente).
    """
    try:
        span = page.locator('span.text-metadata.text-fgCtrlNeutralSecondaryRest:has-text("Falta")')
        if await span.count() > 0:
            texto = await span.first.inner_text()
            match = re.search(r'Falta\s*([\d\.,]+)', texto)
            if match:
                return utils.limpar_pontos(match.group(1))
        return 0
    except Exception as e:
        print(f"⚠️ Erro ao extrair 'Falta': {e}")
        return 0


async def consultar_valor_customizado(page, valor_reais=25):
    """
    Consulta pontos para valor pré-definido (5,15,30) ou personalizado.
    Retorna um dicionário com: pontos, falta e suficiente.
    """
    try:
        seletores = await utils.descobrir_seletores_da_pagina(page, contexto="redeem", salvar=True)
        saldo_atual = await extrair_saldo_perfil(page)
        
        radiogroup = page.locator('[role="radiogroup"]')
        if await radiogroup.count() > 0:
            print(f"🎯 Modo com botões de opção detectado. Valor: {valor_reais}")

            if valor_reais in [5, 15, 30]:
                texto_botao = f"Cartão-presente de R$ {valor_reais}"
                botao = page.locator(f'button:has-text("{texto_botao}")')
                if await botao.count() == 0:
                    botao = page.locator(f'button:has-text("R$ {valor_reais}")')
                if await botao.count() > 0:
                    await botao.first.click()
                    print(f"✅ Clicou em '{texto_botao}'.")
                else:
                    print(f"⚠️ Botão para R$ {valor_reais} não encontrado.")
                    return {"pontos": 0, "falta": 0, "suficiente": False}

                await page.wait_for_function(
                    r'''() => {
                        const els = document.querySelectorAll('p.text-pageHeader');
                        for (let el of els) {
                            const text = el.textContent.trim();
                            if (text && text !== '—' && /\d/.test(text)) {
                                let next = el.nextElementSibling;
                                let found = false;
                                while (next && !found) {
                                    if (next.textContent.trim().toLowerCase().includes('pontos')) {
                                        found = true;
                                    }
                                    next = next.nextElementSibling;
                                }
                                if (found) {
                                    return true;
                                }
                            }
                        }
                        return false;
                    }''',
                    timeout=10000
                )
                await asyncio.sleep(0.5)
                pontos = await extrair_pontos_resgate(page)
                falta = await extrair_falta_resgate(page)
                suficiente = (falta == 0) and (saldo_atual >= pontos)
                return {"pontos": pontos, "falta": falta, "suficiente": suficiente}

            else:
                botao_personalizado = page.locator(seletores.get('botao_personalizado', 'button:has-text("Personalizado")'))
                if await botao_personalizado.count() > 0:
                    await botao_personalizado.first.click()
                    print("✅ Clicou em 'Personalizado'.")
                else:
                    primeiro_botao = page.locator('[role="radiogroup"] button').first
                    if await primeiro_botao.count() > 0:
                        await primeiro_botao.click()
                        print("✅ Clicou no primeiro botão de opção.")
                    else:
                        print("⚠️ Nenhumamp botão encontrado.")
                        return {"pontos": 0, "falta": 0, "suficiente": False}
                await asyncio.sleep(1)

                input_sel = seletores.get('input_valor', 'input[type="text"]')
                if await page.locator(input_sel).count() == 0:
                    input_sel = 'input[aria-label*="personalizado" i]'
                    if await page.locator(input_sel).count() == 0:
                        print("⚠️ Nenhum campo de entrada encontrado.")
                        return {"pontos": 0, "falta": 0, "suficiente": False}

                input_elem = page.locator(input_sel).first
                await input_elem.click()
                await input_elem.fill("")
                await asyncio.sleep(0.3)
                await input_elem.type(str(valor_reais), delay=random.randint(40, 80))
                await asyncio.sleep(0.8)

                await page.wait_for_function(
                    '''() => {
                        const el = document.querySelector('p.text-pageHeader');
                        return el && el.textContent.trim() !== '—' && el.textContent.trim() !== '';
                    }''',
                    timeout=15000
                )
                await asyncio.sleep(0.5)
                pontos = await extrair_pontos_resgate(page)
                falta = await extrair_falta_resgate(page)
                suficiente = (falta == 0) and (saldo_atual >= pontos)
                return {"pontos": pontos, "falta": falta, "suficiente": suficiente}

        else:
            print("🎯 Modo com campo de entrada detectado.")
            input_sel = seletores.get('input_valor', 'input[type="text"]')
            if await page.locator(input_sel).count() == 0:
                input_sel = 'input[aria-label*="personalizado" i]'
                if await page.locator(input_sel).count() == 0:
                    print("⚠️ Nenhum campo de entrada encontrado.")
                    return {"pontos": 0, "falta": 0, "suficiente": False}

            input_elem = page.locator(input_sel).first
            await input_elem.click()
            await input_elem.fill("")
            await asyncio.sleep(0.3)
            await input_elem.type(str(valor_reais), delay=random.randint(40, 80))
            await asyncio.sleep(0.8)

            await page.wait_for_function(
                '''() => {
                    const el = document.querySelector('p.text-pageHeader');
                    return el && el.textContent.trim() !== '—' && el.textContent.trim() !== '';
                }''',
                timeout=15000
            )
            await asyncio.sleep(0.5)
            pontos = await extrair_pontos_resgate(page)
            falta = await extrair_falta_resgate(page)
            suficiente = (falta == 0)
            return {"pontos": pontos, "falta": falta, "suficiente": suficiente}

    except Exception as e:
        print(f"⚠️ Erro no resgate customizado: {e}")
        return {"pontos": 0, "falta": 0, "suficiente": False}


async def coletar_dados_earn(page):
    """Abre /earn, garante autenticação e extrai dados do dashboard."""
    resposta = await navegar_para_url(page, config.URL_EARN)
    if resposta is None:
        return None

    await human_delay(page, 1.5, 2.5)
    if not await garantir_login(page, destino_url=config.URL_DASHBOARD):
        return None

    # Após relogin, retoma explicitamente o fluxo normal no /earn.
    resposta = await navegar_para_url(page, config.URL_EARN)
    if resposta is None:
        return None
    await human_delay(page, 1, 2)

    dados_brutos = await extrair_dados_dashboard_excel(page)
    if dados_brutos["pesquisa"] == "0" and dados_brutos["ofertas"] == "0":
        print(f"{config.YELLOW}⚠️ Dados ainda zerados. Tentando forçar expansão manual...{config.RESET}")
        await expandir_detalhamento(page)
        await human_delay(page, 1, 2)
        dados_brutos = await extrair_dados_dashboard_excel(page)

    return dados_brutos


async def capturar_dados_pagina(page=None):
    """Coleta saldo e cards. Se receber page, reusa o contexto; caso contrário, abre um navegador.

    Retorna: (saldo, cards_fixos)
    """
    if page is not None:
        dados_brutos = await coletar_dados_earn(page)
        if not dados_brutos:
            return 0, config.CARDS_FIXOS_PADRAO.copy()

        pts_totais = utils.limpar_pontos(dados_brutos.get("totais", "0"))
        return pts_totais, config.CARDS_FIXOS_PADRAO.copy()

    utils.inicializar_e_atualizar_seletores()
    user_data_dir = utils.obter_user_data_dir()

    async with async_playwright() as p:
        context, page = await utils.abrir_contexto_inteligente(
            p,
            headless=config.HEADLESS,
            user_data_dir=user_data_dir,
        )

        dados_brutos = await coletar_dados_earn(page)
        await context.close()

        if not dados_brutos:
            return 0, config.CARDS_FIXOS_PADRAO.copy()

        pts_totais = utils.limpar_pontos(dados_brutos.get("totais", "0"))
        return pts_totais, config.CARDS_FIXOS_PADRAO.copy()


async def verificar_site_e_atualizar():
    """Fluxo principal autônomo: coleta dados do /earn e testa resgate com R$ 25."""
    utils.inicializar_e_atualizar_seletores()
    user_data_dir = utils.obter_user_data_dir()

    print(f"{config.YELLOW}⏳ Iniciando Chromium com perfil persistente...{config.RESET}")

    async with async_playwright() as p:
        context, page = await utils.abrir_contexto_inteligente(
            p,
            headless=config.HEADLESS,
            user_data_dir=user_data_dir,
        )

        try:
            print(f"{config.YELLOW}⏳ Navegando para /earn...{config.RESET}")
            resposta_earn = await navegar_para_url(page, config.URL_EARN)
            if resposta_earn is None:
                print(f"{config.RED}❌ Não foi possível carregar /earn. Encerrando fluxo.{config.RESET}")
                await context.close()
                return
            await human_delay(page, 2, 3)

            if not await garantir_login(page, destino_url=config.URL_DASHBOARD):
                await context.close()
                return
            resposta_earn = await navegar_para_url(page, config.URL_EARN)
            if resposta_earn is None:
                print(f"{config.RED}❌ Não foi possível retomar /earn após login.{config.RESET}")
                await context.close()
                return
            await human_delay(page, 2, 3)

            dados_brutos = await extrair_dados_dashboard_excel(page)

            if dados_brutos["pesquisa"] == "0" and dados_brutos["ofertas"] == "0":
                print(f"{config.YELLOW}⚠️ Dados ainda zerados. Tentando forçar expansão manual...{config.RESET}")
                await expandir_detalhamento(page)
                await human_delay(page, 1, 2)
                dados_brutos = await extrair_dados_dashboard_excel(page)

            pts_pesquisa = utils.limpar_pontos(dados_brutos["pesquisa"])
            pts_ofertas = utils.limpar_pontos(dados_brutos["ofertas"])
            pts_mes = utils.limpar_pontos(dados_brutos["mes"])
            pts_ano = utils.limpar_pontos(dados_brutos["ano"])
            pts_totais = utils.limpar_pontos(dados_brutos["totais"])

            if pts_pesquisa == 0 and pts_ofertas == 0 and pts_mes == 0:
                print(f"{config.YELLOW}⚠️ Métricas zeradas – verifique seletores.{config.RESET}")
            else:
                print(f"\n📈 {config.BOLD}MÉTRICAS DO DIA:{config.RESET}")
                print(f"├─ Pesquisa Bing: {pts_pesquisa} pts")
                print(f"├─ Ofertas: {pts_ofertas} pts")
                print(f"├─ Este Mês: {pts_mes} pts")
                print(f"├─ Este Ano: {pts_ano} pts")
                print(f"└─ Pontos na Conta: {pts_totais} pts\n")
                
                salvar_dados_excel(pts_pesquisa, pts_ofertas, pts_mes, pts_ano, pts_totais)

            print(f"{config.YELLOW}⏳ Testando resgate customizado (R$ 25)...{config.RESET}")
            await navegar_para_url(page, config.URL_RESGATE_ALVO)
            await human_delay(page, 2, 3)

            resultado = await consultar_valor_customizado(page, 25)
            if resultado["pontos"] > 0:
                msg = f"{config.GREEN}✅ Para R$ 25,00 são necessários {resultado['pontos']} pontos."
                if resultado["falta"] > 0:
                    msg += f" Faltam {resultado['falta']} pontos."
                elif resultado["suficiente"]:
                    msg += " 🎉 Saldo suficiente! Pode resgatar."
                print(msg)
            else:
                print(f"{config.RED}❌ Falha ao obter pontos para R$ 25,00.{config.RESET}")

        except Exception as e:
            print(f"{config.RED}❌ Erro crítico: {e}{config.RESET}")

        if not config.HEADLESS:
            print("\n⏳ Pressione Enter para fechar o navegador...")
            await asyncio.to_thread(input)

        await context.close()


def capturar_dados_pagina_sync():
    asyncio.run(verificar_site_e_atualizar())


if __name__ == "__main__":
    utils.inicializar_e_atualizar_seletores()
    asyncio.run(verificar_site_e_atualizar())