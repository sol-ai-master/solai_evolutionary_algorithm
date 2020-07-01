from datetime import datetime

import solai_evolutionary_algorithm.evolve_configurations.sol_metrics as sol_metrics
import solai_evolutionary_algorithm.evolve_configurations.sol_properties_ranges as properties_ranges
from solai_evolutionary_algorithm.crossovers.ability_swap_crossover import AbilitySwapCrossover
from solai_evolutionary_algorithm.evaluation.simulation.constrained_novelty_evaluation import \
    ConstrainedNoveltyEvaluation, InfeasibleObjective
from solai_evolutionary_algorithm.evolution.evolver_config import EvolverConfig
from solai_evolutionary_algorithm.evolution.fins_evolver import FinsEvolver
from solai_evolutionary_algorithm.evolution_end_criteria.fixed_generation_end_criteria import \
    FixedGenerationsEndCriteria
from solai_evolutionary_algorithm.initial_population_producers.from_existing_producers import FromExistingProducer
from solai_evolutionary_algorithm.initial_population_producers.random_bounded_producer import RandomBoundedProducer
from solai_evolutionary_algorithm.mutations.default_properties_mutation import default_properties_mutation
from solai_evolutionary_algorithm.plot_services.plot_generations_service import PlotGenerationsLocalService
from solai_evolutionary_algorithm.utils.character_distance_utils import create_character_distance_func


def config(
    population_size: int = 40,
    generations: int = 30,
    initial_population: str = "from_existing",  # "random"
    infeasible_objective: InfeasibleObjective = InfeasibleObjective.NOVELTY,
    feasible_boost: bool = True,
    simulation_population_count: int = 10
):
    run_label = {
        'population_size': population_size,
        'generations': generations,
        'simulate_population_count': simulation_population_count,
        'infeasible_objective': infeasible_objective.value,
        'feasible_boost': feasible_boost,
        'initial_population': initial_population
    }

    plot_filename = "__".join(
        [
            f"{key[:5]}_{value}"
            for key, value in run_label.items()
        ] + [datetime.now().strftime("%m_%d_%Y__%H_%M_%S")]
    ) + ".png"

    random_population_producer = RandomBoundedProducer(RandomBoundedProducer.Config(
        population_size=population_size,
        character_properties_ranges=properties_ranges.character_properties_ranges,
        melee_ability_ranges=properties_ranges.melee_ability_ranges,
        projectile_ability_ranges=properties_ranges.projectile_ability_ranges,
    ))

    properties_mutation = default_properties_mutation(
        probability_per_number_property=0.3,
        probability_per_bool_property=0.1,
        character_properties_ranges=properties_ranges.character_properties_ranges,
        melee_ability_ranges=properties_ranges.melee_ability_ranges,
        projectile_ability_ranges=properties_ranges.projectile_ability_ranges,
    )

    from_existing_population_producer = FromExistingProducer(
        population_size=population_size,
        chars_filename=[
            "shrankConfig.json",
            "schmathiasConfig.json",
            "brailConfig.json",
            "magnetConfig.json"
        ],
        mutation=properties_mutation
    )

    distance_func = create_character_distance_func(
        character_properties_ranges=properties_ranges.character_properties_ranges,
        melee_ability_ranges=properties_ranges.melee_ability_ranges,
        projectile_ability_ranges=properties_ranges.projectile_ability_ranges,
    )

    constrained_novelty_config = EvolverConfig(
        tag_object=run_label,
        initial_population_producer=random_population_producer if initial_population == "random"
            else from_existing_population_producer,
        fitness_evaluator=ConstrainedNoveltyEvaluation(
            simulation_characters=from_existing_population_producer()[:4],
            metrics=list(sol_metrics.feasibility_metric_ranges.keys()),
            feasible_metric_ranges=sol_metrics.feasibility_metric_ranges,
            distance_func=distance_func,
            consider_closest_count=15,
            insert_most_novel_count=5,
            infeasible_objective=infeasible_objective,
            simulation_population_count=simulation_population_count,
            queue_host="localhost",
        ),
        # population_evolver=DefaultGenerationEvolver(DefaultGenerationEvolver.PassThroughConfig),
        population_evolver=FinsEvolver(FinsEvolver.Config(
            use_crossover=True,
            use_mutation=True,
            elitism_count=1,
            infeasible_objective=infeasible_objective,
            feasible_boost=feasible_boost,
            crossover=AbilitySwapCrossover(),
            mutations=[
                properties_mutation
            ],
        )),
        end_criteria=FixedGenerationsEndCriteria(generations=generations),
        evolver_listeners=[
            #UpdateDatabaseService(),
            PlotGenerationsLocalService(
                hold_last_plot=False,
                save_plot_filename=plot_filename
            )
        ],
    )

    return constrained_novelty_config
