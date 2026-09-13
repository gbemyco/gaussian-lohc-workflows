import tempfile
import unittest
from pathlib import Path

from lohcflow.parser import extract_lp_n_to_bd_star, extract_npa, parse_log
from lohcflow.thermo import dehydrogenation_energy, hydrogen_capacity


SAMPLE = """
 SCF Done:  E(RwB97XD) =  -100.000000D+00 A.U. after 12 cycles
 Zero-point correction= 0.200000
 Thermal correction to Gibbs Free Energy= 0.150000
 Frequencies -- -25.0 100.0 200.0
 Summary of Natural Population Analysis:
 C 1 -0.250000 1.9 4.3 0.0 6.25
 N 2 -0.410000 1.9 5.4 0.0 7.41
 125. LP ( 1) N  2          / 261. BD*( 1) C  4 - H  5       11.47  0.75  0.08
 Normal termination of Gaussian 16
"""


class GaussianTests(unittest.TestCase):
    def test_parse_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.log"
            path.write_text(SAMPLE)
            result = parse_log(path)
        self.assertEqual(result.electronic_hartree, -100.0)
        self.assertEqual(result.gibbs_hartree, -99.85)
        self.assertEqual(result.imaginary_frequencies, 1)
        self.assertTrue(result.normal_termination)

    def test_npa(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.log"
            path.write_text(SAMPLE)
            rows = extract_npa(path)
        self.assertEqual(rows[1]["atom"], 2)
        self.assertAlmostEqual(rows[1]["natural_charge"], -0.41)

    def test_selected_nbo_interaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.log"
            path.write_text(SAMPLE)
            rows = extract_lp_n_to_bd_star(path)
        self.assertEqual(rows[0]["donor"], "N2")
        self.assertEqual(rows[0]["acceptor"], "C4-H5")
        self.assertAlmostEqual(rows[0]["e2_kcal_mol"], 11.47)

    def test_thermochemistry(self):
        total, average = dehydrogenation_energy(-79.5, -78.85, -1.15, 1)
        self.assertAlmostEqual(total, -1312.7498195)
        self.assertEqual(total, average)
        self.assertGreater(hydrogen_capacity("C14H25N", 12), 5.0)


if __name__ == "__main__":
    unittest.main()
