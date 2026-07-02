import asyncio
from playwright.async_api import async_playwright
import os
import sys

# Garante que a raiz do projeto seja adicionada ao caminho de busca do Python
raiz_do_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if raiz_do_projeto not in sys.path:
    sys.path.append(raiz_do_projeto)

import config
import utils

# Carrega os seletores no boot do projeto para uso imediato pelo scraper.
utils.inicializar_seletores(verbose=True)

import scraper
from excel_manager import salvar_dados_excel

# Cores
GREEN, YELLOW, RED, RESET, BLUE = utils.GREEN, utils.YELLOW, utils.RED, utils.RESET, utils.BLUE


async def exibir_menu():
    """Exibe o menu principal."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}   MICROSOFT REWARDS - CONSULTA E SALVAMENTO{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print("   1. 📊 Salvar dados atuais (coleta e salva direto na planilha do Excel)")
    print("   2. 💰 Consultar valores (pré-definidos + personalizado direto)")
    print("   0. 🚪 Sair")
    print(f"{BLUE}{'='*60}{RESET}")


async def exibir_menu_resgate():
    """Exibe o submenu de resgate com opções de simulação."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}   SIMULAÇÃO DE RESGATE MICROSOFT REWARDS{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print("   1. 📌 Consultar valores pré-definidos (5, 15, 30)")
    print("   2. ✍️ Consultar valor personalizado")
    print("   0. 🔙 Voltar ao menu principal")
    print(f"{BLUE}{'='*60}{RESET}")


async def main():
    user_data_dir = utils.obter_user_data_dir()
    url_resgate = config.URL_RESGATE_SKU

    print(f"{YELLOW}⏳ Iniciando navegador com perfil persistente...{RESET}")

    async with async_playwright() as p:
        context, page = await utils.abrir_contexto_inteligente(
            p,
            headless=False,
            user_data_dir=user_data_dir,
        )

        await scraper.aplicar_stealth_se_disponivel(page)

        print(f"{YELLOW}⏳ Verificando autenticação...{RESET}")
        resposta = await scraper.navegar_para_url(page, url_resgate)
        if resposta and resposta.status == 404:
            print(f"{YELLOW}⚠️ A URL de resgate retornou 404. Tentando acessar a página genérica de ganhos...{RESET}")
            resposta = await scraper.navegar_para_url(page, config.URL_EARN)

        await scraper.human_delay(page, 1, 2)

        if not await scraper.garantir_login(page, destino_url=config.URL_DASHBOARD):
            await context.close()
            return

        # Retoma a trilha padrao apos login: /earn e depois /redeem SKU.
        await scraper.navegar_para_url(page, config.URL_EARN)
        await scraper.human_delay(page, 1, 2)
        await scraper.navegar_para_url(page, url_resgate)
        await scraper.human_delay(page, 1, 2)

        # Atualiza seletores com os elementos reais das paginas antes de iniciar o menu.
        await scraper.sincronizar_seletores_com_site(page, url_resgate=url_resgate)

        while True:
            await exibir_menu()
            opcao = (await asyncio.to_thread(input, "Escolha uma opção (0-2): ")).strip()

            if opcao == "1":
                print(f"{YELLOW}⏳ Coletando dados do dashboard...{RESET}")
                await scraper.navegar_para_url(page, config.URL_EARN)
                await scraper.human_delay(page, 1, 2)

                dados = await scraper.extrair_dados_dashboard_excel(page)
                pts_pesquisa = utils.limpar_pontos(dados.get("pesquisa", "0"))
                pts_ofertas = utils.limpar_pontos(dados.get("ofertas", "0"))
                pts_mes = utils.limpar_pontos(dados.get("mes", "0"))
                pts_ano = utils.limpar_pontos(dados.get("ano", "0"))
                pts_totais = utils.limpar_pontos(dados.get("totais", "0"))

                print(f"\n📈 Dados coletados:")
                print(f"├─ Pesquisa Bing: {pts_pesquisa} pts")
                print(f"├─ Ofertas: {pts_ofertas} pts")
                print(f"├─ Este Mês: {pts_mes} pts")
                print(f"├─ Este Ano: {pts_ano} pts")
                print(f"└─ Totais: {pts_totais} pts")

                print(f"{YELLOW}⏳ Salvando dados no Excel automaticamente...{RESET}")
                sucesso = salvar_dados_excel(pts_pesquisa, pts_ofertas, pts_mes, pts_ano, pts_totais)
                if sucesso:
                    print(f"{GREEN}✅ Dados salvos com sucesso!{RESET}")
                else:
                    print(f"{RED}❌ Falha ao salvar. Verifique o arquivo .env e se a planilha está fechada.{RESET}")

                resposta = await scraper.navegar_para_url(page, url_resgate)
                if resposta and resposta.status == 404:
                    print(f"{YELLOW}⚠️ URL de resgate retornou 404. Acessando /earn como fallback...{RESET}")
                    await scraper.navegar_para_url(page, config.URL_EARN)
                await scraper.human_delay(page, 1, 2)

            elif opcao == "2":
                print(f"{YELLOW}⏳ Acessando página de resgate...{RESET}")
                if "redeem" not in page.url:
                    resposta = await scraper.navegar_para_url(page, url_resgate)
                    if resposta and resposta.status == 404:
                        print(f"{YELLOW}⚠️ URL de resgate retornou 404. Acessando /earn como fallback...{RESET}")
                        await scraper.navegar_para_url(page, config.URL_EARN)
                    await scraper.human_delay(page, 1, 2)

                valores = [5, 15, 30]
                print("\n💰 VALORES PRÉ-DEFINIDOS:")
                for v in valores:
                    resultado = await scraper.consultar_valor_customizado(page, v)
                    if resultado["pontos"] > 0:
                        msg = f"   R$ {v:>2} → {resultado['pontos']:>6} pontos"
                        if resultado["falta"] > 0:
                            msg += f" {RED}(faltam {resultado['falta']} pts){RESET}"
                        elif resultado["suficiente"]:
                            msg += f" {GREEN}✅ Saldo suficiente!{RESET}"
                        print(msg)
                    else:
                        print(f"   R$ {v:>2} → {RED}❌ falha na consulta{RESET}")
                print()

                # Entra direto no loop de valor personalizado sem perguntas prévias
                while True:
                    valor_str = (await asyncio.to_thread(input, f"Digite o valor em R$ (25 a 500), '{YELLOW}S{RESET}' ou {YELLOW}'0'{RESET} para sair: ")).strip().lower()
                    
                    # Permite digitar 'S' ou '0' para sair direto para o menu principal
                    if valor_str == '0' or valor_str == 's':
                        print("⏭️ Voltando ao menu principal.")
                        break
                        
                    if not valor_str.isdigit():
                        print(f"{RED}❌ Valor inválido. Digite um número inteiro, 'S' ou '0' para sair.{RESET}")
                        continue
                        
                    valor = int(valor_str)
                    if valor < 25 or valor > 500:
                        print(f"{RED}❌ Valor fora do intervalo permitido (25 a 500).{RESET}")
                        continue

                    resultado = await scraper.consultar_valor_customizado(page, valor)
                    if resultado["pontos"] > 0:
                        if resultado["suficiente"]:
                            print(f"{GREEN}✅ Para R$ {valor},00 são necessários {resultado['pontos']} pontos. 🎉 Saldo suficiente! Pode resgatar.{RESET}")
                        else:
                            print(f"{YELLOW}⚠️ Para R$ {valor},00 são necessários {resultado['pontos']} pontos. {RED}❌ Faltam {resultado['falta']} pontos.{RESET}")
                    else:
                        print(f"{RED}❌ Falha ao consultar os pontos para R$ {valor},00.{RESET}")

            elif opcao == "0":
                print(f"\n{GREEN}Encerrando automação com segurança...{RESET}")
                break

            else:
                print(f"{RED}Opção inválida. Tente novamente.{RESET}")

            await asyncio.sleep(0.5)

        await context.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Programa finalizado pelo teclado.{RESET}")