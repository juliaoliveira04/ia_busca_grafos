"""
Arquivo principal do Simulador de Busca em Grafos.
Ponto de entrada da aplicação.
"""

import sys
import os

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Função principal que inicia o simulador.
    """
    try:
        from diversos.interface_visual import InterfaceVisual
        app = InterfaceVisual()
        app.executar()
        
    except Exception as e:
        print(f"Erro ao iniciar: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Executa a função principal e sai com o código de retorno apropriado
    sys.exit(main())
