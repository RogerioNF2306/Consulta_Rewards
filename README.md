# Consulta Rewards

Automacao em Python para consultar pontos do Microsoft Rewards com Playwright, reaproveitando uma sessao persistente de navegador e salvando os dados em planilha Excel (.xlsm) via macro VBA.

## Versao atual

- Projeto em estado final de uso para operacao local no Windows.
- Fluxo principal com menu em terminal (coleta + consulta de resgate).
- Fluxo alternativo autonomo em `scraper.py`.
- Stealth habilitado no scraping com fallback seguro (se a biblioteca nao estiver instalada, o projeto continua executando).

## O que o projeto faz

- abre Chromium com perfil persistente em `microsoft_session/`;
- tenta reaproveitar login existente e aguarda login manual quando necessario;
- extrai metricas da pagina `/earn`:
     - Pesquisa do Bing
     - Ofertas
     - Este mes
     - Este ano
     - Pontos totais da conta
- consulta valores de resgate (fixos e personalizados) na pagina `/redeem`;
- informa pontos necessarios, pontos faltantes e se o saldo atual cobre o resgate;
- salva dados no Excel chamando macro VBA por automacao COM;
- sincroniza e persiste seletores em `seletores.js`.

## Estrutura do projeto

```text
config.py              Configuracoes globais (URLs, timeouts, sessao, seletores-base)
consulta-rewards.py    Entrada principal com menu no terminal
scraper.py             Fluxos de navegacao, extracao, resgate e sincronizacao
utils.py               Helpers de contexto Playwright, seletores e parsing
excel_manager.py       Integracao com Excel (win32com) e execucao da macro
seletores.js           Cache de seletores dinamicos
Consulta Rewards.bat   Atalho para execucao no Windows
microsoft_session/     Perfil persistente do Chromium
VBA do Projeto.bas     Modulo VBA de referencia da planilha
```

## Requisitos

- Windows
- Python 3.10+
- Microsoft Excel instalado
- Planilha `.xlsm` existente com macro `RegistrarPontosEFormatar`
- Conta Microsoft com acesso ao Rewards

## Instalacao

Instale as dependencias:

```bash
pip install playwright pywin32 python-dotenv playwright-stealth
```

Instale o navegador do Playwright:

```bash
playwright install chromium
```

Observacao sobre stealth:

- `playwright-stealth` e recomendado para mais estabilidade contra deteccao de automacao.
- Se nao estiver instalado, o projeto continua rodando (com menor robustez anti-bot).

## Configuracao (.env)

Crie um arquivo `.env` na raiz com:

```env
EXCEL_PATH=C:\caminho\para\sua_planilha.xlsm
EXCEL_SHEET=Rewards
EXCEL_MACRO_NAME=RegistrarPontosEFormatar
```

Variaveis opcionais:

```env
REWARDS_SESSION_DIR=C:\caminho\privado\microsoft_session
REWARDS_SESSION_FOLDER=microsoft_session
REWARDS_SKU_URL=https://rewards.bing.com/redeem/sku/001409000021
REWARDS_USER_AGENT=
REWARDS_ACCEPT_LANGUAGE=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7
```

Notas:

- `EXCEL_PATH` deve apontar para arquivo `.xlsm` ja existente.
- Se `REWARDS_SESSION_DIR` nao for informado, sera usada a pasta local `microsoft_session`.
- Se `REWARDS_USER_AGENT` ficar vazio, o Playwright usa o user agent natural.

## Contrato com a macro VBA

Assinatura esperada:

```vb
RegistrarPontosEFormatar(nomeAba, dataAtual, pesquisa, ofertas, mes, ano, totais)
```

Comportamento atual da integracao:

- data enviada sem horario (data do dia);
- chamada da macro qualificada pelo nome do workbook aberto;
- retorno booleano da macro determina sucesso/falha no Python.

## Como executar

Opcao 1 (principal, com menu):

```bash
python consulta-rewards.py
```

Opcao 2 (fluxo autonomo):

```bash
python scraper.py
```

Opcao 3 (atalho Windows):

```bat
Consulta Rewards.bat
```

## Fluxo resumido

```text
Inicia navegador persistente
-> aplica configuracoes de contexto e stealth (se disponivel)
-> valida login (manual quando necessario)
-> sincroniza seletores
-> coleta metricas em /earn
-> consulta resgate em /redeem
-> salva no Excel via macro
```

## Limitacoes

- Projeto focado em Windows por causa de `pywin32` + COM do Excel.
- Pode quebrar se o DOM do Rewards mudar significativamente.
- Usa textos/seletores com foco em interface em portugues.
- `microsoft_session/` contem dados de sessao e deve ser tratado como sensivel.

## Solucao de problemas

Sessao expirada:

- faca login manual na janela aberta pelo Playwright;
- aguarde redirecionamento para `rewards.bing.com`.

Falha no Excel:

- confira `EXCEL_PATH`, `EXCEL_SHEET` e `EXCEL_MACRO_NAME`;
- confirme que a macro existe e o arquivo e `.xlsm`;
- confirme Excel instalado e acessivel via COM.

Falha de coleta/resgate:

- execute novamente apos login;
- atualize/sincronize seletores;
- valide se a interface do Rewards mudou.