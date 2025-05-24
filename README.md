# Trabalho Prático Final - Fases 1 e 2  
**Disciplina:** GCC262 - Grafos e Suas Aplicações  
**Universidade Federal de Lavras (UFLA)**  
**Professor:** Mayron César O. Moreira  

## Objetivo

Este projeto corresponde às **Fases 1 e 2** do Trabalho Prático Final e tem como objetivos:

- Representar um problema logístico utilizando a modelagem por **multigrafos**.
- Ler e interpretar instâncias de teste fornecidas pelo professor.
- Calcular métricas relacionadas à estrutura do grafo.
- Construir uma **solução inicial viável** que atenda a todos os serviços requeridos, respeitando a capacidade dos veículos envolvidos.
- Gerar a solução em um arquivo `.dat` padronizado conforme exigido.

## Etapa 1 - Cálculo de Métricas

A Fase 1 tem como foco a análise estrutural de grafos. As métricas calculadas incluem:

- Quantidade de vértices, arestas e arcos
- Vértices, arestas e arcos **requeridos**
- Densidade do grafo
- Grau mínimo e máximo
- Número de componentes conectados
- **Intermediação** (centralidade dos vértices)
- Caminho médio e diâmetro
- Matrizes de distâncias e predecessores (Floyd-Warshall)

---

## Etapa 2 - Construção de Solução Inicial

Na Fase 2, é implementada a heurística **Path-Scanning**, uma abordagem clássica para construção de rotas em problemas de roteamento com capacidade, como o **Capacitated Arc Routing Problem (CARP)**.

A cada iteração, uma nova rota é iniciada a partir do **depósito**, e são selecionados serviços requeridos (arestas, arcos ou nós) com base em um critério **guloso**, levando em conta:

- O menor custo de deslocamento a partir do último ponto da rota;
- Se a demanda do serviço cabe na capacidade restante do veículo.

Quando não é possível incluir novos serviços sem ultrapassar a capacidade, a rota é encerrada e uma nova é iniciada. Esse processo se repete até que todos os serviços tenham sido atendidos.

A heurística Path-Scanning se **inspira nos princípios do TSP**, especialmente na ideia do **vizinho mais próximo** – escolher o próximo ponto a ser visitado com base no menor custo de deslocamento.

---

## Como Executar o Projeto

### Executar via Terminal (main.py)

1. Certifique-se de estar dentro da pasta do projeto:
   
   cd grafo-logistica
   

2. Execute o script principal:

   python3 main.py


3. O programa listará as instâncias disponíveis. Digite o número da instância que deseja processar.

4. O terminal exibirá as estatísticas calculadas.

## Autor

- **Nome:** Igor Cunha Ferreira
- **Curso:** Sistemas de Informação  
- **Linguagem utilizada:** Python 3  
- **Bibliotecas utilizadas:** Apenas `math`, `collections`, `pandas` e `matplotlib`
