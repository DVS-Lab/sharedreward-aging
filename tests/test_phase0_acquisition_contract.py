import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase0AcquisitionContract(unittest.TestCase):
    def test_source_data_are_not_tracked_by_parent_repository(self):
        patterns = (ROOT / ".gitignore").read_text().splitlines()
        self.assertIn("sourcedata/", patterns)
        gitmodules = ROOT / ".gitmodules"
        if gitmodules.exists():
            self.assertNotIn("sourcedata/ds003745", gitmodules.read_text())

    def test_download_is_limited_to_sharedreward_bold_runs(self):
        script = (ROOT / "code/get_ds003745.sh").read_text()
        self.assertIn("task-sharedreward_run-01_bold.nii.gz", script)
        self.assertIn("task-sharedreward_run-02_bold.nii.gz", script)
        self.assertNotIn('func/*task-sharedreward*', script)

    def test_fmriprep_is_limited_to_sharedreward_task(self):
        script = (ROOT / "code/run_fmriprep_ds003745.sh").read_text()
        self.assertIn("--task-id sharedreward", script)


if __name__ == "__main__":
    unittest.main()
