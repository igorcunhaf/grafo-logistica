import math
from collections import deque

def calcular_estatisticas(grafo):
    """Calcula e retorna um dicionário com as estatísticas do grafo."""

    # Calcula o número total de arestas e arcos (requeridos + não requeridos)
    total_arestas = len(grafo.arestas_nao_req) + len(grafo.requeridos_e)
    total_arcos = len(grafo.arcos_nao_req) + len(grafo.requeridos_a)

    stats = {
        'Vertices': len(grafo.vertices),
        'Arestas (Total)': total_arestas, 
        'Arcos (Total)': total_arcos,
        'Vertices requeridos': len(grafo.requeridos_v),
        'Arestas requeridas': len(grafo.requeridos_e),
        'Arcos requeridos': len(grafo.requeridos_a),
        'Densidade': calcular_densidade(grafo, total_arestas, total_arcos),
        'Componentes conectados': contar_componentes(grafo),
        'Grau minimo (saída)': calcular_graus(grafo, minimo=True),
        'Grau maximo (saída)': calcular_graus(grafo, minimo=False),
        # Adicionar graus de entrada se necessário
    }

    # Verifica se as matrizes já foram calculadas 
    if grafo.dist_matrix is None or grafo.pred_matrix is None:
        print("Calculando matrizes de caminhos mínimos (Floyd-Warshall) para estatísticas...")
        # Usa o método da própria classe Grafo que já está implementado
        grafo.calcular_distancias_predecessores_floyd_warshall()
        if grafo.dist_matrix is None: # Verifica se o cálculo falhou
             print("Erro: Falha ao calcular matrizes de caminhos mínimos.")
             stats["Caminho medio"] = "Erro"
             stats["Diametro"] = "Erro"
             stats["Intermediacao"] = "Erro"
             return stats

    # Usa as matrizes do objeto grafo
    dist_matrix_dict = grafo.dist_matrix
    pred_matrix_dict = grafo.pred_matrix

    stats["Caminho medio"] = caminho_medio(dist_matrix_dict)
    stats["Diametro"] = diametro(dist_matrix_dict)
    stats["Intermediacao"] = intermediacao(grafo, dist_matrix_dict)

    return stats

def calcular_densidade(g, total_arestas, total_arcos):
    """Calcula a densidade do grafo."""
    n = len(g.vertices)
    # Considera multigrafo: m é o número total de conexões direcionadas na lista de adj
    # Ou usa a soma total de arestas e arcos calculada anteriormente
    m = total_arestas + total_arcos
    # Densidade para grafos direcionados/mistos: m / (n * (n-1))
    return m / (n * (n - 1)) if n > 1 else 0

def contar_componentes(g):
    """Conta o número de componentes conectados (considerando grafo não direcionado)."""
    visitado = set()
    componentes = 0
    adj_undirected = {} # Cria uma adjacência não direcionada temporária

    for u, neighbors in g.adj.items():
        if u not in adj_undirected: adj_undirected[u] = set()
        for v, _ in neighbors:
            if v not in adj_undirected: adj_undirected[v] = set()
            adj_undirected[u].add(v)
            adj_undirected[v].add(u)

    # Adiciona vértices isolados
    for v in g.vertices:
         if v not in adj_undirected: adj_undirected[v] = set()

    def bfs(v_start):
        fila = deque([v_start])
        visitado.add(v_start)
        while fila:
            u_curr = fila.popleft()
            for viz in adj_undirected.get(u_curr, set()):
                if viz not in visitado:
                    visitado.add(viz)
                    fila.append(viz)

    for v_node in g.vertices:
        if v_node not in visitado:
            componentes += 1
            bfs(v_node)

    return componentes

def calcular_graus(g, minimo=True):
    """Calcula o grau de saída mínimo ou máximo dos vértices."""
    if not g.vertices:
        return 0
    graus_saida = {v: 0 for v in g.vertices}
    for u in g.adj:
        graus_saida[u] = len(g.adj[u]) # Grau de saída

    # Inclui vértices sem saída (grau 0)
    for v in g.vertices:
        if v not in graus_saida:
            graus_saida[v] = 0

    if not graus_saida:
         return 0

    return min(graus_saida.values()) if minimo else max(graus_saida.values())

def caminho_medio(dist_dict):
    """Calcula o caminho médio a partir da matriz de distâncias (dicionário)."""
    total = 0
    count = 0
    if not dist_dict: return 0

    for u in dist_dict:
        for v in dist_dict[u]:
            d = dist_dict[u][v]
            if d != float("inf") and u != v: # Considera apenas caminhos finitos entre nós distintos
                total += d
                count += 1
    return total / count if count > 0 else 0

def diametro(dist_dict):
    """Calcula o diâmetro do grafo a partir da matriz de distâncias (dicionário)."""
    max_dist = 0
    if not dist_dict: return 0

    for u in dist_dict:
        for v in dist_dict[u]:
            d = dist_dict[u][v]
            if d == float("inf"):
                # Se houver algum par não conectado, o diâmetro é infinito (ou indefinido)
                # Dependendo da definição, pode retornar infinito ou o maior caminho finito
                # Vamos retornar o maior caminho finito encontrado.
                continue
            if d > max_dist:
                max_dist = d
    return max_dist

def intermediacao(g, dist_dict):
    """Calcula a centralidade de intermediação para cada nó."""
    
    if not g.vertices or g.pred_matrix is None:
        print("Aviso: Matriz de predecessores não disponível para cálculo de intermediação.")
        return {v: 0 for v in g.vertices}

    count = {v: 0 for v in g.vertices}
    vertices_list = list(g.vertices)

    for s in vertices_list:
        for t in vertices_list:
            if s == t or dist_dict.get(s, {}).get(t, float("inf")) == float("inf"):
                continue

            # Reconstrói *um* caminho mínimo usando a matriz de predecessores do grafo
            path = []
            curr = t
            while curr is not None and curr != s:
                pred = g.pred_matrix.get(s, {}).get(curr)
                if pred is None:
                     # Caminho não pode ser reconstruído (pode acontecer se s->t existe mas pred não)
                     path = None # Indica falha na reconstrução
                     break
                path.append(pred) # Adiciona o predecessor
                curr = pred

            if path is not None:
                 # Remove s e t do caminho para contar apenas nós intermediários
                 intermediate_nodes = path[:-1] # Exclui 's' (último adicionado na reconstrução reversa)
                 for node in intermediate_nodes:
                     if node != s and node != t:
                         count[node] += 1

    return count

