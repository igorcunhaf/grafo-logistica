import math
import time

from rota import Rota # Importa a classe Rota do novo módulo


def construir_solucao_path_scanning(grafo):
    """Constrói uma solução inicial usando a heurística Path-Scanning.

    Args:
        grafo (Grafo): Objeto grafo populado com dados da instância e caminhos mínimos.

    Returns:
        tuple: (rotas_finais, custo_total, tempo_execucao)
               rotas_finais: Lista de objetos Rota.
               custo_total: Custo total da solução.
               tempo_execucao: Tempo gasto (em segundos) para construir a solução.
    """
    start_time = time.time()

    if grafo.dist_matrix is None or grafo.pred_matrix is None:
        print("Calculando matrizes de caminhos mínimos (Floyd-Warshall) antes de iniciar Path-Scanning...")
        grafo.calcular_distancias_predecessores_floyd_warshall()
        if grafo.dist_matrix is None:
             raise RuntimeError("Falha ao calcular as matrizes de caminhos mínimos.")

    # Usa uma cópia para não modificar o original no objeto grafo, se houver
    servicos_nao_atendidos = grafo.get_all_required_services().copy()
    rotas_finais = []
    id_proxima_rota = 1
    custo_total_solucao = 0

    print(f"Iniciando Path-Scanning com {len(servicos_nao_atendidos)} serviços requeridos.")

    while servicos_nao_atendidos:
        rota_atual = Rota(id_proxima_rota, grafo.deposito)
        localizacao_atual = grafo.deposito
        # print(f"\nIniciando Rota {id_proxima_rota} a partir do depósito {localizacao_atual}")

        while True:
            melhor_servico_id = -1
            menor_custo_insercao = float("inf")
            melhor_caminho = []
            melhor_custo_travessia = float("inf")
            melhor_detalhes_servico = None

            # print(f"  Buscando próximo serviço. {len(servicos_nao_atendidos)} restantes. Local: {localizacao_atual}")
            for service_id in servicos_nao_atendidos:
                detalhes = grafo.get_service_details(service_id)
                if not detalhes:
                    # print(f"Aviso: Detalhes não encontrados para service_id {service_id}. Pulando.")
                    continue

                demanda_servico = detalhes["demanda"]
                no_inicio_servico = detalhes["endpoints"][0]

                if not rota_atual.verificar_capacidade(demanda_servico, grafo.capacidade):
                    # print(f"    Serviço {service_id} excede capacidade ({rota_atual.demanda_acumulada}+{demanda_servico} > {grafo.capacidade}).")
                    continue

                custo_trav, caminho = grafo.get_shortest_path(localizacao_atual, no_inicio_servico)

                if custo_trav == float("inf"):
                    # print(f"    Serviço {service_id} inalcançável de {localizacao_atual}.")
                    continue

                custo_insercao = custo_trav

                if custo_insercao < menor_custo_insercao:
                    # print(f"    Novo melhor serviço encontrado: {service_id} com custo {custo_insercao}")
                    menor_custo_insercao = custo_insercao
                    melhor_servico_id = service_id
                    melhor_caminho = caminho
                    melhor_custo_travessia = custo_trav
                    melhor_detalhes_servico = detalhes

            if melhor_servico_id != -1:
                # print(f"  Adicionando serviço {melhor_servico_id} à rota {id_proxima_rota}.")
                u, v = melhor_detalhes_servico["endpoints"]
                demanda = melhor_detalhes_servico["demanda"]
                custo_servico = melhor_detalhes_servico["custo_servico"]
                caminho_para_adicionar = melhor_caminho[1:] if len(melhor_caminho) > 1 else []

                rota_atual.adicionar_visita_servico(
                    melhor_servico_id,
                    u, v,
                    demanda,
                    custo_servico,
                    melhor_custo_travessia,
                    caminho_para_adicionar
                )

                localizacao_atual = rota_atual.get_ultimo_no()
                # print(f"    Serviço {melhor_servico_id} adicionado. Localização atual: {localizacao_atual}. Demanda: {rota_atual.demanda_acumulada}")
                servicos_nao_atendidos.remove(melhor_servico_id)
                # print(f"    Serviço {melhor_servico_id} removido da lista. {len(servicos_nao_atendidos)} restantes.")
            else:
                # print(f"  Nenhum serviço viável encontrado para adicionar à rota {id_proxima_rota}.")
                break

        # print(f"Finalizando Rota {id_proxima_rota}. Retornando ao depósito {grafo.deposito} de {localizacao_atual}.")
        custo_retorno, caminho_retorno = grafo.get_shortest_path(localizacao_atual, grafo.deposito)
        if custo_retorno == float("inf"):
             print(f"Alerta: Não foi possível encontrar caminho de retorno ao depósito para a rota {rota_atual.id_rota} a partir do nó {localizacao_atual}.")
             if rota_atual.sequencia_visitas_detalhada[-1][0] != "D":
                 rota_atual.sequencia_visitas_detalhada.append(("D", 0))
        else:
             caminho_retorno_adicionar = caminho_retorno[1:] if len(caminho_retorno) > 1 else []
             rota_atual.adicionar_retorno_deposito(custo_retorno, caminho_retorno_adicionar)

        if rota_atual.servicos_atendidos:
            # print(f"Rota {id_proxima_rota} finalizada com {len(rota_atual.servicos_atendidos)} serviços. Custo: {rota_atual.custo_acumulado}")
            rotas_finais.append(rota_atual)
            custo_total_solucao += rota_atual.custo_acumulado
            id_proxima_rota += 1
        elif not servicos_nao_atendidos:
             print("Nenhum serviço válido atendido ou nenhum serviço requerido.")
             break
        else:
             print(f"Alerta: Rota {id_proxima_rota} criada vazia, mas ainda há {len(servicos_nao_atendidos)} serviços não atendidos.")
             if len(rotas_finais) > 2 * len(grafo.service_map):
                  print("Loop infinito detectado? Abortando construção de rotas.")
                  break

    end_time = time.time()
    tempo_execucao = end_time - start_time

    if servicos_nao_atendidos:
        print(f"\nAlerta Final: {len(servicos_nao_atendidos)} serviços não puderam ser atendidos.")
        print(f"IDs não atendidos: {servicos_nao_atendidos}")

    print(f"\nSolução inicial construída em {tempo_execucao:.4f} segundos.")
    print(f"Total de rotas: {len(rotas_finais)}")
    print(f"Custo total: {custo_total_solucao}")

    return rotas_finais, custo_total_solucao, tempo_execucao

# Exemplo de uso (requer grafo.py e parser.py)
if __name__ == '__main__':
    from grafo import Grafo
    from parser import ler_arquivo_dat
    import os

    # Teste com BHW10
    caminho_instancia = '/home/ubuntu/trabalho_grafos/grafo-logistica_modificado/grafo-logistica/selected_instances/BHW10.dat'

    if not os.path.exists(caminho_instancia):
        print(f"Arquivo de instância não encontrado em {caminho_instancia}.")
    else:
        print(f"Lendo instância: {caminho_instancia}")
        grafo_teste = ler_arquivo_dat(caminho_instancia)

        if grafo_teste:
            try:
                print("Construindo solução inicial...")
                rotas, custo, tempo = construir_solucao_path_scanning(grafo_teste)

                print("\n--- Resumo da Solução Gerada (Teste) ---")
                total_servicos_contados = 0
                for r in rotas:
                    resumo, sequencia = r.get_output_format()
                    print(resumo)
                    # Extrai o número de serviços do resumo para conferir
                    num_servicos_rota = int(resumo.split()[-1])
                    total_servicos_contados += num_servicos_rota
                    # print(sequencia) # Descomente para ver a sequência completa
                print(f"\nTotal de serviços contados nas rotas: {total_servicos_contados}")
                print(f"Total de serviços requeridos na instância: {len(grafo_teste.get_all_required_services())}")
                if total_servicos_contados == len(grafo_teste.get_all_required_services()):
                    print("Validação OK: Número de serviços bate!")
                else:
                    print("ERRO: Número de serviços nas rotas não bate com o total requerido!")

            except Exception as e:
                print(f"Erro ao construir a solução: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Falha ao ler o grafo da instância.")



import random

def construir_solucao_path_scanning_multi(grafo, tentativas=20):
    melhor_rotas = None
    melhor_custo = float("inf")
    melhor_tempo = 0
    for t in range(tentativas):
        random_seed = t * 137  # garante diferentes seeds
        random.seed(random_seed)
        # Supondo que construir_solucao_path_scanning use alguma aleatoriedade
        rotas, custo, tempo = construir_solucao_path_scanning(grafo)
        if custo < melhor_custo:
            melhor_rotas = rotas
            melhor_custo = custo
            melhor_tempo = tempo
    return melhor_rotas, melhor_custo, melhor_tempo
