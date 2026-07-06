import asyncio
import argparse
import os
import sys

# Força UTF-8 no Windows quando o stream suporta reconfigure.
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

# Garante que a raiz do projeto seja adicionada ao caminho de busca do Python
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from modulo_links.config import load_config
    from modulo_links.meta_config import load_meta_env
    from modulo_links.meta_excel_service import gravar_meta_excel
    from modulo_links.meta_xbox_service import coletar_meta_xbox
    from modulo_links.utils import USER_DATA_DIR
except ImportError:
    raise ImportError(
        "Nao foi possivel importar os modulos de modulo_links. "
        "Confirme se a pasta modulo_links existe e se o script esta na raiz do projeto."
    )

async def async_input(prompt):
    """Roda o input dentro de uma thread para não travar o loop do asyncio (Evita EOFError)"""
    return await asyncio.to_thread(input, prompt)


def _campo_resultado(texto):
    """Evita quebrar o delimitador '|' usado no retorno de integração VBA."""
    return str(texto or "").replace("|", "/")


async def adicionar_nova_meta(nome_jogo_informado=None):
    try:
        xbox_config = load_config()
    except Exception as e:
        msg = f"Erro ao carregar configuração do Xbox: {e}"
        print(f"❌ {msg}")
        return {"ok": False, "mensagem": msg}

    cfg = load_meta_env(ROOT_DIR)

    print("\n" + "═"*55)
    print("🎯   ADICIONAR NOVO JOGO ÀS METAS DO REWARDS")
    print("═"*55)
    
    if nome_jogo_informado is None:
        nome_jogo_busca = await async_input("👉 Digite o nome do jogo para buscar no Xbox: ")
    else:
        nome_jogo_busca = nome_jogo_informado
    nome_jogo_busca = nome_jogo_busca.strip()
    if not nome_jogo_busca:
        msg = "Busca cancelada. Nome inválido."
        print(f"❌ {msg}")
        return {"ok": False, "mensagem": msg}

    coleta = await coletar_meta_xbox(nome_jogo_busca, xbox_config, USER_DATA_DIR)
    if not coleta.get("ok"):
        return coleta

    return gravar_meta_excel(
        root_dir=ROOT_DIR,
        cfg=cfg,
        link_escolhido=coleta["link"],
        titulo_final=coleta["titulo"],
        preco_formatado=coleta["preco"],
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Adicionar nova meta na planilha via Xbox store.")
    parser.add_argument("--jogo", dest="jogo", default=None, help="Nome do jogo para busca direta.")
    parser.add_argument(
        "--from-vba",
        dest="from_vba",
        action="store_true",
        help="Ativa saída padronizada para integração com VBA.",
    )
    return parser.parse_args()

if __name__ == '__main__':
    try:
        args = parse_args()
        resultado = asyncio.run(adicionar_nova_meta(nome_jogo_informado=args.jogo))

        if args.from_vba:
            if resultado and resultado.get("ok"):
                print(
                    "RESULTADO_META|OK|{titulo}|{preco}|{linha_link}|{linha_valor}".format(
                        titulo=_campo_resultado(resultado.get("titulo", "")),
                        preco=_campo_resultado(resultado.get("preco", "")),
                        linha_link=_campo_resultado(resultado.get("linha_link", "")),
                        linha_valor=_campo_resultado(resultado.get("linha_valor", "")),
                    )
                )
            else:
                mensagem = _campo_resultado((resultado or {}).get("mensagem", "Falha não identificada"))
                print(f"RESULTADO_META|ERRO|{mensagem}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo abortado pelo usuário.")