# Trabalho Prático Final - Fase 1  
**Disciplina:** GCC262 - Grafos e Suas Aplicações  
**Universidade Federal de Lavras (UFLA)**  
**Professor:** Mayron César O. Moreira  

## Objetivo

Este projeto corresponde à **Fase 1** do Trabalho Prático Final e tem como objetivo:

- Representar um problema logístico modelado como multigrafo.
- Ler instâncias de teste fornecidas pelo professor.
- Calcular métricas sobre o grafo.
- Apresentar os resultados por meio de um **notebook interativo (`.ipynb`) com visualização**.

---

## Estrutura do Projeto

grafo-logistica/
├── grafo.py               # Estrutura do grafo (arestas, arcos, adjacência, etc.)
├── parser.py              # Leitura e interpretação das instâncias .dat
├── estatisticas.py        # Cálculo das métricas da Fase 1
├── main.py                # Execução via terminal com seleção de instância
├── visualizacao.ipynb     # Notebook com visualização das métricas
├── selected_instances/    # Instâncias fornecidas pelo professor
│   ├── BHW1.dat
|    ...

## Como Executar o Projeto

### Executar via Terminal (main.py)

1. Certifique-se de estar dentro da pasta do projeto:
   
   cd grafo-logistica
   

2. Execute o script principal:

   python3 main.py


3. O programa listará as instâncias disponíveis. Digite o número da instância que deseja processar.

4. O terminal exibirá as estatísticas calculadas.


### Executar via Jupyter/Colab (`visualizacao.ipynb`)

1. Abra o arquivo `visualizacao.ipynb` no **[Google Colab](https://colab.research.google.com/)** ou **Jupyter Notebook**.
2. Faça o upload dos seguintes arquivos quando solicitado:
   - `grafo.py`
   - `parser.py`
   - `estatisticas.py`
   - Uma instância de teste `.dat` (ex: `mgval_0.50_10D.dat`)
3. Execute as células:
   - A primeira célula carrega os arquivos
   - A segunda calcula e exibe as métricas em uma tabela
   - A terceira gera o gráfico de **intermediação dos vértices**


## Métricas Calculadas

- Quantidade de vértices, arestas e arcos
- Vértices, arestas e arcos **requeridos**
- Densidade do grafo
- Grau mínimo e máximo
- Número de componentes conectados
- **Intermediação** (centralidade dos vértices)
- Caminho médio e diâmetro
- Matrizes de distâncias e predecessores (Floyd-Warshall)

## Autor

- **Nome:** Igor Cunha Ferreira
- **Curso:** Sistemas de Informação  
- **Linguagem utilizada:** Python 3  
- **Bibliotecas utilizadas:** Apenas `math`, `collections`, `pandas` e `matplotlib`
