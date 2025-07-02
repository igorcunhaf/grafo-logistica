
def calcula_custo_rota(sequencia, grafo):
    custo = 0
    deposito_id = grafo.deposito  # Pega o depósito real
    for i in range(len(sequencia) - 1):
        atual = sequencia[i]
        prox = sequencia[i + 1]

        def tradutor(no):
            # Converte 0 para deposito_id real!
            if no == 0:
                return deposito_id
            return no

        # Se ambos são visitas de serviço ou depósito, pega custo do grafo
        if atual[0] in ['D', 'S'] and prox[0] in ['D', 'S']:
            if atual[0] == 'D':
                no1 = tradutor(atual[1])
            else:
                no1 = atual[2]
            if prox[0] == 'D':
                no2 = tradutor(prox[1])
            else:
                no2 = prox[2]
            custo += grafo.dist_matrix[no1][no2]
        elif atual[0] == 'S' and prox[0] == 'T':
            no1 = atual[3]
            no2 = tradutor(prox[1])
            custo += grafo.dist_matrix[no1][no2]
        elif atual[0] == 'T' and prox[0] == 'T':
            custo += grafo.dist_matrix[atual[1]][tradutor(prox[1])]
        elif atual[0] == 'T' and prox[0] == 'S':
            custo += grafo.dist_matrix[atual[1]][prox[2]]
        elif atual[0] == 'T' and prox[0] == 'D':
            custo += grafo.dist_matrix[atual[1]][tradutor(prox[1])]
    return custo


def two_opt(sequencia, grafo):
    print("[LOG] Entrou no two_opt")
    melhor = sequencia[:]
    melhor_custo = calcula_custo_rota(melhor, grafo)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, len(melhor) - 2):
            for j in range(i + 1, len(melhor)):
                if j - i == 1: continue
                nova = melhor[:]
                nova[i:j] = melhor[j-1:i-1:-1]
                novo_custo = calcula_custo_rota(nova, grafo)
                if novo_custo < melhor_custo:
                    print(f"[LOG] 2-opt melhorou: custo {melhor_custo} -> {novo_custo}")
                    melhor = nova
                    melhor_custo = novo_custo
                    melhorou = True
    print("[LOG] Saiu do two_opt")
    return melhor

def pode_inserir(rota, tarefa, capacidade_maxima, grafo):
    # tarefa deve ser uma tupla ('S', id_serviço, u, v)
    service_id = tarefa[1]
    demanda_tarefa = grafo.service_map[service_id]["demanda"]
    return rota.demanda_acumulada + demanda_tarefa <= capacidade_maxima

def relocate(rotas, grafo, capacidade_maxima):
    print("[LOG] Entrou no relocate")
    melhorou = True
    while melhorou:
        melhorou = False
        for i, rota_a in enumerate(rotas):
            for j, rota_b in enumerate(rotas):
                if i == j:
                    continue
                for idx, tarefa in enumerate(rota_a.sequencia_visitas_detalhada[1:-1]):  # ignora início e fim
                    if tarefa[0] != 'S':
                        continue
                    if pode_inserir(rota_b, tarefa, capacidade_maxima, grafo):
                        nova_a = rota_a.sequencia_visitas_detalhada[:idx] + rota_a.sequencia_visitas_detalhada[idx+1:]
                        nova_b = rota_b.sequencia_visitas_detalhada[:-1] + [tarefa] + [rota_b.sequencia_visitas_detalhada[-1]]
                        custo_antigo = calcula_custo_rota(rota_a.sequencia_visitas_detalhada, grafo) + calcula_custo_rota(rota_b.sequencia_visitas_detalhada, grafo)
                        custo_novo = calcula_custo_rota(nova_a, grafo) + calcula_custo_rota(nova_b, grafo)
                        if custo_novo < custo_antigo:
                            print(f"[LOG] Relocate: moveu serviço {tarefa[1]} da rota {i} para {j}")
                            rota_a.sequencia_visitas_detalhada = nova_a
                            rota_b.sequencia_visitas_detalhada = nova_b
                            melhorou = True
                            # Após cada alteração, atualizar custo e demanda acumulada
                            if hasattr(rota_a, "atualizar_demanda_custo"):
                                rota_a.atualizar_demanda_custo(grafo)
                            if hasattr(rota_b, "atualizar_demanda_custo"):
                                rota_b.atualizar_demanda_custo(grafo)
                            break
                if melhorou:
                    break
            if melhorou:
                break
    print("[LOG] Saiu do relocate")
    return rotas


def swap(rotas, grafo, capacidade_maxima):
    print("[LOG] Entrou no swap")
    melhorou = True
    while melhorou:
        melhorou = False
        for i, rota_a in enumerate(rotas):
            for j, rota_b in enumerate(rotas):
                if i == j:
                    continue
                for idx_a, tarefa_a in enumerate(rota_a.sequencia_visitas_detalhada[1:-1]):
                    if tarefa_a[0] != 'S':
                        continue
                    for idx_b, tarefa_b in enumerate(rota_b.sequencia_visitas_detalhada[1:-1]):
                        if tarefa_b[0] != 'S':
                            continue
                        # Calcule demandas envolvidas
                        demanda_a = grafo.service_map[tarefa_a[1]]["demanda"]
                        demanda_b = grafo.service_map[tarefa_b[1]]["demanda"]
                        nova_demanda_a = rota_a.demanda_acumulada - demanda_a + demanda_b
                        nova_demanda_b = rota_b.demanda_acumulada - demanda_b + demanda_a
                        if nova_demanda_a <= capacidade_maxima and nova_demanda_b <= capacidade_maxima:
                            # Testa troca
                            nova_a = rota_a.sequencia_visitas_detalhada[:]
                            nova_b = rota_b.sequencia_visitas_detalhada[:]
                            nova_a[idx_a] = tarefa_b
                            nova_b[idx_b] = tarefa_a
                            custo_antigo = calcula_custo_rota(rota_a.sequencia_visitas_detalhada, grafo) + calcula_custo_rota(rota_b.sequencia_visitas_detalhada, grafo)
                            custo_novo = calcula_custo_rota(nova_a, grafo) + calcula_custo_rota(nova_b, grafo)
                            if custo_novo < custo_antigo:
                                print(f"[LOG] SWAP: trocou {tarefa_a[1]} da rota {i} com {tarefa_b[1]} da rota {j}")
                                rota_a.sequencia_visitas_detalhada = nova_a
                                rota_b.sequencia_visitas_detalhada = nova_b
                                if hasattr(rota_a, "atualizar_demanda_custo"):
                                    rota_a.atualizar_demanda_custo(grafo)
                                if hasattr(rota_b, "atualizar_demanda_custo"):
                                    rota_b.atualizar_demanda_custo(grafo)
                                melhorou = True
                                break
                    if melhorou:
                        break
                if melhorou:
                    break
            if melhorou:
                break
    print("[LOG] Saiu do swap")
    return rotas
