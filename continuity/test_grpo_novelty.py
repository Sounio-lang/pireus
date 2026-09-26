#!/usr/bin/env python3
"""M8 reward-map tests. The class decision is not made here."""
import json
import subprocess
import unittest
from pathlib import Path

import grpo_reward_engine as engine


def receipt(distance, visited, holdout, class_id):
    return {
        "decision": "CLASSIFIED",
        "corpus_distance": distance,
        "train_visited": visited,
        "holdout": holdout,
        "class_id": class_id,
        "split": "holdout" if holdout else "train",
    }


class NoveltyMapTest(unittest.TestCase):
    def test_nonzero_phase_in_visited_class_is_not_full_novelty(self):
        # M5 phase 1128 is nonzero and still in a visited class.
        graded = engine.novelty_from_classification(receipt(130, 1, 0, 26))
        self.assertEqual(graded["novelty_reward"], 0.15)
        self.assertNotEqual(graded["novelty_reward"], 0.5)

    def test_corpus_operator_stays_low(self):
        graded = engine.novelty_from_classification(receipt(0, 1, 0, 0))
        self.assertEqual(graded["novelty_reward"], 0.1)

    def test_unvisited_distance_is_graded(self):
        near = engine.novelty_from_classification(receipt(108, 0, 0, 5))
        far = engine.novelty_from_classification(receipt(130, 0, 0, 29))
        self.assertLess(near["novelty_reward"], far["novelty_reward"])
        self.assertAlmostEqual(far["novelty_reward"], 0.5)
        self.assertAlmostEqual(near["novelty_reward"], 0.2 + 0.3 * 108 / 130)

    def test_holdout_adds_no_training_reward(self):
        graded = engine.novelty_from_classification(receipt(120, 0, 1, 1))
        self.assertEqual(graded["novelty_reward"], 0.0)
        self.assertGreater(graded["held_out_novelty"], 0.0)
        self.assertEqual(graded["split"], "holdout")

    def test_mixed_batch_advantage_is_not_degenerate(self):
        rows = []
        for item in (
            receipt(0, 1, 0, 0),
            receipt(130, 1, 0, 26),
            receipt(108, 0, 0, 5),
            receipt(130, 0, 0, 29),
            receipt(120, 0, 1, 1),
        ):
            graded = engine.novelty_from_classification(item)
            rows.append({"reward": 0.5 + graded["novelty_reward"], "split": graded["split"]})
        engine.evaluate_group_relative_advantages(rows)
        self.assertGreater(len({round(row["advantage"], 6) for row in rows}), 1)
        self.assertTrue(any(row["advantage"] != 0.0 for row in rows))

    def test_live_oracle_when_present(self):
        binary = Path("/tmp/pireus_novelty_oracle.elf")
        if not binary.is_file():
            self.skipTest("native oracle is built on the Sounio workspace")
        expected = {
            "0": {"class_id": 0, "train_visited": 1, "holdout": 0, "corpus_distance": 0},
            "1128": {"class_id": 26, "train_visited": 1, "holdout": 0, "corpus_distance": 130},
            "32841": {"class_id": 29, "train_visited": 0, "holdout": 0, "corpus_distance": 130},
            "1": {"class_id": 1, "train_visited": 0, "holdout": 1, "corpus_distance": 8},
            "32768": {"class_id": 2, "train_visited": 0, "holdout": 1},
        }
        for phase, want in expected.items():
            proc = subprocess.run([str(binary), phase], capture_output=True, text=True, check=True)
            got = json.loads(proc.stdout)
            for key, value in want.items():
                self.assertEqual(got[key], value, phase)


if __name__ == "__main__":
    unittest.main()
