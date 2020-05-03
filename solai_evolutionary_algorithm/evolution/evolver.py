from dataclasses import dataclass

from solai_evolutionary_algorithm.evolution.evolution_types import InitialPopulationProducer, FitnessEvaluator, \
    PopulationEvolver, EndCriteria, Population, EvaluatedPopulation


class FixedGenerationsEndCriteria:
    def __init__(self, generations: int):
        self.generations = generations
        self.curr_generation = 0

    def __call__(self) -> bool:
        self.curr_generation += 1
        return self.generations >= self.curr_generation


@dataclass(frozen=True)
class EvolverConfig:
    initial_population_producer: InitialPopulationProducer
    fitness_evaluator: FitnessEvaluator
    population_evolver: PopulationEvolver
    end_criteria: EndCriteria


class Evolver:

    def __init__(self):
        pass

    def evolve(self, config: EvolverConfig):
        initial_population: Population = config.initial_population_producer()

        curr_population = initial_population
        generation = 0
        while True:
            evaluated_population: EvaluatedPopulation = config.fitness_evaluator(curr_population)
            new_population: Population = config.population_evolver(evaluated_population)
            if config.end_criteria():
                break

            generation += 1

            curr_population = new_population
