import copy
import time
from rota import Rota

def calcular_custo_rota_completa(grafo, rota_sequencia, deposito_id):
    """Calcula o custo total de uma rota dada sua sequência de nós e serviços.
    Isso é necessário para avaliar o impacto de movimentos na busca local.
    """
    custo_total = 0
    demanda_total = 0
    current_node = deposito_id
    servicos_atendidos_nesta_rota = set()

    # A sequência detalhada inclui (Tipo, ID, u, v) para serviços e (Tipo, Nó) para travessias/depósito
    # Vamos iterar sobre a sequência para calcular o custo e demanda.
    # Ignoramos os nós de travessia ('T') na sequência, pois o custo já é coberto pelo shortest_path
    # entre os nós de serviço e depósito.

    # A rota sempre começa e termina no depósito.
    # A sequência é algo como [('D', 0), ('S', id1, u1, v1), ('T', no_travessia), ..., ('S', id2, u2, v2), ('D', 0)]

    # A forma mais robusta de calcular o custo é iterar pelos nós visitados e somar os custos de travessia
    # e os custos de serviço.

    # Vamos simplificar e assumir que a rota é uma sequência de nós a serem visitados
    # e que os serviços são atendidos quando o veículo passa por seus endpoints.

    # Para a busca local, precisamos de uma forma de recalcular o custo de uma rota modificada.
    # A classe Rota já tem custo_acumulado e demanda_acumulada.
    # O problema é que a sequência_visitas_detalhada inclui nós de travessia que não são nós de serviço.

    # Vamos re-simular a rota para calcular o custo e demanda de forma precisa.
    # A sequência_visitas_detalhada é uma lista de tuplas.
    # Ex: [('D', 0), ('S', service_id, u, v), ('T', node), ..., ('D', 0)]

    # Reconstruir a sequência de nós que o veículo realmente visita (sem os detalhes de serviço/depósito)
    # e os serviços que são atendidos.
    
    # A forma mais simples é ter uma lista de (tipo, id_servico_ou_no, no_origem, no_destino)
    # e recalcular os custos de travessia entre eles.

    # Para o 2-opt, a rota é uma sequência de serviços. O custo é o custo de ir de um serviço para o próximo.
    # E o custo de serviço em si.

    # Vamos redefinir o que é uma rota para o 2-opt: uma lista de service_ids na ordem em que são visitados.
    # E o custo é calculado com base nisso.

    # Se a rota_sequencia for uma lista de service_ids:
    current_node_for_cost = deposito_id
    current_demanda = 0
    current_cost = 0
    servicos_visitados_ids = set()

    for service_id in rota_sequencia:
        detalhes = grafo.get_service_details(service_id)
        if not detalhes:
            return float("inf"), float("inf") # Erro

        u_servico, v_servico = detalhes["endpoints"]
        demanda_servico = detalhes["demanda"]
        custo_servico = detalhes["custo_servico"]

        # Custo de travessia do nó atual até o início do serviço
        custo_travessia_para_servico, _ = grafo.get_shortest_path(current_node_for_cost, u_servico)
        if custo_travessia_para_servico == float("inf"):
            return float("inf"), float("inf") # Inalcançável

        current_cost += custo_travessia_para_servico + custo_servico
        current_demanda += demanda_servico
        current_node_for_cost = v_servico # O último nó visitado é o final do serviço
        servicos_visitados_ids.add(service_id)

    # Custo de retorno ao depósito
    custo_retorno_deposito, _ = grafo.get_shortest_path(current_node_for_cost, deposito_id)
    if custo_retorno_deposito == float("inf"):
        return float("inf"), float("inf") # Inalcançável

    current_cost += custo_retorno_deposito

    return current_cost, current_demanda

def melhorar_solucao_2opt(grafo, rotas_iniciais, max_iteracoes=100):
    """Aplica a heurística 2-opt para melhorar as rotas existentes.

    Args:
        grafo (Grafo): Objeto grafo com os dados da instância.
        rotas_iniciais (list): Lista de objetos Rota da solução inicial.
        max_iteracoes (int): Número máximo de iterações para a busca local.

    Returns:
        tuple: (rotas_melhoradas, custo_total_melhorado, tempo_execucao)
    """
    start_time = time.time()
    
    # Converter rotas_iniciais para um formato mais fácil de manipular para 2-opt
    # Uma rota será uma lista de service_ids na ordem de visita.
    rotas_para_otimizar = []
    for r in rotas_iniciais:
        servicos_na_rota = []
        for item in r.sequencia_visitas_detalhada:
            if item[0] == 'S':
                servicos_na_rota.append(item[1]) # Adiciona o service_id
        if servicos_na_rota: # Adiciona apenas rotas que realmente atendem serviços
            rotas_para_otimizar.append(servicos_na_rota)

    melhor_custo_total = sum(r.custo_acumulado for r in rotas_iniciais)
    melhor_solucao_2opt = copy.deepcopy(rotas_para_otimizar)

    print(f"Iniciando 2-opt. Custo inicial: {melhor_custo_total}, Rotas: {len(rotas_para_otimizar)}")

    for iteracao in range(max_iteracoes):
        melhoria_encontrada_nesta_iteracao = False
        for idx_rota, rota_servicos in enumerate(rotas_para_otimizar):
            if len(rota_servicos) < 2: # Não é possível aplicar 2-opt em rotas com menos de 2 serviços
                continue

            for i in range(len(rota_servicos) - 1):
                for j in range(i + 1, len(rota_servicos)):
                    # Cria uma nova rota invertendo o segmento entre i e j
                    nova_rota_servicos = rota_servicos[:i] + rota_servicos[i:j+1][::-1] + rota_servicos[j+1:]

                    # Calcula o custo e demanda da nova rota
                    novo_custo_rota, nova_demanda_rota = calcular_custo_rota_completa(grafo, nova_rota_servicos, grafo.deposito)

                    # Verifica se a nova rota é válida (não excede capacidade) e se é melhor
                    custo_rota_original, _ = calcular_custo_rota_completa(grafo, rota_servicos, grafo.deposito)
                    if nova_demanda_rota <= grafo.capacidade and novo_custo_rota < custo_rota_original:
                        # Aplica a melhoria
                        rotas_para_otimizar[idx_rota] = nova_rota_servicos
                        melhoria_encontrada_nesta_iteracao = True
                        # Atualiza o custo total da solução
                        # Recalcula o custo total de todas as rotas após a melhoria
                        melhor_custo_total = sum(calcular_custo_rota_completa(grafo, r, grafo.deposito)[0] for r in rotas_para_otimizar)
                        melhor_solucao_2opt = copy.deepcopy(rotas_para_otimizar)
                        print(f"  Melhoria 2-opt na rota {idx_rota+1} (segmento {i}-{j}). Custo original da rota: {custo_rota_original}, Novo custo da rota: {novo_custo_rota}. Novo custo total da solução: {melhor_custo_total}")
                        # Não quebra aqui, continua buscando melhorias na mesma rota

        if not melhoria_encontrada_nesta_iteracao:
            print(f"Nenhuma melhoria 2-opt encontrada na iteração {iteracao + 1}. Parando a busca local.")
            break

    # Converter de volta para objetos Rota
    rotas_melhoradas = []
    for idx, rota_servicos in enumerate(melhor_solucao_2opt):
        rota_obj = Rota(idx + 1, grafo.deposito)
        
        # Reconstruir a rota com os serviços otimizados
        current_node = grafo.deposito
        for service_id in rota_servicos:
            detalhes = grafo.get_service_details(service_id)
            u_servico, v_servico = detalhes["endpoints"]
            
            # Adicionar caminho até o serviço
            if current_node != u_servico:
                custo_travessia_ate_servico, caminho_ate_servico = grafo.get_shortest_path(current_node, u_servico)
            else:
                custo_travessia_ate_servico = 0
                caminho_ate_servico = [current_node]
            
            # Adicionar o serviço
            demanda_servico = detalhes["demanda"]
            custo_servico = detalhes["custo_servico"]
            rota_obj.adicionar_visita_servico(service_id, u_servico, v_servico, demanda_servico, custo_servico, custo_travessia_ate_servico, caminho_ate_servico)
            current_node = v_servico
        
        # Retornar ao depósito
        if current_node != grafo.deposito:
            custo_retorno, caminho_retorno = grafo.get_shortest_path(current_node, grafo.deposito)
            rota_obj.adicionar_retorno_deposito(custo_retorno, caminho_retorno)
        
        rotas_melhoradas.append(rota_obj)

    tempo_execucao = time.time() - start_time
    custo_total_final = sum(r.custo_acumulado for r in rotas_melhoradas)
    
    print(f"2-opt concluído. Custo final: {custo_total_final}, Tempo: {tempo_execucao:.2f}s")
    
    return rotas_melhoradas, custo_total_final, tempo_execucao
