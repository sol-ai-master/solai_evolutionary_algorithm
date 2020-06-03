
from solai_evolutionary_algorithm.plot_services.plot_generations_service import PlotGenerationsLocalService
from solai_evolutionary_algorithm.mutations.default_properties_mutation import default_properties_mutation
from solai_evolutionary_algorithm.evolution_end_criteria.fixed_generation_end_criteria import \
    FixedGenerationsEndCriteria
import json
from pkg_resources import resource_stream
from solai_evolutionary_algorithm.initial_population_producers.random_bounded_producer import RandomBoundedProducer
from solai_evolutionary_algorithm.evolution.novelty_and_fitness_evolver import NoveltyAndFitnessEvolver
from solai_evolutionary_algorithm.evolution.novelty_evolver import NoveltyEvolver
from solai_evolutionary_algorithm.crossovers.ability_swap_crossover import AbilitySwapCrossover
from solai_evolutionary_algorithm.database.update_database_service import UpdateDatabaseService
from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation
from solai_evolutionary_algorithm.evaluation.simulation.novelty_simulation_fitness_evaluation import NoveltySimulationFitnessEvaluation
from solai_evolutionary_algorithm.evaluation.simulation.constrained_novelty_evaluation import ConstrainedNoveltyEvaluation
from solai_evolutionary_algorithm.evaluation.novel_archive import NovelArchive
from solai_evolutionary_algorithm.evaluation.fitness_archive import FitnessArchive
from solai_evolutionary_algorithm.evolution.evolver_config import EvolverConfig
from solai_evolutionary_algorithm.evolution.generation_evolver import DefaultGenerationEvolver
from solai_evolutionary_algorithm.evolution_end_criteria.fixed_generation_end_criteria import \
    FixedGenerationsEndCriteria
from solai_evolutionary_algorithm.initial_population_producers.from_existing_producers import FromExistingProducer
from solai_evolutionary_algorithm.initial_population_producers.random_bounded_producer import RandomBoundedProducer
from solai_evolutionary_algorithm.mutations.default_properties_mutation import default_properties_mutation
from solai_evolutionary_algorithm.plot_services.plot_generations_service import PlotGenerationsLocalService


random_population_producer = RandomBoundedProducer(RandomBoundedProducer.Config(
    population_size=20,
    character_properties_ranges={},
    melee_ability_ranges={},
    projectile_ability_ranges={}
))

character_properties_ranges = {"radius": (28.0, 50.0),
                               "moveVelocity": (200.0, 800.0)}

melee_ability_ranges = {
    "name": "abilityName",
    "type": "MELEE",
    "radius": (16.0, 200.0),
    "distanceFromChar": (0.0, 200.0),
    "speed": (0.0, 0.0),
    "startupTime": (10, 60),
    "activeTime": (10, 60),
    "executionTime": (0, 60),
    "endlagTime": (10, 60),
    "rechargeTime": (0, 60),
    "damage": (100.0, 1000.0),
    "baseKnockback": (10.0, 1000.0),
    "knockbackRatio": (0.1, 1.0),
    "knockbackPoint": (-500.0, 500.0),
    "knockbackTowardPoint": (False, True)
}


projectile_ability_ranges = {
    "name": "abilityName",
    "type": "PROJECTILE",
    "radius": (5, 50),
    "distanceFromChar": (0, 200),
    "speed": (100, 800),
    "startupTime": (1, 60),
    "activeTime": (20, 1000),
    "executionTime": (0, 60),
    "endlagTime": (6, 60),
    "rechargeTime": (13, 80),
    "damage": (15, 500),
    "baseKnockback": (50, 1000),
    "knockbackRatio": (0.1, 1.0),
    "knockbackPoint": (-500, 500),
    "knockbackTowardPoint": (False, True)
}

from_existing_population_producer = FromExistingProducer(
    population_size=12,
    chars_filename=[
        "shrankConfig.json",
        "schmathiasConfig.json",
        "brailConfig.json",
        "magnetConfig.json"
    ]
)

feasibility_metric_ranges = {
    "leadChange": (1, 100),
    "characterWon": (0.2, 0.6),
    "stageCoverage": (0.1, 0.7),
    "nearDeathFrames": (100, 1000),
    "gameLength": (100, 10000),
    "hitInteractions": (1, 100)
}

novel_archive = NovelArchive(NovelArchive.Config(
    novel_archive_size=10,
    nearest_neighbour_number=8,
    character_properties_ranges=character_properties_ranges,
    melee_ability_ranges=melee_ability_ranges,
    projectile_ability_ranges=projectile_ability_ranges,
))


fitness_archive = FitnessArchive(FitnessArchive.Config(
    fitness_archive_size=50,
))

constrained_novelty_config = EvolverConfig(
    initial_population_producer=from_existing_population_producer,
    # fitness_evaluator=RandomFitnessEvaluation(),
    fitness_evaluator=ConstrainedNoveltyEvaluation(
        simulation_characters=from_existing_population_producer()[:4],
        metrics=["leadChange", "characterWon",
                 "stageCoverage", "nearDeathFrames", "gameLength", "hitInteractions"],
        feasible_metric_ranges=feasibility_metric_ranges,
        novel_archive=novel_archive,
        simulation_population_count=10,
        queue_host="localhost",
    ),
    # population_evolver=DefaultGenerationEvolver(DefaultGenerationEvolver.PassThroughConfig),
    population_evolver=NoveltyEvolver(NoveltyEvolver.Config(
        crossover_share=0.4,
        mutate_only_share=0.5,
        new_individuals_share=0,
        elitism_share=0.1,
        crossover=AbilitySwapCrossover(),
        mutations=[
            default_properties_mutation(
                probability_per_number_property=0.1,
                probability_per_bool_property=0.05,
                character_properties_ranges=character_properties_ranges,
                melee_ability_ranges=melee_ability_ranges,
                projectile_ability_ranges=projectile_ability_ranges
            )
        ],
        new_individuals_producer=[]
    )),
    end_criteria=FixedGenerationsEndCriteria(generations=5),
    evolver_listeners=[
        UpdateDatabaseService(),
        # PlotGenerationsLocalService()
    ],
)
