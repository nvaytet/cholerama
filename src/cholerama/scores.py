# SPDX-License-Identifier: BSD-3-Clause

import os
from typing import Dict

import numpy as np

from .player import Player


def read_round() -> int:
    fname = "scores.txt"
    rounds_played = 0
    if os.path.exists(fname):
        with open(fname, "r") as f:
            line = f.readline()
        rounds_played = int(line.strip())
    return rounds_played


def read_scores(players: Dict[str, Player], test: bool) -> Dict[str, int]:
    scores = {name: 0 for name in players}
    peaks = {name: 0 for name in players}
    fname = "scores.txt"
    if os.path.exists(fname) and (not test):
        with open(fname, "r") as f:
            contents = f.readlines()
        for line in contents[1:]:
            name, score, peak = line.split(":")
            scores[name] = int(score.strip())
            peaks[name] = int(peak.strip())
    return scores, peaks


def _write_scores(scores: Dict[str, int], peaks: Dict[str, int]):
    fname = "scores.txt"
    r = read_round()
    with open(fname, "w") as f:
        f.write(f"{r + 1}\n")
        for name, score in scores.items():
            f.write(f"{name}: {score} : {peaks[name]}\n")


def _print_scores(
    round_scores: Dict[str, int],
    final_scores: Dict[str, int],
    final_peaks: Dict[str, int],
):
    all_scores = [
        (team, round_scores[team], final_scores[team]) for team in final_scores
    ]
    sorted_scores = sorted(all_scores, key=lambda tup: tup[2], reverse=True)
    print("\nScores:")
    for i, (name, score, total) in enumerate(sorted_scores):
        print(
            f"{i + 1}. {name}: {total} (this round: {score}) "
            f"[peak: {final_peaks[name]}]"
        )


def finalize_scores(player_histories: Dict[str, np.ndarray], test: bool = False):
    scores, peaks = read_scores(player_histories, test=test)
    round_scores = {k: p[-1] for k, p in player_histories.items()}
    final_scores = {k: scores[k] + round_scores[k] for k in player_histories}
    final_peaks = {k: max(peaks[k], p.max()) for k, p in player_histories.items()}
    _print_scores(
        round_scores=round_scores, final_scores=final_scores, final_peaks=final_peaks
    )
    _write_scores(final_scores, final_peaks)
