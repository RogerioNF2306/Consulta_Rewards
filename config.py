import json
import os

# ============================================================
# 🎨 Configurações Visuais da Interface (ANSI Escape Codes)
# ============================================================
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[94m"

# ============================================================
# 🌐 URLs e Endpoints do Microsoft Rewards
# ============================================================
REWARDS_BASE_URL = "https://rewards.bing.com"
URL_EARN = f"{REWARDS_BASE_URL}/earn"                     # Página com a tabela de ganhos (Atividade de hoje)
URL_DASHBOARD = URL_EARN                                   # Alias para compatibilidade com código legado
URL_RESGATE_ALVO = f"{REWARDS_BASE_URL}/redeem"  # Página genérica de resgate para evitar 404 em SKUs específicos
URL_RESGATE_SKU = os.getenv("REWARDS_SKU_URL", f"{REWARDS_BASE_URL}/redeem/sku/001409000021")

# ============================================================
# 🕒 Configurações de Timeout e Navegador
# ============================================================
TIMEOUT_MS = 30000          # 30 segundos para operações do Playwright
TIMEOUT_LOGIN_MS = 180000   # 3 minutos para login manual
HEADLESS = False            # Modo headless (False para ver o navegador)
USER_AGENT = os.getenv("REWARDS_USER_AGENT", "").strip() or None
ACCEPT_LANGUAGE = os.getenv("REWARDS_ACCEPT_LANGUAGE", "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")

# ============================================================
# 📂 Caminhos de Perfil Persistente
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ESTATICO_SESSAO = os.path.expandvars(os.path.expanduser(os.getenv("REWARDS_SESSION_DIR", ""))).strip()
NOME_PASTA_SESSAO_LOCAL = os.getenv("REWARDS_SESSION_FOLDER", "microsoft_session")

# ============================================================
# 🎁 Valores Padrão de Fallback dos Cards Fixos (R$: Pontos)
# ============================================================
CARDS_FIXOS_PADRAO = {5: 1005, 15: 2580, 30: 5165}

# ============================================================
# 🎯 Seletores CSS Centralizados (usados no scraper)
# ============================================================
SELETORES = {
    # Grid principal que contém a tabela de atividades
    "grid_earn": 'div.grid:has(div:has-text("Atividade de hoje"))',
    "grid_historico": 'div.grid:has(div:has-text("Histórico"))',
    
    # Elementos dentro do grid
    "wrap_anywhere": 'div.wrap-anywhere',
    "label_pesquisa": "Pesquisa do Bing",
    "label_ofertas": "Ofertas",
    "label_mes": "Este mês",
    "label_ano": "Este ano",
    
    # Perfil e saldo
    "perfil_botao": 'button[aria-label="Exibir perfil"] p',
    
    # Resgate customizado
    "botao_personalizado": 'button:has-text("Personalizado")',
    "input_valor": 'input[type="text"]',
    "campo_pontos_resultado": 'p.text-pageHeader.text-fgCtrlNeutralSecondaryRest',
    
    # Estado do campo de pontos (quando ainda não calculado)
    "placeholder_sem_pontos": "—",
}

# ============================================================
# 📜 Arquivo de Seletores Persistente (JSON puro)
# ============================================================
SELETORES_BASE = SELETORES.copy()

CONTEUDO_SELETORES_JS = json.dumps(SELETORES_BASE, ensure_ascii=False, indent=4)