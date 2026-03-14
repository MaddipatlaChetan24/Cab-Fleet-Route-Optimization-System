import random
from typing import List
from backend.app.models.domain import Employee


class GeneticOptimizer:

    def __init__(self, distance_fn, population_size=40, generations=60):
        self.distance = distance_fn
        self.population_size = population_size
        self.generations = generations

    # -------------------------
    # Fitness = inverse distance
    # -------------------------
    def fitness(self, route: List[Employee]):
        total = 0
        for i in range(len(route)-1):
            total += self.distance(
                route[i].x, route[i].y,
                route[i+1].x, route[i+1].y
            )
        return 1 / (total + 1e-6)

    # -------------------------
    # Crossover
    # -------------------------
    def crossover(self, p1, p2):
        if len(p1) < 2: return p1
        a, b = sorted(random.sample(range(len(p1)), 2))
        child = p1[a:b]
        child += [g for g in p2 if g not in child]
        return child

    # -------------------------
    # Mutation
    # -------------------------
    def mutate(self, route):
        if len(route) < 2: return route
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
        return route

    # -------------------------
    # Improved MAIN SOLVER with Elitism and adaptive mutation
    # -------------------------
    def solve(self, employees: List[Employee]):
        if len(employees) <= 2:
            return employees

        population = [
            random.sample(employees, len(employees))
            for _ in range(self.population_size)
        ]

        best_fitness = 0
        stagnation = 0

        for gen in range(self.generations):
            population.sort(key=self.fitness, reverse=True)
            
            # Elitism: keep top 2
            new_pop = population[:2]
            
            current_best = self.fitness(population[0])
            if current_best > best_fitness:
                best_fitness = current_best
                stagnation = 0
            else:
                stagnation += 1

            # Adaptive mutation rate
            mut_rate = 0.4 if stagnation > 10 else 0.2

            while len(new_pop) < self.population_size:
                # Tournament selection
                p1 = max(random.sample(population[:20], 3), key=self.fitness)
                p2 = max(random.sample(population[:20], 3), key=self.fitness)
                
                child = self.crossover(p1, p2)

                if random.random() < mut_rate:
                    child = self.mutate(child)

                new_pop.append(child)

            population = new_pop
            if stagnation > 20: break # Convergence jump

        return population[0]