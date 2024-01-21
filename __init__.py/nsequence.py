from typing import Callable
from math import ceil, floor


class NSequenceException(Exception):
    base_message = "NSequenceExecption"

    def __init__(self, *, msg, **kwargs):
        self.msg = msg

    def __str__(self):
        return f"{self.base_message}: {self.msg}"


class NSequence(object):
    def __init__(
        self,
        *,
        func: Callable[[int], float],
        inverse_func: Callable[[float], float | int] = None,
        initial_position=0,
        **kwargs,
    ) -> None:
        super().__init__()
        self._func = func
        self._inverse_func = inverse_func
        self._initial_position = initial_position
        self._kwargs = kwargs or {}

    def nth_term(self, n: int):
        """ """
        return self._func(n)

    def sum_up_to_nth_term(self, n: int):
        """ """
        sum_to_return = 0

        sum_up_func: Callable[[int, dict], float] = self._kwargs.get("sum_up_func")
        if sum_up_func and callable(sum_up_func):
            sum_to_return = sum_up_func(
                n,
                initial_position=self._initial_position,
            )
        else:
            # No `sum_up_func` provided
            sum_to_return = sum(
                [
                    self._func(position)
                    for position in range(
                        self._initial_position, n - self._initial_position + 1
                    )
                ]
            )

        return sum_to_return

    # METHODS FOR INVERSIBLE SEQUENCES

    def position_of_term(self, term: float, raise_exception_if_not_exact=True):
        """ """
        if not self.is_inversible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but \ got {self._inverse_func}"
            )

        position = self._inverse_func(term)

        if not raise_exception_if_not_exact:
            return position

        if position % 1 != 0:
            raise NSequenceException(
                f"Expect `inverse_fun` to give integers as results but got a float \
                    with non-zero decimale {position}"
            )

        return int(position)

    def count_terms_between_terms(self, term1: float, term2: float):
        """ """
        if not self.is_inversible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_position = self._inverse_func(term1)
        term2_position = self._inverse_func(term2)

        return self.count_terms_between(term1_position, term2_position)

    def count_terms_between(self, n1: int, n2: int):
        """ """
        return abs(n2 - n1) + 1

    def terms_between_terms(self, term1: float, term2: float):
        if not self.is_inversible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_position = self._inverse_func(term1)
        term2_position = self._inverse_func(term2)

        return self.terms_between(term1_position, term2_position)

        ""

    def terms_between(self, n1: int, n2: int, include_args_terms=True):
        range_inf = min(n1, n2)
        range_sup = max(n1, n2)

        if not include_args_terms:
            range_inf = range_inf + 1
            range_sup = range_sup - 1

        return [self._func(position) for position in range(range_inf, range_sup + 1)]

    def nearest_term_position(self, term_neighbor: float, *, prefere_left_term=True):
        term_neighbor_position = self._inverse_func(term_neighbor)

        if term_neighbor_position % 1 == 0:
            # The provided term is a term of the sequence so do nothing
            return term_neighbor_position

        left_nearest_term_position = floor(term_neighbor_position)
        right_rearest_term_position = ceil(term_neighbor_position)

        left_nearest_term = self._func(left_nearest_term_position)
        right_rearest_term = self._func(right_rearest_term_position)

        left_distance_to_neighbor = abs(term_neighbor - left_nearest_term)
        right_distance_to_neighbor = abs(term_neighbor - right_rearest_term)

        if (
            not prefere_left_term
            and left_distance_to_neighbor == right_distance_to_neighbor
        ):
            return right_rearest_term_position

        return (
            right_rearest_term_position
            if left_distance_to_neighbor > right_distance_to_neighbor
            else left_nearest_term_position
        )

    def nearest_term(
        self, term_neighbor: float, *, prefere_left_term=True
    ) -> tuple[float, int]:
        """The nearest term in the sequence to the given `term_neighbor` and its position."""
        return self._func(self.nearest_term_position(term_neighbor, prefere_left_term=prefere_left_term))

    # PROPERTIES

    @property
    def initial_term(self) -> float:
        """ """
        return self._func(self._initial_position)

    @property
    def is_inversible(self):
        """ """
        return self._inverse_func or callable(self._inverse_func)

