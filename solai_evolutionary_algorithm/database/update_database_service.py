
from solai_evolutionary_algorithm.evolution.evolver_listener import EvolverListener
from solai_evolutionary_algorithm.database.database import Database


class UpdateDatabaseService(EvolverListener):

    def on_start(self, config):
        self.database = Database()
        self.database.init_evolution_instance(config)

    def on_new_generation(self, evaluated_generation, is_last_generation):
        self.database.add_character_generation(evaluated_generation)

    def on_end(self, novel_archive):
        self.database.add_novel_archive(novel_archive)
        self.database.end_evolution_instance()
