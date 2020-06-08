import solai_evolutionary_algorithm.evolve_configurations.sol_metrics as sol_metrics
import solai_evolutionary_algorithm.evolve_configurations.sol_properties_ranges as properties_ranges
from solai_evolutionary_algorithm.crossovers.ability_swap_crossover import AbilitySwapCrossover
from solai_evolutionary_algorithm.evaluation.novel_archive import NovelArchive
from solai_evolutionary_algorithm.evaluation.simulation.constrained_novelty_evaluation import \
    ConstrainedNoveltyEvaluation
from solai_evolutionary_algorithm.evolution.evolver_config import EvolverConfig
from solai_evolutionary_algorithm.evolution.fins_evolver import FinsEvolver
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

from_existing_population_producer = FromExistingProducer(
    population_size=12,
    chars_filename=[
        "shrankConfig.json",
        "schmathiasConfig.json",
        "brailConfig.json",
        "magnetConfig.json"
    ]
)

novel_archive = NovelArchive(NovelArchive.Config(
    novel_archive_size=10,
    nearest_neighbour_number=8,
    character_properties_ranges=properties_ranges.character_properties_ranges,
    melee_ability_ranges=properties_ranges.melee_ability_ranges,
    projectile_ability_ranges=properties_ranges.projectile_ability_ranges,
))


constrained_novelty_config = EvolverConfig(
    initial_population_producer=from_existing_population_producer,
    # fitness_evaluator=RandomFitnessEvaluation(),
    fitness_evaluator=ConstrainedNoveltyEvaluation(
        simulation_characters=from_existing_population_producer()[:4],
        metrics=list(sol_metrics.feasibility_metric_ranges.keys()),
        feasible_metric_ranges=sol_metrics.feasibility_metric_ranges,
        novel_archive=novel_archive,
        simulation_population_count=1,
        queue_host="localhost",
    ),
    # population_evolver=DefaultGenerationEvolver(DefaultGenerationEvolver.PassThroughConfig),
    population_evolver=FinsEvolver(FinsEvolver.Config(
        crossover_share=0.4,
        mutate_only_share=0.5,
        new_individuals_share=0,
        elitism_share=0.1,
        crossover=AbilitySwapCrossover(),
        mutations=[
            default_properties_mutation(
                probability_per_number_property=0.1,
                probability_per_bool_property=0.05,
                character_properties_ranges=properties_ranges.character_properties_ranges,
                melee_ability_ranges=properties_ranges.melee_ability_ranges,
                projectile_ability_ranges=properties_ranges.projectile_ability_ranges,
            )
        ],
        new_individuals_producer=None
    )),
    end_criteria=FixedGenerationsEndCriteria(generations=20),
    evolver_listeners=[
        # UpdateDatabaseService(),
        PlotGenerationsLocalService()
    ],
)
