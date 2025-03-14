from SimulatedAnnealing import SimulatedAnnealing

if __name__ == '__main__':
    sa = SimulatedAnnealing()
    solution, cost = sa.run()
    print(f'Solução: {solution}')
    print(f'Custo: {cost}')