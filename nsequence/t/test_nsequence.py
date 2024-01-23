import unittest

from nsequence import NSequence, NSequenceException


class TestNSequenceInstanciation(unittest.TestCase):
    def test__should_instantiate_sequence_instance(self):
        self.assertIsInstance(
            NSequence(
                func=lambda x: x,
                initial_position=1,
            ),
            NSequence
        )


class TestNSequenceMethods(unittest.TestCase):
    def setUp(self):
        self.invertible_sequence = NSequence(
            func=lambda x: x ** 4 + 9,
            inverse_func=lambda y: (y - 9) ** (1 / 4),
            initial_position=1,
        )
        self.non_invertible_sequence = NSequence(
            # The `func` provided here does not matter because for
            # inversion, we just check if `inverse_fun` is callable
            func=lambda x: abs(x - 10),
            inverse_func=None
        )

    def tearDown(self):
        # We are not doing side effect operations yet.
        # del self.invertible_sequence
        # def self.non_invertible_sequence
        super().tearDown()

    def test__nth_term(self):
        n = 2  # n**2 == 16
        self.assertEqual(self.invertible_sequence.nth_term(2), 16 + 9)

    def test__sum_up_nth_term(self):
        # Ensure that the sum to the initial_position gives the first term
        # of the sequence
        self.assertEqual(
            self.invertible_sequence.sum_up_to_nth_term(
                self.invertible_sequence.initial_position
            ),
            10
        )

        # Ensure that correct sum is returned if n=4
        # 2**1 + 2**2 + 2**3 + 2**4 + (9*4) = 390
        self.assertEqual(self.invertible_sequence.sum_up_to_nth_term(4), 390)

    def test__position_of_term(self):
        # 2**4 + 9=265
        self.assertEqual(
            self.invertible_sequence.position_of_term(265),
            4
        )

    def test__is_invertible(self):
        self.assertTrue(self.invertible_sequence.is_invertible)
        self.assertFalse(self.non_invertible_sequence.is_invertible)

    def test__initial_term(self):
        self.assertEqual(self.invertible_sequence.initial_term, 1 ** 2 + 9)

    def test__initial_position(self):
        self.assertEqual(
            self.invertible_sequence.initial_position, 1
        )


if __name__ == "__main__":
    unittest.main()
