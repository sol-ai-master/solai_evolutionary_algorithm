import sys
from typing import List, Optional, Any, Dict, TypedDict, Iterable, cast, Tuple, OrderedDict
from solai_evolutionary_algorithm.evaluation.simulation.simulation_queue import SimulationQueue, SimulationData, \
    CharacterConfig, SimulationResult

from solai_evolutionary_algorithm.evolution.evolution_types import FitnessEvaluation, EvaluatedPopulation, Population
from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation
from solai_evolutionary_algorithm.evolution.evolution_types import Population, FitnessEvaluation, EvaluatedPopulation, \
    EvaluatedIndividual, NovelArchive

from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation, \
    EvaluatedMetrics, SimulationMeasurements, CharacterAllMeasurements, CharactersAllMeasurements, MetricsByCharacter

from solai_evolutionary_algorithm.utils.kwargs_utils import filter_not_none_values
from statistics import mean


class ConstrainedNoveltyEvaluation(SimulationFitnessEvaluation):

    """
    feasible_metric_ranges: The ranges of a simulation result that determines an individual feasible or infeasible.
    minimum_required_feasible_metric_percentage: The percentage of metrics that must fall into the feasible metric ranges.
    """

    def __init__(self,
                 metrics: List[str],
                 simulation_characters: List,
                 feasible_metric_ranges: Dict[str, Tuple],
                 queue_host: Optional[str] = None,
                 queue_port: Optional[str] = None,
                 minimum_required_feasible_metric_percentage: Optional[float] = 1.0,
                 simulation_population_count: Optional[int] = 1,
                 ):

        self.metrics = metrics
        self.simulation_characters = simulation_characters
        self.feasible_metric_ranges = feasible_metric_ranges

        self.simulation_queue = SimulationQueue(
            **filter_not_none_values({
                'host': queue_host,
                'port': queue_port
            })
        )

        self.minimum_required_feasible_metric_percentage = minimum_required_feasible_metric_percentage
        self.simulation_population_count = simulation_population_count

    def __call__(self, population: Population) -> EvaluatedPopulation:
        return self.evaluate_one_population(population)

    def evaluate_one_population(self, population: Population) -> EvaluatedPopulation:
        simulations_results = self.simulate_population(
            population, self.simulation_queue)

        simulations_measurements = self.simulation_results_to_simulation_measurements(
            simulations_results)

        all_measurements_by_character: CharacterAllMeasurements = self.group_all_measures_by_character(
            simulations_measurements)

        feasibility_of_population = self.evaluate_feasibility_of_population(
            all_measurements_by_character)

        evaluated_population: EvaluatedPopulation = [
            EvaluatedIndividual(
                individual=individual,
                feasible=feasibility_of_population[individual['characterId']]
            )
            for individual in population
        ]

        return evaluated_population

    def simulate_population(self, population: Population, simulation_queue: SimulationQueue) -> List[SimulationResult]:

        character_pairs: List[Tuple[CharacterConfig, CharacterConfig]] = [
            (individual, opponent)
            for opponent in self.simulation_characters
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

    def evaluate_feasibility_of_population(self, measurements_by_character):
        evaluated_population = {individual: self.is_feasible(
            measurements) for individual, measurements in measurements_by_character.items()}
        return evaluated_population

    def is_feasible(self, character_simulation_result) -> bool:
        mean_simulation_results = {metric: mean(metric_result) for (
            metric, metric_result) in character_simulation_result.items()}
        feasible_number = len(list(filter(None, map(lambda x: self.is_feasible_metric_result(
            x[0], x[1]), mean_simulation_results.items()))))
        return feasible_number/len(character_simulation_result) >= self.minimum_required_feasible_metric_percentage

    def is_feasible_metric_result(self, metric, metric_result):
        return metric_result >= self.feasible_metric_ranges[metric][0] and metric_result <= self.feasible_metric_ranges[metric][1]
