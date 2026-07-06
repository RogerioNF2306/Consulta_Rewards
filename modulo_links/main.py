import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modulo_links.order_links import executar_modo
from modulo_links.utils import run_diagnostic


def main():
    asyncio.run(run_diagnostic())
    while True:
        modo = ''
        while modo not in ['a', 'v', 's', '0']:
            print("\n" + "═"*45 + "\n      🎮 GERENCIADOR XBOX (MODULAR)\n" + "═"*45)
            print("[A] ATUALIZAR | [V] VERIFICAR | [S] SELECIONAR | [0] VOLTAR")
            modo = input("Selecione: ").strip().lower()
        if modo == '0':
            print("⏪ Retornando ao menu principal do projeto...")
            break
        asyncio.run(executar_modo(modo))


if __name__ == '__main__':
    main()
