import re
import os # Adicionado para checagem de existência no main
from grafo import Grafo # Assume que grafo.py está no mesmo diretório ou PYTHONPATH

def ler_arquivo_dat(caminho):
    """Lê um arquivo de instância .dat e retorna um objeto Grafo populado.

    Args:
        caminho (str): O caminho para o arquivo .dat.

    Returns:
        Grafo: Um objeto da classe Grafo contendo os dados da instância.
               Retorna None se ocorrer um erro na leitura ou parsing.
    """
    grafo = Grafo()
    service_id_counter = 1
    grafo.service_map = {}

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        # 1. Extrair informações do cabeçalho (mais flexível)
        grafo.capacidade = None
        grafo.deposito = None
        for linha in linhas:
            linha_lower = linha.lower().strip()
            # Procura por linhas contendo 'capacity:' ou 'depot node:' (case-insensitive)
            if 'capacity:' in linha_lower:
                try:
                    # Pega o valor após o último ':'
                    grafo.capacidade = int(linha.split(':')[-1].strip())
                except (ValueError, IndexError):
                    print(f"Aviso: Falha ao extrair capacidade da linha: {linha.strip()}")
            elif 'depot node:' in linha_lower:
                try:
                    # Pega o valor após o último ':'
                    grafo.deposito = int(linha.split(':')[-1].strip())
                except (ValueError, IndexError):
                    print(f"Aviso: Falha ao extrair depósito da linha: {linha.strip()}")

            # Otimização: parar se ambos foram encontrados (geralmente estão no início)
            if grafo.capacidade is not None and grafo.deposito is not None:
                 break

        # Lida com casos onde capacidade/depósito não foram encontrados
        if grafo.capacidade is None:
            print(f"Aviso: Capacidade não encontrada explicitamente em {caminho}. Assumindo infinito.")
            grafo.capacidade = float('inf')
        if grafo.deposito is None:
            print(f"Aviso: Depósito não encontrado explicitamente em {caminho}. Assumindo nó 1.")
            grafo.deposito = 1
        print(f"Valores usados: Capacidade={grafo.capacidade}, Depósito={grafo.deposito}")


        # 2. Encontrar índices de início e fim das seções relevantes (mais flexível)
        section_indices = {}
        # Cabeçalhos simplificados para detecção mais robusta
        section_starts = {
            "ReN": "ReN.",
            "ReE": "ReE.",
            "ReA": "ReA.",
            "ARC": "ARC", # Seção de arcos não requeridos
            "EDGE": "EDGE", # Seção de arestas não requeridas (se existir)
            "FIM": "FIM"
        }
        active_sections = list(section_starts.keys())

        # Encontra o início de cada seção potencial
        for i, linha in enumerate(linhas):
            linha_strip = linha.strip()
            for key, start_text in section_starts.items():
                if linha_strip.startswith(start_text) and f"{key}_start" not in section_indices:
                    # Armazena o índice da linha *após* o cabeçalho
                    # Considera possível linha em branco após cabeçalho
                    start_index = i + 1
                    if start_index < len(linhas) and not linhas[start_index].strip():
                        start_index += 1
                    section_indices[f"{key}_start"] = start_index
                    break # Passa para a próxima linha após encontrar um cabeçalho

        # Define o fim de cada seção baseado no início da próxima ou no fim do arquivo
        sorted_sections = sorted(section_indices.items(), key=lambda item: item[1])
        num_sections = len(sorted_sections)

        for i in range(num_sections):
            current_section_key, start_index = sorted_sections[i]
            section_name = current_section_key.replace("_start", "")

            # O fim é a linha *antes* do início da próxima seção
            if i + 1 < num_sections:
                next_section_key, next_start_index = sorted_sections[i+1]
                # O índice de início já considera a linha após o cabeçalho
                # O fim é a linha do cabeçalho da próxima seção
                end_index = next_start_index - (2 if (next_start_index > 0 and not linhas[next_start_index-2].strip()) else 1)
            else:
                # Última seção vai até o fim do arquivo
                end_index = len(linhas)

            section_indices[f"{section_name}_end"] = end_index

        # --- Parsing das Seções --- #

        # 3. Processar Nós Requeridos (ReN)
        if "ReN_start" in section_indices:
            start = section_indices["ReN_start"]
            end = section_indices["ReN_end"]
            print(f"Processando ReN de {start} a {end}")
            for i in range(start, end):
                linha = linhas[i]
                partes = linha.strip().split()
                if len(partes) >= 3 and partes[0].startswith('N'):
                    try:
                        no = int(partes[0][1:])
                        demanda = int(partes[1])
                        custo_servico = int(partes[2])
                        grafo.adicionar_vertice_requerido(no, demanda, custo_servico, service_id_counter)
                        grafo.service_map[service_id_counter] = {'tipo': 'N', 'id': no, 'demanda': demanda, 'custo_servico': custo_servico, 'endpoints': (no, no)}
                        service_id_counter += 1
                    except (ValueError, IndexError):
                        print(f"Aviso: Linha de nó requerido mal formatada: {linha.strip()}")
                        continue
        else:
             print("Aviso: Seção ReN não encontrada.")

        # 4. Processar Arestas Requeridas (ReE)
        if "ReE_start" in section_indices:
            start = section_indices["ReE_start"]
            end = section_indices["ReE_end"]
            print(f"Processando ReE de {start} a {end}")
            for i in range(start, end):
                linha = linhas[i]
                partes = linha.strip().split()
                if len(partes) >= 6 and partes[0].startswith('E'):
                    try:
                        u, v = int(partes[1]), int(partes[2])
                        custo_travessia = int(partes[3])
                        demanda = int(partes[4])
                        custo_servico = int(partes[5])
                        grafo.adicionar_aresta_requerida(u, v, custo_travessia, demanda, custo_servico, service_id_counter)
                        grafo.service_map[service_id_counter] = {'tipo': 'E', 'id': partes[0], 'demanda': demanda, 'custo_servico': custo_servico, 'endpoints': tuple(sorted((u, v)))}
                        service_id_counter += 1
                    except (ValueError, IndexError):
                        print(f"Aviso: Linha de aresta requerida mal formatada: {linha.strip()}")
                        continue
        else:
            print("Aviso: Seção ReE não encontrada ou vazia.")

        # 5. Processar Arcos Requeridos (ReA)
        if "ReA_start" in section_indices:
            start = section_indices["ReA_start"]
            end = section_indices["ReA_end"]
            print(f"Processando ReA de {start} a {end}")
            for i in range(start, end):
                linha = linhas[i]
                partes = linha.strip().split()
                if len(partes) >= 6 and partes[0].startswith('A'):
                    try:
                        u, v = int(partes[1]), int(partes[2])
                        custo_travessia = int(partes[3])
                        demanda = int(partes[4])
                        custo_servico = int(partes[5])
                        grafo.adicionar_arco_requerido(u, v, custo_travessia, demanda, custo_servico, service_id_counter)
                        grafo.service_map[service_id_counter] = {'tipo': 'A', 'id': partes[0], 'demanda': demanda, 'custo_servico': custo_servico, 'endpoints': (u, v)}
                        service_id_counter += 1
                    except (ValueError, IndexError):
                        print(f"Aviso: Linha de arco requerido mal formatada: {linha.strip()}")
                        continue
        else:
            print("Aviso: Seção ReA não encontrada.")

        # 6. Processar Arestas NÃO Requeridas (EDGE) - Se existir
        if "EDGE_start" in section_indices:
            start = section_indices["EDGE_start"]
            end = section_indices["EDGE_end"]
            print(f"Processando EDGE (não req.) de {start} a {end}")
            for i in range(start, end):
                linha = linhas[i]
                partes = linha.strip().split()
                # Formato pode variar, exemplo: NrE<id> FROM_N TO_N T_COST
                if len(partes) >= 4: # Precisa de pelo menos u, v, custo
                    try:
                        # Tenta pegar as colunas corretas (pode precisar de ajuste)
                        u, v, custo = int(partes[1]), int(partes[2]), int(partes[3])
                        grafo.adicionar_aresta_nao_requerida(u, v, custo)
                    except (ValueError, IndexError):
                        # Tenta formato alternativo sem ID: FROM_N TO_N T_COST
                        if len(partes) == 3:
                             try:
                                 u, v, custo = int(partes[0]), int(partes[1]), int(partes[2])
                                 grafo.adicionar_aresta_nao_requerida(u, v, custo)
                             except (ValueError, IndexError):
                                 print(f"Aviso: Linha de aresta não requerida mal formatada: {linha.strip()}")
                                 continue
                        else:
                            print(f"Aviso: Linha de aresta não requerida mal formatada: {linha.strip()}")
                            continue
        else:
            print("Aviso: Seção EDGE (arestas não requeridas) não encontrada.")

        # 7. Processar Arcos NÃO Requeridos (ARC)
        if "ARC_start" in section_indices:
            start = section_indices["ARC_start"]
            end = section_indices["ARC_end"]
            print(f"Processando ARC (não req.) de {start} a {end}")
            for i in range(start, end):
                linha = linhas[i]
                partes = linha.strip().split()
                # Formato esperado: NrA<id> FROM_N TO_N T_COST
                if len(partes) >= 4: # Precisa de ID, u, v, custo
                    try:
                        u, v, custo = int(partes[1]), int(partes[2]), int(partes[3])
                        grafo.adicionar_arco_nao_requerido(u, v, custo)
                    except (ValueError, IndexError):
                        print(f"Aviso: Linha de arco não requerido mal formatada: {linha.strip()}")
                        continue
        else:
            print("Aviso: Seção ARC (arcos não requeridos) não encontrada.")

        # Garante que todos os vértices mencionados estão no conjunto de vértices
        # (já tratado em _add_adj e adicionar_vertice_requerido)
        # Adiciona vértices isolados requeridos que podem não ter arestas/arcos
        grafo.vertices.update(grafo.requeridos_v.keys())

        print(f"Leitura de {caminho} concluída. Vértices: {len(grafo.vertices)}, Serviços: {len(grafo.service_map)}")
        # Verifica se algum serviço foi lido
        if not grafo.service_map:
             print("Aviso: Nenhum serviço requerido foi lido ou mapeado. Verifique as seções ReN, ReE, ReA.")

        return grafo

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {caminho}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao ler o arquivo {caminho}: {e}")
        import traceback
        traceback.print_exc()
        return None

# Exemplo de uso (para teste)
if __name__ == '__main__':
    # Teste com BHW10
    caminho_teste = '/home/ubuntu/trabalho_grafos/grafo-logistica_modificado/grafo-logistica/selected_instances/BHW10.dat'

    if not os.path.exists(caminho_teste):
         print(f"Arquivo de teste não encontrado em {caminho_teste}.")
    else:
        print(f"\n--- Testando Parser com: {caminho_teste} ---")
        grafo_teste = ler_arquivo_dat(caminho_teste)
        if grafo_teste:
            print("\n--- Informações do Grafo Lido (Teste) ---")
            print(f"Depósito: {grafo_teste.deposito}")
            print(f"Capacidade: {grafo_teste.capacidade}")
            print(f"Total de Vértices: {len(grafo_teste.vertices)}")
            print(f"Total de Arestas (Não Req): {len(grafo_teste.arestas_nao_req)}")
            print(f"Total de Arcos (Não Req): {len(grafo_teste.arcos_nao_req)}")
            print(f"Total de Nós Requeridos: {len(grafo_teste.requeridos_v)}")
            print(f"Total de Arestas Requeridas: {len(grafo_teste.requeridos_e)}")
            print(f"Total de Arcos Requeridos: {len(grafo_teste.requeridos_a)}")
            print(f"Total de Serviços Mapeados: {len(grafo_teste.service_map)}")
            # print("Lista de Adjacência (amostra):", dict(list(grafo_teste.adj.items())[:5]))
        else:
            print("Falha ao ler o grafo de teste.")

