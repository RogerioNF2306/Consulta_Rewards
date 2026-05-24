#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para exibir informações sobre user-agents centralizados.
Mostra como usar o módulo config_useragents.py
"""

from config_useragents import (
    obter_identidade_perfil, 
    obter_config_humana,
    obter_ua_aleatorio,
    listar_user_agents,
    info_perfis,
    LISTA_USER_AGENTS,
    HARDWARE_CONFIGS
)

def teste_completo():
    """Executa teste completo do sistema de user-agents"""
    
    print("\n" + "="*80)
    print(" "*20 + "TESTE DO SISTEMA DE USER-AGENTS CENTRALIZADO")
    print("="*80)
    
    # Test 1: Informações detalhadas de cada perfil
    print("\n[1] INFORMAÇÕES DETALHADAS DOS PERFIS")
    print("-" * 80)
    info_perfis()
    
    # Test 2: Obter UA aleatório
    print("[2] TESTANDO OBTER USER-AGENT ALEATÓRIO")
    print("-" * 80)
    for i in range(3):
        ua = obter_ua_aleatorio()
        print(f"  Aleatório {i+1}: {ua[:60]}...")
    
    # Test 3: Listar todos os UAs
    print("\n[3] LISTA COMPLETA DE USER-AGENTS")
    print("-" * 80)
    print(f"Total de User-Agents: {len(LISTA_USER_AGENTS)}\n")
    for idx, ua in enumerate(LISTA_USER_AGENTS, 1):
        print(f"  [{idx:02d}] {ua[:70]}...")
    
    # Test 4: Configurações de hardware
    print("\n[4] CONFIGURAÇÕES DE HARDWARE")
    print("-" * 80)
    for perfil_id, config in HARDWARE_CONFIGS.items():
        print(f"  Perfil {perfil_id}: {config['cores']} CPU Cores | {config['ram']}GB RAM")
    
    # Test 5: Verificar consistência (mesmo UA por perfil)
    print("\n[5] VERIFICAÇÃO DE CONSISTÊNCIA (chamadas múltiplas)")
    print("-" * 80)
    for perfil_id in ["1", "2", "3", "4"]:
        ua1, cores1, ram1 = obter_identidade_perfil(perfil_id)
        ua2, cores2, ram2 = obter_identidade_perfil(perfil_id)
        
        consistente = (ua1 == ua2) and (cores1 == cores2) and (ram1 == ram2)
        status = "✓ CONSISTENTE" if consistente else "✗ INCONSISTENTE"
        
        print(f"  Perfil {perfil_id}: {status}")
        print(f"    Chamada 1: {ua1[:50]}... | {cores1} cores | {ram1}GB")
        print(f"    Chamada 2: {ua2[:50]}... | {cores2} cores | {ram2}GB")
    
    # Test 6: Exemplo de uso em código
    print("\n[6] EXEMPLO DE USO EM CÓDIGO")
    print("-" * 80)
    print("""
    # No seu arquivo Python:
    from config_useragents import obter_identidade_perfil, obter_config_humana
    
    # Para pesquisador-unificado.py:
    ua, cores, ram = obter_identidade_perfil("1")
    
    # Para navegador.py:
    ua, cores, memoria = obter_config_humana("2")
    
    # Para navegação Playwright:
    page.add_init_script(f\"\"\"
        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cores}}});
        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {memoria}}});
    \"\"\")
    """)
    
    print("\n" + "="*80)
    print(" "*25 + "TESTES CONCLUÍDOS COM SUCESSO ✓")
    print("="*80 + "\n")

if __name__ == "__main__":
    teste_completo()
