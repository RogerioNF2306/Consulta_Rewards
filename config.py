"""
Módulo de Configuração - Carrega variáveis do .env
Sistema Rewards Automação 2026
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# ============================================================================
# USER-AGENTS
# ============================================================================
def obter_lista_user_agents():
    """Retorna lista de user-agents a partir do .env"""
    user_agents_str = os.getenv('USER_AGENTS', '')
    if not user_agents_str:
        raise ValueError("USER_AGENTS não definido no arquivo .env")
    return user_agents_str.split('|')

def obter_user_agent_por_perfil(id_perfil):
    """Retorna user-agent específico para um perfil"""
    lista_ua = obter_lista_user_agents()
    idx = (int(id_perfil) - 1) % len(lista_ua)
    return lista_ua[idx]

# ============================================================================
# CONFIGURAÇÕES DE HARDWARE
# ============================================================================
def obter_hardware_perfil(id_perfil):
    """Retorna cores e memória para um perfil específico"""
    chave = f'HARDWARE_PERFIL_{id_perfil}'
    valor = os.getenv(chave, '8,16')  # Default: 8 cores, 16GB
    cores, memoria = map(int, valor.split(','))
    return cores, memoria

# ============================================================================
# CONFIGURAÇÕES GERAIS
# ============================================================================
TERMO_BASE = os.getenv('TERMO_BASE', 'flask')
QUANTIDADE_BUSCAS = int(os.getenv('QUANTIDADE_BUSCAS', '30'))
LOCALE = os.getenv('LOCALE', 'pt-BR')
TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')
FAILSAFE = os.getenv('FAILSAFE', 'True').lower() == 'true'

# ============================================================================
# CONFIGURAÇÕES DE DELAYS
# ============================================================================
DELAY_ENTRE_BUSCAS_MIN = float(os.getenv('DELAY_ENTRE_BUSCAS_MIN', '1.2'))
DELAY_ENTRE_BUSCAS_MAX = float(os.getenv('DELAY_ENTRE_BUSCAS_MAX', '2.2'))
DELAY_LEITURA_MIN = int(os.getenv('DELAY_LEITURA_MIN', '18'))
DELAY_LEITURA_MAX = int(os.getenv('DELAY_LEITURA_MAX', '25'))
DELAY_PAUSA_MIN = int(os.getenv('DELAY_PAUSA_MIN', '15'))
DELAY_PAUSA_MAX = int(os.getenv('DELAY_PAUSA_MAX', '25'))
DELAY_CLICK_MIN = float(os.getenv('DELAY_CLICK_MIN', '0.07'))
DELAY_CLICK_MAX = float(os.getenv('DELAY_CLICK_MAX', '0.17'))

# ============================================================================
# CONFIGURAÇÕES DE MOUSE
# ============================================================================
MOUSE_OFFSET_X = int(os.getenv('MOUSE_OFFSET_X', '5'))
MOUSE_OFFSET_Y = int(os.getenv('MOUSE_OFFSET_Y', '5'))

def obter_mouse_offsets():
    """Retorna offsets X e Y para movimento de mouse"""
    return MOUSE_OFFSET_X, MOUSE_OFFSET_Y

def obter_mouse_durations():
    """Retorna durações de movimento do mouse (min, max)"""
    duracao_str = os.getenv('MOUSE_DURATION_MOVE', '0.6,1.1')
    min_dur, max_dur = map(float, duracao_str.split(','))
    return min_dur, max_dur

def obter_mouse_adjust_durations():
    """Retorna durações de ajuste do mouse (min, max)"""
    duracao_str = os.getenv('MOUSE_DURATION_ADJUST', '0.1,0.3')
    min_dur, max_dur = map(float, duracao_str.split(','))
    return min_dur, max_dur

# ============================================================================
# URLs
# ============================================================================
URL_REWARDS = os.getenv('URL_REWARDS', 'https://rewards.bing.com')
URL_BING = os.getenv('URL_BING', 'https://www.bing.com')

# ============================================================================
# MODO DEBUG
# ============================================================================
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
HEADLESS = os.getenv('HEADLESS', 'False').lower() == 'true'

# ============================================================================
# FUNÇÃO PARA DEBUG
# ============================================================================
def exibir_configuracoes():
    """Exibe todas as configurações carregadas (para debug)"""
    if DEBUG:
        print("\n" + "="*60)
        print("CONFIGURAÇÕES CARREGADAS DO .env")
        print("="*60)
        print(f"TERMO_BASE: {TERMO_BASE}")
        print(f"QUANTIDADE_BUSCAS: {QUANTIDADE_BUSCAS}")
        print(f"LOCALE: {LOCALE}")
        print(f"TIMEZONE: {TIMEZONE}")
        print(f"USER_AGENTS_TOTAL: {len(obter_lista_user_agents())}")
        print(f"URL_REWARDS: {URL_REWARDS}")
        print(f"URL_BING: {URL_BING}")
        print(f"DEBUG: {DEBUG}")
        print(f"HEADLESS: {HEADLESS}")
        print("="*60 + "\n")

if __name__ == "__main__":
    # Test: Exibir configurações
    exibir_configuracoes()
    
    # Test: Obter user-agents
    print(f"Total de User-Agents: {len(obter_lista_user_agents())}\n")
    
    # Test: Obter hardware por perfil
    for perfil_id in ['1', '2', '3', '4']:
        cores, mem = obter_hardware_perfil(perfil_id)
        ua = obter_user_agent_por_perfil(perfil_id)
        print(f"Perfil {perfil_id}: {cores} cores, {mem}GB RAM")
        print(f"  UA: {ua[:70]}...")
