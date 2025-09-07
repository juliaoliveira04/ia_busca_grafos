from typing import Dict, List, Tuple, Any
import heapq
import time

from .search_base import AlgoritmoBusca


class BuscaCustoUniforme(AlgoritmoBusca):
    def resolver(self, grafo: Dict[str, Dict[str, float]], inicio: str, objetivo: str, **kwargs):
        caminho, custo, segundos, _ = self.resolver_com_trilha(grafo, inicio, objetivo)
        return caminho, custo, segundos

    def resolver_com_trilha(self, grafo: Dict[str, Dict[str, float]], inicio: str, objetivo: str):
        t0 = time.perf_counter()
        fronteira: List[Tuple[float, str, List[str]]] = []
        heapq.heappush(fronteira, (0.0, inicio, [inicio]))

        melhor_custo = {inicio: 0.0}
        visitados = set()

        expandidos: List[str] = []
        arestas_exploradas: List[Tuple[str, str]] = []

        while fronteira:
            g, no, caminho = heapq.heappop(fronteira)
            if no in visitados:
                continue
            visitados.add(no)
            expandidos.append(no)

            if no == objetivo:
                trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": caminho}
                return caminho, float(g), float(time.perf_counter() - t0), trilha

            for viz, passo in grafo.get(no, {}).items():
                g_novo = g + float(passo)
                if viz not in melhor_custo or g_novo < melhor_custo[viz]:
                    melhor_custo[viz] = g_novo
                    heapq.heappush(fronteira, (g_novo, viz, caminho + [viz]))
                    arestas_exploradas.append((no, viz))

        trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": []}
        return [], float('inf'), float(time.perf_counter() - t0), trilha
