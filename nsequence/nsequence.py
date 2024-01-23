from typing import Callable
from math import ceil, floor

# We supposed that the indexing set is a subsequence of [0, 1, 2, 3, ...]

class NSequenceException(Exception):
    base_message = "NSequenceException"

    def __init__(self, msg, **kwargs):
        """Initialize NSequenceException with a custom message."""
        self.msg = msg

    def __str__(self):
        """Return a string representation of the exception."""
        return f"{self.base_message}: {self.msg}"


class NSequence(object):
    """
    Represents a numerical sequence with optional inversion capabilities.

    Attributes:
    - func: Callable[[int], float] - Function to compute the nth term of the sequence.
    - inverse_func: Callable[[float], float | int] - Function to compute the position of a term.
    - initial_position: int - Initial position for term computation.
    - _kwargs: dict - Additional keyword arguments.

    Methods:
    - nth_term(n: int) -> float: Computes the nth term of the sequence.
    - sum_up_to_nth_term(n: int) -> float: Computes the sum of the sequence up to the nth term.
    - position_of_term(term: float, raise_exception_if_not_exact=True) -> int: Computes the position of a term.
    - count_terms_between_terms(term1: float, term2: float) -> int: Counts terms between two given terms.
    - count_terms_between(n1: int, n2: int) -> int: Counts terms between two positions.
    - terms_between_terms(term1: float, term2: float, include_args_terms=True) -> List[float]: Lists terms between two given terms.
    - terms_between(n1: int, n2: int, include_args_terms=True) -> List[float]: Lists terms between two positions.
    - nearest_term_position(term_neighbor: float, prefer_left_term=True) -> int: Finds the position of the nearest term to a given term.
    - nearest_term(term_neighbor: float, prefer_left_term=True) -> tuple[float, int]: Finds the nearest term and its position.

    Properties:
    - initial_term: float - Gets the initial term of the sequence.
    - is_invertible: bool - Checks if the sequence is invertible.
    """

    def __init__(
        self,
        *,
        func: Callable[[int], float],
        inverse_func: Callable[[float], float | int] = None,
        initial_position=0,
        **kwargs,
    ) -> None:
        super().__init__()
        # FIXME: Ensure funcs are callables
        self._func = func
        self._inverse_func = inverse_func
        self._initial_position = initial_position
        self._kwargs = kwargs or {}

    def nth_term(self, n: int):
        """Computes the nth term of the sequence"""
        return self._func(n)

    def sum_up_to_nth_term(self, n: int):
        """Computes the sum of the sequence up to the nth term."""
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
                        self._initial_position, n - self._initial_position + 1 + 1
                        # The last +1 helps to include the `itself` as a position to
                        # considerate in the sommation
                    )
                ]
            )

        return sum_to_return

    # METHODS FOR INVERTIBLE SEQUENCES

    def position_of_term(self, term: float, raise_exception_if_not_exact=True):
        """
        Computes the position of a given term in the sequence.

        Parameters:
        - term (float): The term for which to find the position.
        - raise_exception_if_not_exact (bool): If True, raises an exception if the position is not an integer.

        Returns:
        int: The position of the term in the sequence.

        Raises:
        NSequenceException: If inverse_func is not defined or not callable, or if the position is not an integer.
        """
        if not self.is_invertible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but \
                 got {self._inverse_func}"
            )

        position = self._inverse_func(term)

        if not raise_exception_if_not_exact:
            return position

        if position % 1 != 0:
            raise NSequenceException(
                f"Expect `inverse_fun` to give integers as results but got a float"
                f"with non-zero decimal {position}"
            )

        return int(position)

    def count_terms_between_terms(self, term1: float, term2: float):
        """
        Counts the number of terms between two given terms in the sequence.

        Parameters:
        - term1 (float): The first term.
        - term2 (float): The second term.

        Returns:
        int: The number of terms between term1 and term2.

        Raises:
        NSequenceException: If inverse_func is not defined or not callable.
        """

        if not self.is_inversible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_position = self._inverse_func(term1)
        term2_position = self._inverse_func(term2)

        return self.count_terms_between(term1_position, term2_position)

    @staticmethod
    def count_terms_between(n1: int, n2: int):
        """
        Counts the number of terms between two given positions in the sequence.

        Parameters:
        - n1 (int): The first position.
        - n2 (int): The second position.

        Returns:
        int: The number of terms between n1 and n2.
        """
        return abs(n2 - n1) + 1

    def terms_between_terms(self, term1: float, term2: float):
        """
        Lists the terms between two given terms in the sequence.

        Parameters:
        - term1 (float): The first term.
        - term2 (float): The second term.

        Returns:
        List[float]: The terms between term1 and term2.

        Raises:
        NSequenceException: If inverse_func is not defined or not callable.
        """
        if not self.is_inversible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_position = self._inverse_func(term1)
        term2_position = self._inverse_func(term2)

        return self.terms_between(term1_position, term2_position)

        ""

    def terms_between(self, n1: int, n2: int, include_args_terms=True):
        """
        Lists the terms between two given positions in the sequence.

        Parameters:
        - n1 (int): The first position.
        - n2 (int): The second position.
        - include_args_terms (bool): If True, includes the terms at n1 and n2.

        Returns:
        List[float]: The terms between n1 and n2, optionally including n1 and n2.
        """
        range_inf = min(n1, n2)
        range_sup = max(n1, n2)

        if not include_args_terms:
            range_inf = range_inf + 1
            range_sup = range_sup - 1

        return [self._func(position) for position in range(range_inf, range_sup + 1)]

    def nearest_term_position(self, term_neighbor: float, *, prefer_left_term=True):
        """
        Finds the position of the nearest term in the sequence to a given term.

        Parameters:
        - term_neighbor (float): The term for which to find the nearest position.
        - prefer_left_term (bool): If True, prefers the left term in case of a tie.

        Returns:
        int: The position of the nearest term to term_neighbor.
        """

        term_neighbor_position = self._inverse_func(term_neighbor)

        if term_neighbor_position % 1 == 0:
            # The provided term is a term of the sequence so do nothing
            return term_neighbor_position

        left_nearest_term_position = floor(term_neighbor_position)
        right_nearest_term_position = ceil(term_neighbor_position)

        left_nearest_term = self._func(left_nearest_term_position)
        right_nearest_term = self._func(right_nearest_term_position)

        left_distance_to_neighbor = abs(term_neighbor - left_nearest_term)
        right_distance_to_neighbor = abs(term_neighbor - right_nearest_term)

        if (
            not prefer_left_term
            and left_distance_to_neighbor == right_distance_to_neighbor
        ):
            return right_nearest_term_position

        return (
            right_nearest_term_position
            if left_distance_to_neighbor > right_distance_to_neighbor
            else left_nearest_term_position
        )

    def nearest_term(
        self, term_neighbor: float, *, prefer_left_term=True
    ) -> tuple[float, int]:
        """Gets the nearest term in the sequence to the given `term_neighbor`."""
        return self._func(
            self.nearest_term_position(
                term_neighbor, prefere_left_term=prefer_left_term
            )
        )

    # PROPERTIES

    @property
    def initial_position(self) -> float:
        """Gets the initial position provided while creating the sequence."""
        return self._initial_position

    @property
    def initial_term(self) -> float:
        """Gets the initial term of the sequence."""
        return self._func(self._initial_position)

    @property
    def is_invertible(self):
        """Checks if the sequence is invertible."""
        return self._inverse_func or callable(self._inverse_func)
