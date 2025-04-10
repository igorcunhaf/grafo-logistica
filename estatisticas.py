import math
from collections import deque

def calcular_estatisticas(grafo):
    stats = {
        'Vertices': len(grafo.vertices),
        'Arestas': len(grafo.arestas),
        'Arcos': len(grafo.arcos),
        'Vertices requeridos': len(grafo.requeridos_v),
        'Arestas requeridas': len(grafo.requeridos_e),
        'Arcos requeridos': len(grafo.requeridos_a),
        'Densidade': calcular_densidade(grafo),
        'Componentes conectados': contar_componentes(grafo),
        'Grau minimo': calcular_graus(grafo, minimo=True),
        'Grau maximo': calcular_graus(grafo, minimo=False),
    }

    caminhos, predecessores = floyd_warshall(grafo)
    stats['Caminho medio'] = caminho_medio(caminhos)
    stats['Diametro'] = diametro(caminhos)
    stats['Intermediacao'] = intermediacao(grafo, caminhos)

    return stats

def calcular_densidade(g):
    n = len(g.vertices)
    m = len(g.arestas) + len(g.arcos)
    return m / (n * (n - 1)) if n > 1 else 0

def contar_componentes(g):
    visitado = set()
    componentes = 0

    def bfs(v):
        fila = deque([v])
        visitado.add(v)
        while fila:
            u = fila.popleft()
            for viz, _ in g.adj.get(u, []):
                if viz not in visitado:
                    visitado.add(viz)
                    fila.append(viz)

    for v in g.vertices:
        if v not in visitado:
            componentes += 1
            bfs(v)

    return componentes

def calcular_graus(g, minimo=True):
    graus = {v: 0 for v in g.vertices}
    for u in g.adj:
        for v, _ in g.adj[u]:
            graus[u] += 1
    return min(graus.values()) if minimo else max(graus.values())

def floyd_warshall(g):
    vertices = list(g.vertices)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    dist = [[math.inf]*n for _ in range(n)]
    pred = [[-1]*n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u in g.adj:
        for v, custo in g.adj[u]:
            i, j = idx[u], idx[v]
            dist[i][j] = custo
            pred[i][j] = u

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]

    return dist, pred

def caminho_medio(dist):
    total = count = 0
    for linha in dist:
        for d in linha:
            if d < math.inf and d > 0:
                total += d
                count += 1
    return total / count if count > 0 else 0

def diametro(dist):
    return max(d for linha in dist for d in linha if d < math.inf)

def intermediacao(g, dist):
    count = {v: 0 for v in g.vertices}
    vertices = list(g.vertices)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    for s in vertices:
        for t in vertices:
            if s == t: continue
            for v in vertices:
                if v == s or v == t: continue
                i, j, k = idx[s], idx[t], idx[v]
                if dist[i][j] == dist[i][k] + dist[k][j]:
                    count[v] += 1

    return count
