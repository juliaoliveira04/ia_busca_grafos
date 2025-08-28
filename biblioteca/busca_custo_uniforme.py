"""
Implementação do algoritmo de busca com custo uniforme (Dijkstra).
Utiliza ondas de busca para encontrar o caminho de menor custo.
"""

import heapq
import time
from typing import Dict, List, Tuple
from .algoritmo_busca import AlgoritmoBusca

class BuscaCustoUniforme(AlgoritmoBusca):
    """
    Algoritmo de Dijkstra - busca o caminho de menor custo.
    Implementação com fila de prioridade usando heapq.
    """
    
    def buscar(self, no_inicial: str, no_final: str) -> Tuple[List[str], float, float]:
        """
        Executa a busca com custo uniforme entre dois nós.
        
        Args:
            no_inicial: Nó de origem
            no_final: Nó de destino
            
        Returns:
            Tuple contendo:
            - Lista com o caminho encontrado (vazia se não houver caminho)
            - Custo total do caminho (infinito se não houver caminho)
            - Tempo de execução em segundos
        """
        inicio_tempo = time.time()
        
        # Obtém todos os nós disponíveis (principais + vizinhos mencionados)
        from .carregador_grafo import CarregadorGrafo
        todos_nos = set(CarregadorGrafo.obter_nos_disponiveis(self.grafo))
        
        # Verifica se os nós existem no grafo
        if no_inicial not in todos_nos or no_final not in todos_nos:
            self.tempo_execucao = time.time() - inicio_tempo
            return [], float('inf'), self.tempo_execucao
        
        # Inicialização das estruturas de dados
        # Fila de prioridade: (custo, nó)
        fila_prioridade = [(0, no_inicial)]
        
        # Dicionário de custos mínimos para cada nó
        custos = {no_inicial: 0}
        
        # Dicionário para rastrear o caminho (nó -> predecessor)
        anteriores = {no_inicial: None}
        
        # Conjunto de nós já processados
        visitados = set()
        
        # Lista para rastrear ordem de visita (para visualização)
        self.nos_visitados = []
        
        while fila_prioridade:
            # Remove o nó com menor custo da fila
            custo_atual, no_atual = heapq.heappop(fila_prioridade)
            
            # Se já foi processado, pula
            if no_atual in visitados:
                continue
            
            # Marca como visitado
            visitados.add(no_atual)
            self.nos_visitados.append(no_atual)
            
            # Se chegou ao destino, reconstrói o caminho
            if no_atual == no_final:
                caminho = self._reconstruir_caminho(anteriores, no_final)
                self.tempo_execucao = time.time() - inicio_tempo
                return caminho, custo_atual, self.tempo_execucao
            
            # Explora os vizinhos do nó atual
            vizinhos = self._obter_vizinhos(no_atual)
            
            for vizinho, custo_aresta in vizinhos.items():
                # Verifica se o vizinho existe na lista de nós disponíveis
                if vizinho not in todos_nos:
                    continue
                    
                # Calcula o novo custo para chegar ao vizinho
                novo_custo = custo_atual + custo_aresta
                
                # Se encontrou um caminho melhor ou é a primeira vez visitando
                if vizinho not in custos or novo_custo < custos[vizinho]:
                    custos[vizinho] = novo_custo
                    anteriores[vizinho] = no_atual
                    heapq.heappush(fila_prioridade, (novo_custo, vizinho))
        
        # Não foi possível encontrar um caminho
        self.tempo_execucao = time.time() - inicio_tempo
        return [], float('inf'), self.tempo_execucao
    
    def obter_estatisticas(self) -> Dict[str, any]:
        """
        Retorna estatísticas da última busca executada.
        
        Returns:
            Dicionário com estatísticas da busca
        """
        return {
            'nos_visitados': len(self.nos_visitados),
            'ordem_visita': self.nos_visitados.copy(),
            'tempo_execucao': self.tempo_execucao
        }
