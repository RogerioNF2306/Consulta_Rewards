import sys
import os

# Garante que a raiz do projeto seja adicionada ao caminho de busca do Python
raiz_do_projeto = os.path.dirname(os.path.abspath(__file__))
if raiz_do_projeto not in sys.path:
    sys.path.append(raiz_do_projeto)

from excel_manager import salvar_dados_excel

# Cores para o terminal organizado
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BLUE = "\033[94m"

def obter_pontos_valido(prompt):
    """Garante que o usuário digite apenas números inteiros"""
    while True:
        try:
            entrada = input(prompt).strip()
            if entrada.lower() == 's':
                print(f"\n{YELLOW}Operação cancelada pelo usuário. Voltando ao menu...{RESET}")
                sys.exit(2)  # Envia o código 2 (Cancelado) para o arquivo .bat
            return int(entrada)
        except ValueError:
            print(f"{RED}❌ Entrada inválida! Digite um número inteiro válido (ou 'S' para sair).{RESET}")

def main():
    print(f"{BLUE}{'='*55}{RESET}")
    print(f"{BLUE}📝   PAINEL DE ENTRADA MANUAL - REWARDS   {RESET}")
    print(f"{BLUE}{'='*55}{RESET}")
    print(f"Aperte 'S' a qualquer momento para sair do programa.\n")
    print(" Abra o site do Rewards manualmente no seu Edge, veja os")
    print(" valores atuais e digite-os nos campos abaixo:\n")

    # Coleta de dados interativa
    pts_pesquisa = obter_pontos_valido(" 🔍 Pontos de Pesquisas: ")
    pts_ofertas  = obter_pontos_valido(" 🎯 Pontos de Ofertas: ")
    pts_mes      = obter_pontos_valido(" 📅 Acumulado deste mês: ")
    pts_ano      = obter_pontos_valido(" 📆 Recebidos neste ano: ")
    pts_totais   = obter_pontos_valido(" 💰 Saldo disponível na Conta: ")

    print(f"\n{YELLOW}⏳ Integrando dados com o seu ecossistema Excel...{RESET}")
    
    try:
        # Reutiliza o gerenciador do Excel que você já validou e usa nos outros scripts
        sucesso = salvar_dados_excel(pts_pesquisa, pts_ofertas, pts_mes, pts_ano, pts_totais)
        if sucesso:
            print(f"{GREEN}✅ Sucesso absoluto! Os dados foram injetados na planilha. Seu painel está atualizado!{RESET}")
            sys.exit(0)  # Sucesso padrão
        else:
            print(f"{RED}❌ Falha ao salvar os dados. Verifique as mensagens acima para mais detalhes.{RESET}")
            sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Erro ao salvar dados no Excel: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Programa encerrado.{RESET}")
        sys.exit(2)