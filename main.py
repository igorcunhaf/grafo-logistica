import os
from parser import ler_arquivo_dat
from estatisticas import calcular_estatisticas
from leitura_input import ler_dados_via_input

def listar_instancias(pasta):
    return [f for f in os.listdir(pasta) if f.endswith('.dat')]

def main():
    print("=== Modo de entrada ===")
    print("[1] Escolher uma instância da pasta 'selected_instances'")
    print("[2] Inserir os dados manualmente via terminal")
    escolha_modo = input("Digite sua escolha [1/2]: ").strip()

    if escolha_modo == "1":
        pasta = 'selected_instances'
        instancias = listar_instancias(pasta)

        if not instancias:
            print("Nenhuma instância .dat encontrada na pasta.")
            return

        print("\n=== Escolha uma instância de teste ===")
        for i, nome in enumerate(instancias):
            print(f"[{i}] {nome}")

        try:
            escolha = int(input("Digite o número da instância: "))
            caminho = os.path.join(pasta, instancias[escolha])
        except (ValueError, IndexError):
            print("Opção inválida.")
            return

        grafo = ler_arquivo_dat(caminho)

    elif escolha_modo == "2":
        grafo = ler_dados_via_input()

    else:
        print("Opção inválida.")
        return

    stats = calcular_estatisticas(grafo)

    print("\n=== Estatísticas do Grafo ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    main()
