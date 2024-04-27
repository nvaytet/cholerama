# SPDX-License-Identifier: BSD-3-Clause

import os
from typing import Dict

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
    scores = {p: 0 for p in players}
    peaks = {p: 0 for p in players}
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


def finalize_scores(players: Dict[str, Player], test: bool = False):
    scores, peaks = read_scores(players, test=test)
    round_scores = {k: p.ncells for k, p in players.items()}
    final_scores = {k: scores[k] + p.ncells for k, p in players.items()}
    final_peaks = {k: max(peaks[k], p.peak) for k, p in players.items()}
    _print_scores(
        round_scores=round_scores, final_scores=final_scores, final_peaks=final_peaks
    )
    _write_scores(final_scores, final_peaks)
