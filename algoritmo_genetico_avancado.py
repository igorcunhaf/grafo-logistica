import copy
import time
import random
from rota import Rota

def calcular_custo_rota_completa(grafo, rota_sequencia, deposito_id):
    """Calcula o custo total de uma rota dada sua sequência de serviços."""
    if not rota_sequencia:
        return 0, 0
    
    custo_total = 0
    demanda_total = 0
    current_node = deposito_id

    for service_id in rota_sequencia:
        detalhes = grafo.get_service_details(service_id)
        if not detalhes:
            return float("inf"), float("inf")

        u_servico, v_servico = detalhes["endpoints"]
        demanda_servico = detalhes["demanda"]
        custo_servico = detalhes["custo_servico"]

        custo_travessia, _ = grafo.get_shortest_path(current_node, u_servico)
        if custo_travessia == float("inf"):
            return float("inf"), float("inf")

        custo_total += custo_travessia + custo_servico
        demanda_total += demanda_servico
        current_node = v_servico

    custo_retorno, _ = grafo.get_shortest_path(current_node, deposito_id)
    if custo_retorno == float("inf"):
        return float("inf"), float("inf")

    custo_total += custo_retorno
    return custo_total, demanda_total

def avaliar_solucao(grafo, rotas_servicos):
    """Avalia uma solução completa e retorna o custo total."""
    custo_total = 0
    for rota in rotas_servicos:
        if rota:
            custo_rota, demanda_rota = calcular_custo_rota_completa(grafo, rota, grafo.deposito)
            if demanda_rota > grafo.capacidade:
                return float("inf")  # Solução inválida
            custo_total += custo_rota
    return custo_total

def aplicar_2opt_local(grafo, rota_servicos, deposito_id, capacidade):
    """Aplica 2-opt local em uma rota."""
    if len(rota_servicos) < 2:
        return rota_servicos, False
    
    melhor_rota = rota_servicos[:]
    custo_original, _ = calcular_custo_rota_completa(grafo, rota_servicos, deposito_id)
    melhor_custo = custo_original
    melhoria_encontrada = False
    
    for i in range(len(rota_servicos) - 1):
        for j in range(i + 1, len(rota_servicos)):
            nova_rota = rota_servicos[:i] + rota_servicos[i:j+1][::-1] + rota_servicos[j+1:]
            
            novo_custo, nova_demanda = calcular_custo_rota_completa(grafo, nova_rota, deposito_id)
            
            if nova_demanda <= capacidade and novo_custo < melhor_custo:
                melhor_rota = nova_rota
                melhor_custo = novo_custo
                melhoria_encontrada = True
    
    return melhor_rota, melhoria_encontrada

def busca_local_hibrida(grafo, rotas_servicos):
    """Aplica busca local híbrida em uma solução."""
    rotas_melhoradas = copy.deepcopy(rotas_servicos)
    melhoria_global = False
    
    # 1. Aplica 2-opt em cada rota
    for i in range(len(rotas_melhoradas)):
        if rotas_melhoradas[i]:
            nova_rota, melhoria = aplicar_2opt_local(grafo, rotas_melhoradas[i], grafo.deposito, grafo.capacidade)
            if melhoria:
                rotas_melhoradas[i] = nova_rota
                melhoria_global = True
    
    # 2. Tenta relocar serviços entre rotas
    for i in range(len(rotas_melhoradas)):
        if not rotas_melhoradas[i]:
            continue
        for pos in range(len(rotas_melhoradas[i])):
            servico = rotas_melhoradas[i][pos]
            
            # Remove o serviço da rota atual
            rota_sem_servico = rotas_melhoradas[i][:pos] + rotas_melhoradas[i][pos+1:]
            custo_original_i, _ = calcular_custo_rota_completa(grafo, rotas_melhoradas[i], grafo.deposito)
            custo_sem_servico, _ = calcular_custo_rota_completa(grafo, rota_sem_servico, grafo.deposito)
            
            melhor_economia = 0
            melhor_j = -1
            melhor_pos_j = -1
            
            # Testa inserir em outras rotas
            for j in range(len(rotas_melhoradas)):
                if i == j:
                    continue
                
                for pos_j in range(len(rotas_melhoradas[j]) + 1):
                    nova_rota_j = (rotas_melhoradas[j][:pos_j] + 
                                 [servico] + 
                                 rotas_melhoradas[j][pos_j:])
                    
                    custo_original_j, _ = calcular_custo_rota_completa(grafo, rotas_melhoradas[j], grafo.deposito)
                    novo_custo_j, nova_demanda_j = calcular_custo_rota_completa(grafo, nova_rota_j, grafo.deposito)
                    
                    if nova_demanda_j <= grafo.capacidade:
                        economia = (custo_original_i + custo_original_j) - (custo_sem_servico + novo_custo_j)
                        if economia > melhor_economia:
                            melhor_economia = economia
                            melhor_j = j
                            melhor_pos_j = pos_j
            
            # Aplica a melhor relocação encontrada
            if melhor_economia > 0.1:
                rotas_melhoradas[i] = rota_sem_servico
                rotas_melhoradas[melhor_j].insert(melhor_pos_j, servico)
                melhoria_global = True
                break
    
    return rotas_melhoradas, melhoria_global

def gerar_solucao_inteligente(grafo, todos_servicos):
    """Gera uma solução usando heurística do vizinho mais próximo."""
    servicos_restantes = set(todos_servicos)
    rotas = []
    
    while servicos_restantes:
        rota_atual = []
        demanda_atual = 0
        posicao_atual = grafo.deposito
        
        while servicos_restantes:
            melhor_servico = None
            menor_custo = float("inf")
            
            for servico_id in servicos_restantes:
                detalhes = grafo.get_service_details(servico_id)
                if not detalhes:
                    continue
                
                u, v = detalhes["endpoints"]
                demanda = detalhes["demanda"]
                custo_servico = detalhes["custo_servico"]
                
                if demanda_atual + demanda > grafo.capacidade:
                    continue
                
                # Custo de ir até o serviço
                custo_travessia, _ = grafo.get_shortest_path(posicao_atual, u)
                custo_total = custo_travessia + custo_servico
                
                if custo_total < menor_custo:
                    menor_custo = custo_total
                    melhor_servico = servico_id
            
            if melhor_servico is None:
                break
            
            # Adiciona o melhor serviço à rota
            detalhes = grafo.get_service_details(melhor_servico)
            rota_atual.append(melhor_servico)
            demanda_atual += detalhes["demanda"]
            posicao_atual = detalhes["endpoints"][1]
            servicos_restantes.remove(melhor_servico)
        
        if rota_atual:
            rotas.append(rota_atual)
    
    return rotas

def crossover_avancado(grafo, pai1, pai2):
    """Crossover mais sofisticado que preserva estruturas boas."""
    # Coleta todos os serviços
    todos_servicos_pai1 = []
    todos_servicos_pai2 = []
    
    for rota in pai1:
        todos_servicos_pai1.extend(rota)
    for rota in pai2:
        todos_servicos_pai2.extend(rota)
    
    if set(todos_servicos_pai1) != set(todos_servicos_pai2):
        return pai1
    
    # Crossover baseado em rotas: pega as melhores rotas de cada pai
    rotas_pai1_com_custo = []
    rotas_pai2_com_custo = []
    
    for rota in pai1:
        if rota:
            custo, _ = calcular_custo_rota_completa(grafo, rota, grafo.deposito)
            rotas_pai1_com_custo.append((rota, custo))
    
    for rota in pai2:
        if rota:
            custo, _ = calcular_custo_rota_completa(grafo, rota, grafo.deposito)
            rotas_pai2_com_custo.append((rota, custo))
    
    # Ordena rotas por custo
    rotas_pai1_com_custo.sort(key=lambda x: x[1])
    rotas_pai2_com_custo.sort(key=lambda x: x[1])
    
    # Pega as melhores rotas de cada pai
    rotas_filho = []
    servicos_incluidos = set()
    
    # Adiciona as melhores rotas alternando entre os pais
    todas_rotas = rotas_pai1_com_custo + rotas_pai2_com_custo
    todas_rotas.sort(key=lambda x: x[1])
    
    for rota, custo in todas_rotas:
        if not any(s in servicos_incluidos for s in rota):
            rotas_filho.append(rota)
            servicos_incluidos.update(rota)
    
    # Adiciona serviços faltantes
    servicos_faltantes = set(todos_servicos_pai1) - servicos_incluidos
    if servicos_faltantes:
        rota_faltantes = gerar_solucao_inteligente(grafo, list(servicos_faltantes))
        rotas_filho.extend(rota_faltantes)
    
    return rotas_filho

def mutar_avancado(grafo, solucao, taxa_mutacao=0.3):
    """Mutação mais agressiva com múltiplas estratégias."""
    if random.random() > taxa_mutacao:
        return solucao
    
    solucao_mutada = copy.deepcopy(solucao)
    
    # Aplica múltiplas mutações
    num_mutacoes = random.randint(1, 3)
    
    for _ in range(num_mutacoes):
        tipo_mutacao = random.choice([
            'swap_servicos', 'inverter_rota', 'mover_servico', 
            'dividir_rota', 'combinar_rotas', 'reordenar_rota'
        ])
        
        if tipo_mutacao == 'reordenar_rota':
            # Reordena uma rota usando vizinho mais próximo
            if solucao_mutada:
                rota_idx = random.randint(0, len(solucao_mutada) - 1)
                if solucao_mutada[rota_idx] and len(solucao_mutada[rota_idx]) > 2:
                    nova_rota = gerar_solucao_inteligente(grafo, solucao_mutada[rota_idx])
                    if nova_rota:
                        solucao_mutada[rota_idx] = nova_rota[0]
        
        elif tipo_mutacao == 'dividir_rota':
            # Divide uma rota grande em duas
            if solucao_mutada:
                rota_idx = random.randint(0, len(solucao_mutada) - 1)
                if solucao_mutada[rota_idx] and len(solucao_mutada[rota_idx]) > 3:
                    rota = solucao_mutada[rota_idx]
                    ponto_divisao = len(rota) // 2
                    nova_rota1 = rota[:ponto_divisao]
                    nova_rota2 = rota[ponto_divisao:]
                    
                    # Verifica se ambas as partes respeitam a capacidade
                    _, demanda1 = calcular_custo_rota_completa(grafo, nova_rota1, grafo.deposito)
                    _, demanda2 = calcular_custo_rota_completa(grafo, nova_rota2, grafo.deposito)
                    
                    if demanda1 <= grafo.capacidade and demanda2 <= grafo.capacidade:
                        solucao_mutada[rota_idx] = nova_rota1
                        solucao_mutada.append(nova_rota2)
        
        elif tipo_mutacao == 'combinar_rotas' and len(solucao_mutada) > 1:
            # Combina duas rotas pequenas
            rotas_pequenas = [(i, rota) for i, rota in enumerate(solucao_mutada) 
                            if rota and len(rota) <= 3]
            
            if len(rotas_pequenas) >= 2:
                idx1, rota1 = rotas_pequenas[0]
                idx2, rota2 = rotas_pequenas[1]
                
                rota_combinada = rota1 + rota2
                _, demanda_combinada = calcular_custo_rota_completa(grafo, rota_combinada, grafo.deposito)
                
                if demanda_combinada <= grafo.capacidade:
                    solucao_mutada[idx1] = rota_combinada
                    solucao_mutada[idx2] = []
        
        # Outras mutações existentes...
        elif tipo_mutacao == 'swap_servicos' and len(solucao_mutada) >= 2:
            rota1_idx = random.randint(0, len(solucao_mutada) - 1)
            rota2_idx = random.randint(0, len(solucao_mutada) - 1)
            
            if (rota1_idx != rota2_idx and 
                solucao_mutada[rota1_idx] and 
                solucao_mutada[rota2_idx]):
                
                pos1 = random.randint(0, len(solucao_mutada[rota1_idx]) - 1)
                pos2 = random.randint(0, len(solucao_mutada[rota2_idx]) - 1)
                
                solucao_mutada[rota1_idx][pos1], solucao_mutada[rota2_idx][pos2] = \
                    solucao_mutada[rota2_idx][pos2], solucao_mutada[rota1_idx][pos1]
    
    # Remove rotas vazias
    solucao_mutada = [rota for rota in solucao_mutada if rota]
    
    return solucao_mutada

def algoritmo_genetico_avancado(grafo, solucao_inicial, populacao_size=40, geracoes=300):
    """Algoritmo genético avançado com busca local híbrida."""
    start_time = time.time()
    
    todos_servicos = []
    for rota in solucao_inicial:
        todos_servicos.extend(rota)
    
    # Gera população inicial mais diversificada
    populacao = [solucao_inicial]
    
    # Adiciona soluções inteligentes
    for _ in range(populacao_size // 4):
        solucao_inteligente = gerar_solucao_inteligente(grafo, todos_servicos)
        populacao.append(solucao_inteligente)
    
    # Adiciona soluções aleatórias
    for _ in range(populacao_size - len(populacao)):
        servicos_embaralhados = todos_servicos[:]
        random.shuffle(servicos_embaralhados)
        
        rotas = []
        rota_atual = []
        demanda_atual = 0
        
        for servico_id in servicos_embaralhados:
            detalhes = grafo.get_service_details(servico_id)
            if not detalhes:
                continue
                
            demanda_servico = detalhes["demanda"]
            
            if demanda_atual + demanda_servico <= grafo.capacidade:
                rota_atual.append(servico_id)
                demanda_atual += demanda_servico
            else:
                if rota_atual:
                    rotas.append(rota_atual)
                rota_atual = [servico_id]
                demanda_atual = demanda_servico
        
        if rota_atual:
            rotas.append(rota_atual)
        
        populacao.append(rotas)
    
    melhor_solucao = solucao_inicial
    melhor_custo = avaliar_solucao(grafo, solucao_inicial)
    
    print(f"Iniciando algoritmo genético avançado. População: {populacao_size}, Gerações: {geracoes}")
    print(f"Custo inicial: {melhor_custo}")
    
    for geracao in range(geracoes):
        # Aplica busca local híbrida nas melhores soluções
        if geracao % 10 == 0:
            custos = [avaliar_solucao(grafo, sol) for sol in populacao]
            indices_melhores = sorted(range(len(custos)), key=lambda i: custos[i])[:populacao_size//4]
            
            for idx in indices_melhores:
                if custos[idx] != float("inf"):
                    solucao_melhorada, _ = busca_local_hibrida(grafo, populacao[idx])
                    populacao[idx] = solucao_melhorada
        
        # Avalia toda a população
        custos = []
        for solucao in populacao:
            custo = avaliar_solucao(grafo, solucao)
            custos.append(custo)
        
        # Encontra a melhor solução desta geração
        melhor_idx_geracao = custos.index(min(custos))
        melhor_custo_geracao = custos[melhor_idx_geracao]
        
        if melhor_custo_geracao < melhor_custo:
            melhor_custo = melhor_custo_geracao
            melhor_solucao = copy.deepcopy(populacao[melhor_idx_geracao])
            print(f"  Geração {geracao + 1}: Novo melhor custo: {melhor_custo}")
        
        # Seleção e reprodução
        nova_populacao = []
        
        # Elitismo mais forte (20% da população)
        indices_ordenados = sorted(range(len(custos)), key=lambda i: custos[i])
        elite_size = populacao_size // 5
        for i in range(elite_size):
            if custos[indices_ordenados[i]] != float("inf"):
                nova_populacao.append(copy.deepcopy(populacao[indices_ordenados[i]]))
        
        # Gera o resto da população
        while len(nova_populacao) < populacao_size:
            # Seleção por torneio maior
            torneio_size = 5
            pai1_idx = min(random.sample(range(len(populacao)), torneio_size), 
                          key=lambda i: custos[i])
            pai2_idx = min(random.sample(range(len(populacao)), torneio_size), 
                          key=lambda i: custos[i])
            
            # Crossover avançado
            filho = crossover_avancado(grafo, populacao[pai1_idx], populacao[pai2_idx])
            
            # Mutação mais agressiva
            filho = mutar_avancado(grafo, filho, taxa_mutacao=0.4)
            
            nova_populacao.append(filho)
        
        populacao = nova_populacao
    
    tempo_execucao = time.time() - start_time
    print(f"Algoritmo genético avançado concluído. Melhor custo: {melhor_custo}, Tempo: {tempo_execucao:.2f}s")
    
    return melhor_solucao, melhor_custo, tempo_execucao

def converter_para_objetos_rota(grafo, rotas_servicos):
    """Converte lista de rotas de serviços para objetos Rota."""
    rotas_objetos = []
    
    for idx, rota_servicos in enumerate(rotas_servicos):
        if not rota_servicos:
            continue
            
        rota_obj = Rota(idx + 1, grafo.deposito)
        
        current_node = grafo.deposito
        for service_id in rota_servicos:
            detalhes = grafo.get_service_details(service_id)
            u_servico, v_servico = detalhes["endpoints"]
            
            if current_node != u_servico:
                custo_travessia_ate_servico, caminho_ate_servico = grafo.get_shortest_path(current_node, u_servico)
            else:
                custo_travessia_ate_servico = 0
                caminho_ate_servico = [current_node]
            
            demanda_servico = detalhes["demanda"]
            custo_servico = detalhes["custo_servico"]
            rota_obj.adicionar_visita_servico(
                service_id, u_servico, v_servico, demanda_servico, 
                custo_servico, custo_travessia_ate_servico, caminho_ate_servico
            )
            current_node = v_servico
        
        if current_node != grafo.deposito:
            custo_retorno, caminho_retorno = grafo.get_shortest_path(current_node, grafo.deposito)
            rota_obj.adicionar_retorno_deposito(custo_retorno, caminho_retorno)
        
        rotas_objetos.append(rota_obj)
    
    return rotas_objetos

def otimizar_com_algoritmo_genetico_avancado(grafo, rotas_iniciais):
    """Função principal que aplica algoritmo genético avançado."""
    # Converte rotas iniciais para formato de lista de serviços
    rotas_servicos = []
    for r in rotas_iniciais:
        servicos_na_rota = []
        for item in r.sequencia_visitas_detalhada:
            if item[0] == 'S':
                servicos_na_rota.append(item[1])
        if servicos_na_rota:
            rotas_servicos.append(servicos_na_rota)
    
    # Aplica algoritmo genético avançado
    melhor_solucao, melhor_custo, tempo_execucao = algoritmo_genetico_avancado(
        grafo, rotas_servicos, populacao_size=50, geracoes=500
    )
    
    # Converte de volta para objetos Rota
    rotas_melhoradas = converter_para_objetos_rota(grafo, melhor_solucao)
    
    return rotas_melhoradas, melhor_custo, tempo_execucao

