from solai_evolutionary_algorithm.evaluation.random_fitness_evaluation import RandomFitnessEvaluation
from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation
from solai_evolutionary_algorithm.evolution.evolver import EvolverConfig, FixedGenerationsEndCriteria
from solai_evolutionary_algorithm.evolution.generation_evolver import DefaultGenerationEvolver
from solai_evolutionary_algorithm.initial_population_producers.random_bounded_producer import RandomBoundedProducer


test_config = EvolverConfig(
    initial_population_producer=RandomBoundedProducer(RandomBoundedProducer.Config(
        population_size=10,
        character_properties_ranges={},
        melee_ability_ranges={},
        projectile_ability_ranges={}
    )),
    # fitness_evaluator=RandomFitnessEvaluation(),
    fitness_evaluator=SimulationFitnessEvaluation(
        metrics=["gameLength"],
        queue_host="localhost"
    ),
    population_evolver=DefaultGenerationEvolver(DefaultGenerationEvolver.PassThroughConfig),
    # population_evolver=DefaultGenerationEvolver(DefaultGenerationEvolver.Config(
    #     population_orderer=None,
    #     crossover_share=0,
    #     elitism_share=0,
    #     new_individuals_share=0,
    #     crossover=None,
    #     mutations=[],
    #     new_individuals_producer=None
    # )),
    end_criteria=FixedGenerationsEndCriteria(generations=10)
)