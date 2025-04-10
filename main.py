import os
from parser import ler_arquivo_dat
from estatisticas import calcular_estatisticas

def listar_instancias(pasta):
    return [f for f in os.listdir(pasta) if f.endswith('.dat')]

if __name__ == '__main__':
    pasta = 'selected_instances'
    instancias = listar_instancias(pasta)

    print("=== Escolha uma instância de teste ===")
    for i, nome in enumerate(instancias):
        print(f"[{i}] {nome}")

    escolha = int(input("Digite o número da instância: "))
    caminho = os.path.join(pasta, instancias[escolha])

    grafo = ler_arquivo_dat(caminho)
    stats = calcular_estatisticas(grafo)

    print(f"\n=== Estatísticas da Instância {instancias[escolha]} ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

