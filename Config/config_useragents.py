# ==============================================================================
# CONFIGURAÇÃO CENTRALIZADA DE USER-AGENTS & IDENTIDADES
# ==============================================================================
# Este módulo gerencia todos os user-agents e configurações de hardware
# Usado pelos arquivos: pesquisador-unificado.py e navegador.py
# ==============================================================================

import random

# Lista completa de User-Agents reais de 2026
LISTA_USER_AGENTS = [
    # Chrome versões reais 2026
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36",
    
    # Edge versões reais 2026
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36 Edg/124.0.2478.109",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36 Edg/123.0.2420.97",
    
    # Firefox versões reais 2026
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    
    # Chrome macOS versões 2026
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36",
    
    # Safari macOS versões 2026
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    
    # Opera versões 2026
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36 OPR/109.0.5097.137",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.111 Safari/537.36 OPR/108.0.5049.118"
]

# Configurações de Hardware por Perfil (simulam máquinas reais diferentes)
HARDWARE_CONFIGS = {
    "1": {"cores": 8, "ram": 16},
    "2": {"cores": 4, "ram": 8},
    "3": {"cores": 12, "ram": 32},
    "4": {"cores": 8, "ram": 16}
}

def obter_identidade_perfil(id_perfil):
    """
    Retorna um User-Agent consistente e configurações de hardware baseadas no perfil.
    Isso garante que cada conta tenha uma 'impressão digital' única e consistente.
    
    Args:
        id_perfil: String com ID da conta (1, 2, 3 ou 4)
    
    Returns:
        tuple: (user_agent, cpu_cores, ram_gb)
    
    Uso:
        ua, cores, ram = obter_identidade_perfil("1")
    """
    # Seleciona UA fixo por ID para manter consistência entre sessões do mesmo perfil
    # (a mesma conta sempre recebe o MESMO user-agent)
    idx = (int(id_perfil) - 1) % len(LISTA_USER_AGENTS)
    ua = LISTA_USER_AGENTS[idx]
    
    # Obtém configuração de hardware para este perfil
    config = HARDWARE_CONFIGS.get(id_perfil, {"cores": 8, "ram": 16})
    cores = config["cores"]
    ram = config["ram"]
    
    return ua, cores, ram

def obter_config_humana(id_perfil):
    """
    Versão alternativa com nomes mais descritivos.
    Retorna um User-Agent e configurações de hardware baseadas no perfil.
    
    Args:
        id_perfil: String com ID da conta (1, 2, 3 ou 4)
    
    Returns:
        tuple: (user_agent, cpu_cores, memoria_gb)
    """
    return obter_identidade_perfil(id_perfil)

def obter_ua_aleatorio():
    """
    Retorna um user-agent aleatório da lista.
    Útil para testes ou quando não há necessidade de consistência por perfil.
    
    Returns:
        str: User-Agent aleatório
    """
    return random.choice(LISTA_USER_AGENTS)

def listar_user_agents():
    """
    Retorna a lista completa de user-agents.
    
    Returns:
        list: Lista com todos os 15 user-agents disponíveis
    """
    return LISTA_USER_AGENTS

def info_perfis():
    """
    Imprime informações detalhadas sobre cada perfil e seu user-agent atribuído.
    """
    print("\n" + "="*70)
    print("  INFORMAÇÕES DE PERFIS E USER-AGENTS")
    print("="*70)
    
    for perfil_id in ["1", "2", "3", "4"]:
        ua, cores, ram = obter_identidade_perfil(perfil_id)
        print(f"\n[Perfil {perfil_id}]")
        print(f"  User-Agent: {ua[:60]}...")
        print(f"  Hardware: {cores} CPU Cores | {ram}GB RAM")
    
    print("\n" + "="*70 + "\n")

# ==============================================================================
# EXEMPLO DE USO:
# ==============================================================================
# from config_useragents import obter_identidade_perfil
# 
# ua, cores, ram = obter_identidade_perfil("1")
# print(f"User-Agent: {ua}")
# print(f"Hardware: {cores} cores, {ram}GB RAM")
