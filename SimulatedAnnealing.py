from pathlib import Path
import math
import random

ROOT_DIR = Path(__file__).parent
FILE_DIR = ROOT_DIR / 'files'

class SimulatedAnnealing:
    def __init__(self, name=None, cooling_rate=0.02, iter_max=100, T_min=1e-3, no_improve_limit=10):
        '''
        Inicializa o Simulated Annealing com os parâmetros padrões:

        :param name: Nome do arquivo
        :param cooling_rate: Taxa de resfriamento
        :param iter_max: Número máximo de iterações
        :param T_min: Temperatura mínima
        :param no_improve_limit: Limite de iterações sem melhora

        :return: None
        '''
        self.name = name
        self.temperature = None 
        self.cooling_rate = cooling_rate
        self.iter_max = iter_max
        self.T_min = T_min  
        self.no_improve_limit = no_improve_limit  

        self.neighbors_amount = 0
        self.best_solutions_vector = []
        self.best_cost_vector = []
        self.solution = None
        self.capacity = None
        self.profit = None
        self.weight = None

    def read_file(self):
        '''
        Lê o arquivo de entrada e armazena os valores de capacidade, quantidade de itens, lucros e pesos.

        :return: capacidade, quantidade de itens, lucros e pesos
        '''
        print("Arquivos: ")
        for file in FILE_DIR.iterdir():
            if file.suffix == '.txt':
                print(f"{file.stem}")
        
        open_file = input("Escolha o arquivo que deseja abrir: ")
        open_file += ".txt"
        
        with open(f'{FILE_DIR}/{open_file}', "r") as file:
            self.capacity = int(file.readline().strip())
            self.profit = list(map(int, file.readline().split()))  
            self.weight = list(map(int, file.readline().split()))  
            self.amount = len(self.profit)

            if len(self.profit) != len(self.weight):
                raise ValueError("Erro: A quantidade de itens em profit e weight não são iguais!")

            print(f"Capacidade da mochila: {self.capacity}")
            print(f"Quantidade de itens: {self.amount}")
            print(f"Lucros: {self.profit}")
            print(f"Pesos: {self.weight}")
        
        return self.capacity, self.amount, self.profit, self.weight

    def generate_initial_solution(self):
        '''
        Gera uma solução inicial para o problema da mochila.

        :return: solução inicial
        '''
        items = sorted(range(self.amount), key=lambda i: self.profit[i] / self.weight[i], reverse=True)
        solution = [0] * self.amount
        weight = 0
        for i in items:
            if weight + self.weight[i] <= self.capacity:
                solution[i] = 1
                weight += self.weight[i]
        return solution

    def calculate_cost(self, solution):
        '''
        Calcula o custo de uma solução.

        :param solution: solução

        :return: custo
        '''
        return sum(solution[i] * self.profit[i] for i in range(len(solution)))

    def calculate_number_of_neighbors(self, amount):
        '''
        Calcula o número de vizinhos a serem gerados.

        :param amount: quantidade de itens

        :return: None
        '''
        self.neighbors_amount = max(1, int(amount * 0.15))

    def generate_neighbors(self, solution):
        ''''
        Gera vizinhos de uma solução.

        :param solution: solução

        :return: vizinhos
        '''
        neighbors = []
        for _ in range(self.neighbors_amount):
            neighbor = solution[:]
            i = random.randint(0, len(neighbor) - 1)
            neighbor[i] = 1 - neighbor[i]
            weight = sum(neighbor[i] * self.weight[i] for i in range(len(neighbor)))
            while weight > self.capacity:
                indices_1 = [i for i in range(len(neighbor)) if neighbor[i] == 1]
                if not indices_1:
                    break
                i = random.choice(indices_1)
                neighbor[i] = 0
                weight -= self.weight[i]
            neighbors.append(neighbor)
        return neighbors

    def initial_temperature(self, solution):
        '''
        Calcula a temperatura inicial.
        Fórumla: temperatura = soma dos custos dos vizinhos / quantidade de vizinhos

        :param solution: solução

        :return: None
        '''
        neighbors = self.generate_neighbors(solution)
        neighbors_cost = [self.calculate_cost(neighbor) for neighbor in neighbors]
        self.temperature = sum(neighbors_cost) / len(neighbors_cost) if neighbors_cost else 1

    def check_acceptance(self, cost, new_cost):
        '''
        Checa se a solução é aceita.

        :param cost: custo atual
        :param new_cost: novo custo

        :return: True se a solução é aceita, False caso contrário
        '''
        if new_cost > cost:
            return True
        else:
            acceptance_probability = math.exp((new_cost - cost) / self.temperature)
            return random.random() < acceptance_probability

    def cooling(self):
        '''
        Taxa de resfriamento.
        Fórmula: temperatura = temperatura / (1 + taxa de resfriamento * raiz quadrada da temperatura)

        :return: temperatura
        '''
        self.temperature /= (1 + self.cooling_rate * math.sqrt(self.temperature))
        return self.temperature

    def run(self):
        '''
        Executa o Simulated Annealing.

        :return: melhor solução e custo
        '''
        self.capacity, self.amount, self.profit, self.weight = self.read_file()
        self.calculate_number_of_neighbors(self.amount)

        # Gerar solução inicial antes do loop
        best_solution = self.generate_initial_solution()
        self.initial_temperature(best_solution) 
        best_cost = self.calculate_cost(best_solution)
        no_improve_count = 0  

        while self.temperature > self.T_min and no_improve_count < self.no_improve_limit:
            solution = best_solution[:] 
            cost = best_cost

            for _ in range(self.iter_max):
                neighbors = self.generate_neighbors(solution)
                for neighbor in neighbors:
                    new_cost = self.calculate_cost(neighbor)
                    if self.check_acceptance(cost, new_cost):
                        solution = neighbor
                        cost = new_cost
                        if cost > best_cost:
                            best_solution = solution
                            best_cost = cost
                            self.best_solutions_vector.append(best_solution)
                            self.best_cost_vector.append(best_cost)
                            no_improve_count = 0  # Reset se houver melhora
                        else:
                            no_improve_count += 1  # Conta quantas iterações sem melhora
            
                self.cooling()
        
        return best_solution, best_cost
