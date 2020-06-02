from solai_evolutionary_algorithm.utils.kwargs_utils import filter_not_none_values
from copy import deepcopy
from functools import reduce
from itertools import combinations, chain
from statistics import mean
from typing import List, Optional, Any, Dict, TypedDict, Iterable, cast, Tuple, OrderedDict

from solai_evolutionary_algorithm.evaluation.simulation.simulation_queue import SimulationQueue, SimulationData, \
    CharacterConfig, SimulationResult
from solai_evolutionary_algorithm.evolution.evolution_types import Population, FitnessEvaluation, EvaluatedPopulation, \
    EvaluatedIndividual, NovelArchive
from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation, \
    EvaluatedMetrics, SimulationMeasurements, CharacterAllMeasurements, CharactersAllMeasurements, MetricsByCharacter


class NoveltySimulationFitnessEvaluation(SimulationFitnessEvaluation):

    def __init__(
            self,
            novel_archive: NovelArchive,
            metrics: List[str],
            metrics_weights: Dict[str, float],
            desired_values: Dict[str, float],
            simulation_population_count: int,
            queue_host: Optional[str] = None,
            queue_port: Optional[int] = None,
    ):
        super(NoveltySimulationFitnessEvaluation, self).__init__(
            metrics=metrics,
            metrics_weights=metrics_weights,
            desired_values=desired_values,
            simulation_population_count=simulation_population_count,
            queue_host=queue_host,
            queue_port=queue_port
        )
        self.novel_archive = novel_archive

    def __call__(self, population: Population) -> EvaluatedPopulation:
        return self.evaluate_one_population(population)

    def evaluate_one_population(self, population: Population) -> EvaluatedPopulation:

        if not self.novel_archive.get_all_individuals():

            evaluated_population: EvaluatedPopulation = [
                EvaluatedIndividual(
                    individual=individual,
                    fitness=[0]
                )
                for individual in population
            ]
            return evaluated_population

        simulations_results = self.simulate_population(
            population, self.simulation_queue)
        self.__prev_simulation_results = simulations_results

        simulations_measurements = self.simulation_results_to_simulation_measurements(
            simulations_results)

        all_measurements_by_character: CharactersAllMeasurements =\
            self.group_all_measures_by_character(simulations_measurements)
        self.__prev_measures_by_character_id = all_measurements_by_character

        metric_fitness_by_character = self.evaluate_fitness_all_characters(
            all_measurements_by_character)

        evaluated_population: EvaluatedPopulation = [
            EvaluatedIndividual(
                individual=individual,
                fitness=[metric_fitness_by_character[individual['characterId']]]
            )
            for individual in population
        ]

        fitness_by_character_id = {
            evaluated_individual['individual']['characterId']: evaluated_individual['fitness']
            for evaluated_individual in evaluated_population
        }
        print(f"Population fitness: {fitness_by_character_id}")

        return evaluated_population

    def simulate_population(self, population: Population, simulation_queue: SimulationQueue) -> List[SimulationResult]:
        character_pairs: List[Tuple[CharacterConfig, CharacterConfig]] = [
            (individual, novel_individual['individual'])
            for novel_individual in self.novel_archive.get_all_individuals()
            for individual in population
        ]

        all_simulation_pairs = self.simulation_population_count*character_pairs

        current_simulations_data = [
            SimulationData(
                simulationId=simulation_queue.create_simulation_id(),
                charactersConfigs=char_pair,
                metrics=self.metrics
            )
            for char_pair in all_simulation_pairs
        ]

        print(
            f"Pushing {len(current_simulations_data)} simulations, waiting for simulation results...\n\n")
        simulations_result = simulation_queue.push_simulations_data_wait_results(
            current_simulations_data)

        return simulations_result

    def serialize(self):
        config = {'metrics': self.metrics,
                  'desiredValues': self.desired_values, 'metricsWeights': self.metrics_weights}
        return config
