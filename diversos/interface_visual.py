"""
Interface gráfica com visualização do grafo usando tkinter Canvas.
Desenha os nós como círculos e as arestas como linhas na tela.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import math
import random
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biblioteca import BuscaCustoUniforme, CarregadorGrafo

class InterfaceVisual:
    """
    Interface gráfica com visuavlizão real do grafo
    """
    
    def __init__(self):
        """Inicializa a interface gráfica."""
        self.root = tk.Tk()
        self.root.title("Simulador de Busca em Grafos - Visualização Gráfica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variáveis de estado
        self.grafo = None
        self.arquivo_carregado = None
        self.algoritmo = None
        self.posicoes_nos = {}  # Posições x,y dos nós para desenho
        self.ultimo_resultado = None  # Guarda resultado da última busca
        
        # Configuração das cores
        self.cores = {
            'no_normal': '#E8F4FD',
            'no_inicial': '#4CAF50',
            'no_final': '#F44336',
            'no_caminho': '#FF9800',
            'no_explorado': '#2196F3',
            'aresta_normal': '#666666',
            'aresta_caminho': '#FF5722',
            'texto': '#000000',
            'fundo': '#FFFFFF'
        }
        
        # Configura o estilo
        self.configurar_estilo()
        
        # Cria a interface
        self.criar_interface()
        
        # Centraliza a janela
        self.centralizar_janela()
    
    def configurar_estilo(self):
        """Configura o estilo visual da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Result.TLabel', font=('Arial', 10))
    
    def criar_interface(self):
        """Cria todos os elementos da interface gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura o redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Simulador de Busca em Grafos", 
                          style='Title.TLabel')
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Painel de controle (esquerda)
        self.criar_painel_controle(main_frame)
        
        # Painel de visualização (direita)
        self.criar_painel_visualizacao(main_frame)
        
        # Painel de resultados (baixo)
        self.criar_painel_resultados(main_frame)
    
    def criar_painel_controle(self, parent):
        """Cria o painel de controle com opções de configuração."""
        # Frame do painel de controle
        controle_frame = ttk.LabelFrame(parent, text="Configuração", padding="10")
        controle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                           padx=(0, 10))
        controle_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Seção de carregamento de arquivo
        ttk.Label(controle_frame, text="1. Carregar Grafo", 
                 style='Header.TLabel').grid(row=row, column=0, columnspan=2, 
                                           sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Botão para carregar arquivo
        self.btn_carregar = ttk.Button(controle_frame, text="Selecionar Arquivo", 
                                      command=self.carregar_arquivo)
        self.btn_carregar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                              pady=(0, 5))
        row += 1
        
        # Label para mostrar arquivo carregado
        self.lbl_arquivo = ttk.Label(controle_frame, text="Nenhum arquivo carregado", 
                                    foreground="gray")
        self.lbl_arquivo.grid(row=row, column=0, columnspan=2, sticky=tk.W, 
                             pady=(0, 15))
        row += 1
        
        # Seção de algoritmo
        ttk.Label(controle_frame, text="2. Algoritmo de Busca", 
                 style='Header.TLabel').grid(row=row, column=0, columnspan=2, 
                                           sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Combobox para algoritmo (por enquanto só Dijkstra)
        self.algoritmo_var = tk.StringVar(value="Busca com Custo Uniforme (Dijkstra)")
        self.cmb_algoritmo = ttk.Combobox(controle_frame, textvariable=self.algoritmo_var,
                                         values=["Busca com Custo Uniforme (Dijkstra)"],
                                         state="readonly", width=30)
        self.cmb_algoritmo.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                               pady=(0, 15))
        row += 1
        
        # Seção de nós
        ttk.Label(controle_frame, text="3. Selecionar Nós", 
                 style='Header.TLabel').grid(row=row, column=0, columnspan=2, 
                                           sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Nó inicial
        ttk.Label(controle_frame, text="Nó Inicial:").grid(row=row, column=0, 
                                                           sticky=tk.W, pady=(0, 5))
        self.no_inicial_var = tk.StringVar()
        self.cmb_no_inicial = ttk.Combobox(controle_frame, textvariable=self.no_inicial_var,
                                          state="readonly", width=15)
        self.cmb_no_inicial.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Nó final
        ttk.Label(controle_frame, text="Nó Final:").grid(row=row, column=0, 
                                                         sticky=tk.W, pady=(0, 15))
        self.no_final_var = tk.StringVar()
        self.cmb_no_final = ttk.Combobox(controle_frame, textvariable=self.no_final_var,
                                        state="readonly", width=15)
        self.cmb_no_final.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        # Botão para executar busca
        self.btn_buscar = ttk.Button(controle_frame, text="Executar Busca", 
                                    command=self.executar_busca, state="disabled")
        self.btn_buscar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                            pady=(0, 10))
        row += 1
        
        # Botão para reorganizar layout
        self.btn_reorganizar = ttk.Button(controle_frame, text="Reorganizar Layout", 
                                         command=self.reorganizar_layout, state="disabled")
        self.btn_reorganizar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                                 pady=(0, 10))
        row += 1
        
        # Botão para salvar resultados
        self.btn_salvar = ttk.Button(controle_frame, text="Salvar Resultados", 
                                    command=self.salvar_resultados, state="disabled")
        self.btn_salvar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def criar_painel_visualizacao(self, parent):
        """Cria o painel de visualização gráfica do grafo."""
        # Frame da visualização
        vis_frame = ttk.LabelFrame(parent, text="Visualização do Grafo", padding="5")
        vis_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        vis_frame.columnconfigure(0, weight=1)
        vis_frame.rowconfigure(0, weight=1)
        
        # Canvas para desenhar o grafo
        self.canvas = tk.Canvas(
            vis_frame,
            bg=self.cores['fundo'],
            width=600,
            height=400,
            relief='sunken',
            borderwidth=2
        )
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars para o canvas
        scrollbar_v = ttk.Scrollbar(vis_frame, orient="vertical", command=self.canvas.yview)
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(yscrollcommand=scrollbar_v.set)
        
        scrollbar_h = ttk.Scrollbar(vis_frame, orient="horizontal", command=self.canvas.xview)
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.canvas.configure(xscrollcommand=scrollbar_h.set)
        
        # Legenda de cores (sempre visível)
        self.criar_legenda_cores(vis_frame)
        
        # Bind para redimensionamento
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Mensagem inicial
        self.mostrar_mensagem_inicial()
    
    def criar_legenda_cores(self, parent):
        """Cria uma legenda de cores sempre visível."""
        legenda_frame = ttk.LabelFrame(parent, text="Legenda de Cores", padding="5")
        legenda_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Cria um canvas pequeno para desenhar as cores da legenda
        legenda_canvas = tk.Canvas(legenda_frame, height=60, bg='white')
        legenda_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # Define as legendas
        legendas = [
            ("Nó Inicial", self.cores['no_inicial']),
            ("Nó Final", self.cores['no_final']),
            ("Caminho Ótimo", self.cores['no_caminho']),
            ("Nó Explorado", self.cores['no_explorado']),
            ("Não Visitado", self.cores['no_normal'])
        ]
        
        # Desenha cada item da legenda
        x_start = 10
        for i, (texto, cor) in enumerate(legendas):
            x = x_start + i * 120
            
            # Desenha o círculo colorido
            legenda_canvas.create_oval(
                x, 20, x + 20, 40,
                fill=cor,
                outline='#333333',
                width=2
            )
            
            # Desenha o texto
            legenda_canvas.create_text(
                x + 30, 30,
                text=texto,
                anchor='w',
                font=('Arial', 9),
                fill='#333333'
            )
        
        # Legenda para arestas
        y_arestas = 45
        # Linha normal
        legenda_canvas.create_line(
            10, y_arestas, 30, y_arestas,
            fill=self.cores['aresta_normal'],
            width=2
        )
        legenda_canvas.create_text(
            35, y_arestas,
            text="Aresta Normal",
            anchor='w',
            font=('Arial', 9),
            fill='#333333'
        )
        
        # Linha do caminho
        legenda_canvas.create_line(
            150, y_arestas, 170, y_arestas,
            fill=self.cores['aresta_caminho'],
            width=4
        )
        legenda_canvas.create_text(
            175, y_arestas,
            text="Caminho Ótimo",
            anchor='w',
            font=('Arial', 9),
            fill='#333333'
        )
    
    def criar_painel_resultados(self, parent):
        """Cria o painel de resultados na parte inferior."""
        # Frame dos resultados
        resultado_frame = ttk.LabelFrame(parent, text="Resultados da Busca", padding="10")
        resultado_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                            pady=(10, 0))
        resultado_frame.columnconfigure(0, weight=1)
        
        # Label para mostrar resultados
        self.lbl_resultado = ttk.Label(resultado_frame, text="Execute uma busca para ver os resultados", 
                                      style='Result.TLabel')
        self.lbl_resultado.grid(row=0, column=0, sticky=tk.W)
    
    def mostrar_mensagem_inicial(self):
        """Mostra mensagem inicial no canvas."""
        self.canvas.delete("all")
        
        # Centraliza a mensagem
        canvas_width = self.canvas.winfo_width() or 600
        canvas_height = self.canvas.winfo_height() or 400
        
        x_center = canvas_width // 2
        y_center = canvas_height // 2
        
        mensagens = [
            "SIMULADOR DE BUSCA EM GRAFOS",
            "",
            "1. Carregue um arquivo de grafo (JSON/YAML)",
            "2. Selecione nós inicial e final",
            "3. Execute a busca para ver o caminho",
            "",
        ]
        
        y_offset = -len(mensagens) * 15 // 2
        for i, mensagem in enumerate(mensagens):
            self.canvas.create_text(
                x_center, y_center + y_offset + i * 30,
                text=mensagem,
                font=('Arial', 12, 'bold' if i == 0 else 'normal'),
                fill='#333333'
            )
    
    def on_canvas_configure(self, event):
        """Callback para redimensionamento do canvas."""
        # Atualiza a região de scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def carregar_arquivo(self):
        """Abre dialog para carregar arquivo de grafo."""
        tipos_arquivo = [
            ("Arquivos JSON", "*.json"),
            ("Arquivos YAML", "*.yaml *.yml"),
            ("Todos os arquivos", "*.*")
        ]
        
        arquivo = filedialog.askopenfilename(
            title="Selecionar Arquivo de Grafo",
            filetypes=tipos_arquivo,
            initialdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entrada")
        )
        
        if arquivo:
            try:
                # Carrega o grafo
                self.grafo = CarregadorGrafo.carregar_arquivo(arquivo)
                self.arquivo_carregado = arquivo
                
                # Atualiza interface
                nome_arquivo = os.path.basename(arquivo)
                self.lbl_arquivo.config(text=f"Arquivo: {nome_arquivo}", foreground="green")
                
                # Popula os comboboxes de nós
                nos_disponiveis = CarregadorGrafo.obter_nos_disponiveis(self.grafo)
                self.cmb_no_inicial['values'] = nos_disponiveis
                self.cmb_no_final['values'] = nos_disponiveis
                
                # Limpa seleções anteriores
                self.no_inicial_var.set("")
                self.no_final_var.set("")
                
                # Habilita os botões
                self.btn_buscar.config(state="normal")
                self.btn_reorganizar.config(state="normal")
                
                # Calcula posições dos nós e desenha o grafo
                self.calcular_posicoes_nos()
                self.desenhar_grafo()
                
                messagebox.showinfo("Sucesso", f"Grafo carregado com sucesso!\n{len(nos_disponiveis)} nós encontrados.")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
    
    def calcular_posicoes_nos(self):
        """Calcula posições dos nós para desenho em layout circular."""
        if not self.grafo:
            return
        
        nos_disponiveis = CarregadorGrafo.obter_nos_disponiveis(self.grafo)
        num_nos = len(nos_disponiveis)
        
        # Dimensões do canvas
        canvas_width = 600
        canvas_height = 400
        margin = 80
        
        # Raio do círculo para posicionamento
        raio = min(canvas_width - margin, canvas_height - margin) // 2
        centro_x = canvas_width // 2
        centro_y = canvas_height // 2
        
        # Calcula posições em círculo
        self.posicoes_nos = {}
        for i, no in enumerate(sorted(nos_disponiveis)):
            angulo = 2 * math.pi * i / num_nos
            x = centro_x + raio * math.cos(angulo)
            y = centro_y + raio * math.sin(angulo)
            self.posicoes_nos[no] = (x, y)
    
    def reorganizar_layout(self):
        """Reorganiza o layout dos nós aleatoriamente."""
        if not self.grafo:
            return
        
        nos_disponiveis = CarregadorGrafo.obter_nos_disponiveis(self.grafo)
        
        # Dimensões do canvas
        canvas_width = 600
        canvas_height = 400
        margin = 60
        
        # Posicionamento aleatório
        self.posicoes_nos = {}
        for no in nos_disponiveis:
            x = random.randint(margin, canvas_width - margin)
            y = random.randint(margin, canvas_height - margin)
            self.posicoes_nos[no] = (x, y)
        
        # Redesenha o grafo
        self.desenhar_grafo()
    
    def desenhar_grafo(self):
        """Desenha o grafo completo no canvas."""
        if not self.grafo or not self.posicoes_nos:
            return
        
        # Limpa o canvas
        self.canvas.delete("all")
        
        # Cria instância do algoritmo para obter vizinhos
        algoritmo_temp = BuscaCustoUniforme(self.grafo)
        
        # Primeiro desenha todas as arestas (atrás dos nós)
        for no in self.posicoes_nos:
            x1, y1 = self.posicoes_nos[no]
            vizinhos = algoritmo_temp._obter_vizinhos(no)
            
            for vizinho, custo in vizinhos.items():
                if vizinho in self.posicoes_nos:
                    x2, y2 = self.posicoes_nos[vizinho]
                    
                    # Determina a cor da aresta
                    cor_aresta = self.cores['aresta_normal']
                    largura = 1
                    
                    # Se há resultado de busca, destaca o caminho
                    if (self.ultimo_resultado and 
                        self.ultimo_resultado['caminho'] and
                        no in self.ultimo_resultado['caminho'] and
                        vizinho in self.ultimo_resultado['caminho']):
                        
                        caminho = self.ultimo_resultado['caminho']
                        if abs(caminho.index(no) - caminho.index(vizinho)) == 1:
                            cor_aresta = self.cores['aresta_caminho']
                            largura = 3
                    
                    # Desenha a linha
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=cor_aresta,
                        width=largura,
                        tags="aresta"
                    )
                    
                    # Desenha o custo da aresta
                    meio_x = (x1 + x2) // 2
                    meio_y = (y1 + y2) // 2
                    self.canvas.create_text(
                        meio_x, meio_y,
                        text=str(custo),
                        font=('Arial', 8),
                        fill='#444444',
                        tags="custo"
                    )
        
        # Depois desenha todos os nós (na frente das arestas)
        for no in self.posicoes_nos:
            x, y = self.posicoes_nos[no]
            
            # Determina a cor do nó
            cor_no = self.cores['no_normal']
            if self.ultimo_resultado:
                if (self.ultimo_resultado.get('no_inicial') == no):
                    cor_no = self.cores['no_inicial']
                elif (self.ultimo_resultado.get('no_final') == no):
                    cor_no = self.cores['no_final']
                elif (self.ultimo_resultado.get('caminho') and 
                      no in self.ultimo_resultado['caminho']):
                    cor_no = self.cores['no_caminho']
                elif (self.ultimo_resultado.get('nos_visitados') and 
                      no in self.ultimo_resultado['nos_visitados']):
                    cor_no = self.cores['no_explorado']
            
            # Desenha o círculo do nó
            raio = 20
            self.canvas.create_oval(
                x - raio, y - raio, x + raio, y + raio,
                fill=cor_no,
                outline='#333333',
                width=2,
                tags="no"
            )
            
            # Desenha o nome do nó
            self.canvas.create_text(
                x, y,
                text=no,
                font=('Arial', 10, 'bold'),
                fill=self.cores['texto'],
                tags="texto"
            )
        
        # Atualiza a região de scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def executar_busca(self):
        """Executa o algoritmo de busca selecionado."""
        if not self.grafo:
            messagebox.showerror("Erro", "Carregue um grafo primeiro!")
            return
        
        no_inicial = self.no_inicial_var.get()
        no_final = self.no_final_var.get()
        
        if not no_inicial or not no_final:
            messagebox.showerror("Erro", "Selecione os nós inicial e final!")
            return
        
        if no_inicial == no_final:
            messagebox.showwarning("Aviso", "Nó inicial e final são iguais!")
            return
        
        try:
            # Cria a instância do algoritmo
            self.algoritmo = BuscaCustoUniforme(self.grafo)
            
            # Executa a busca
            caminho, custo, tempo = self.algoritmo.buscar(no_inicial, no_final)
            estatisticas = self.algoritmo.obter_estatisticas()
            
            # Armazena o resultado
            self.ultimo_resultado = {
                'caminho': caminho,
                'custo': custo,
                'tempo': tempo,
                'no_inicial': no_inicial,
                'no_final': no_final,
                'nos_visitados': estatisticas.get('ordem_visita', [])
            }
            
            # Atualiza a visualização
            self.desenhar_grafo()
            
            # Exibe os resultados
            if caminho:
                resultado_texto = (
                    f"Caminho encontrado"
                    f"Rota: {' → '.join(caminho)} | "
                    f"Custo: {custo:.2f} | "
                    f"Tempo: {tempo:.6f}s | "
                    f"Nós explorados: {len(estatisticas.get('ordem_visita', []))}"
                )
                self.lbl_resultado.config(text=resultado_texto, foreground="green")
            else:
                self.lbl_resultado.config(text="Caminho não encontraod", foreground="red")
            
            # Habilita o botão de salvar
            self.btn_salvar.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a busca:\n{str(e)}")
    
    def salvar_resultados(self):
        """Salva os resultados automaticamente na pasta 'saida'."""
        if not self.ultimo_resultado:
            messagebox.showerror("Erro", "Execute uma busca primeiro!")
            return

        # Cria a pasta 'saida' se não existir
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_saida = os.path.join(raiz_projeto, "saida")
        os.makedirs(pasta_saida, exist_ok=True)
        
        # Gera nome do arquivo automaticamente baseado na busca
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        no_inicial = self.ultimo_resultado['no_inicial'] 
        no_final = self.ultimo_resultado['no_final']
        nome_arquivo = f"busca_{no_inicial}_para_{no_final}_{timestamp}.txt"
        arquivo_completo = os.path.join(pasta_saida, nome_arquivo)
        
        try:
            with open(arquivo_completo, 'w', encoding='utf-8') as f:
                f.write(f"RESULTADO DA BUSCA EM GRAFO\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Arquivo do grafo: {os.path.basename(self.arquivo_carregado)}\n")
                f.write(f"Algoritmo: Busca com Custo Uniforme (Dijkstra)\n\n")
                
                f.write(f"Busca: {self.ultimo_resultado['no_inicial']} → {self.ultimo_resultado['no_final']}\n\n")
                
                if self.ultimo_resultado['caminho']:
                    f.write(f"CAMINHO ENCONTRADO:\n")
                    f.write(f"Rota: {' → '.join(self.ultimo_resultado['caminho'])}\n")
                    f.write(f"Custo total: {self.ultimo_resultado['custo']:.2f}\n")
                    f.write(f"Número de nós no caminho: {len(self.ultimo_resultado['caminho'])}\n")
                else:
                    f.write(f"CAMINHO NÃO ENCONTRADO\n")
                
                f.write(f"\nTempo de execução: {self.ultimo_resultado['tempo']:.6f} segundos\n")
                f.write(f"Nós explorados: {len(self.ultimo_resultado['nos_visitados'])}\n")
                f.write(f"Ordem de exploração: {' → '.join(self.ultimo_resultado['nos_visitados'])}\n")
            
            messagebox.showinfo("Sucesso", f"Resultados salvos automaticamente em:\n{arquivo_completo}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def executar(self):
        """Inicia a interface gráfica."""
        self.root.mainloop()

if __name__ == "__main__":
    app = InterfaceVisual()
    app.executar()
