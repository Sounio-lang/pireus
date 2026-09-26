#!/usr/bin/env python3
"""Exhaustive behavioral check of group_variance.sio against integer arithmetic.

Vectors cover the published batch, degenerate groups, single rows, maximum
rewards, and boundary rewards. Each result is compared against Python integer
arithmetic. No float is consulted.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

VECTORS = (
    ([600, 650, 949, 1000, 500, 500, 500, 500], "published_eight"),
    ([100, 100, 100, 100, 100, 100, 100, 100], "degenerate_eight"),
    ([0, 0, 0], "degenerate_zero"),
    ([1000], "single_maximum"),
    ([0], "single_zero"),
    ([0, 1000], "two_extremes"),
    ([500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500], "sixteen_equal"),
    ([0, 1, 2, 3, 4, 5, 6, 7], "eight_small"),
    ([1000, 0, 1000, 0, 1000, 0, 1000, 0], "alternating"),
    ([800, 100, 500, 500], "mixed_fragments"),
)


def expected_stats(rewards):
    count = len(rewards)
    total = sum(rewards)
    deviations = [count * reward - total for reward in rewards]
    centered = sum(d * d for d in deviations)
    return {
        "count": count,
        "reward_sum": total,
        "centered_sum_squares": centered,
        "variance_numerator": centered,
        "variance_denominator": count ** 3,
        "degenerate": centered == 0,
        "centered_deviation": deviations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    args = parser.parse_args()
    mismatches = []
    started = time.perf_counter()
    for rewards, label in VECTORS:
        proc = subprocess.run(
            [str(args.oracle), *[str(reward) for reward in rewards]],
            capture_output=True, text=True, check=True,
        )
        got = json.loads(proc.stdout)
        want = expected_stats(rewards)
        if (
            got.get("decision") != "COMPUTED"
            or got.get("claim_ready") is not False
            or int(got.get("count", -1)) != want["count"]
            or int(got.get("reward_sum", -1)) != want["reward_sum"]
            or int(got.get("centered_sum_squares", -1)) != want["centered_sum_squares"]
            or int(got.get("variance_numerator", -1)) != want["variance_numerator"]
            or int(got.get("variance_denominator", -1)) != want["variance_denominator"]
            or bool(got.get("degenerate")) != want["degenerate"]
            or [int(x) for x in got.get("centered_deviation", [])] != want["centered_deviation"]
        ):
            mismatches.append({"label": label, "rewards": rewards, "got": got, "want": want})
            if len(mismatches) == 5:
                break
    if mismatches:
        raise SystemExit(json.dumps(mismatches, indent=2))
    print(json.dumps({
        "status": "PASS",
        "vectors_checked": len(VECTORS),
        "mismatches": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
