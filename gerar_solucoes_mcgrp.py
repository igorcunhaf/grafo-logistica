# import os
# from grafo import Grafo
# from parser import ler_arquivo_dat
# from heuristica_path_scanning import construir_solucao_path_scanning
# from gerar_arquivo_solucao import escrever_arquivo_solucao

# # Caminho da pasta com as instâncias
# PASTA_INSTANCIAS = "dados/MCGRP"
# PASTA_SAIDA = "solucoes_mcgrp"

# # Criar pasta de saída se não existir
# os.makedirs(PASTA_SAIDA, exist_ok=True)

# # Listar todas as instâncias .dat
# instancias = [f for f in os.listdir(PASTA_INSTANCIAS) if f.endswith(".dat")]
# instancias.sort()

# print(f"Total de instâncias encontradas: {len(instancias)}")

# for nome_arquivo in instancias:
#     caminho = os.path.join(PASTA_INSTANCIAS, nome_arquivo)
#     print(f"Processando: {nome_arquivo}")
#     try:
#         grafo, deposito = ler_arquivo_dat(caminho)
#         rotas = construir_solucao_path_scanning(grafo)
#         nome_saida = f"sol-{nome_arquivo}"
#         caminho_saida = os.path.join(PASTA_SAIDA, nome_saida)
#         escrever_arquivo_solucao(rotas, caminho_saida)
#     except Exception as e:
#         print(f"Erro ao processar {nome_arquivo}: {e}")

# print("Processamento concluído.")
