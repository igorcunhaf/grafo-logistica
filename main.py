from busca_local import two_opt, relocate, swap
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import ler_arquivo_dat
from grafo import Grafo
from estatisticas import calcular_estatisticas
from heuristica_path_scanning import construir_solucao_path_scanning, construir_solucao_path_scanning_multi
from melhoria import melhorar_solucao_2opt
from algoritmo_genetico_avancado import otimizar_com_algoritmo_genetico_avancado
from gerar_arquivo_solucao import escrever_arquivo_solucao
from entrada_manual import ler_dados_via_input
from ruin_and_recreate import ruin_and_recreate   # << INTEGRAÇÃO DO R&R

def listar_instancias(pasta):
    try:
        if not os.path.isdir(pasta):
            return []
        return sorted([f for f in os.listdir(pasta) if f.endswith(".dat")])
    except Exception as e:
        print(f"Erro ao listar instâncias em {pasta}: {e}")
        return []

def selecionar_instancia(pastas_dados):
    instancias_encontradas = []
    mapa_indices = {}
    idx_global = 0

    print("\n=== Escolha uma instância de teste ===")
    for pasta in pastas_dados:
        instancias = listar_instancias(pasta)
        if instancias:
            pasta_relativa = os.path.relpath(pasta, os.getcwd())
            for nome in instancias:
                print(f"[{idx_global}] {nome}")
                mapa_indices[idx_global] = os.path.join(pasta, nome)
                idx_global += 1

    if not mapa_indices:
        print("Nenhuma instância .dat encontrada nas pastas configuradas.")
        return None, None

    while True:
        try:
            escolha = int(input(f"Digite o número da instância: "))
            if escolha in mapa_indices:
                caminho_completo = mapa_indices[escolha]
                nome_arquivo = os.path.basename(caminho_completo)
                return caminho_completo, nome_arquivo
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def executar_etapa1(grafo):
    if not grafo:
        print("Erro: Grafo não carregado.")
        return False
    try:
        stats = calcular_estatisticas(grafo)
        print("\n=== Estatísticas do Grafo ===")
        for k, v in stats.items():
            print(f"{k}: {v}")
        return True
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        import traceback
        traceback.print_exc()
        return False

def executar_etapa2(grafo, nome_instancia):
    print("\n--- Executando Etapa 2: Geração de Solução Inicial (Path-Scanning) ---")

    if not grafo:
        print("Erro: Objeto grafo não foi carregado corretamente.")
        return None

    try:
        if grafo.dist_matrix is None:
            print("Calculando matrizes de caminhos mínimos (Floyd-Warshall)...", end=" ", flush=True)
            start_fw = time.time()
            grafo.calcular_distancias_predecessores_floyd_warshall()
            end_fw = time.time()
            print(f"Concluído em {end_fw - start_fw:.4f} segundos.")

        print("Construindo rotas com Path-Scanning...", end=" ", flush=True)
        rotas, custo_total, tempo_heuristica = construir_solucao_path_scanning(grafo)
        print(f"Concluído em {tempo_heuristica:.4f} segundos.")

        pasta_solucoes = "solucoes_etapa2"
        os.makedirs(pasta_solucoes, exist_ok=True)
        nome_base_instancia = os.path.splitext(nome_instancia)[0]
        nome_arquivo_solucao = f"sol-{nome_base_instancia}.dat"
        caminho_arquivo_saida = os.path.join(pasta_solucoes, nome_arquivo_solucao)

        escrever_arquivo_solucao(rotas, custo_total, grafo, caminho_arquivo_saida)

        print(f"\nSolução da Etapa 2 gerada para a instância {nome_instancia}.")
        print(f"Custo Total: {int(round(custo_total))}")
        print(f"Número de Rotas: {len(rotas)}")
        print(f"Arquivo de solução salvo em: {caminho_arquivo_saida}")
        return caminho_arquivo_saida

    except ValueError as ve:
        print(f"\nErro durante a execução da Etapa 2: {ve}")
    except Exception as e:
        print(f"\nErro inesperado durante a Etapa 2: {e}")
        import traceback
        traceback.print_exc()
    return None

def main():
    print("==================================================")
    print("   Trabalho Prático - Algoritmos em Grafos")
    print("==================================================")

    grafo_obj = None
    nome_instancia_carregada = None
    caminho_instancia_carregada = None

    pastas_instancias = [
        "selected_instances",
        "../G0/G0",
        "../dados/dados/MCGRP"
    ]
    pastas_validas = [p for p in pastas_instancias if os.path.isdir(p)]

    print("\n=== Modo de entrada ===")
    print("[1] Escolher uma instância da pasta 'selected_instances' (ou outras configuradas)")
    print("[2] Inserir os dados manualmente via terminal")
    escolha_modo = input("Digite sua escolha [1/2]: ").strip()

    if escolha_modo == "1":
        if not pastas_validas:
            print("Aviso: Nenhuma das pastas de instâncias configuradas foi encontrada.")
            return
        caminho_instancia, nome_instancia = selecionar_instancia(pastas_validas)
        if caminho_instancia:
            print(f"\nLendo instância: {caminho_instancia}...")
            grafo_obj = ler_arquivo_dat(caminho_instancia)
            if grafo_obj:
                print("Instância lida com sucesso.")
                nome_instancia_carregada = nome_instancia
                caminho_instancia_carregada = caminho_instancia
            else:
                print("Falha ao carregar o grafo da instância selecionada.")
        else:
            return

    elif escolha_modo == "2":
        print("\n--- Inserção Manual de Grafo (Etapa 1) ---")
        try:
            grafo_obj = ler_dados_via_input()
            if grafo_obj:
                print("Grafo criado manualmente com sucesso.")
                nome_instancia_carregada = "Manual"
            else:
                print("Falha ao criar grafo manualmente.")
                return
        except Exception as e:
            print(f"Erro durante a entrada manual: {e}")
            return
    else:
        print("Opção inválida.")
        return

    if grafo_obj:
        sucesso_stats = executar_etapa1(grafo_obj)

        if sucesso_stats and nome_instancia_carregada != "Manual":
            print("\n--- Gerando Solução Otimizada (Todas as Estratégias) ---")
            # 1. Path-Scanning Multi-Start
            rotas_iniciais, custo_inicial, tempo_inicial = construir_solucao_path_scanning_multi(grafo_obj, tentativas=30)
            print(f'[Multi-Start] Melhor custo inicial encontrado: {custo_inicial}')

            capacidade_maxima = grafo_obj.capacidade

            # 2. Otimização Conservadora
            rotas_conserv, custo_conserv, tempo_conserv = melhorar_solucao_2opt(grafo_obj, rotas_iniciais)
            print(f'[Conservadora] Custo após otimização conservadora: {custo_conserv}')

            # 3. Busca Local Avançada (2-opt, relocate, swap)
            melhor_rotas = [r for r in rotas_iniciais]
            for i, rota in enumerate(melhor_rotas):
                rota.sequencia_visitas_detalhada = two_opt(rota.sequencia_visitas_detalhada, grafo_obj)
                if hasattr(rota, "atualizar_demanda_custo"):
                    rota.atualizar_demanda_custo(grafo_obj)

            for ciclo in range(3):
                melhor_rotas = relocate(melhor_rotas, grafo_obj, capacidade_maxima)
                for rota in melhor_rotas:
                    rota.sequencia_visitas_detalhada = two_opt(rota.sequencia_visitas_detalhada, grafo_obj)
                    if hasattr(rota, "atualizar_demanda_custo"):
                        rota.atualizar_demanda_custo(grafo_obj)
            for ciclo in range(3):
                melhor_rotas = swap(melhor_rotas, grafo_obj, capacidade_maxima)
                for rota in melhor_rotas:
                    rota.sequencia_visitas_detalhada = two_opt(rota.sequencia_visitas_detalhada, grafo_obj)
                    if hasattr(rota, "atualizar_demanda_custo"):
                        rota.atualizar_demanda_custo(grafo_obj)
            custo_melhorado = sum(rota.custo_acumulado for rota in melhor_rotas)
            print(f'[Busca Local] Custo após melhorias locais: {custo_melhorado}')

            # 4. Algoritmo Genético Avançado sobre a melhor solução encontrada até aqui
            rotas_rr, custo_rr, tempo_ag = otimizar_com_algoritmo_genetico_avancado(grafo_obj, melhor_rotas)
            print(f'[Algoritmo Genético Avançado] Custo após AG: {custo_rr}')

            # Seleciona a melhor entre as quatro estratégias
            melhor_solucao = rotas_iniciais
            melhor_custo_final = custo_inicial
            metodo = "Path-Scanning Multi-Start"
            if custo_conserv < melhor_custo_final:
                melhor_solucao = rotas_conserv
                melhor_custo_final = custo_conserv
                metodo = "Otimização Conservadora"
            if custo_melhorado < melhor_custo_final:
                melhor_solucao = melhor_rotas
                melhor_custo_final = custo_melhorado
                metodo = "Busca Local Avançada"
            if custo_rr < melhor_custo_final:
                melhor_solucao = rotas_rr
                melhor_custo_final = custo_rr
                metodo = "Ruin & Recreate"
            print(f'[FINAL] Melhor método: {metodo}, Custo final: {melhor_custo_final}')

            pasta_solucoes_otimizadas = "solucoes_otimizadas"
            os.makedirs(pasta_solucoes_otimizadas, exist_ok=True)
            nome_base_instancia = os.path.splitext(nome_instancia_carregada)[0]
            nome_arquivo_solucao_otimizada = f"sol-{nome_base_instancia}.dat"
            caminho_arquivo_saida_otimizada = os.path.join(pasta_solucoes_otimizadas, nome_arquivo_solucao_otimizada)

            escrever_arquivo_solucao(melhor_solucao, melhor_custo_final, grafo_obj, caminho_arquivo_saida_otimizada)

            print(f"\nSolução Otimizada gerada para a instância {nome_instancia_carregada}.")
            print(f"Custo Inicial (Path-Scanning): {int(round(custo_inicial))}")
            print(f"Custo Conservadora: {int(round(custo_conserv))}")
            print(f"Custo Busca Local: {int(round(custo_melhorado))}")
            print(f"Custo Ruin & Recreate: {int(round(custo_rr))}")
            print(f"Custo Otimizado (Melhor): {int(round(melhor_custo_final))}")
            print(f"Número de Rotas (Inicial): {len(rotas_iniciais)}")
            print(f"Arquivo de solução otimizada salvo em: {caminho_arquivo_saida_otimizada}")
        else:
            print("Não foi possível gerar a solução inicial para otimização.")
    else:
        print("Não foi possível carregar ou criar o grafo.")

    print("\nEncerrando o programa.")

if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if dname:
        os.chdir(dname)
    main()
