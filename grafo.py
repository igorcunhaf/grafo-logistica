class Grafo:
    def __init__(self):
        self.vertices = set()
        self.arestas = []  # (u, v, custo)
        self.arcos = []    # (u, v, custo)
        self.requeridos_v = set()
        self.requeridos_e = []  # (u, v, custo, demanda, servico)
        self.requeridos_a = []  # (u, v, custo, demanda, servico)
        self.adj = dict()

    def adicionar_vertice_requerido(self, v):
        self.vertices.add(v)
        self.requeridos_v.add(v)

    def adicionar_aresta(self, u, v, custo, demanda, servico):
        self.arestas.append((u, v, custo))
        self.vertices.update([u, v])
        self.requeridos_e.append((u, v, custo, demanda, servico))
        self._add_adj(u, v, custo)
        self._add_adj(v, u, custo)

    def adicionar_arco(self, u, v, custo, demanda, servico):
        self.arcos.append((u, v, custo))
        self.vertices.update([u, v])
        self.requeridos_a.append((u, v, custo, demanda, servico))
        self._add_adj(u, v, custo)

    def _add_adj(self, u, v, custo):
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append((v, custo))
