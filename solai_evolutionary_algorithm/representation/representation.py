import json
import random
import uuid
import os
from solai_evolutionary_algorithm.utils.useful_functions import UsefulFunctions
from pkg_resources import resource_stream
from copy import deepcopy


class Representation:

    ability_types = ["MELEE", "PROJECTILE"]
    no_of_abilities = 3
    character_config = json.load(resource_stream(
        'solai_evolutionary_algorithm', 'resources/character_config.json'))['character_config']
    melee_config = json.load(resource_stream(
        'solai_evolutionary_algorithm', 'resources/melee.json'))
    projectile_config = json.load(resource_stream(
        'solai_evolutionary_algorithm', 'resources/projectile.json'))

    ability_configs = {'MELEE': melee_config, 'PROJECTILE': projectile_config}
    useful_functions = UsefulFunctions()

    def generate_initial_population(self, n):
        return 0

    def generate_random_character_file(self):
        new_character = self.generate_random_character()
        file_name = "character_" + new_character["characterId"] + ".json"
        path = "./sample_characters/"
        with open(path + file_name, 'w', encoding='utf-8') as output_file:
            json.dump(new_character, output_file, ensure_ascii=False, indent=4)

    def generate_random_character_for_runtime(self):
        new_character = self.generate_random_character()
        return new_character

    def generate_random_character(self):
        no_of_abilites = self.no_of_abilities
        new_character = {}
        new_character["characterId"] = str(uuid.uuid1())
        config = self.character_config

        min_radius = config["radius"][0]
        max_radius = config["radius"][1]
        radius = random.randint(min_radius, max_radius)
        new_character["radius"] = radius

        min_moveVelocity = config["moveVelocity"][0]
        max_moveVelocity = config["moveVelocity"][1]
        moveVelocity = random.randint(min_moveVelocity, max_moveVelocity)
        new_character["moveVelocity"] = moveVelocity
        new_character["abilities"] = []

        for _ in range(no_of_abilites):
            new_character["abilities"].append(self.__generate_random_ability())

        return new_character

    def clone_character(self, genome):
        character_copy = deepcopy(genome)
        character_copy['characterId'] = str(uuid.uuid1())
        return character_copy

    def generate_random_ability():
        ability_type = self.ability_types[random.randint(
            0, len(self.ability_types)-1)]
        return generate_random_ability_by_type(ability_type)

    def generate_random_ability_by_type(type):
        ability = {}
        data = self.ability_configs[ability_type]
        ability["type"] = data["type"]
        for attribute in data:
            if attribute not in ability:
                min_value = data[attribute][0]
                max_value = data[attribute][1]
                if type(min_value) == int:
                    ability[attribute] = random.randint(
                        min_value, max_value)
                elif type(min_value) == float:
                    ability[attribute] = random.uniform(
                        min_value, max_value)
                elif type(min_value) == bool or type(min_value) == str:
                    no_values = len(data[attribute])
                    ability[attribute] = data[attribute][random.randint(
                        0, no_values-1)]

        return ability

    def euclidean_distance(self, genome1, genome2):
        normalize_genome = self.useful_functions.normalize_genome
        normalized_genome1 = normalize_genome(genome1)
        normalized_genome2 = normalize_genome(genome2)

        genome1_abilities = normalized_genome1['abilities']
        genome2_abilities = normalized_genome2['abilities']

        distance = 0

        for ability1, ability2 in zip(genome1_abilities, genome2_abilities):
            genome1_abilities[ability1]
            distance += self.euclidean_distance_ability(
                genome1_abilities[ability1], genome2_abilities[ability2])

        return distance

    def euclidean_distance_ability(self, ability1, ability2):
        if ability1['type'] != ability2['type']:
            return 10
        distance = 0
        for attribute in ability1:
            if type(ability1[attribute]) == str:
                continue
            distance += (ability1[attribute] - ability2[attribute])**2
        return distance

    def change_random_ability_of_character(self, character_config):
        ability_number = random.randint(
            0, len(character_config['abilities'])-1)

        character_config['abilities'][ability_number] = self.__generate_random_ability(
        )
