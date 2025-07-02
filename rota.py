import math

class Rota:
    """Representa uma única rota de um veículo."""
    def __init__(self, id_rota, deposito_id):
        """Inicializa uma rota.

        Args:
            id_rota (int): Identificador único da rota.
            deposito_id (int): ID do nó do depósito.
        """
        self.id_rota = id_rota
        self.deposito_id = deposito_id
        self.sequencia_visitas_detalhada = [("D", 0)] # Começa no depósito
        self.servicos_atendidos = set() # Conjunto de service_ids atendidos nesta rota
        self.demanda_acumulada = 0
        self.custo_acumulado = 0
        self.ultimo_no_visitado = deposito_id

    def adicionar_visita_servico(self, service_id, u, v, demanda, custo_servico, custo_travessia_ate_servico, caminho_ate_servico):
        """Adiciona a visita a um serviço à rota."""
        # Adiciona nós de travessia
        for i in range(len(caminho_ate_servico) -1):
             no_travessia = caminho_ate_servico[i]
             if no_travessia != self.deposito_id and no_travessia != u:
                 self.sequencia_visitas_detalhada.append(("T", no_travessia))

        # Adiciona a visita ao serviço
        self.sequencia_visitas_detalhada.append(("S", service_id, u, v))
        self.servicos_atendidos.add(service_id)
        self.demanda_acumulada += demanda
        self.custo_acumulado += custo_travessia_ate_servico + custo_servico
        self.ultimo_no_visitado = v

    def adicionar_retorno_deposito(self, custo_travessia_retorno, caminho_retorno):
        """Adiciona o retorno ao depósito no final da rota."""
        for i in range(len(caminho_retorno) -1):
             no_travessia = caminho_retorno[i]
             if no_travessia != self.deposito_id:
                 self.sequencia_visitas_detalhada.append(("T", no_travessia))

        self.sequencia_visitas_detalhada.append(("D", 0))
        self.custo_acumulado += custo_travessia_retorno
        self.ultimo_no_visitado = self.deposito_id

    def verificar_capacidade(self, nova_demanda, capacidade_maxima):
        """Verifica se adicionar uma nova demanda excederia a capacidade."""
        return self.demanda_acumulada + nova_demanda <= capacidade_maxima

    def get_ultimo_no(self):
        """Retorna o ID do último nó visitado na rota."""
        return self.ultimo_no_visitado

    def get_output_format(self):
        """Formata a rota para o padrão de saída especificado.

        Correção: Conta apenas visitas de serviço (S) para o número de visitas no resumo.
        """
        visitas_output = []
        for tipo_entrada in self.sequencia_visitas_detalhada:
            tipo = tipo_entrada[0]
            if tipo == "D":
                # Formato: (D 0,1,ID_ROTA)
                visitas_output.append(f"(D 0,1,{self.id_rota})")
            elif tipo == "S":
                # Formato: (S id_serviço,exterminadade_serviço,outra_extermidade_do_servico)
                service_id = tipo_entrada[1]
                u = tipo_entrada[2]
                v = tipo_entrada[3]
                visitas_output.append(f"(S {service_id},{u},{v})")
            elif tipo == "T":
                # Formato: (T no_travessia,no_travessia,no_travessia) - assumindo que 'T' é um nó de travessia
                # O padrão de escrita não especifica 'T', então vamos ignorar para o output final, mas manter na lógica interna
                # Ou, se for para representar o nó, pode ser (N no_id,no_id,no_id) ou similar se o professor aceitar
                # Por enquanto, vamos manter apenas D e S no output final, conforme o padrao_escrita.dat indica:
                # "2) Só serão impressos as informações das visitas dos serviços nas rotas."
                pass # Ignora nós de travessia no output final, conforme a regra 2 do padrao_escrita.dat

        num_visitas_para_output = sum(1 for item in self.sequencia_visitas_detalhada if item[0] in ["D", "S"])

        # Linha de resumo da rota
        # depósito(0) dia(1) id_rota demanda_total custo_total total_de_visitas (formato output)
        resumo = f"0 1 {self.id_rota} {self.demanda_acumulada} {self.custo_acumulado} {num_visitas_para_output}"
        sequencia = " ".join(visitas_output)
        return resumo, sequencia

    def atualizar_demanda_custo(self, grafo):
        """Recalcula a demanda acumulada e o custo acumulado da rota, baseada na sequencia_visitas_detalhada."""
        demanda = 0
        custo = 0
        ultimo = self.deposito_id
        for item in self.sequencia_visitas_detalhada:
            if item[0] == "S":
                service_id = item[1]
                demanda += grafo.service_map[service_id]["demanda"]
                u, v = item[2], item[3]
                custo += grafo.dist_matrix[ultimo][u]
                custo += grafo.dist_matrix[u][v]
                ultimo = v
            elif item[0] == "D":
                custo += grafo.dist_matrix[ultimo][self.deposito_id]
                ultimo = self.deposito_id
            elif item[0] == "T":
                no = item[1]
                custo += grafo.dist_matrix[ultimo][no]
                ultimo = no
        self.demanda_acumulada = demanda
        self.custo_acumulado = custo
