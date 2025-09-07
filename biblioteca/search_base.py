from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any


class AlgoritmoBusca(ABC):
    @abstractmethod
    def resolver(
        self,
        grafo: Dict[str, Dict[str, float]],
        inicio: str,
        objetivo: str,
        **kwargs
    ) -> Tuple[List[str], float, float]:
        
        raise NotImplementedError
