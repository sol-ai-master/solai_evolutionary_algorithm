
from solai_evolutionary_algorithm.evolution.evolver import EvolutionListener
from solai_evolutionary_algorithm.database.database import Database


class UpdateDatabaseService(EvolutionListener):

    def on_start(self, config):
        self.database = Database()
        self.database.init_evolution_instance(config)

    def on_new_generation(self, evaluated_generation):
        self.database.add_character_generation(evaluated_generation)

    def on_end(self):
        pass
