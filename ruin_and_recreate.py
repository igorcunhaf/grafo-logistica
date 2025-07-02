import random
import copy
from rota import Rota

def inserir_servico_na_melhor_posicao(rotas, grafo, servico, capacidade):
    """Insere o serviço na melhor posição possível em qualquer rota (ou cria nova)"""
    melhor_custo = float('inf')
    melhor_insercao = None
    for idx_rota, rota in enumerate(rotas):
        servicos_ids = [item[1] for item in rota.sequencia_visitas_detalhada if item[0] == 'S']
        for pos in range(len(servicos_ids) + 1):
            nova_seq = servicos_ids[:pos] + [servico] + servicos_ids[pos:]
            custo, demanda = calcular_custo_rota_completa(grafo, nova_seq, grafo.deposito)
            if demanda <= capacidade and custo < melhor_custo:
                melhor_custo = custo
                melhor_insercao = (idx_rota, pos, nova_seq)
    # Se não couber em nenhuma rota, cria nova rota
    if melhor_insercao is None:
        nova_rota = Rota(len(rotas) + 1, grafo.deposito)
        nova_seq = [servico]
        custo, demanda = calcular_custo_rota_completa(grafo, nova_seq, grafo.deposito)
        if demanda <= capacidade:
            return rotas + [nova_rota], True
        else:
            return rotas, False
    # Faz a inserção na melhor rota
    idx_rota, pos, nova_seq = melhor_insercao
    nova_rota_obj = Rota(idx_rota + 1, grafo.deposito)
    current_node = grafo.deposito
    for s in nova_seq:
        detalhes = grafo.get_service_details(s)
        u, v = detalhes["endpoints"]
        if current_node != u:
            custo_travessia, caminho = grafo.get_shortest_path(current_node, u)
        else:
            custo_travessia = 0
            caminho = [current_node]
        nova_rota_obj.adicionar_visita_servico(s, u, v, detalhes["demanda"], detalhes["custo_servico"], custo_travessia, caminho)
        current_node = v
    if current_node != grafo.deposito:
        custo_ret, caminho_ret = grafo.get_shortest_path(current_node, grafo.deposito)
        nova_rota_obj.adicionar_retorno_deposito(custo_ret, caminho_ret)
    rotas[idx_rota] = nova_rota_obj
    return rotas, True

def calcular_custo_rota_completa(grafo, rota_sequencia, deposito_id):
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
        custo_travessia_para_servico, _ = grafo.get_shortest_path(current_node, u_servico)
        if custo_travessia_para_servico == float("inf"):
            return float("inf"), float("inf")
        custo_total += custo_travessia_para_servico + custo_servico
        demanda_total += demanda_servico
        current_node = v_servico
    custo_retorno_deposito, _ = grafo.get_shortest_path(current_node, deposito_id)
    if custo_retorno_deposito == float("inf"):
        return float("inf"), float("inf")
    custo_total += custo_retorno_deposito
    return custo_total, demanda_total

def ruin_and_recreate(grafo, rotas, capacidade, porc_remove=0.35, max_iter=50):
    """Ruin & Recreate simples"""
    melhor_rotas = copy.deepcopy(rotas)
    melhor_custo = sum(r.custo_acumulado for r in melhor_rotas)
    todos_servicos = []
    for rota in melhor_rotas:
        todos_servicos += [item[1] for item in rota.sequencia_visitas_detalhada if item[0] == 'S']
    for iter in range(max_iter):
        num_remove = max(1, int(porc_remove * len(todos_servicos)))
        servicos_remover = random.sample(todos_servicos, num_remove)
        # Remove serviços das rotas
        novas_rotas = []
        for rota in melhor_rotas:
            nova_rota = copy.deepcopy(rota)
            nova_rota.sequencia_visitas_detalhada = [item for item in rota.sequencia_visitas_detalhada if item[0] != 'S' or item[1] not in servicos_remover]
            if any(item[0] == 'S' for item in nova_rota.sequencia_visitas_detalhada):
                novas_rotas.append(nova_rota)
        # Reinsere cada serviço removido na melhor posição possível
        sucesso = True
        for s in servicos_remover:
            novas_rotas, ok = inserir_servico_na_melhor_posicao(novas_rotas, grafo, s, capacidade)
            if not ok:
                sucesso = False
                break
        # Se deu tudo certo, calcula custo
        if sucesso:
            custo_novo = sum(r.custo_acumulado for r in novas_rotas)
            if custo_novo < melhor_custo:
                melhor_custo = custo_novo
                melhor_rotas = copy.deepcopy(novas_rotas)
                print(f"[R&R] Iter {iter+1} melhorou: custo {custo_novo}")
    return melhor_rotas, melhor_custo

