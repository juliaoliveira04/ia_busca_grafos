import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, List, Tuple

from biblioteca.io_utils import carregar_com_heuristica
from biblioteca.ucs import BuscaCustoUniforme
from biblioteca.astar import BuscaAEstrela, BuscaAEstrelaPonderada, BuscaGulosa


ALGOS = ["UCS (Dijkstra)", "A* (peso=1.0)", "A* Ponderado", "Gulosa"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Busca — UCS, A*, A* Ponderado, Gulosa")
        self.geometry("1600x800")

        self.grafo: Dict[str, Dict[str, float]] = {}
        self.heuristica: Dict[str, Dict[str, float]] = {}
        self.config_arq: Dict[str, Any] = {}

        self.pos: Dict[str, Tuple[float, float]] = {}
        self.nos: List[str] = []
        self.arestas: List[Tuple[str, str, float]] = []

        self._build_ui()

    def _build_ui(self):
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.controls_frame = ttk.Frame(self.paned_window, padding=8)
        self.paned_window.add(self.controls_frame, weight=1)

        file_frame = ttk.LabelFrame(self.controls_frame, text="Arquivo do Grafo", padding=4)
        file_frame.pack(fill=tk.X, pady=(0, 8))

        self.arquivo_var = tk.StringVar(value="")
        ttk.Label(file_frame, text="Arquivo:").pack(anchor=tk.W)
        file_entry_frame = ttk.Frame(file_frame)
        file_entry_frame.pack(fill=tk.X, pady=(2, 4))
        ttk.Entry(file_entry_frame, textvariable=self.arquivo_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(file_entry_frame, text="...", command=self._pick_file, width=3).pack(side=tk.RIGHT)
        ttk.Button(file_frame, text="Carregar", command=self._carregar).pack(fill=tk.X, pady=(2, 0))

        search_frame = ttk.LabelFrame(self.controls_frame, text="Parâmetros da Busca", padding=4)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        self.inicio_var = tk.StringVar()
        self.objetivo_var = tk.StringVar()

        ttk.Label(search_frame, text="Nó inicial:").pack(anchor=tk.W)
        self.cb_inicio = ttk.Combobox(search_frame, textvariable=self.inicio_var, state="readonly")
        self.cb_inicio.pack(fill=tk.X, pady=(2, 4))

        ttk.Label(search_frame, text="Nó objetivo:").pack(anchor=tk.W)
        self.cb_obj = ttk.Combobox(search_frame, textvariable=self.objetivo_var, state="readonly")
        self.cb_obj.pack(fill=tk.X, pady=(2, 4))

        algo_frame = ttk.LabelFrame(self.controls_frame, text="Algoritmo", padding=4)
        algo_frame.pack(fill=tk.X, pady=(0, 8))

        self.algo_var = tk.StringVar(value=ALGOS[0])
        self.cb_algo = ttk.Combobox(algo_frame, textvariable=self.algo_var, state="readonly", values=ALGOS)
        self.cb_algo.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(algo_frame, text="Peso (A*):").pack(anchor=tk.W)
        self.peso_var = tk.StringVar(value="1.0")
        self.ent_peso = ttk.Entry(algo_frame, textvariable=self.peso_var)
        self.ent_peso.pack(fill=tk.X, pady=(2, 4))

        ttk.Button(algo_frame, text="Rodar Busca", command=self._rodar).pack(fill=tk.X, pady=(4, 0))

        info_frame = ttk.LabelFrame(self.controls_frame, text="Informações", padding=4)
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.lbl_info = ttk.Label(info_frame, text="Carregue um grafo. Para A*/Gulosa, inclua heurística.", 
                                 wraplength=200, justify=tk.LEFT)
        self.lbl_info.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.canvas_frame, weight=4)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", lambda e: (self._layout(), self._desenhar()) if self.nos else None)

        self.after(100, self._set_pane_sizes)

    def _set_pane_sizes(self):
        total_width = self.paned_window.winfo_width()
        if total_width > 0:
            left_width = int(total_width * 0.2)
            self.paned_window.sashpos(0, left_width)

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Escolha arquivo JSON/YAML do grafo",
            filetypes=[("JSON/YAML", "*.json;*.jsn;*.yaml;*.yml"), ("Todos", "*.*")],
            initialfile=self.arquivo_var.get() or ""
        )
        if path:
            self.arquivo_var.set(path)

    def _carregar(self):
        try:
            grafo, heur, cfg = carregar_com_heuristica(self.arquivo_var.get())
        except Exception as e:
            messagebox.showerror("Erro ao carregar", str(e))
            return

        self.grafo, self.heuristica, self.config_arq = grafo, heur, cfg
        self.nos = sorted(self.grafo.keys())
        self.arestas = [(u, v, float(c)) for u, viz in self.grafo.items() for v, c in viz.items()]

        self.cb_inicio["values"] = self.nos
        self.cb_obj["values"] = self.nos
        if self.nos:
            self.inicio_var.set(self.nos[0])
            self.objetivo_var.set(self.nos[-1])

        self._layout()
        self._desenhar()
        msg = "Grafo carregado. Selecione início/objetivo, algoritmo e peso (se A*)."
        if not self.heuristica:
            msg += " (Sem heurística: A* e Gulosa usarão h=0)"
        self._set_info(msg)

    def _layout(self):
        W = self.canvas.winfo_width() or 960
        H = self.canvas.winfo_height() or 560
        cx, cy = W/2, H/2
        r = min(W, H) * 0.38
        n = max(1, len(self.nos))
        self.pos = {}
        for i, no in enumerate(self.nos):
            ang = 2 * math.pi * i / n
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            self.pos[no] = (x, y)

    def _desenhar(self):
        self.canvas.delete("all")
        for u, v, c in self.arestas:
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#999", width=2, tags=("aresta", f"{u}->{v}"))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            texto = str(int(c) if float(c).is_integer() else f"{c:.1f}")
            self.canvas.create_text(mx, my, text=texto, fill="#444", font=("Arial", 9))

        R = 18
        for no in self.nos:
            x, y = self.pos[no]
            self.canvas.create_oval(x - R, y - R, x + R, y + R,
                                    fill="#f7f7ff", outline="#333", width=2,
                                    tags=("no", no))
            self.canvas.create_text(x, y, text=no, font=("Arial", 10, "bold"), fill="#222")

    def _set_info(self, msg: str):
        self.lbl_info.configure(text=msg)

    def _rodar(self):
        if not self.grafo:
            messagebox.showwarning("Aviso", "Carregue um grafo primeiro.")
            return
        inicio = self.inicio_var.get()
        objetivo = self.objetivo_var.get()
        if not inicio or not objetivo:
            messagebox.showwarning("Aviso", "Selecione início e objetivo.")
            return

        algo_nome = self.algo_var.get()
        try:
            peso = float(self.peso_var.get() or "1.0")
            if peso <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Peso inválido", "Informe um valor numérico > 0 para o peso do A*.")
            return

        if algo_nome.startswith("UCS"):
            algoritmo = BuscaCustoUniforme()
            caminho, custo, segundos, trilha = algoritmo.resolver_com_trilha(self.grafo, inicio, objetivo)

        elif algo_nome.startswith("A* (peso=1.0)"):
            algoritmo = BuscaAEstrela(peso=1.0)
            caminho, custo, segundos, trilha = algoritmo.resolver_com_trilha(
                self.grafo, inicio, objetivo, self.heuristica, 1.0
            )

        elif algo_nome.startswith("A* Ponderado"):
            algoritmo = BuscaAEstrelaPonderada(peso=peso)
            caminho, custo, segundos, trilha = algoritmo.resolver_com_trilha(
                self.grafo, inicio, objetivo, self.heuristica, peso
            )

        else:  # Gulosa
            algoritmo = BuscaGulosa()
            caminho, custo, segundos, trilha = algoritmo.resolver_com_trilha(
                self.grafo, inicio, objetivo, self.heuristica
            )

        self._desenhar()
        self.update()

        for no in trilha.get("expandidos", []):
            self._pintar_no(no, fill="#cfe9ff")
            self.update()
            self.after(150)

        for (u, v) in trilha.get("arestas_exploradas", []):
            self._pintar_aresta(u, v, color="#66a3ff", width=3)
            self.update()
            self.after(120)

        caminho = caminho or []
        melhores = set()
        for i in range(len(caminho) - 1):
            melhores.add((caminho[i], caminho[i + 1]))
            melhores.add((caminho[i + 1], caminho[i])) 
        descartadas = []
        for (u, v) in trilha.get("arestas_exploradas", []):
            if (u, v) not in melhores and (v, u) not in melhores:
                descartadas.append((u, v))
        for (u, v) in descartadas:
            self._pintar_aresta(u, v, color="#f39c12", width=3)

        if caminho:
            for i in range(len(caminho) - 1):
                u, v = caminho[i], caminho[i + 1]
                self._pintar_aresta(u, v, color="#0b7", width=5)
                self._pintar_no(u, outline="#0b7", width=3)
                self._pintar_no(v, outline="#0b7", width=3)
            n_exp = len(trilha.get("expandidos", []))
            n_expl = len(trilha.get("arestas_exploradas", []))
            n_desc = len(descartadas)
            self._set_info(
                f"Algoritmo: {algo_nome} | Caminho: {' -> '.join(caminho)} | "
                f"Custo: {custo:.3f} | Tempo (s): {segundos:.6f} | "
                f"Expandidos: {n_exp} | Exploradas: {n_expl} | Descartadas: {n_desc}"
            )
        else:
            self._set_info(f"Algoritmo: {algo_nome} | Sem caminho. Tempo (s): {segundos:.6f}")

    def _pintar_aresta(self, u: str, v: str, color="#66a3ff", width=3):
        tag = f"{u}->{v}"
        for item in self.canvas.find_withtag(tag):
            self.canvas.itemconfigure(item, fill=color, width=width)
        tag2 = f"{v}->{u}"
        for item in self.canvas.find_withtag(tag2):
            self.canvas.itemconfigure(item, fill=color, width=width)

    def _pintar_no(self, no: str, fill=None, outline=None, width=None):
        for item in self.canvas.find_withtag(no):
            if fill is not None:
                self.canvas.itemconfigure(item, fill=fill)
            if outline is not None:
                self.canvas.itemconfigure(item, outline=outline)
            if width is not None:
                self.canvas.itemconfigure(item, width=width)


if __name__ == "__main__":
    app = App()
    app.mainloop()
