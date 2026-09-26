#!/usr/bin/env python3
"""M8 reward-map tests. The class decision is not made here."""
import json
import subprocess
import unittest
from pathlib import Path

import grpo_reward_engine as engine


def receipt(distance, visited, holdout, class_id, novelty_milli, graded_milli):
    return {
        "decision": "CLASSIFIED",
        "corpus_distance": distance,
        "train_visited": visited,
        "holdout": holdout,
        "class_id": class_id,
        "split": "holdout" if holdout else "train",
        "novelty_milli": novelty_milli,
        "graded_milli": graded_milli,
    }


class NoveltyMapTest(unittest.TestCase):
    def test_nonzero_phase_in_visited_class_is_not_full_novelty(self):
        # M5 phase 1128 is nonzero and still in a visited class.
        graded = engine.novelty_from_classification(receipt(130, 1, 0, 26, 150, 500))
        self.assertEqual(graded["novelty_reward"], 0.15)
        self.assertNotEqual(graded["novelty_reward"], 0.5)

    def test_corpus_operator_stays_low(self):
        graded = engine.novelty_from_classification(receipt(0, 1, 0, 0, 100, 200))
        self.assertEqual(graded["novelty_reward"], 0.1)

    def test_unvisited_distance_is_graded(self):
        near = engine.novelty_from_classification(receipt(108, 0, 0, 5, 449, 449))
        far = engine.novelty_from_classification(receipt(130, 0, 0, 29, 500, 500))
        self.assertLess(near["novelty_reward"], far["novelty_reward"])
        self.assertAlmostEqual(far["novelty_reward"], 0.5)
        self.assertEqual(near["novelty_reward"], 0.449)

    def test_holdout_adds_no_training_reward(self):
        graded = engine.novelty_from_classification(receipt(120, 0, 1, 1, 0, 476))
        self.assertEqual(graded["novelty_reward"], 0.0)
        self.assertGreater(graded["held_out_novelty"], 0.0)
        self.assertEqual(graded["split"], "holdout")

    def test_mixed_batch_advantage_is_not_degenerate(self):
        rewards = []
        for item in (
            receipt(0, 1, 0, 0, 100, 200),
            receipt(130, 1, 0, 26, 150, 500),
            receipt(108, 0, 0, 5, 449, 449),
            receipt(130, 0, 0, 29, 500, 500),
            receipt(120, 0, 1, 1, 0, 476),
        ):
            graded = engine.novelty_from_classification(item)
            rewards.append(500 + int(item["novelty_milli"] if graded["split"] == "train" else 0))
        count = len(rewards)
        total = sum(rewards)
        deviations = [count * reward - total for reward in rewards]
        self.assertGreater(len(set(deviations)), 1)
        self.assertTrue(any(deviation != 0 for deviation in deviations))

    def test_published_eight_have_nonzero_integer_moment(self):
        rewards = (600, 650, 949, 1000, 500, 500, 500, 500)
        total = sum(rewards)
        centered = sum((len(rewards) * reward - total) ** 2 for reward in rewards)
        deviations = [len(rewards) * reward - total for reward in rewards]
        self.assertEqual(total, 5199)
        self.assertEqual(centered, 19481656)
        self.assertEqual(deviations, [-399, 1, 2393, 2801, -1199, -1199, -1199, -1199])
        self.assertEqual([reward / 1000 for reward in rewards], [0.6, 0.65, 0.949, 1.0, 0.5, 0.5, 0.5, 0.5])
        self.assertNotEqual(centered, 0)
        self.assertEqual(len(rewards) ** 3, 512)

    def test_component_split_follows_the_native_total(self):
        row = {}
        engine.apply_reward_milli(row, 949)
        self.assertEqual((row["syntax_reward"], row["admission_reward"], row["novelty_reward"], row["reward"]), (0.1, 0.4, 0.449, 0.949))
        refused = {}
        engine.apply_reward_milli(refused, 100)
        self.assertEqual((refused["syntax_reward"], refused["admission_reward"], refused["novelty_reward"]), (0.1, 0.0, 0.0))

    def test_live_group_variance_when_present(self):
        binary = Path("/tmp/pireus_group_variance.elf")
        if not binary.is_file():
            self.skipTest("native group variance is built on the Sounio workspace")
        stats = engine.group_statistics(binary, [600, 650, 949, 1000, 500, 500, 500, 500])
        self.assertFalse(stats["degenerate"])
        self.assertEqual(stats["reward_sum"], 5199)
        self.assertEqual(stats["centered_sum_squares"], 19481656)
        self.assertEqual(stats["variance_denominator"], 512)
        self.assertEqual(stats["centered_deviation"], [-399, 1, 2393, 2801, -1199, -1199, -1199, -1199])

    def test_live_oracle_when_present(self):
        binary = Path("/tmp/pireus_novelty_oracle.elf")
        if not binary.is_file():
            self.skipTest("native oracle is built on the Sounio workspace")
        expected = {
            "0": {"class_id": 0, "train_visited": 1, "holdout": 0, "corpus_distance": 0, "novelty_milli": 100, "admitted_reward_milli": 600},
            "1128": {"class_id": 26, "train_visited": 1, "holdout": 0, "corpus_distance": 130, "novelty_milli": 150, "admitted_reward_milli": 650},
            "32841": {"class_id": 29, "train_visited": 0, "holdout": 0, "corpus_distance": 130, "novelty_milli": 500, "admitted_reward_milli": 1000},
            "1": {"class_id": 1, "train_visited": 0, "holdout": 1, "corpus_distance": 8, "novelty_milli": 0, "graded_milli": 218, "admitted_reward_milli": 500},
            "32768": {"class_id": 2, "train_visited": 0, "holdout": 1, "novelty_milli": 0},
        }
        for phase, want in expected.items():
            proc = subprocess.run([str(binary), phase], capture_output=True, text=True, check=True)
            got = json.loads(proc.stdout)
            for key, value in want.items():
                self.assertEqual(got[key], value, phase)


if __name__ == "__main__":
    unittest.main()
