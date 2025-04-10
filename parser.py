from grafo import Grafo

def ler_arquivo_dat(caminho):
    grafo = Grafo()

    with open(caminho, 'r') as f:
        linhas = f.readlines()

    # Encontrar seções
    index_reN = linhas.index('ReN.\tDEMAND\tS. COST\n')
    index_reE = next(i for i, linha in enumerate(linhas) if linha.startswith('ReE.'))
    index_reA = next(i for i, linha in enumerate(linhas) if linha.startswith('ReA.'))

    # Processar nós requeridos
    for linha in linhas[index_reN + 1 : index_reE]:
        partes = linha.strip().split()
        if len(partes) >= 1 and partes[0].startswith('N'):
            no = int(partes[0][1:])  # Remove o "N"
            grafo.adicionar_vertice_requerido(no)

    # Processar arestas requeridas
    for linha in linhas[index_reE + 2 : index_reA]:  # pula linha de cabeçalho
        partes = linha.strip().split()
        if len(partes) >= 6:
            try:
                u = int(partes[1])
                v = int(partes[2])
                custo = int(partes[3])
                demanda = int(partes[4])
                servico = int(partes[5])
                grafo.adicionar_aresta(u, v, custo, demanda, servico)
            except ValueError:
                continue  # pula linha mal formatada

    # Processar arcos requeridos
    for linha in linhas[index_reA + 2:]:  # pula linha de cabeçalho
        partes = linha.strip().split()
        if len(partes) >= 6:
            try:
                u = int(partes[1])
                v = int(partes[2])
                custo = int(partes[3])
                demanda = int(partes[4])
                servico = int(partes[5])
                grafo.adicionar_arco(u, v, custo, demanda, servico)
            except ValueError:
                continue

    return grafo
