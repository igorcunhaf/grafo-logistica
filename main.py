import os
import sys
import time

# Adiciona o diretório atual ao path para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import ler_arquivo_dat
from grafo import Grafo # Importa a classe Grafo atualizada

# Imports específicos das Etapas
from estatisticas import calcular_estatisticas # Corrigido para Etapa 1
from heuristica_path_scanning import construir_solucao_path_scanning # Etapa 2
from gerar_arquivo_solucao import escrever_arquivo_solucao # Etapa 2 (CORRIGIDO)
from entrada_manual import ler_dados_via_input # Restaurado para entrada manual

def listar_instancias(pasta):
    """Lista arquivos .dat em uma pasta."""
    try:
        if not os.path.isdir(pasta):
            return []
        return sorted([f for f in os.listdir(pasta) if f.endswith(".dat")])
    except Exception as e:
        print(f"Erro ao listar instâncias em {pasta}: {e}")
        return []

def selecionar_instancia(pastas_dados):
    """Permite ao usuário selecionar uma instância de uma lista de pastas."""
    instancias_encontradas = []
    mapa_indices = {}
    idx_global = 0

    print("\n=== Escolha uma instância de teste ===") # Mantendo texto original
    for pasta in pastas_dados:
        instancias = listar_instancias(pasta)
        if instancias:
            pasta_relativa = os.path.relpath(pasta, os.getcwd())
            # print(f"--- Pasta: {pasta_relativa} ---") # Removido para ficar igual ao original
            for nome in instancias:
                print(f"[{idx_global}] {nome}")
                mapa_indices[idx_global] = os.path.join(pasta, nome)
                idx_global += 1
            # print("---")

    if not mapa_indices:
        print("Nenhuma instância .dat encontrada nas pastas configuradas.")
        return None, None

    while True:
        try:
            # Mantendo texto original
            escolha = int(input(f"Digite o número da instância: "))
            if escolha in mapa_indices:
                caminho_completo = mapa_indices[escolha]
                nome_arquivo = os.path.basename(caminho_completo)
                return caminho_completo, nome_arquivo
            else:
                print("Opção inválida.") # Mantendo texto original
        except ValueError:
            print("Entrada inválida. Digite um número.")

def executar_etapa1(grafo):
    """Calcula e exibe as estatísticas da Etapa 1 no formato original."""
    # Removido o print "--- Executando Etapa 1 ---" para seguir fluxo original
    if not grafo:
        print("Erro: Grafo não carregado.")
        return False # Indica falha
    try:
        stats = calcular_estatisticas(grafo)
        print("\n=== Estatísticas do Grafo ===")
        for k, v in stats.items():
            print(f"{k}: {v}")
        return True # Indica sucesso
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        import traceback
        traceback.print_exc()
        return False # Indica falha

def executar_etapa2(grafo, nome_instancia):
    """Executa a lógica da Etapa 2 (solução inicial Path-Scanning)."""
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

        # CORRIGIDO: Passa o objeto grafo como terceiro argumento
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

    # Pastas onde procurar por instâncias .dat
    pastas_instancias = [
        "selected_instances",
        "../G0/G0",
        "../dados/dados/MCGRP"
    ]
    pastas_validas = [p for p in pastas_instancias if os.path.isdir(p)]

    # Menu inicial para escolher o modo de entrada (como no original)
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
             return # Sai se não selecionou instância

    elif escolha_modo == "2":
        print("\n--- Inserção Manual de Grafo (Etapa 1) ---")
        try:
            grafo_obj = ler_dados_via_input()
            if grafo_obj:
                print("Grafo criado manualmente com sucesso.")
                nome_instancia_carregada = "Manual"
            else:
                print("Falha ao criar grafo manualmente.")
                return # Sai se falhou
        except Exception as e:
            print(f"Erro durante a entrada manual: {e}")
            return # Sai se deu erro
    else:
        print("Opção inválida.")
        return # Sai se opção inválida

    # Se chegou aqui, um grafo foi carregado ou criado
    if grafo_obj:
        # Calcula e exibe estatísticas imediatamente (Fluxo Etapa 1 original)
        sucesso_stats = executar_etapa1(grafo_obj)

        # Após exibir estatísticas, oferece opção para Etapa 2 (se aplicável)
        if sucesso_stats and nome_instancia_carregada != "Manual":
            while True:
                print("\n--- Opções Adicionais ---")
                print("[1] Gerar Solução Inicial (Etapa 2 - Path-Scanning)")
                print("[0] Sair")
                escolha_extra = input("Digite sua escolha: ").strip()
                if escolha_extra == "1":
                    executar_etapa2(grafo_obj, nome_instancia_carregada)
                    # Após executar a Etapa 2, volta para este menu ou sai?
                    # Vamos sair por simplicidade, mas pode voltar ao menu.
                    break
                elif escolha_extra == "0":
                    break
                else:
                    print("Opção inválida.")
    else:
        # Caso algo tenha falhado na carga/criação e não saiu antes
        print("Não foi possível carregar ou criar o grafo.")

    print("\nEncerrando o programa.")

if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if dname:
        os.chdir(dname)
    main()

