"""
Classe responsável por carregar e processar arquivos de grafo.
Suporta formatos JSON e YAML.
"""

import json
import yaml
import os
from typing import Dict, List

class CarregadorGrafo:
    """
    Classe para carregar grafos de arquivos JSON ou YAML.
    Processa e valida a estrutura dos dados.
    """
    
    @staticmethod
    def carregar_arquivo(caminho_arquivo: str) -> Dict:
        """
        Carrega um grafo de um arquivo JSON ou YAML.
        
        Args:
            caminho_arquivo: Caminho para o arquivo do grafo
            
        Returns:
            Dicionário representando o grafo
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se o formato do arquivo não for suportado
        """
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                if extensao == '.json':
                    grafo = json.load(arquivo)
                elif extensao in ['.yaml', '.yml']:
                    grafo = yaml.safe_load(arquivo)
                else:
                    raise ValueError(f"Formato de arquivo não suportado: {extensao}")
            
            # Valida e normaliza o grafo
            grafo_normalizado = CarregadorGrafo._normalizar_grafo(grafo)
            CarregadorGrafo._validar_grafo(grafo_normalizado)
            
            return grafo_normalizado
            
        except Exception as e:
            raise ValueError(f"Erro ao carregar arquivo: {str(e)}")
    
    @staticmethod
    def _normalizar_grafo(grafo: Dict) -> Dict:
        """
        Normaliza a estrutura do grafo para um formato padrão.
        
        Args:
            grafo: Grafo em formato original
            
        Returns:
            Grafo em formato normalizado
        """
        grafo_normalizado = {}
        
        for no, dados in grafo.items():
            if isinstance(dados, dict) and 'arestas' in dados:
                # Formato JSON: já está normalizado
                grafo_normalizado[no] = dados
            elif isinstance(dados, list):
                # Formato YAML: precisa ser convertido
                arestas = {}
                n_arestas = 0
                
                for item in dados:
                    if isinstance(item, dict):
                        for chave, valor in item.items():
                            if chave == 'n_arestas':
                                n_arestas = valor
                            else:
                                arestas[chave] = valor
                
                grafo_normalizado[no] = {
                    'n_arestas': n_arestas,
                    'arestas': arestas
                }
        
        return grafo_normalizado
    
    @staticmethod
    def _validar_grafo(grafo: Dict) -> None:
        """
        Valida se o grafo possui a estrutura correta.
        
        Args:
            grafo: Grafo a ser validado
            
        Raises:
            ValueError: Se a estrutura do grafo for inválida
        """
        if not isinstance(grafo, dict) or len(grafo) == 0:
            raise ValueError("Grafo deve ser um dicionário não vazio")
        
        for no, dados in grafo.items():
            if not isinstance(dados, dict):
                raise ValueError(f"Dados do nó {no} devem ser um dicionário")
            
            if 'arestas' not in dados:
                raise ValueError(f"Nó {no} deve ter a chave 'arestas'")
            
            arestas = dados['arestas']
            if not isinstance(arestas, dict):
                raise ValueError(f"Arestas do nó {no} devem ser um dicionário")
            
            # Valida se os custos são números positivos
            for vizinho, custo in arestas.items():
                if not isinstance(custo, (int, float)) or custo < 0:
                    raise ValueError(f"Custo da aresta {no}->{vizinho} deve ser um número não negativo")
    
    @staticmethod
    def obter_nos_disponiveis(grafo: Dict) -> List[str]:
        """
        Retorna uma lista com todos os nós disponíveis no grafo.
        Inclui tanto os nós principais quanto os vizinhos mencionados nas arestas.
        
        Args:
            grafo: Dicionário representando o grafo
            
        Returns:
            Lista ordenada com os nomes dos nós
        """
        todos_nos = set()
        
        # Adiciona os nós principais (chaves do dicionário)
        todos_nos.update(grafo.keys())
        
        # Adiciona todos os nós mencionados como vizinhos nas arestas
        for no, dados in grafo.items():
            if 'arestas' in dados:
                todos_nos.update(dados['arestas'].keys())
        
        return sorted(list(todos_nos))
    
    @staticmethod
    def validar_nos(grafo: Dict, no_inicial: str, no_final: str) -> bool:
        """
        Verifica se os nós inicial e final existem no grafo.
        Considera tanto nós principais quanto nós mencionados como vizinhos.
        
        Args:
            grafo: Dicionário representando o grafo
            no_inicial: Nó de origem
            no_final: Nó de destino
            
        Returns:
            True se ambos os nós existem, False caso contrário
        """
        todos_nos = set(CarregadorGrafo.obter_nos_disponiveis(grafo))
        return no_inicial in todos_nos and no_final in todos_nos
