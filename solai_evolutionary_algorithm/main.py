from solai_evolutionary_algorithm.evolution.evolver import Evolver, EvolverConfig
# import solai_evolutionary_algorithm.evolve_configurations.test_config as test_config
# import solai_evolutionary_algorithm.evolve_configurations.fitness_evaluation_on_existing_character_config as fitness_evaluation_on_existing_character_config
import solai_evolutionary_algorithm.evolve_configurations.fitness_archive_config as fitness_archive_config


def main():
    evolver = Evolver()
    evolver.evolve(fitness_archive_config.fitness_archive_config)
