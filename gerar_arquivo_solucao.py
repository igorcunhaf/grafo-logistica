import os

def escrever_arquivo_solucao(rotas, custo_total, grafo, arquivo_saida):
    """Escreve o arquivo de solução no formato padrão.

    Args:
        rotas (list): Lista de objetos Rota construídos pela solução inicial.
        custo_total (float or int): Custo total da solução encontrada.
        grafo (Grafo): O objeto grafo da instância, usado para obter o total de serviços.
        arquivo_saida (str): Caminho completo onde o arquivo de solução será salvo.
    """
    try:
        # Garante que o diretório de saída exista
        diretorio_saida = os.path.dirname(arquivo_saida)
        if diretorio_saida:
            os.makedirs(diretorio_saida, exist_ok=True)

        # Calcula o número total de serviços requeridos a partir do grafo
        total_servicos_requeridos = len(grafo.get_all_required_services())

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            # 1. Cabeçalho
            f.write(f"{int(round(custo_total))}\n") # Custo total (arredondado para inteiro, se necessário)
            f.write(f"{len(rotas)}\n")     # Total de rotas
            # Linhas 3 e 4: Número total de serviços requeridos
            f.write(f"{total_servicos_requeridos}\n") 
            f.write(f"{total_servicos_requeridos}\n") 

            # 2. Detalhes de cada rota
            for rota in rotas:
                # Passa o ID correto da rota para formatação
                resumo_rota, sequencia_visitas = rota.get_output_format()
                f.write(f"{resumo_rota} {sequencia_visitas}\n")


    except IOError as e:
        print(f"Erro ao escrever o arquivo de solução em {arquivo_saida}: {e}")
        raise # Re-levanta a exceção para ser tratada no main
    except Exception as e:
        print(f"Erro inesperado ao escrever o arquivo de solução: {e}")
        import traceback
        traceback.print_exc()
        raise # Re-levanta a exceção

# Exemplo de uso (requer Rota from solucao_inicial e Grafo)
if __name__ == '__main__':
    # Simular dados de entrada
    from rota import Rota # Importa a classe Rota do novo módulo
    from grafo import Grafo # Precisa da classe Grafo

    # Criar rotas de exemplo
    rota1 = Rota(id_rota=1, deposito_id=1)
    rota1.sequencia_visitas_detalhada = [('D', 0), ('S', 14, 7, 8), ('S', 2, 3, 3), ('D', 0)]
    rota1.demanda_acumulada = 15
    rota1.custo_acumulado = 150
    rota1.servicos_atendidos = {14, 2}

    rota2 = Rota(id_rota=2, deposito_id=1)
    rota2.sequencia_visitas_detalhada = [('D', 0), ('S', 26, 7, 6), ('D', 0)]
    rota2.demanda_acumulada = 5
    rota2.custo_acumulado = 80
    rota2.servicos_atendidos = {26}

    rotas_exemplo = [rota1, rota2]
    custo_total_exemplo = 230

    # Criar um grafo de exemplo mínimo para obter o total de serviços
    grafo_exemplo = Grafo()
    grafo_exemplo.requeridos_v = {100: {'demanda': 1, 'custo_servico': 1, 'service_id': 100}}
    grafo_exemplo.requeridos_e = {(200, 201): {'custo_travessia': 1, 'demanda': 1, 'custo_servico': 1, 'service_id': 200}}
    grafo_exemplo.requeridos_a = {(300, 301): {'custo_travessia': 1, 'demanda': 1, 'custo_servico': 1, 'service_id': 300}}
    # Adiciona os serviços do exemplo às listas do grafo para teste
    grafo_exemplo.requeridos_v[7] = {'demanda': 1, 'custo_servico': 1, 'service_id': 14}
    grafo_exemplo.requeridos_v[3] = {'demanda': 1, 'custo_servico': 1, 'service_id': 2}
    grafo_exemplo.requeridos_v[6] = {'demanda': 1, 'custo_servico': 1, 'service_id': 26}


    arquivo_saida_exemplo = "/home/ubuntu/trabalho_grafos/exemplo_solucao_corrigido.dat"

    print(f"Gerando arquivo de exemplo corrigido: {arquivo_saida_exemplo}")
    try:
        escrever_arquivo_solucao(rotas_exemplo, custo_total_exemplo, grafo_exemplo, arquivo_saida_exemplo)

        # Verificar conteúdo do arquivo gerado (opcional)
        with open(arquivo_saida_exemplo, 'r') as f_check:
            print("\n--- Conteúdo do Arquivo Gerado (Corrigido) ---")
            print(f_check.read())
    except Exception as e:
        print(f"Erro ao gerar ou ler arquivo de exemplo: {e}")

