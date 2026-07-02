import os
from datetime import datetime
import pywintypes
import win32com.client
from dotenv import load_dotenv
import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prioriza o .env na raiz do projeto e mantem compatibilidade com a estrutura antiga.
ENV_PATH = os.path.join(BASE_DIR, ".env")
LEGACY_ENV_PATH = os.path.join(BASE_DIR, "config", ".env")

# Carrega as variáveis do arquivo .env local do projeto
load_dotenv(dotenv_path=ENV_PATH if os.path.exists(ENV_PATH) else LEGACY_ENV_PATH)

XL_UP = -4162


def _obter_workbook_aberto(excel_app, caminho_excel):
    """Retorna o workbook aberto correspondente ao caminho informado, se existir."""
    caminho_normalizado = os.path.normcase(os.path.abspath(caminho_excel))
    for workbook in excel_app.Workbooks:
        try:
            if os.path.normcase(os.path.abspath(workbook.FullName)) == caminho_normalizado:
                return workbook
        except Exception:
            continue
    return None


def _obter_worksheet(workbook, nome_aba):
    """Retorna a worksheet pelo nome, ou None se ela nao existir."""
    try:
        return workbook.Worksheets(nome_aba)
    except Exception:
        return None


def _normalizar_valor_excel(valor):
    """Converte valores vindos do Excel/COM para inteiro comparavel."""
    if valor in (None, ""):
        return 0
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, (int, float)):
        return int(valor)

    texto = str(valor).strip()
    if not texto:
        return 0

    numeros = "".join(ch for ch in texto if ch.isdigit())
    return int(numeros) if numeros else 0

def salvar_dados_excel(pontos_pesquisa: int, pontos_ofertas: int, pontos_mes: int, pontos_ano: int, pontos_totais: int):
    """
    Salva os dados coletados do Microsoft Rewards na planilha do Excel.
    Se já existir registro para o dia atual, compara os valores e só atualiza quando houver mudança.
    
    Mapeamento de colunas gerenciado pela Macro:
    - Coluna 1 (A): Data do Registro
    - Coluna 2 (B): Pontos Pesquisa Bing
    - Coluna 3 (C): Pontos Ofertas
    - Coluna 4 (D): [PULADO] - Soma dos pontos no dia (calculado internamente)
    - Coluna 5 (E): Pontos do Mês
    - Coluna 6 (F): Pontos do Ano
    - Coluna 7 (G): Pontos Totais da Conta
    """
    caminho_excel = os.getenv("EXCEL_PATH")
    nome_aba = os.getenv("EXCEL_SHEET", "Rewards")
    nome_macro = os.getenv("EXCEL_MACRO_NAME", "RegistrarPontosEFormatar")

    if not caminho_excel:
        print(f"{config.RED}❌ ERRO: Variável 'EXCEL_PATH' não localizada no arquivo .env!{config.RESET}")
        return False

    caminho_excel = os.path.abspath(os.path.expandvars(os.path.expanduser(caminho_excel)))

    # Valida se o diretório do arquivo existe, caso contrário cria
    diretorio_pai = os.path.dirname(caminho_excel)
    if diretorio_pai and not os.path.exists(diretorio_pai):
        os.makedirs(diretorio_pai, exist_ok=True)

    # Verifica se a extensão suporta macros
    if not caminho_excel.lower().endswith('.xlsm'):
        print(f"{config.RED}❌ ERRO: O arquivo configurado precisa ser um arquivo habilitado para macros (.xlsm).{config.RESET}")
        return False

    if not os.path.exists(caminho_excel):
        print(f"{config.YELLOW}⚠️ Planilha não localizada em: {caminho_excel}. Crie o arquivo base com suporte a macros primeiro.{config.RESET}")
        return False

    excel_app = None
    workbook = None
    fechar_ao_final = False
    macro_salvou = False

    try:
        # Tenta se atrelar a um Excel que já esteja aberto pelo usuário
        try:
            excel_app = win32com.client.GetActiveObject("Excel.Application")
            print(f"{config.GREEN}🔄 Conectado à instância ativa do Excel (Planilha Aberta).{config.RESET}")
        except Exception:
            # Caso esteja fechado, abre uma instância oculta em segundo plano
            excel_app = win32com.client.Dispatch("Excel.Application")
            excel_app.Visible = False
            fechar_ao_final = True

        # Verifica se o arquivo específico já está aberto na instância para não reabri-lo como somente-leitura
        nome_arquivo = os.path.basename(caminho_excel)
        workbook = _obter_workbook_aberto(excel_app, caminho_excel)
        if workbook is not None:
            print(f"{config.GREEN}📌 Arquivo '{nome_arquivo}' já em foco. Efetuando inserção direta.{config.RESET}")
        else:
            workbook = excel_app.Workbooks.Open(caminho_excel)

        # Envia apenas a data, sem componente de hora, para evitar serial com timestamp no Excel.
        data_hoje_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        data_hoje = pywintypes.Time(data_hoje_dt)

        print(f"{config.YELLOW}⏳ Invocando procedimento interno VBA para atualização segura de dados...{config.RESET}")
        
        # Executa a macro enviando dinamicamente o nome da aba lida do .env e os pontos coletados
        macro_salvou = bool(workbook.Application.Run(
            f"'{workbook.Name}'!{nome_macro}",
            nome_aba,
            data_hoje, 
            int(pontos_pesquisa), 
            int(pontos_ofertas), 
            int(pontos_mes), 
            int(pontos_ano), 
            int(pontos_totais)
        ))

        if not macro_salvou:
            print(f"{config.RED}❌ [EXCEL] A macro '{nome_macro}' sinalizou falha ao salvar os dados.{config.RESET}")
            return False
        
        print(
            f"{config.GREEN}✅ [EXCEL] Macro executada com sucesso via VBA na aba '{nome_aba}'!{config.RESET}"
        )
        return True

    except Exception as e:
        print(f"{config.RED}❌ [EXCEL] Falha crítica na integração Python-VBA/Macro '{nome_macro}': {e}{config.RESET}")
        return False

    finally:
        # Finaliza os objetos COM de forma limpa para não deixar processos fantasmas no Windows
        if workbook and fechar_ao_final:
            workbook.Close(SaveChanges=False)
        if excel_app and fechar_ao_final:
            excel_app.Quit()
        
        # Coleta de lixo explícita para liberar o arquivo
        workbook = None
        excel_app = None

if __name__ == "__main__":
    # Teste de execução estrutural simulando a coleta
    print("🧪 Testando módulo integrado com variáveis de ambiente (.env) e VBA...")
    salvar_dados_excel(90, 15, 2500, 28000, 14200)