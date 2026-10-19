import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from analyze_raw_ratings import CELLS
from plot_ratings_comparison import bar_summary, plot_version
from plot_normalized_loss_ratings import transform


class MatchedFigures(unittest.TestCase):
    def test_summaries_and_exports(self):
        rng = np.random.default_rng(1703)
        d = pd.DataFrame(dict(age=rng.uniform(18, 88, 90), sex=['F', 'M', 'O']*30,
                              dataset=['rf1', 'ds003745']*45))
        d[CELLS] = rng.uniform(-5, 5, (90, 6))
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            for method, name in [('raw', 'raw'), ('person_zscored', 'normalized')]:
                values = transform(d, method)[CELLS].to_numpy()
                bars, tests, predictions = plot_version(d, method, out)
                np.testing.assert_allclose(bars['mean'], values.mean(axis=0))
                np.testing.assert_allclose(bars['sem'], values.std(axis=0, ddof=1)/np.sqrt(90))
                self.assertTrue(tests.n.eq(90).all())
                self.assertTrue((predictions.ci95_low <= predictions.adjusted_mean).all())
                for ext in ('png', 'svg'):
                    self.assertGreater((out/f'{name}-ratings-bars-age-contrast.{ext}').stat().st_size, 1000)
        with self.assertRaises(ValueError):
            bar_summary(d.iloc[:1])
