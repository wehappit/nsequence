import unittest
import pytest
from nsequence import (
    NSequence,
    ArityMismatchError,
    UnexpectedIndexError,
    UnexpectedPositionError,
    InversionError,
)


identity_x = lambda x: x
linear_x = lambda x: 11 * x - 18
quartic_x = lambda x: x ** 4 + 9
absolute_x = lambda x: abs(x - 20)
cubic_x = lambda x: x ** 3 - x ** 2 - 1
harmonic_x = lambda x: 1 / x
# Used when injective function is needed x(x−1)(x−2)(x−3)(x−4)(x-5)
sextique_x = lambda x: x ** 6 - 10 * (x ** 5) + 35 * (x ** 4) - 50 * (x ** 3) + 24 * (x ** 2)


class TestNSequenceInstantiation(unittest.TestCase):

    def test_should_instantiate_nsequence_with_minimal_params(self):
        """
        Ensure we can instantiate with minimal param(s)
        """
        self.assertIsInstance(
            NSequence(
                func=identity_x,
            ),
            NSequence,
        )

    def test_should_instantiate_nsequence_with_maximal_params(self):
        """
        Ensure we can instantiate with every parameter set
        """

        # We don't care about the correctness of function-like parameters
        # here.
        self.assertIsInstance(
            NSequence(
                func=identity_x,
                inverse_func=identity_x,
                indexing_func=identity_x,
                indexing_inverse_func=identity_x,
                initial_index=0,
            ),
            NSequence,
        )

    def test_should_not_instantiate_nsequence_if_func_not_provided(self):
        with pytest.raises(TypeError) as context:
            NSequence(
                inverse_func=identity_x,
                indexing_func=identity_x,
                indexing_inverse_func=identity_x,
                initial_index=0,
            )

        self.assertIn(
            "NSequence.__init__() missing 1 required keyword-only argument: 'func'",
            context.value.args[0],
        )


    def test_should_not_instantiate_nsequence_if_any_bad_object_provided_as_function(
        self,
    ):
        
        def f_xyz(x, y, z):
            return x, y, z


        with pytest.raises(ArityMismatchError) as context:
            NSequence(
                #
                func=f_xyz,
                initial_index=1,
                # Bad inverse
                inverse_func="bad object as func",
            )

        self.assertTrue(
            "Function b_x expected 1 argument(s), but got 3", context.value.args[0]
        )


    def test_should_not_instantiate_nsequence_if_any_bad_object_provided_as_function(
        self,
    ):
        with pytest.raises(TypeError) as context:
            NSequence(
                func=identity_x,
                initial_index=1,
                # Bad inverse
                inverse_func="bad object as func",
            )

        self.assertTrue(
            "Expect a function, but got `bad object as func`", context.value.args[0]
        )

        with pytest.raises(TypeError) as context:
            NSequence(
                func=identity_x,
                initial_index=1,
                # Bad objects as functions
                indexing_func="bad object as func",
            )

        self.assertIn(
            "Expect a function, but got `bad object as func`", context.value.args[0]
        )

        with pytest.raises(TypeError) as context:
            NSequence(
                func=identity_x,
                initial_index=1,
                # Bad objects as functions
                indexing_inverse_func=list,
            )

        self.assertIn(f"Expect a function, but got `{list}`", context.value.args[0])

        with pytest.raises(TypeError) as context:
            NSequence(
                func=identity_x,
                initial_index=1,
                # Bad objects as functions
                inverse_func=dict,
                indexing_func=list,
                indexing_inverse_func="bad object as func",
            )

        # No need to match 100% of the message here, cause done enough previously
        self.assertIn("Expect a function, but got ", context.value.args[0])


class TestNthTermComputation(unittest.TestCase):

    def test_should_compute_nth_term_if_no_indexing_func_provided(self):
        """
        Ensure the default indexing func is used.
        The default initial_index is 0.
        """
        nsequence1 = NSequence(
            func=absolute_x,
        )

        # Ensure the first term computed is correct

        self.assertEqual(nsequence1.nth_term(1), 20)

        self.assertEqual(nsequence1.nth_term(1000), 979)

        # Set an initial_index
        nsequence2 = NSequence(
            func=absolute_x,
            inverse_func=None,
            initial_index=5,
        )

        self.assertEqual(nsequence2.nth_term(1), 15)

        self.assertEqual(nsequence2.nth_term(1000), 984)

    def test_should_compute_nth_term_if_indexing_func_provided(self):
        """
        Ensure the provided `indexing_func` is used.
        When an indexing function is provided, the default
        `initial_index` is `indexing_func(1)`
        """

        nsequence1 = NSequence(
            func=absolute_x,
            indexing_func=cubic_x,
        )

        # Ensure the first term computed is correct

        self.assertEqual(nsequence1.nth_term(1), 21)

        self.assertEqual(nsequence1.nth_term(1000), 998999979)


class TestSumUpToNthTermComputation(unittest.TestCase):

    def test_should_fail_if_bad_position_is_provided(self):
        sequence = NSequence(
            func=identity_x,
            initial_index=1,
        )

        for bad_param in (-20, 29.31, 2.1, 2.00001):
            with pytest.raises(UnexpectedPositionError) as context:
                sequence.sum_up_to_nth_term(bad_param)

            self.assertIn(
                "Expect `positions` to be tuple of integers (strictly greater than 0), but actually "
                "got a tuple of float(s) with non zero decimal(s) ",
                context.value.message,
            )

    def test_should_fail_if_sequence_nth_term_failed(self):
        sequence = NSequence(
            func=harmonic_x,
            # Make `nth_term` failed
            initial_index=0,
        )

        with pytest.raises(NotImplementedError) as exc_info:
            sequence.sum_up_to_nth_term(10)

        self.assertIn(
            "Failed to compute the sequence's n first terms sum with the default `sump_up_func`."
            "The default `sump_up_func` implementation seems not appropriate for your use case."
            "You should provide your own `sum_up_func` implementation.",
            exc_info.value.args[0],
        )

    def test_should_compute_sum_up_to_nth_term_if_no_indexing_func_provided(self):
        sequence1 = NSequence(
            func=quartic_x,
        )

        # Ensure we get the correct sum if position is 1. We are supposed
        # to get the first term of the sequence. As `indexing_func` is not
        # provided, the default initial_index is 0
        self.assertEqual(
            sequence1.sum_up_to_nth_term(1),
            9,
        )

        # Ensure that correct sum is returned if position is 5
        # 0**4 + 1**4 + 2**4 + 3**4 + 4**4 + (9*5) = 399
        self.assertEqual(sequence1.sum_up_to_nth_term(5), 399)

        # Sequence with initial_index

        sequence1 = NSequence(
            func=quartic_x,
            initial_index=2,
        )

        # Ensure we get the correct sum if position is 1.
        self.assertEqual(
            sequence1.sum_up_to_nth_term(1),
            25,
        )

        # Ensure that correct sum is returned if position is 5
        # 2**4 + 3**4 + 4**4 + + 5**4 + 6**4 + (9*5) = 2319
        self.assertEqual(sequence1.sum_up_to_nth_term(5), 2319)

    def test_should_compute_sum_up_to_nth_term_if_indexing_func_provided(self):
        sequence1 = NSequence(
            func=quartic_x,
            indexing_func=linear_x,
        )

        # Ensure we get the correct sum if position is 1. We are supposed
        # to get the first term of the sequence.
        self.assertEqual(
            sequence1.sum_up_to_nth_term(1),
            2410,
        )

        sequence2 = NSequence(
            func=quartic_x,
            indexing_func=linear_x,
        )

        self.assertEqual(
            sequence2.sum_up_to_nth_term(3),
            53309,
        )


class TestIndexOfTermComputation(unittest.TestCase):
    # to be continued
    def test_should_fail_if_no_inverse_func_provided_and_naive_technic_is_not_activated(
        self,
    ):
        sequence = NSequence(
            func=absolute_x,
        )

        with pytest.raises(InversionError) as exc_info:
            # The provided term as arg does not matter here
            sequence.index_of_term(3)
            self.assertEqual(
                "Cannot calculate `index_of_term` for sequence without `inverse_func` and with "
                "`naive_technic` set to `False`. You need either to provide `inverse_func` or set "
                "`naive_technic` to `True`",
                exc_info.value.message,
            )

    def test_should_naively_compute_term_index_if_no_inverse_func_and_naive_technic_is_activated(
        self,
    ):
        sequence1 = NSequence(
            func=quartic_x,
        )

        # Ensure the result is correct for the first term.
        # The default `initial_index` is 0 and the first term is 9
        self.assertEqual(sequence1.index_of_term(9, naive_technic=True), 0)

        # quartic_x(8) = 4105
        self.assertEqual(sequence1.index_of_term(4105, naive_technic=True), 8)

        # Ensure we get correct results if `initial_index` was set

        sequence2 = NSequence(func=quartic_x, initial_index=10)

        # Ensure the result is correct for the first term.
        # quartic_x(10) = 10009
        self.assertEqual(sequence2.index_of_term(10009, naive_technic=True), 10)

        # quartic_x(14) = 38425
        self.assertEqual(sequence2.index_of_term(38425, naive_technic=True), 14)

        sequence3 = NSequence(
            func=quartic_x,
            indexing_func=cubic_x,
        )

        # Ensure the result is correct for the first term.
        # quartic_x(c_x(1)) = 10 and c_x(1) = -1
        self.assertEqual(sequence3.index_of_term(10, naive_technic=True), -1)

        # quartic_x(c_x(14)) = 42083880609690 and c_x(14) = 2547
        self.assertEqual(
            sequence3.index_of_term(42083880609690, naive_technic=True), 2547
        )

        # Sequence having descending indexing function

        sequence4 = NSequence(
            func=quartic_x,
            indexing_func=lambda x: -c_x(x),
        )

        # Ensure the result is correct for the first term.
        # quartic_x(-c_x(1)) = 10 and -c_x(1) = 1
        self.assertEqual(sequence4.index_of_term(10, naive_technic=True), 1)

        # quartic_x(-c_x(14)) = 42083880609690 and -c_x(14) = -2547
        self.assertEqual(
            sequence4.index_of_term(42083880609690, naive_technic=True), -2547
        )

    def test_should_return_the_first_index_if_func_is_injective_and_naive_technic_is_activated(
        self,
    ):
        sequence = NSequence(
            func=sextique_x,
        )

        self.assertEqual(sequence.index_of_term(0, naive_technic=True), 0)

    def test_should_compute_index_of_term_using_inverse_func_if_provided(self):
        sequence = NSequence(
            func=identity_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=quartic_x,
        )

        self.assertEqual(
            sequence.index_of_term(4),
            # quartic_x(4) = 265
            265,
        )

    def test_should_compute_index_of_term_using_inverse_func_if_provided_and_ignore_naive_technic_param(
        self,
    ):
        sequence = NSequence(
            func=identity_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=quartic_x,
        )

        self.assertEqual(
            sequence.index_of_term(4, naive_technic=True),
            # quartic_x(4) = 265
            265,
        )

    def test_should_not_raise_indexing_exception_if_param_is_not_activated(self):
        sequence = NSequence(
            func=identity_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=harmonic_x,
        )

        self.assertEqual(sequence.index_of_term(4, exact_exception=False), 0.25)

    def test_should_not_raise_indexing_exception_if_param_is_activated(self):
        sequence = NSequence(
            func=identity_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=harmonic_x,
        )

        with pytest.raises(UnexpectedIndexError) as exc_info:
            self.assertEqual(sequence.index_of_term(4, exact_exception=True), 0.25)

        self.assertIn(
            f"Expect an `indices` to be a tuple of integers, but actually got a "
            f"tuple containing None or float(s) with non zero decimal(s) ",
            exc_info.value.message,
        )

    def test_should_not_compute_index_of_term_using_indexing_func_if_inverse_func_provided(
        self,
    ):
        sequence = NSequence(
            func=identity_x,
            indexing_func=quartic_x,
            # The correctness of the `inverse_func` does not matter too much
            # but should just be chosen to avoid coincidences
            inverse_func=harmonic_x,
        )

        self.assertEqual(sequence.index_of_term(4, exact_exception=False), 0.25)


class TestCountTermsBetweenTermsComputation(unittest.TestCase):
    def test_should_not_compute_count_terms_between_terms_if_no_inverse_func_provided(
        self,
    ):
        sequence = NSequence(
            func=identity_x,
        )

        with pytest.raises(InversionError) as exc_info:
            sequence.count_terms_between_terms(5, 10)

        self.assertEqual(
            exc_info.value.message,
            "Cannot calculate `count_terms_between_indices_terms` for sequence "
            "without `inverse_func`. It was not set.",
        )

    def test_should_compute_count_terms_between_terms_if_inverse_func_provided(self):
        sequence1 = NSequence(func=linear_x, inverse_func=lambda y: (y + 18) / 11)

        # When the two terms are the same and with the default initial_index
        self.assertEqual(sequence1.count_terms_between_terms(-18, -18), 1)

        # linear_x(10) = 92
        self.assertEqual(sequence1.count_terms_between_terms(-18, 92), 11)

        sequence2 = NSequence(
            func=linear_x,
            inverse_func=lambda y: (y + 18) / 11,
            initial_index=3,
        )

        # When the two terms are the same and with the default initial_index
        self.assertEqual(sequence2.count_terms_between_terms(15, 15), 1)

        # linear_x(10) = 92
        self.assertEqual(sequence2.count_terms_between_terms(15, 92), 8)

        # With indexing function provided

        sequence3 = NSequence(
            func=linear_x,
            inverse_func=lambda y: (y + 18) / 11,
            indexing_func=quartic_x,
        )

        # linear_x(quartic_x(1)) = 92
        self.assertEqual(sequence1.count_terms_between_terms(92, 92), 1)

        # linear_x(quartic_x(10)) = 110081
        self.assertEqual(sequence3.count_terms_between_terms(92, 110081), 10)

    def test_should_raise_exception_if_inverse_func_gives_decimal_bad_index_for_any_provided_term(
        self,
    ):
        sequence1 = NSequence(func=linear_x, inverse_func=lambda y: (y + 18) / 11)

        with pytest.raises(UnexpectedIndexError) as exc_info:
            # Provide terms that will make the inverse_func returns decimals
            sequence1.count_terms_between_terms(-0, -20)

        self.assertIn(
            f"Expect an `indices` to be a tuple of integers, but actually got a "
            f"tuple containing None or float(s) with non zero decimal(s) ",
            exc_info.value.message,
        )

    def test_should_raise_exception_if_inverse_func_gives_non_zero_decimal_float(self):
        sequence = NSequence(
            func=identity_x,
            initial_index=1,
            # Bad inverse
            inverse_func=lambda y: 1 / y,
        )

        with pytest.raises(UnexpectedIndexError) as context:
            sequence.count_terms_between_terms(3, 4)

        self.assertIn(
            f"Expect an `indices` to be a tuple of integers, but actually got a "
            f"tuple containing None or float(s) with non zero decimal(s) ",
            context.value.message,
        )


class TestCountTermsBetweenIndices(unittest.TestCase):
    def test_should_count_terms_between_indices_if_no_indexing_func_provided(self):
        sequence1 = NSequence(
            func=linear_x,
        )

        # When the two terms are the same and with the default initial_index
        self.assertEqual(sequence1.count_terms_between_indices(0, 0), 1)

        self.assertEqual(sequence1.count_terms_between_indices(0, 92), 93)

        # Sequence with custom initial_index
        sequence2 = NSequence(
            func=linear_x,
            initial_index=4,
        )

        # When the two terms are the same
        self.assertEqual(sequence2.count_terms_between_indices(4, 4), 1)

        # Different term
        self.assertEqual(sequence2.count_terms_between_indices(4, 92), 89)

    def test_should_count_terms_between_indices_if_indexing_func_provided_and_no_indexing_inverse_func_provided(
        self,
    ):
        """Ensure that we (kinda) brute-force to imitate the indexing_inverse_func behavior"""
        sequence1 = NSequence(
            func=linear_x,
            indexing_func=quartic_x,
        )

        # When the two terms are the same
        self.assertEqual(sequence1.count_terms_between_indices(10, 10), 1)

        self.assertEqual(sequence1.count_terms_between_indices(10, 10009), 10)

    def test_should_count_terms_between_indices_if_indexing_func_provided_and_indexing_inverse_func_provided(
        self,
    ):
        """Ensure `indexing_inverse_func` is used to do the computation"""

        sequence1 = NSequence(
            func=linear_x,
            indexing_func=quartic_x,
            # We don't care about the effectiveness of the `indexing_inverse_func` here
            # We just want to make sure that indexing_inverse_func is used to compute the count
            indexing_inverse_func=identity_x,
        )

        # When the two terms are the same
        self.assertEqual(sequence1.count_terms_between_indices(10, 10), 1)

        self.assertEqual(sequence1.count_terms_between_indices(10, 10009), 10000)

    def test_should_raise_indices_exception_if_bad_indices_provided(self):
        sequence1 = NSequence(
            func=linear_x,
            indexing_func=quartic_x,
            # We don't care about the effectiveness of the `indexing_inverse_func` here
            # We just want to make sure that indexing_inverse_func is used to compute the count
            indexing_inverse_func=harmonic_x,
        )

        # When the two terms are the same

        with pytest.raises(UnexpectedPositionError) as exc_info:
            self.assertEqual(sequence1.count_terms_between_indices(10, 10), 1)
        self.assertIn(
            "Expect `positions` to be tuple of integers (strictly greater than 0), but actually "
            f"got a tuple of float(s) with non zero decimal(s) `",
            exc_info.value.args[0],
        )


class TestTermsBetweenIndicesComputation(unittest.TestCase):

    def test_should_compute_terms_between_indices_if_no_indexing_func_provided(self):
        sequence1 = NSequence(
            func=linear_x,
        )

        # When the two terms are the same and with the default initial_index
        self.assertEqual(sequence1.terms_between_indices(0, 0), [-18])

        self.assertEqual(
            sequence1.terms_between_indices(0, 10),
            [-18, -7, 4, 15, 26, 37, 48, 59, 70, 81, 92],
        )

        # Sequence with custom initial_index
        sequence2 = NSequence(
            func=linear_x,
            initial_index=4,
        )

        self.assertEqual(sequence2.terms_between_indices(4, 4), [26])

        # Different term
        self.assertEqual(sequence2.terms_between_indices(4, 6), [26, 37, 48])

    def test_should_compute_terms_between_indices_if_indexing_func_provided_and_no_indexing_inverse_func_provided(
        self,
    ):
        sequence1 = NSequence(
            func=linear_x,
            indexing_func=quartic_x,
        )

        # When the two terms are the same
        self.assertEqual(sequence1.terms_between_indices(10, 10), [92])

        self.assertEqual(
            sequence1.terms_between_indices(10, 10009),
            [92, 257, 972, 2897, 6956, 14337, 26492, 45137, 72252, 110081],
        )

    def test_should_compute_terms_between_indices_if_indexing_func_provided_and_indexing_inverse_func_provided(
        self,
    ):
        sequence1 = NSequence(
            func=linear_x,
            indexing_func=quartic_x,
            # We don't care about the effectiveness of the `indexing_inverse_func` here
            # We just want to make sure that indexing_inverse_func is used to do the computation
            indexing_inverse_func=identity_x,
        )

        # When the two terms are the same
        self.assertEqual(sequence1.terms_between_indices(10, 10), [110081])

        self.assertEqual(
            sequence1.terms_between_indices(10, 20),
            [
                110081,
                161132,
                228177,
                314252,
                422657,
                556956,
                720977,
                918812,
                1154817,
                1433612,
                1760081,
            ],
        )


class TestNearestEntryComputation(unittest.TestCase):
    def test_should_compute_nearest_entry_naively_if_param_activated(self):
        sequence = NSequence(
            func=quartic_x,
        )

        # When the term is one entry of the sequence (the default `initial_index`)
        self.assertEqual(sequence.nearest_entry(25, inversion_technic=False), (2, 25))

        # When the term is not an entry of the sequence
        self.assertEqual(sequence.nearest_entry(30, inversion_technic=False), (2, 25))

    def test_should_compute_nearest_entry_inversely_if_param_activated(self):
        sequence = NSequence(
            func=quartic_x,
            # Here, the effectiveness of the inverse_func does not matter
            inverse_func=identity_x,
        )

        # When the term is a term of the sequence
        self.assertEqual(sequence.nearest_entry(25), (25, 25))

        self.assertEqual(sequence.nearest_entry(25.54), (25, 390634))

    # TODO: Tests for extra params


class TestNSequenceProperties(unittest.TestCase):

    def test_initial_term(self):
        self.assertEqual(NSequence(func=sextique_x).initial_term, 0)
        self.assertEqual(NSequence(func=linear_x, initial_index=4).initial_term, 26)

    def test_initial_index(self):
        self.assertEqual(NSequence(func=sextique_x, initial_index=50).initial_index, 50)

        # When indexing func provided, initial_index is ignored
        self.assertEqual(
            NSequence(func=identity_x, indexing_func=quartic_x, initial_index=400).initial_index, 10
        )


if __name__ == "__main__":
    unittest.main()
