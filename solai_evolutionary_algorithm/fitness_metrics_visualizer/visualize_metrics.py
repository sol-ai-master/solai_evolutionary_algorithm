import collections
from dataclasses import dataclass
from itertools import chain
from statistics import mean
from typing import List, Dict, OrderedDict, Optional

from solai_evolutionary_algorithm.evaluation.simulation.simulation_fitness_evaluation import SimulationFitnessEvaluation
from solai_evolutionary_algorithm.evaluation.simulation.simulation_queue import CharacterConfig
from solai_evolutionary_algorithm.evolution.evolution_types import EvaluatedPopulation
from solai_evolutionary_algorithm.fitness_metrics_visualizer.simulation_repeater import repeat_simulate
from solai_evolutionary_algorithm.initial_population_producers.from_existing_producers import load_char_from_file
from solai_evolutionary_algorithm.utils.character_id import create_character_id
import matplotlib.pyplot as plt
import numpy as np


def plot_metrics_values_by_char_grouped(title: str, chars_name: List[str], chars_metrics_value_by_metric: List[Dict[str, List[float]]]):
    fig, axis_grid = plt.subplots(2, 2, constrained_layout=True)
    fig.suptitle(title)
    axis = axis_grid.reshape(-1)
    for plot_axes, char_name, metric_values_by_metric in zip(
            axis,
            chars_name,
            chars_metrics_value_by_metric
    ):
        plot_axes.set_title(char_name)
        metrics = list(metric_values_by_metric.keys())
        measurements = list(metric_values_by_metric.values())
        plot_axes.set_xticklabels(metrics, rotation=20, ha='right')
        plot_axes.boxplot(measurements)


def plot_metrics_values_by_char_individually(
        title: str,
        chars_name: List[str],
        chars_metrics_value_by_metric: List[Dict[str, List[float]]],
        baseline_metrics_value: Optional[Dict[str, float]] = None
):
    char_count = len(chars_name)
    metrics = list(chars_metrics_value_by_metric[0].keys())
    metrics_count = len(metrics)
    fig, axis_grid = plt.subplots(metrics_count, char_count, constrained_layout=True)

    for ax, char_name in zip(axis_grid[0], chars_name):
        ax.set_title(char_name, rotation=0, size='large')

    for ax, metric in zip(axis_grid[:, 0], metrics):
        ax.set_ylabel(metric, rotation=0, size='large', ha='right')

    for plot_metrics_axis, char_name, metric_values_by_metric in zip(
            axis_grid.T,
            chars_name,
            chars_metrics_value_by_metric
    ):
        for plot_metric_axes, (metric, metric_values) in zip(plot_metrics_axis, metric_values_by_metric.items()):
            if baseline_metrics_value is not None:
                plot_metric_axes.plot([1], [baseline_metrics_value[metric]], 'r_')
            plot_metric_axes.boxplot([metric_values], showmeans=True, meanline=True)
            plot_metric_axes.set_xticks([])

    fig.suptitle(title)


def visualize_metrics(chars: List[CharacterConfig]):
    metrics_desired_values = {
        "leadChange": 50,
        "characterWon": 0.8,
        "stageCoverage": 0.7,
        "nearDeathFrames": 700,
        "gameLength": 7200
    }
    metrics_weights = {
        "leadChange": 0.2,
        "characterWon": 0.2,
        "stageCoverage": 0.2,
        "nearDeathFrames": 0.2,
        "gameLength": 0.2
    }
    repeat_sim_data = repeat_simulate(
        chars,
        metrics_desired_values=metrics_desired_values,
        metrics_weights=metrics_weights,
        repeat=1000
    )

    # Dicts are ordered by default in python 3.7+
    chars_id = repeat_sim_data.fitnesses_by_char_id.keys()
    char_names = [
        char['name']
        for char in chars
    ]
    fitnesses = repeat_sim_data.fitnesses_by_char_id.values()
    plt.figure()
    plt.boxplot(fitnesses)
    plt.xticks(range(1, len(char_names) + 1), char_names)

    plot_metrics_values_by_char_individually(
        "Metric score",
        char_names,
        list(repeat_sim_data.metrics_score_by_char_id.values())
    )
    plot_metrics_values_by_char_individually(
        "measurements by metric by character",
        char_names,
        list(repeat_sim_data.avr_measurements_by_char_id.values()),
        baseline_metrics_value=metrics_desired_values
    )

    plt.show()


if __name__ == '__main__':
    chars_filename = [
        "existing_characters/shrankConfig.json",
        "existing_characters/schmathiasConfig.json",
        # "existing_characters/brailConfig.json",
        # "existing_characters/magnetConfig.json"
    ]
    char_configs = [
        {**load_char_from_file(char_filename), 'characterId': create_character_id()}
        for char_filename in chars_filename
    ]

    visualize_metrics(char_configs)
