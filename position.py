import pyautogui
import time
import os

def capturar_posicao_estratigica():
    print("=== CAPTURADOR DE COORDENADAS (MODO GRAVAÇÃO) ===")
    tempo_espera = 2
    
    print(f"\nPrepare o mouse! A captura ocorrerá em {tempo_espera} segundos...")
    
    # Contagem regressiva visual
    for i in range(tempo_espera, 0, -1):
        print(f"Capturando em: {i}...", end="\r")
        time.sleep(1)
    
    # Captura a posição e a cor
    x, y = pyautogui.position()
    cor = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
    
    resultado = f"\n\n[GRAVAÇÃO CONCLUÍDA]"
    resultado += f"\nCoordenadas: X={x}, Y={y}"
    resultado += f"\nCor (RGB): {cor}"
    
    print(resultado)
    print("O código será encerrado agora.")

if __name__ == "__main__":
    capturar_posicao_estratigica()