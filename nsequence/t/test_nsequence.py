import unittest
import pytest
from nsequence import (
    NSequence,
    UnexpectedIndexError,
    UnexpectedPositionError,
    InversionError,
)
from .utils import i_x, a_x, l_x, q_x, c_x, h_x, s_x


# TODO: Test that the initial_index provided by the dev will be ignored if indexing_fun


class TestNSequenceInstantiation(unittest.TestCase):

    def test_should_instantiate_nsequence_with_minimal_params(self):
        """
        Ensure we can instantiate with minimal param(s)
        """
        self.assertIsInstance(
            NSequence(
                func=i_x,
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
                func=i_x,
                inverse_func=i_x,
                indexing_func=i_x,
                indexing_inverse_func=i_x,
                initial_index=0,
            ),
            NSequence,
        )

    def test_should_not_instantiate_nsequence_if_func_not_provided(self):
        with pytest.raises(TypeError) as context:
            NSequence(
                inverse_func=i_x,
                indexing_func=i_x,
                indexing_inverse_func=i_x,
                initial_index=0,
            )

        self.assertIn(
            "NSequence.__init__() missing 1 required keyword-only argument: 'func'",
            context.value.args[0],
        )

    def test_should_not_instantiate_nsequence_if_any_bad_object_provided_as_function(
            self,
    ):
        with pytest.raises(TypeError) as context:
            NSequence(
                func=i_x,
                initial_index=1,
                # Bad inverse
                inverse_func="bad object as func",
            )

        self.assertTrue(
            "Expect a function, but got `bad object as func`", context.value.args[0]
        )

        with pytest.raises(TypeError) as context:
            NSequence(
                func=i_x,
                initial_index=1,
                # Bad objects as functions
                indexing_func="bad object as func",
            )

        self.assertIn(
            "Expect a function, but got `bad object as func`", context.value.args[0]
        )

        with pytest.raises(TypeError) as context:
            NSequence(
                func=i_x,
                initial_index=1,
                # Bad objects as functions
                indexing_inverse_func=list,
            )

        self.assertIn(f"Expect a function, but got `{list}`", context.value.args[0])

        with pytest.raises(TypeError) as context:
            NSequence(
                func=i_x,
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
            func=a_x,
        )

        # Ensure the first term computed is correct

        self.assertEqual(nsequence1.nth_term(1), 20)

        self.assertEqual(nsequence1.nth_term(1000), 979)

        # Set an initial_index
        nsequence2 = NSequence(
            func=a_x,
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
            func=a_x,
            indexing_func=c_x,
        )

        # Ensure the first term computed is correct

        self.assertEqual(nsequence1.nth_term(1), 21)

        self.assertEqual(nsequence1.nth_term(1000), 998999979)


class TestSumUpToNthTermComputation(unittest.TestCase):

    def test_should_fail_if_bad_position_is_provided(self):
        sequence = NSequence(
            func=i_x,
            initial_index=1,
        )

        for bad_param in (-20, 29.31, 2.1, 2.00001):
            with pytest.raises(UnexpectedPositionError) as context:
                sequence.sum_up_to_nth_term(bad_param)

            self.assertIn(
                "Expect `positions` to be tuple of integers (only from 1), but actually "
                "got a tuple of float(s) with non zero decimal(s) ",
                context.value.message,
            )

    def test_should_fail_if_sequence_nth_term_failed(self):
        sequence = NSequence(
            func=h_x,
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
            func=q_x,
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
            func=q_x,
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
            func=q_x,
            indexing_func=l_x,
        )

        # Ensure we get the correct sum if position is 1. We are supposed
        # to get the first term of the sequence.
        self.assertEqual(
            sequence1.sum_up_to_nth_term(1),
            2410,
        )

        sequence2 = NSequence(
            func=q_x,
            indexing_func=l_x,
        )

        self.assertEqual(
            sequence2.sum_up_to_nth_term(3),
            53309,
        )


class TestIndexOfTermComputation(unittest.TestCase):
    # to be continued
    def test_should_fail_if_no_inverse_func_provided_and_naive_technic_is_not_activated(self):
        sequence = NSequence(
            func=a_x,
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

    def test_should_naively_compute_term_index_if_no_inverse_func_and_naive_technic_is_activated(self):
        sequence1 = NSequence(
            func=q_x,
        )

        # Ensure the result is correct for the first term.
        # The default `initial_index` is 0 and the first term is 9
        self.assertEqual(
            sequence1.index_of_term(9, naive_technic=True),
            0
        )

        # q_x(8) = 4105
        self.assertEqual(
            sequence1.index_of_term(4105, naive_technic=True),
            8
        )

        # Ensure we get correct results if `initial_index` was set

        sequence2 = NSequence(
            func=q_x,
            initial_index=10
        )

        # Ensure the result is correct for the first term.
        # q_x(10) = 10009
        self.assertEqual(
            sequence2.index_of_term(10009, naive_technic=True),
            10
        )

        # q_x(14) = 38425
        self.assertEqual(
            sequence2.index_of_term(38425, naive_technic=True),
            14
        )

        sequence3 = NSequence(
            func=q_x,
            indexing_func=c_x,
        )

        # Ensure the result is correct for the first term.
        # q_x(c_x(1)) = 10 and c_x(1) = -1
        self.assertEqual(
            sequence3.index_of_term(10, naive_technic=True),
            -1
        )

        # q_x(c_x(14)) = 42083880609690 and c_x(14) = 2547
        self.assertEqual(
            sequence3.index_of_term(42083880609690, naive_technic=True),
            2547
        )

        # Sequence having descending indexing function

        sequence4 = NSequence(
            func=q_x,
            indexing_func=lambda x: -c_x(x),
        )

        # Ensure the result is correct for the first term.
        # q_x(-c_x(1)) = 10 and -c_x(1) = 1
        self.assertEqual(
            sequence4.index_of_term(10, naive_technic=True),
            1
        )

        # q_x(-c_x(14)) = 42083880609690 and -c_x(14) = -2547
        self.assertEqual(
            sequence4.index_of_term(42083880609690, naive_technic=True),
            -2547
        )

    def test_should_compute_index_of_term_using_inverse_func_if_provided(self):
        sequence = NSequence(
            func=i_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=q_x,
        )

        self.assertEqual(
            sequence.index_of_term(4),
            # q_x(4) = 265
            265
        )

    def test_should_compute_index_of_term_using_inverse_func_if_provided_and_ignore_naive_technic_param(self):
        sequence = NSequence(
            func=i_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=q_x,
        )

        self.assertEqual(
            sequence.index_of_term(4, naive_technic=True),
            # q_x(4) = 265
            265
        )

    def test_should_not_raise_indexing_exception_if_param_is_not_activated(self):
        sequence = NSequence(
            func=i_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=h_x,
        )

        self.assertEqual(
            sequence.index_of_term(4, exact_exception=False),
            0.25
        )

    def test_should_not_raise_indexing_exception_if_param_is_activated(self):
        sequence = NSequence(
            func=i_x,
            # The correctness of the `inverse_func` does not matter too much
            inverse_func=h_x,
        )

        with pytest.raises(UnexpectedIndexError) as exc_info:
            self.assertEqual(
                sequence.index_of_term(4, exact_exception=True),
                0.25
            )

        self.assertIn(
            f"Expect an `indices` to be a tuple of integers, but actually got a "
            f"tuple containing None or float(s) with non zero decimal(s) ",
            exc_info.value.message
        )

    def test_should_not_compute_index_of_term_using_indexing_func_if_inverse_func_provided(self):
        sequence = NSequence(
            func=i_x,
            indexing_func=q_x,
            # The correctness of the `inverse_func` does not matter too much
            # but should just be chosen to avoid coincidences
            inverse_func=h_x,
        )

        self.assertEqual(
            sequence.index_of_term(4, exact_exception=False),
            0.25
        )


class BaseNSequenceMethodTestCase(unittest.TestCase):
    def setUp(self):
        self.invertible_sequence = NSequence(
            func=i_x ** 4 + 9,
            inverse_func=lambda y: (y - 9) ** (1 / 4),
            initial_index=1,
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


# TODO: Aller methode par methode : TestNSequenceSumUpNTh,.....
class TestNSequenceMethods(BaseNSequenceMethodTestCase):
    def setUp(self):
        self.invertible_sequence = NSequence(
            func=q_x,
            inverse_func=lambda y: (y - 9) ** (1 / 4),
            initial_index=1,
        )
        self.non_invertible_sequence = NSequence(
            # The `func` provided here does not matter because, for
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
        # Ensure that the sum to the initial_index gives the first term
        # of the sequence
        self.assertEqual(
            self.invertible_sequence.sum_up_to_nth_term(
                self.invertible_sequence.initial_index
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
        self.assertEqual(self.invertible_sequence.initial_term, 1 ** 2 + 9)

    def test__initial_index(self):
        self.assertEqual(self.invertible_sequence.initial_index, 1)


class TestExceptionRaising(unittest.TestCase):
    def test_should_raise_exception_if_inversion_gives_non_zero_decimal_float(self):
        sequence = NSequence(
            func=i_x,
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


if __name__ == "__main__":
    unittest.main()
