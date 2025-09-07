from typing import Dict, List, Tuple
import heapq
import time

from .search_base import AlgoritmoBusca


def _h(heuristica: Dict[str, Dict[str, float]], objetivo: str, no: str) -> float:
    if not heuristica:
        return 0.0
    return float(heuristica.get(objetivo, {}).get(no, 0.0))


class BuscaAEstrela(AlgoritmoBusca):
    def __init__(self, peso: float = 1.0):
        self.peso = float(peso)

    def resolver(self, grafo, inicio, objetivo, **kwargs):
        heuristica = kwargs.get("heuristica", {})
        peso = float(kwargs.get("peso", self.peso))
        caminho, custo, segundos, _ = self.resolver_com_trilha(grafo, inicio, objetivo, heuristica, peso)
        return caminho, custo, segundos

    def resolver_com_trilha(self, grafo, inicio, objetivo, heuristica, peso=1.0):
        t0 = time.perf_counter()
        fronteira: List[Tuple[float, float, str, List[str]]] = []
        g_melhor = {inicio: 0.0}
        f0 = 0.0 + peso * _h(heuristica, objetivo, inicio)
        heapq.heappush(fronteira, (f0, 0.0, inicio, [inicio]))

        visitados = set()
        expandidos: List[str] = []
        arestas_exploradas: List[Tuple[str, str]] = []

        while fronteira:
            f_atual, g_atual, no, caminho = heapq.heappop(fronteira)
            if no in visitados:
                continue
            visitados.add(no)
            expandidos.append(no)

            if no == objetivo:
                trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": caminho}
                return caminho, float(g_atual), float(time.perf_counter() - t0), trilha

            for viz, passo in grafo.get(no, {}).items():
                g_novo = g_atual + float(passo)
                if viz not in g_melhor or g_novo < g_melhor[viz]:
                    g_melhor[viz] = g_novo
                    f_novo = g_novo + peso * _h(heuristica, objetivo, viz)
                    heapq.heappush(fronteira, (f_novo, g_novo, viz, caminho + [viz]))
                    arestas_exploradas.append((no, viz))

        trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": []}
        return [], float('inf'), float(time.perf_counter() - t0), trilha


class BuscaAEstrelaPonderada(BuscaAEstrela):
    def __init__(self, peso: float = 1.5):
        super().__init__(peso=peso)


class BuscaGulosa(AlgoritmoBusca):
   
    def resolver(self, grafo, inicio, objetivo, **kwargs):
        heuristica = kwargs.get("heuristica", {})
        caminho, custo, segundos, _ = self.resolver_com_trilha(grafo, inicio, objetivo, heuristica)
        return caminho, custo, segundos

    def resolver_com_trilha(self, grafo, inicio, objetivo, heuristica):
        t0 = time.perf_counter()
        fronteira: List[Tuple[float, float, str, List[str]]] = []
        heapq.heappush(fronteira, (_h(heuristica, objetivo, inicio), 0.0, inicio, [inicio]))
        melhor_g = {inicio: 0.0}
        visitados = set()

        expandidos: List[str] = []
        arestas_exploradas: List[Tuple[str, str]] = []

        while fronteira:
            h_atual, g_atual, no, caminho = heapq.heappop(fronteira)
            if no in visitados:
                continue
            visitados.add(no)
            expandidos.append(no)

            if no == objetivo:
                trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": caminho}
                return caminho, float(g_atual), float(time.perf_counter() - t0), trilha

            for viz, passo in grafo.get(no, {}).items():
                g_novo = g_atual + float(passo)
                if viz not in melhor_g or g_novo < melhor_g[viz]:
                    melhor_g[viz] = g_novo
                    heapq.heappush(fronteira, (_h(heuristica, objetivo, viz), g_novo, viz, caminho + [viz]))
                    arestas_exploradas.append((no, viz))

        trilha = {"expandidos": expandidos, "arestas_exploradas": arestas_exploradas, "caminho_final": []}
        return [], float('inf'), float(time.perf_counter() - t0), trilha
