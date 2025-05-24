import heapq
import math

class Grafo:
    """Representa o multigrafo do problema de logística."""
    def __init__(self):
        """Inicializa um grafo vazio."""
        self.vertices = set() # Conjunto de todos os IDs de vértices
        self.arestas_nao_req = [] # Lista de tuplas (u, v, custo) para arestas não requeridas
        self.arcos_nao_req = []   # Lista de tuplas (u, v, custo) para arcos não requeridos

        # Dicionários para armazenar detalhes dos serviços requeridos
        # Chave: ID do vértice/aresta/arco original; Valor: detalhes
        self.requeridos_v = {} # {no_id: {"demanda": d, "custo_servico": cs, "service_id": sid}}
        self.requeridos_e = {} # {(u, v): {"custo_travessia": ct, "demanda": d, "custo_servico": cs, "service_id": sid}}
        self.requeridos_a = {} # {(u, v): {"custo_travessia": ct, "demanda": d, "custo_servico": cs, "service_id": sid}}

        self.adj = {} # Lista de adjacência: {u: [(v1, custo1), (v2, custo2), ...]}

        # Atributos populados pelo parser a partir do cabeçalho da instância
        self.deposito = None
        self.capacidade = float("inf") # Default para infinito se não especificado

        # Mapa de serviços (populado pelo parser)
        # Chave: service_id (inteiro sequencial); Valor: dicionário com detalhes
        self.service_map = {}

        # Matrizes de caminhos mínimos (a serem calculadas ou definidas externamente)
        self.dist_matrix = None # Dicionário de dicionários: {origem: {destino: custo}}
        self.pred_matrix = None # Dicionário de dicionários: {origem: {destino: predecessor}}

    def _add_adj(self, u, v, custo):
        """Adiciona uma conexão direcionada à lista de adjacência."""
        self.vertices.add(u)
        self.vertices.add(v)
        if u not in self.adj:
            self.adj[u] = []
        # Evita adicionar a mesma adjacência múltiplas vezes se a aresta/arco for lido novamente
        if not any(neighbor == v and c == custo for neighbor, c in self.adj[u]):
             self.adj[u].append((v, custo))

    def adicionar_aresta_nao_requerida(self, u, v, custo):
        """Adiciona uma aresta não requerida ao grafo."""
        self.arestas_nao_req.append((u, v, custo))
        self._add_adj(u, v, custo)
        self._add_adj(v, u, custo)

    def adicionar_arco_nao_requerido(self, u, v, custo):
        """Adiciona um arco não requerido ao grafo."""
        self.arcos_nao_req.append((u, v, custo))
        self._add_adj(u, v, custo)

    def adicionar_vertice_requerido(self, v, demanda, custo_servico, service_id):
        """Adiciona um vértice requerido."""
        self.vertices.add(v)
        if v not in self.requeridos_v:
            self.requeridos_v[v] = {"demanda": demanda, "custo_servico": custo_servico, "service_id": service_id}
        # O service_map é populado no parser

    def adicionar_aresta_requerida(self, u, v, custo_travessia, demanda, custo_servico, service_id):
        """Adiciona uma aresta requerida. A travessia é adicionada à adjacência."""
        aresta_key = tuple(sorted((u, v)))
        if aresta_key not in self.requeridos_e:
            self.requeridos_e[aresta_key] = {"custo_travessia": custo_travessia, "demanda": demanda, "custo_servico": custo_servico, "service_id": service_id}
        # Adiciona a travessia à lista de adjacência (se já não existir com o mesmo custo)
        self._add_adj(u, v, custo_travessia)
        self._add_adj(v, u, custo_travessia)
        # O service_map é populado no parser

    def adicionar_arco_requerido(self, u, v, custo_travessia, demanda, custo_servico, service_id):
        """Adiciona um arco requerido. A travessia é adicionada à adjacência."""
        arco_key = (u, v)
        if arco_key not in self.requeridos_a:
            self.requeridos_a[arco_key] = {"custo_travessia": custo_travessia, "demanda": demanda, "custo_servico": custo_servico, "service_id": service_id}
        # Adiciona a travessia à lista de adjacência (se já não existir com o mesmo custo)
        self._add_adj(u, v, custo_travessia)
        # O service_map é populado no parser

    def set_shortest_paths(self, dist_matrix, pred_matrix):
        """Define as matrizes de distância e predecessores calculadas."""
        self.dist_matrix = dist_matrix
        self.pred_matrix = pred_matrix

    def get_shortest_path(self, u, v):
        """Retorna o custo e a sequência de nós do caminho mais curto entre u e v.

        Utiliza as matrizes pré-calculadas (dist_matrix, pred_matrix).

        Args:
            u: Nó de origem.
            v: Nó de destino.

        Returns:
            tuple: (custo, caminho) onde custo é o custo total do caminho
                   e caminho é uma lista de nós [u, ..., v].
                   Retorna (float("inf"), []) se não houver caminho.
        """
        if self.dist_matrix is None or self.pred_matrix is None:
            # print("Aviso: Matrizes de caminhos mínimos não calculadas/definidas.")
            # Tenta calcular on-demand usando Dijkstra para um par específico
            # return self.dijkstra(u, v)
            raise ValueError("Matrizes de caminhos mínimos não estão disponíveis. Execute o cálculo primeiro.")

        if u not in self.dist_matrix or v not in self.dist_matrix[u]:
            return float("inf"), [] # Origem ou destino não alcançável

        custo = self.dist_matrix[u].get(v, float("inf"))
        if custo == float("inf"):
            return float("inf"), []

        # Reconstruir caminho usando a matriz de predecessores
        caminho = []
        curr = v
        while curr is not None:
            caminho.append(curr)
            if curr == u:
                break
            # Verifica se u e curr existem nas matrizes antes de acessar
            if u not in self.pred_matrix or curr not in self.pred_matrix[u]:
                 print(f"Erro na reconstrução do caminho: Predecessor não encontrado para {curr} vindo de {u}")
                 return float("inf"), [] # Erro na matriz de predecessores
            curr = self.pred_matrix[u].get(curr)
            if curr is not None and curr not in self.vertices:
                 print(f"Erro na reconstrução do caminho: Predecessor inválido {curr}")
                 return float("inf"), []

        if not caminho or caminho[-1] != u:
             # Isso pode acontecer se u == v ou se houver um problema na pred_matrix
             if u == v:
                 return 0, [u]
             else:
                 print(f"Erro na reconstrução do caminho entre {u} e {v}. Caminho parcial: {caminho}")
                 # Tenta retornar o custo se disponível, mas caminho vazio indica problema
                 return custo, []

        return custo, caminho[::-1] # Inverte para ter u -> v

    def get_service_details(self, service_id):
        """Retorna os detalhes de um serviço específico a partir do service_map."""
        return self.service_map.get(service_id)

    def get_all_required_services(self):
        """Retorna um conjunto com os IDs de todos os serviços requeridos."""
        return set(self.service_map.keys())

    def calcular_distancias_predecessores_floyd_warshall(self):
        """Calcula as matrizes de distância e predecessores usando Floyd-Warshall.

        Este método preenche self.dist_matrix e self.pred_matrix.
        É computacionalmente intensivo (O(V^3)).
        """
        print("Calculando caminhos mínimos com Floyd-Warshall...")
        num_vertices = len(self.vertices)
        if num_vertices == 0:
            self.dist_matrix = {}
            self.pred_matrix = {}
            return

        # Mapeamento de ID de vértice para índice inteiro (0 a n-1) se necessário
        # Ou usar dicionários diretamente
        vertices_list = list(self.vertices)
        dist = {v: {w: float("inf") for w in self.vertices} for v in self.vertices}
        pred = {v: {w: None for w in self.vertices} for v in self.vertices}

        # Inicialização
        for v in self.vertices:
            dist[v][v] = 0
            pred[v][v] = v # Ou None, dependendo da convenção para reconstrução

        for u in self.adj:
            for v, custo in self.adj[u]:
                if custo < dist[u][v]: # Considera a aresta/arco de menor custo se houver múltiplos
                    dist[u][v] = custo
                    pred[u][v] = u

        # Iterações do Floyd-Warshall
        for k in vertices_list: # Vértice intermediário
            for i in vertices_list: # Origem
                for j in vertices_list: # Destino
                    if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                        novo_custo = dist[i][k] + dist[k][j]
                        if novo_custo < dist[i][j]:
                            dist[i][j] = novo_custo
                            # O predecessor de j no caminho i->j via k é o mesmo predecessor de j no caminho k->j
                            pred[i][j] = pred[k][j]

        self.dist_matrix = dist
        self.pred_matrix = pred
        print("Cálculo de Floyd-Warshall concluído.")

    # --- Métodos Adicionais (Exemplo: Dijkstra para um único par, se necessário) ---
    def dijkstra(self, origem, destino):
        """Calcula o caminho mais curto entre uma origem e um destino usando Dijkstra.

        Menos eficiente que usar Floyd-Warshall pré-calculado para múltiplos pares,
        mas útil se apenas um caminho for necessário ou como fallback.

        Args:
            origem: Nó de origem.
            destino: Nó de destino.

        Returns:
            tuple: (custo, caminho) ou (float("inf"), []) se não houver caminho.
        """
        if origem not in self.vertices or destino not in self.vertices:
            return float("inf"), []

        dist = {v: float("inf") for v in self.vertices}
        pred = {v: None for v in self.vertices}
        dist[origem] = 0
        pq = [(0, origem)] # Fila de prioridade (custo, vértice)

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                continue

            if u == destino:
                break # Encontrou o destino

            if u in self.adj:
                for v, custo_aresta in self.adj[u]:
                    if dist[u] + custo_aresta < dist[v]:
                        dist[v] = dist[u] + custo_aresta
                        pred[v] = u
                        heapq.heappush(pq, (dist[v], v))

        # Reconstruir caminho
        custo_final = dist[destino]
        if custo_final == float("inf"):
            return float("inf"), []

        caminho = []
        curr = destino
        while curr is not None:
            caminho.append(curr)
            if curr == origem:
                break
            curr = pred[curr]

        if not caminho or caminho[-1] != origem:
             if origem == destino:
                 return 0, [origem]
             else:
                 # Pode acontecer se o grafo for desconectado
                 return float("inf"), []

        return custo_final, caminho[::-1]

# Exemplo de uso (para teste)
if __name__ == '__main__':
    g = Grafo()
    # Adicionar elementos manualmente para teste
    g.deposito = 1
    g.capacidade = 100
    g.adicionar_aresta_nao_requerida(1, 2, 10)
    g.adicionar_aresta_nao_requerida(2, 3, 5)
    g.adicionar_arco_nao_requerido(1, 3, 12)
    g.adicionar_vertice_requerido(3, 20, 2, 1)
    g.service_map[1] = {"tipo": "N", "id": 3, "demanda": 20, "custo_servico": 2, "endpoints": (3, 3)}

    print("Vértices:", g.vertices)
    print("Adjacência:", g.adj)
    print("Serviços Requeridos (Nós):", g.requeridos_v)
    print("Mapa de Serviços:", g.service_map)

    # Calcular caminhos mínimos
    g.calcular_distancias_predecessores_floyd_warshall()

    # Testar get_shortest_path
    custo, caminho = g.get_shortest_path(1, 3)
    print(f"Caminho mais curto de 1 para 3: Custo={custo}, Caminho={caminho}")

    custo, caminho = g.get_shortest_path(3, 1)
    print(f"Caminho mais curto de 3 para 1: Custo={custo}, Caminho={caminho}") # Deve usar adjacências

    custo, caminho = g.get_shortest_path(1, 1)
    print(f"Caminho mais curto de 1 para 1: Custo={custo}, Caminho={caminho}")

