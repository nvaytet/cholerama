# SPDX-License-Identifier: BSD-3-Clause

import json
import os
from typing import Dict

import numpy as np

from .player import Player


def read_scores(players: Dict[str, Player], test: bool) -> Dict[str, int]:
    scores = {"0": {name: {"score": 0, "peak": 0} for name in players}}
    fname = "scores.json"
    if os.path.exists(fname) and (not test):
        with open(fname, "r") as f:
            scores = json.load(f)
    return scores


def _write_scores(scores: dict):
    fname = "scores.json"
    with open(fname, "w") as f:
        json.dump(scores, f)


def _print_scores(scores: dict):
    names = list(scores["0"].keys())
    sum_scores = {
        name: sum([v[name]["score"] for v in scores.values()]) for name in names
    }
    max_peaks = {
        name: max([v[name]["peak"] for v in scores.values()]) for name in names
    }
    scores_this_round = {
        name: scores[str(len(scores) - 1)][name]["score"] for name in names
    }
    sorted_names = dict(
        sorted(sum_scores.items(), key=lambda item: item[1], reverse=True)
    )
    print("\nScores:")
    for i, name in enumerate(sorted_names):
        print(
            f"{i + 1}. {name}: {sum_scores[name]} (this round: {scores_this_round[name]}) "
            f"[peak: {max_peaks[name]}]"
        )


def finalize_scores(player_histories: Dict[str, np.ndarray], test: bool = False):
    scores = read_scores(player_histories, test=test)
    round_scores = {k: int(p[-1]) for k, p in player_histories.items()}
    round_peaks = {k: int(p.max()) for k, p in player_histories.items()}
    scores[str(len(scores))] = {
        k: {"score": round_scores[k], "peak": round_peaks[k]} for k in player_histories
    }
    _print_scores(scores)
    _write_scores(scores)
