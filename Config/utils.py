# utils.py
import re
import os
import asyncio

# Cores da interface compartilhadas
GREEN, YELLOW, RED, RESET, BOLD, BLUE = "\033[92m", "\033[93m", "\033[91m", "\033[0m", "\033[1m", "\033[94m"

def inicializar_e_atualizar_seletores():
    """
    Gera ou atualiza dinamicamente o arquivo 'seletores.js' com base na 
    estrutura cirúrgica do HTML real mapeado do Microsoft Rewards.
    """
    caminho_js = os.path.join(os.getcwd(), "seletores.js")
    
    conteudo_js = """// Seletores extraídos cirurgicamente da estrutura HTML fornecida do Microsoft Rewards
const SELETORES = {
    classes: {
        textoPontosCard: '.text-pageHeader', // Presente nos blocos de R$5, R$15, R$30 e no customizado
        textoMetadata: '.text-metadata'
    },
    elementos: {
        perfilBotao: 'button[aria-label="Exibir perfil"] p',
        inputValorCustomizado: 'input[type="text"]' // Input contido no span wrapper do valor personalizado
    },
    validacoes: {
        placeholderSemPontos: '—'
    }
};

function extrairPontosPorTexto(elementoTexto) {
    if (!elementoTexto || elementoTexto.includes('—')) return 0;
    return parseInt(elementoTexto.replace(/\\D/g, '')) || 0;
}
"""
    try:
        with open(caminho_js, "w", encoding="utf-8") as f:
            f.write(conteudo_js)
    except Exception as e:
        print(f"{RED}⚠️ Falha ao atualizar o arquivo de seletores: {e}{RESET}")

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
    """Realiza a varredura baseada na classe de cabeçalho obtida no HTML real (.text-pageHeader)"""
    saldo = 0
    cards_fixos = {}
    
    try:
        seletor_perfil = 'button[aria-label="Exibir perfil"] p'
        await page.wait_for_selector(seletor_perfil, timeout=3000)
        saldo_texto = await page.locator(seletor_perfil).first.inner_text()
        saldo = limpar_pontos(saldo_texto)
    except:
        saldo = await extrair_pontos_com_js(page)

    try:
        # Pega a classe idêntica aos blocos de R$5, R$15 e R$30 fornecidos
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
    """Interage diretamente com o elemento input[type="text"] mapeado do HTML personalizado"""
    try:
        seletor_input = 'input[type="text"]'
        await page.wait_for_selector(seletor_input, timeout=2000)
        
        await page.locator(seletor_input).click()
        await page.locator(seletor_input).fill("")
        await page.locator(seletor_input).type(str(valor_reais), delay=30)
        
        await asyncio.sleep(1.2) # Aguarda cálculo reativo do site
        
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

    print(f"{BOLD}💰 SALDO ATUAL:{RESET} {GREEN}{saldo:,.0f}{RESET} pts🏅\n")
    
    print(f"{BOLD}🎁 CARDS FIXOS ATUAIS:{RESET}")
    for valor, pts in cards_fixos.items():
        status = f"{GREEN}DISPONÍVEL ✅{RESET}" if saldo >= pts else f"{RED}Faltam {(pts - saldo):,.0f} pts ❌{RESET}"
        print(f"├─ R$ {valor:<2} ({pts:,.0f} pts) ──> {status}")
    
    print(f"\n{BOLD}🔍 RESULTADO DA ÚLTIMA CONSULTA:{RESET}")
    if meta_usuario and pontos_meta > 0:
        print(f"├─ Solicitado: R$ {meta_usuario} ── Custo: {YELLOW}{pontos_meta:,.0f}{RESET} pts")
        if saldo >= pontos_meta:
            print(f"└─ STATUS: {GREEN}SALDO SUFICIENTE PARA O RESGATE! ✅{RESET}")
        else:
            print(f"└─ STATUS: {RED}Insuficiente! Faltam exatos {(pontos_meta - saldo):,.0f} pontos. ❌{RESET}")
    elif meta_usuario:
        print(f"└─ {RED}Valor R$ {meta_usuario} fora do limite permitido pelo site (25 a 500).{RESET}")
    else:
        print(f"└─ {YELLOW}Nenhuma consulta realizada ainda.{RESET}")

    print(f"\n{BLUE}{'='*75}{RESET}")
    print(f"{BOLD}Digite o VALOR EM REAIS, [R] para Recarregar ou [S] para Sair.{RESET}")