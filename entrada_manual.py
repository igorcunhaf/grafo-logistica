from grafo import Grafo

def ler_dados_via_input():
    print("=== Entrada manual de dados do grafo ===")

    capacidade = int(input("Digite a capacidade dos veículos: "))
    veiculos = int(input("Digite o número de veículos disponíveis: "))

    num_vertices = int(input("Digite o número total de vértices: "))

    grafo = Grafo()

    # entrada de vértices requeridos (opcional)
    add_vr = input("Deseja adicionar vértices requeridos? (s/n): ").strip().lower()
    if add_vr == 's':
        num_vr = int(input("Quantos vértices requeridos deseja informar? "))
        for _ in range(num_vr):
            v = int(input("  Vértice requerido: "))
            grafo.adicionar_vertice_requerido(v)

    num_arestas = int(input("Digite o número de arestas bidirecionais (ruas de mão dupla): "))
    for i in range(num_arestas):
        print(f"Aresta {i + 1}:")
        u = int(input("  Vértice origem: "))
        v = int(input("  Vértice destino: "))
        custo = float(input("  Custo (peso): "))
        demanda = int(input("  Demanda (0 se não for requerida): "))
        servico = demanda > 0
        grafo.adicionar_aresta(u, v, custo, demanda, servico)

    num_arcos = int(input("Digite o número de arcos direcionados (ruas de mão única): "))
    for i in range(num_arcos):
        print(f"Arco {i + 1}:")
        u = int(input("  Vértice origem: "))
        v = int(input("  Vértice destino: "))
        custo = float(input("  Custo (peso): "))
        demanda = int(input("  Demanda (0 se não for requerido): "))
        servico = demanda > 0
        grafo.adicionar_arco(u, v, custo, demanda, servico)

    print("\nDados inseridos com sucesso.")
    return grafo
