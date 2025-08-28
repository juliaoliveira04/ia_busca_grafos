"""
Classe base abstrata para algoritmos de busca em grafos.
Define a interface padrão que todos os algoritmos devem implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import time

class AlgoritmoBusca(ABC):
    """
    Classe abstrata que define a interface para algoritmos de busca.
    Todos os algoritmos de busca devem herdar desta classe.
    """
    
    def __init__(self, grafo: Dict):
        """
        Inicializa o algoritmo com um grafo.
        
        Args:
            grafo: representa o grafo com nós e arestas
        """
        self.grafo = grafo
        self.tempo_execucao = 0.0
        self.nos_visitados = []
        
    @abstractmethod
    def buscar(self, no_inicial: str, no_final: str) -> Tuple[List[str], float, float]:
        """
        Método abstrato para realizar a busca entre dois nós.
        
        Args:
            no_inicial: Nó de origem
            no_final: Nó de destino
            
        Returns:
            Tuple contendo:
            - Lista com o caminho encontrado
            - Custo total do caminho
            - Tempo de execução
        """
        pass
    
    def _obter_vizinhos(self, no: str) -> Dict[str, float]:
        """
        Obtém os vizinhos de um nó e seus custos.
        
        Args:
            no: Nome do nó
            
        Returns:
            Dicionário com vizinhos e custos das arestas
        """
        vizinhos = {}
        
        # Busca vizinhos diretos (quando o nó tem suas próprias arestas definidas)
        if no in self.grafo:
            # Suporte para formato JSON
            if 'arestas' in self.grafo[no]:
                vizinhos.update(self.grafo[no]['arestas'])
            else:
                # Suporte para formato YAML (lista de dicionários)
                for item in self.grafo[no]:
                    if isinstance(item, dict):
                        for vizinho, custo in item.items():
                            if vizinho != 'n_arestas':
                                vizinhos[vizinho] = custo
        
        # Para grafos bidirecionais, busca conexões inversas
        # (quando o nó atual é mencionado como vizinho de outros nós)
        for outro_no, dados in self.grafo.items():
            if outro_no != no:  # Não verifica o próprio nó
                arestas_outro = {}
                
                # Obtém arestas do outro nó
                if 'arestas' in dados:
                    arestas_outro = dados['arestas']
                else:
                    # Formato YAML
                    for item in dados:
                        if isinstance(item, dict):
                            for vizinho, custo in item.items():
                                if vizinho != 'n_arestas':
                                    arestas_outro[vizinho] = custo
                
                # Se o nó atual é vizinho do outro nó, adiciona conexão bidirecional
                if no in arestas_outro:
                    custo = arestas_outro[no]
                    # Só adiciona se não existe ou se é o mesmo custo (consistência)
                    if outro_no not in vizinhos:
                        vizinhos[outro_no] = custo
                    elif vizinhos[outro_no] != custo:
                        # Aviso sobre inconsistência (usa o menor custo)
                        vizinhos[outro_no] = min(vizinhos[outro_no], custo)
        
        return vizinhos
    
    def _reconstruir_caminho(self, anteriores: Dict[str, str], no_final: str) -> List[str]:
        """
        Reconstrói o caminho a partir do dicionário de nós anteriores.
        
        Args:
            anteriores: Dicionário mapeando cada nó ao seu antecessor
            no_final: Nó de destino
            
        Returns:
            Lista com o caminho do nó inicial ao final
        """
        caminho = []
        no_atual = no_final
        
        while no_atual is not None:
            caminho.append(no_atual)
            no_atual = anteriores.get(no_atual)
        
        return caminho[::-1]  # Inverte para obter ordem correta
