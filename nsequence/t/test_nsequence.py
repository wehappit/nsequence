import unittest

from ..nsequence import NSequence, NSequenceException

class TestNSequence(unittest.TestCase):

    def setUp(self):
        self.nsequence = NSequence(
            func=lambda x: 2 * x,
            initial_position=1,
        )

    def tearDown(self):
        del self.nsequence

    def test_should_instantiate_nsequence(self):
        nsequence = NSequence(
            func=lambda x: x,
            initial_position=1,
        )

        self.assertIsInstance(nsequence, NSequence)

    def test_should_compute_nth_term(self):
        n = 3
        expected_result = 2 * n  
        self.assertEqual(self.nsequence.nth_term(n), expected_result)

if __name__ == "__main__":
    unittest.main()
