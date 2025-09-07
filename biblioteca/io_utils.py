from typing import Dict, Any, Tuple
import json
import os

try:
    import yaml
except Exception:
    yaml = None


def carregar_com_heuristica(caminho: str) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]], Dict[str, Any]]:
    data = _carregar_raw(caminho)
    return _normalizar_tudo(data)


def _carregar_raw(caminho: str):
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    _, ext = os.path.splitext(caminho.lower())
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    if ext in (".json", ".jsn"):
        return json.loads(conteudo)
    elif ext in (".yml", ".yaml"):
        if yaml is None:
            raise RuntimeError("PyYAML não instalado. Use JSON ou instale pyyaml.")
        return yaml.safe_load(conteudo)
    else:
        raise ValueError("Extensão não suportada. Use .json ou .yaml/.yml")


def _normalizar_tudo(data: Any) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]], Dict[str, Any]]:
    if isinstance(data, dict) and any(k in data for k in ("grafo", "heuristica", "config")):
        grafo_raw = data.get("grafo", {})
        heur_raw = data.get("heuristica", {})
        cfg = data.get("config", {})
        grafo = _normalizar_adjacencia(grafo_raw)
        heuristica = _normalizar_heuristica(heur_raw)
        return grafo, heuristica, cfg

    if isinstance(data, dict) and data:
        amostra = next(iter(data.values()))
        if isinstance(amostra, dict) and "arestas" in amostra:
            g = {}
            for no, info in data.items():
                arestas = info.get("arestas", {})
                g[no] = {str(v): float(c) for v, c in arestas.items()}
            return g, {}, {}

    if isinstance(data, dict):
        try:
            g = _normalizar_adjacencia(data)
            return g, {}, {}
        except Exception:
            pass

    if isinstance(data, dict) and data:
        ok_yaml = True
        g = {}
        for no, lista in data.items():
            if not isinstance(lista, list):
                ok_yaml = False
                break
            g[no] = {}
            for item in lista:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if k == "n_arestas":
                            continue
                        g[no][str(k)] = float(v)
        if ok_yaml:
            return g, {}, {}

    raise ValueError("Estrutura não reconhecida. Veja exemplos na pasta /entrada.")


def _normalizar_adjacencia(d: Any) -> Dict[str, Dict[str, float]]:
    if not isinstance(d, dict):
        raise ValueError("Adjacência inválida.")
    g: Dict[str, Dict[str, float]] = {}
    for no, viz in d.items():
        if not isinstance(viz, dict):
            raise ValueError(f"Vizinhos inválidos em {no}.")
        g[no] = {str(v): float(c) for v, c in viz.items()}
    return g


def _normalizar_heuristica(h: Any) -> Dict[str, Dict[str, float]]:
    if not h:
        return {}
    if not isinstance(h, dict):
        raise ValueError("Heurística inválida.")
    out: Dict[str, Dict[str, float]] = {}
    for objetivo, mapa in h.items():
        if not isinstance(mapa, dict):
            continue
        out[str(objetivo)] = {str(no): float(val) for no, val in mapa.items()}
    return out
