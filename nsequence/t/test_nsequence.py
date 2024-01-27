import unittest

from nsequence import NSequence, NSequenceException


class TestNSequenceInstanciation(unittest.TestCase):
    def test_should_instantiate_sequence_instance(self):
        self.assertIsInstance(
            NSequence(
                func=lambda x: x,
                initial_position=1,
            ),
            NSequence,
        )


class TestNSequenceMethods(unittest.TestCase):
    def setUp(self):
        self.invertible_sequence = NSequence(
            func=lambda x: x**4 + 9,
            inverse_func=lambda y: (y - 9) ** (1 / 4),
            initial_position=1,
        )
        self.non_invertible_sequence = NSequence(
            # The `func` provided here does not matter because for
            # inversion, we just check if `inverse_fun` is callable
            func=lambda x: abs(x - 10),
            inverse_func=None,
        )

    def tearDown(self):
        # We are not doing side effect operations yet.
        # del self.invertible_sequence
        # def self.non_invertible_sequence
        super().tearDown()

    def test__nth_term(self):
        # n**2 == 16
        self.assertEqual(self.invertible_sequence.nth_term(2), 16 + 9)

    def test__sum_up_nth_term(self):
        # Ensure that the sum to the initial_position gives the first term
        # of the sequence
        self.assertEqual(
            self.invertible_sequence.sum_up_to_nth_term(
                self.invertible_sequence.initial_position
            ),
            10,
        )

        # Ensure that correct sum is returned if n=4
        # 2**1 + 2**2 + 2**3 + 2**4 + (9*4) = 390
        self.assertEqual(self.invertible_sequence.sum_up_to_nth_term(4), 390)

    def test__position_of_term(self):
        # 2**4 + 9 = 265
        self.assertEqual(self.invertible_sequence.position_of_term(265), 4)

    def test__count_terms_between(self):
        # Ensure we get correct result when the two positions are same
        self.assertEqual(self.invertible_sequence.count_terms_between(4, 4), 1)

        self.assertEqual(self.invertible_sequence.count_terms_between(1, 4), 4)

        # Ensure we get correct result when parameters a not passed ordered
        self.assertEqual(self.invertible_sequence.count_terms_between(4, 3), 2)

    def test__count_terms_between_terms(self):
        # Ensure that the count for two same terms is 1
        # 2**4 + 9 = 25
        # 3**4 + 9 = 90
        # 30**4 + 9 = 810009
        self.assertEqual(self.invertible_sequence.count_terms_between_terms(25, 25), 1)

        self.assertEqual(
            self.invertible_sequence.count_terms_between_terms(90, 810009), 28
        )

        self.assertEqual(
            self.invertible_sequence.count_terms_between_terms(810009, 90), 28
        )

    def test__terms_between(self):
        self.assertEqual(self.invertible_sequence.terms_between(2, 2), [25])

        self.assertEqual(self.invertible_sequence.terms_between(2, 3), [25, 90])

        self.assertEqual(
            self.invertible_sequence.terms_between(2, 5), [25, 90, 265, 634]
        )

    def test__terms_between_terms(self):
        # 3**4 + 9 = 90
        # 30**4 + 9 = 810009

        self.assertEqual(self.invertible_sequence.terms_between_terms(90, 90), [90])

        self.assertEqual(
            self.invertible_sequence.terms_between_terms(810009, 90),
            [
                90,
                265,
                634,
                1305,
                2410,
                4105,
                6570,
                10009,
                14650,
                20745,
                28570,
                38425,
                50634,
                65545,
                83530,
                104985,
                130330,
                160009,
                194490,
                234265,
                279850,
                331785,
                390634,
                456985,
                531450,
                614665,
                707290,
                810009,
            ],
        )

        self.assertEqual(self.invertible_sequence.terms_between_terms(90, 90), [90])

    def test__nearest_term_position(self):
        # 2**4 + 9 = 25
        # 3**4 + 9 = 90
        # 29**4 + 9 = 707290
        # 30**4 + 9 = 810009

        self.assertEqual(
            self.invertible_sequence.nearest_term_position(707290 + 10), 29
        )

        # Test with a term that's exactly in the sequence
        self.assertEqual(self.invertible_sequence.nearest_term_position(25), 2)

        # Test prefer_left_term param
        self.assertEqual(
            self.invertible_sequence.nearest_term_position(
                (25 + 90) / 2, prefer_left_term=True
            ),
            2,
        )
        self.assertEqual(
            self.invertible_sequence.nearest_term_position(
                (25 + 90) / 2, prefer_left_term=False
            ),
            3,
        )

    def test__nearest_term(self):
        # 2**4 + 9
        # 29**4 + 9 = 707290
        # 30**4 + 9 = 810009

        self.assertEqual(self.invertible_sequence.nearest_term(707290 + 10), 707290)

        # Test with a term that's exactly in the sequence
        self.assertEqual(self.invertible_sequence.nearest_term(25), 25)

    def test__is_invertible(self):
        self.assertTrue(self.invertible_sequence.is_invertible)
        self.assertFalse(self.non_invertible_sequence.is_invertible)

    def test__initial_term(self):
        self.assertEqual(self.invertible_sequence.initial_term, 1**2 + 9)

    def test__initial_position(self):
        self.assertEqual(self.invertible_sequence.initial_position, 1)


class TestExceptionRaising(unittest.TestCase):
    def test_should_raise_exception_if_inversion_gives_non_zero_decimal_float(self):
        sequence = NSequence(
            func=lambda x: x,
            initial_position=1,
            # Bad inverse
            inverse_func=lambda y: 1 / y,
        )

        with self.assertRaises(NSequenceException) as context:
            sequence.count_terms_between_terms(3, 4)

        self.assertTrue(
            "Expect `inverse_fun` to give integers as results but got a float"
            in context.exception.msg
        )

    def test_should_raise_exception_if_inverse_fun_is_not_callable(self):
        sequence = NSequence(
            func=lambda x: x,
            initial_position=1,
            # Bad inverse
            inverse_func="not callable",
        )

        with self.assertRaises(NSequenceException) as context:
            sequence.position_of_term(3)

        self.assertTrue(
            "Expect `inverse_func` to be defined and to be callable"
            in context.exception.msg
        )

    def test_should_raise_exception_if_sum_up_nth_term_gets_bad_param(self):
        sequence = NSequence(
            func=lambda x: x,
            initial_position=1,
        )

        with self.assertRaises(NSequenceException) as context:
            sequence.sum_up_to_nth_term(-20)

        self.assertTrue(
            "Expect position to be at least equal to `1`" in context.exception.msg
        )


class TestKwargs(unittest.TestCase):

    def test_should_sum_up_using_the_provided_sum_up_func(self):
        # Provide a bad sum_up_fun and ensure that we get the sum from it
        sequence = NSequence(
            func=lambda x: x**x + 1,
            initial_position=7,
            # Bad sum_up_fun, but it does not matter as long as it is different from
            # the sequence `func`. But be carefull to not get into coincidence.
            sum_up_func=lambda x, **kwargs: x + 1,
        )

        # 29 + 1 = 30
        self.assertEqual(sequence.sum_up_to_nth_term(29), 30)


if __name__ == "__main__":
    unittest.main()
