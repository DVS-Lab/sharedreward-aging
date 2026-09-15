"""Prove both model types start, both are waited on, and failures propagate."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ParallelTypesTest(unittest.TestCase):
    def exercise(self, level, fail):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wrapper = root / f"run_L{level}stats.sh"
            wrapper.write_text((ROOT / "code" / wrapper.name).read_text())
            unit = "ds003745|144|none|1|bold|mask|confounds" if level == 1 else "ds003745|144|none|1|2"
            (root / f"read_l{level}_manifest.py").write_text(f"print({unit!r})\n")
            act, ppi, position = ("0", "vs", 5) if level == 1 else ("act", "ppi_seed-vs", 4)
            (root / f"L{level}stats.sh").write_text(
                f'kind="${position}"\n'
                'touch "$MARKERS/$kind-started"\n'
                'for attempt in $(seq 1 100); do\n'
                f'  if [[ -f "$MARKERS/{act}-started" && -f "$MARKERS/{ppi}-started" ]]; then\n'
                '    touch "$MARKERS/$kind-finished"\n'
                f'    [[ "$kind" == "{act}" && "$FAIL_ACT" == 1 ]] && {{ echo "TEST_MODEL_FAILURE" >&2; exit 7; }}\n'
                '    exit 0\n'
                '  fi\n'
                '  sleep 0.02\n'
                'done\nexit 9\n'
            )
            manifest = root / "manifest.tsv"; manifest.touch()
            result = subprocess.run(["bash", str(wrapper), "--manifest", str(manifest),
                                     "--parallel-types", "--jobs", "1", "--log-dir", str(root / "logs")],
                                    env={**os.environ, "MARKERS": str(root), "FAIL_ACT": str(int(fail))},
                                    capture_output=True, text=True, timeout=10)
            for kind in (act, ppi):
                self.assertTrue((root / f"{kind}-finished").exists(), result.stdout + result.stderr)
            self.assertEqual(result.returncode, 1 if fail else 0, result.stdout + result.stderr)
            self.assertIn(f"up to 2 L{level} FEAT jobs", result.stdout)
            if fail:
                self.assertIn("TEST_MODEL_FAILURE", result.stderr)
                self.assertIn("BEGIN FAILED WORKER LOG TAIL", result.stderr)

    def test_l1_types_overlap(self):
        self.exercise(1, False)

    def test_l2_types_overlap(self):
        self.exercise(2, False)

    def test_l1_failure_still_waits_for_ppi(self):
        self.exercise(1, True)

    def test_l2_failure_still_waits_for_ppi(self):
        self.exercise(2, True)


if __name__ == "__main__":
    unittest.main()
