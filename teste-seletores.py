#!/usr/bin/env python3
"""
Script de Teste - Validar extração de saldo
Teste rápido para verificar se os seletores estão funcionando
"""

import asyncio
from playwright.async_api import async_playwright

async def testar_selemetores():
    """Testa os seletores de forma isolada."""
    
    print("\n" + "="*70)
    print("🧪 TESTE DE SELETORES - REWARDS BING")
    print("="*70 + "\n")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "microsoft_session",
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        
        page = context.pages[0]
        
        try:
            print("⏳ Acessando: https://rewards.bing.com/redeem/001409000021\n")
            await page.goto("https://rewards.bing.com/redeem/001409000021", wait_until="networkidle", timeout=30000)
            
            print("✅ Página carregada! Aguardando 3 segundos para animações...\n")
            await asyncio.sleep(3)
            
            # Teste 1: Seletor CSS direto
            print("[1/3] Testando seletor CSS: p.pointsValue span")
            try:
                await page.wait_for_selector("p.pointsValue span", timeout=3000)
                texto = await page.locator("p.pointsValue span").first.inner_text()
                print(f"    ✅ SUCESSO! Encontrado: '{texto}'\n")
            except Exception as e:
                print(f"    ❌ FALHOU: {str(e)[:50]}\n")
            
            # Teste 2: JavaScript
            print("[2/3] Testando extração com JavaScript")
            try:
                resultado = await page.evaluate("""
                    () => {
                        const seletores = [
                            'p.pointsValue span',
                            '[mee-element-ready]',
                            '.pointsValue',
                            'span[aria-label*="."]'
                        ];
                        
                        for (let seletor of seletores) {
                            const elem = document.querySelector(seletor);
                            if (elem && elem.textContent) {
                                const texto = elem.textContent.trim();
                                if (texto && /\\d/.test(texto)) {
                                    return { seletor: seletor, valor: texto };
                                }
                            }
                        }
                        return null;
                    }
                """)
                
                if resultado:
                    print(f"    ✅ SUCESSO!")
                    print(f"    Seletor: {resultado['seletor']}")
                    print(f"    Valor: '{resultado['valor']}'\n")
                else:
                    print(f"    ❌ FALHOU: Nenhum elemento encontrado\n")
                    
            except Exception as e:
                print(f"    ❌ FALHOU: {str(e)[:50]}\n")
            
            # Teste 3: Form de resgate
            print("[3/3] Testando formulário de resgate (#variableAmount)")
            try:
                await page.wait_for_selector("#variableAmount", timeout=5000)
                min_val = await page.get_attribute("#variableAmount", "min")
                max_val = await page.get_attribute("#variableAmount", "max")
                curr_val = await page.get_attribute("#variableAmount", "value")
                
                print(f"    ✅ SUCESSO!")
                print(f"    Min: {min_val}, Max: {max_val}, Atual: {curr_val}\n")
                
            except Exception as e:
                print(f"    ❌ FALHOU: {str(e)[:50]}\n")
            
            # Resumo
            print("="*70)
            print("📋 RESUMO VISUAL DA PÁGINA")
            print("="*70 + "\n")
            
            # Exibir HTML relevante
            print("Pressione ENTER para ver o HTML da página no console do navegador...")
            print("(F12 > Console)") 
            await page.evaluate("() => { console.log('===HTML DO SALDO==='); console.log(document.querySelector('p.pointsValue').outerHTML); console.log('===HTML DO FORM==='); console.log(document.querySelector('#variableAmount').outerHTML); }")
            
            input("\n✋ Deixe o navegador aberto para inspecionar manualmente se necessário.")
            input("Pressione ENTER para fechar...\n")
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL: {e}\n")
            input("Pressione ENTER...")
        
        finally:
            await context.close()

if __name__ == "__main__":
    try:
        asyncio.run(testar_selemetores())
        print("✅ Teste concluído!")
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
