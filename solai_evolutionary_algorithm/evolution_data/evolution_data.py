import os
from datetime import datetime
from typing import Dict
from solai_evolutionary_algorithm.utils.character_distance_utils import create_character_distance_func
from solai_evolutionary_algorithm.evolve_configurations.sol_properties_ranges import character_properties_ranges, melee_ability_ranges, projectile_ability_ranges
from itertools import combinations
import random
from statistics import mean

import pymongo


USERNAME = "haraldvinje"
PASSWORD = os.environ["SOLAI_DB_PASSWORD"]
CLUSTER_URL = "mongodb+srv://" + USERNAME + ":" + PASSWORD + \
    "@cluster0-dzimv.mongodb.net/test?retryWrites=true&w=majority"


class ReadOnlyDatabase:

    def __init__(self):
        self.client = pymongo.MongoClient(CLUSTER_URL)
        self.database = self.client.solai
        self.evolution_instances = self.database.evolution_instances

    def get_FINS_with_random_init_pop_instances(self):
        return self.evolution_instances.find({'$and': [{'evolutionConfig.tag_object.infeasible_objective': "FEASIBILITY"},
                                                       {'evolutionConfig.tag_object.initial_population': "random"},
                                                       {"generations.25": {"$exists": "true"}}]},
                                             {'generations'})

    def get_FINS_with_existing_init_pop_instances(self):
        return self.evolution_instances.find({'$and': [{'evolutionConfig.tag_object.infeasible_objective': "FEASIBILITY"},
                                                       {'evolutionConfig.tag_object.initial_population': "from_existing"},
                                                       {"generations.25": {"$exists": "true"}}]},
                                             {'generations'})

    def get_FI2NS_with_random_init_pop_instances(self):
        return self.evolution_instances.find({'$and': [{'evolutionConfig.tag_object.infeasible_objective': "NOVELTY"},
                                                       {'evolutionConfig.tag_object.initial_population': "random"},
                                                       {"generations.25": {"$exists": "true"}}]},
                                             {'generations'})

    def get_FI2NS_with_existing_init_pop_instances(self):
        return self.evolution_instances.find({'$and': [{'evolutionConfig.tag_object.infeasible_objective': "NOVELTY"},
                                                       {'evolutionConfig.tag_object.initial_population': "from_existing"},
                                                       {"generations.25": {"$exists": "true"}}]},
                                             {'generations'})


def filter_feasible_from_population(population):
    return list(filter(lambda individual: individual['feasibility_score'] == 1, population))


normalized_euclidean_distance = create_character_distance_func(
    character_properties_ranges=character_properties_ranges,
    melee_ability_ranges=melee_ability_ranges,
    projectile_ability_ranges=projectile_ability_ranges)


def avg_diversity_of_populations(populations) -> float:
    return mean([diversity(population) for population in populations.values()])


def average_largest_population_diversity(populations, method):
    population_distances = [
        larges_permutation_diversity(population)
        for population in populations
    ]
    average_distance = mean(map(lambda x: x[1], population_distances))
    max_population_with_distance = max(
        population_distances, key=lambda x: x[1])

    for char in max_population_with_distance[0]:
        print(char['individual']['characterId'])

    print(method)


def larges_permutation_diversity(population) -> float:
    populations_of_6 = list(combinations(population, 6))
    permutation_distances = [
        (sub_population, diversity(sub_population))
        for sub_population in populations_of_6
    ]

    return max(permutation_distances, key=lambda pop: pop[1])


def diversity(population):
    return sum([normalized_euclidean_distance(
        char1['individual'],
        char2['individual'])
        for (char1, char2) in combinations(population, 2)])


def get_stats_from_evolution_instances(instance, method: str):
    last_generation_feasible_individuals = []
    for (i, e) in enumerate(instance):
        feasible_population = filter_feasible_from_population(
            e['generations'][-1])
        last_generation_feasible_individuals.append(feasible_population)
        print(
            f"feasible individuals in last generation of method {method}: \n {len(feasible_population)}")
    print()
    return last_generation_feasible_individuals


read_only_db = ReadOnlyDatabase()

FINS_w_random_evolutions = read_only_db.get_FINS_with_random_init_pop_instances()
FINS_w_existing_evolutions = read_only_db.get_FINS_with_existing_init_pop_instances()
FI2NS_w_random_evolutions = read_only_db.get_FI2NS_with_random_init_pop_instances()
FI2NS_w_existing_evolutions = read_only_db.get_FI2NS_with_existing_init_pop_instances()

last_generation_feasible_individuals_FINS_w_random = get_stats_from_evolution_instances(
    FINS_w_random_evolutions, "FINS w random")
last_generation_feasible_individuals_FINS_w_existing = get_stats_from_evolution_instances(
    FINS_w_existing_evolutions, "FINS w existing")
last_generation_feasible_individuals_FI2NS_w_random = get_stats_from_evolution_instances(
    FI2NS_w_random_evolutions, "FI2NS w random")
last_generation_feasible_individuals_FI2NS_w_existing = get_stats_from_evolution_instances(
    FI2NS_w_existing_evolutions, "FI2NS w existing")


most_diverse_pop_of_6_FINS_random = average_largest_population_diversity(
    last_generation_feasible_individuals_FINS_w_random, "FINS w random")

most_diverse_pop_of_6_FINS_existing = average_largest_population_diversity(
    last_generation_feasible_individuals_FINS_w_existing, "FINS w existing")

most_diverse_pop_of_6_FI2NS_random = average_largest_population_diversity(
    last_generation_feasible_individuals_FI2NS_w_random, "FI2NS w random")

most_diverse_pop_of_6_FI2NS_existing = average_largest_population_diversity(
    last_generation_feasible_individuals_FI2NS_w_existing, "FI2NS w existing")
