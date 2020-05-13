from typing import Callable, List, Tuple, TypedDict, Any


Individual = Any
Population = List[Individual]

EvaluatedIndividual = TypedDict("EvaluatedIndividual", {
    'individual': Individual,
    'fitness': List[float]
})

NoveltyAndFitnessEvaluatedIndividual = TypedDict("EvaluatedIndividual", {
    'individual': Individual,
    'fitness': List[float],
    'novelty': float
})

NoveltyAndFitnessEvaluatedPopulation = List[EvaluatedIndividual]
EvaluatedPopulation = List[EvaluatedIndividual]
SubPopulation = List[Individual]

NovelArchive = Callable[[Individual], None]

FitnessEvaluation = Callable[[Population], EvaluatedPopulation]

InitialPopulationProducer = Callable[[], Population]

PopulationEvolver = Callable[[EvaluatedPopulation], Population]

CrossoverStrategy = Callable[[Population], SubPopulation]

MutationStrategy = Callable[[Population], Population]

# determine if evolution should stop
EndCriteria = Callable[[], bool]
