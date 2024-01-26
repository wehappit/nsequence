from typing import Callable

from math import ceil, floor

from .utils import is_floating_integer


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

    Notes
    - A position of a term in a sequence is its rank in the sequence. For instance, the position of
        50 in the sequence (1, 4, 50, 20, ...) is 3.
    - But the index of a term in a given sequence depends on the sequence's indexing function.
        The indexing function maps the position of a given term to its index.
    """

    default_indexing_func: Callable[[int, int], int] = lambda position, initial_index: initial_index + position - 1
    default_initial_index = 0
    default_inverse_func = None
    def __init__(
            self,
            *,
            func: Callable[[int], float],
            inverse_func: Callable[[float], float | int] = None,
            indexing_func: Callable[[int], int] = None,
            initial_position=0,
            initial_index=0,
            **kwargs,
    ) -> None:
        super().__init__()

        # Ensure that the provided functions are callables
        for fn in (func, inverse_func, indexing_func,):
            if fn is not None and not callable(fn):
                raise NSequenceException(
                    f"Expect a callable .i.e a function but got non callable object {fn}"
                )

        # This function may hold the implementation of a recursive sequence.
        # In that case, the client could have cache add caching capability to
        # the function
        self._func = func

        # The supposed inverse of `self._func`
        self._inverse_func = inverse_func

        # The starting index of the sequence
        self._initial_index = initial_index

        # The indexing function takes a position (of a term in the sequence) and gives
        # its index. Such function maps `{1, 2, 3,.., }` to the sequence indices set
        self._indexing_func = indexing_func or (lambda position: self._initial_index + position - 1)

        # FIXME: Complexe funcs
        # Extra data
        self._kwargs = kwargs or {}

    def nth_term(self, n: int):
        """Computes the nth term of the sequence"""

        # Compute the index of the nth term
        nth_term_index = self._indexing_func(n)

        return self._func(nth_term_index)

    def sum_up_to_nth_term(self, n: int):
        """
        Computes the sum of the sequence up to the nth term.
        `n` is the position of a the nth term of the sequence.

        For instance, if the sequence's initial index is -2 then the `nth` term
        here is the sequence's term at the nth position, counting from -2 . The count
        is made here regarding the sequence's initial position

        TODO: Improve this doc
        """

        if n < 1:
            raise NSequenceException(
                f"Expect position to be at least equal to `1`, but got {n}"
            )

        sum_up_func: Callable[[int, dict], float] = self._kwargs.get("sum_up_func")
        if sum_up_func and callable(sum_up_func):
            sum_to_return = sum_up_func(
                n,
                initial_index=self._initial_index,
            )
        else:
            # No `sum_up_func` func provided through kwargs
            sum_to_return = sum(
                [
                    self._func(index)
                    for index in range(
                        self._initial_index, n - self._initial_index + 1 + 1
                    )
                    # The last `+1` helps to include the `nth` index in the sum range
                ]
            )

        return sum_to_return

    # METHODS FOR INVERTIBLE SEQUENCES

    def index_of_term(self, term: float, raise_exception_if_not_exact=True):
        """
        Computes the index of a given term in the sequence.

        Parameters:
        - term (float): The term for which to find the index.
        - raise_exception_if_not_exact (bool): If True, raises an exception if the index is not an integer.

        Returns:
        int: The index of the given term in the sequence.

        Raises:
        NSequenceException: If inverse_func is not defined, or if the index is not an integer.
        """
        if not self.is_invertible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but "
                f"got {self._inverse_func}"
            )

        index = self._inverse_func(term)

        if not raise_exception_if_not_exact:
            return index

        self._ensure_indices_are_integers(index)

        return int(index)

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

        if not self.is_invertible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Ensure that all the computed indices are integers

        self._ensure_indices_are_integers(
            term1_index, term2_index
        )

        # Provide the int versions of indices for the count computation
        return self.count_terms_between(int(term1_index), int(term2_index))

    @staticmethod
    def count_terms_between(n1: int, n2: int):
        """
        Counts the number of terms between two given indices in the sequence.

        Parameters:
        - n1 (int): The first index.
        - n2 (int): The second index.

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
        if not self.is_invertible:
            raise NSequenceException(
                f"Expect `inverse_func` to be defined and to be callable but got {self._inverse_func}"
            )

        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Raise an exception if any index is not integer
        self._ensure_indices_are_integers(term1_index, term2_index)

        return self.terms_between(int(term1_index), int(term2_index))

    def terms_between(self, index1: int, index2: int, include_args_terms=True):
        """
        Lists the terms between two given indices in the sequence.

        Parameters:
        - index1 (int): The first index.
        - index2 (int): The second index.
        - include_args_terms (bool): If True, includes the terms at index1 and index2.

        Returns:
        List[float]: The terms between index1 and index2, optionally including index1 and index2.
        """
        range_inf = min(index1, index2)
        range_sup = max(index1, index2)

        if not include_args_terms:
            range_inf = range_inf + 1
            range_sup = range_sup - 1

        return [self._func(index) for index in range(range_inf, range_sup + 1)]

    def nearest_term_index(self, term_neighbor: float, *, prefer_left_term=True):
        """
        Finds the index of the nearest term in the sequence to a given term.

        Parameters:
        - term_neighbor (float): The term for which to find the nearest index.
        - prefer_left_term (bool): If True, prefers the left term in case of a tie.

        Returns:
        int: The index of the nearest term to term_neighbor.
        """

        # Here the index of `term_neighbor` can be float because it
        # may not one of the sequence's terms.
        term_neighbor_index = self._inverse_func(term_neighbor)

        if is_floating_integer(term_neighbor_index):
            # The provided term is a term of the sequence so do nothing
            return term_neighbor_index

        left_nearest_term_index = floor(term_neighbor_index)
        right_nearest_term_index = ceil(term_neighbor_index)

        left_nearest_term = self._func(left_nearest_term_index)
        right_nearest_term = self._func(right_nearest_term_index)

        left_distance_to_neighbor = abs(term_neighbor - left_nearest_term)
        right_distance_to_neighbor = abs(term_neighbor - right_nearest_term)

        if (
                not prefer_left_term
                and left_distance_to_neighbor == right_distance_to_neighbor
        ):
            return right_nearest_term_index

        return (
            right_nearest_term_index
            if left_distance_to_neighbor > right_distance_to_neighbor
            else left_nearest_term_index
        )

    def nearest_term(
            self, term_neighbor: float, *, prefer_left_term=True
    ) -> tuple[float, int]:
        """Gets the nearest term in the sequence to the given `term_neighbor`."""
        return self._func(
            self.nearest_term_index(
                term_neighbor, prefer_left_term=prefer_left_term
            )
        )

    # PROPERTIES

    @property
    def initial_index(self) -> float:
        """Gets the initial index provided while creating the sequence."""
        return self._initial_index

    @property
    def initial_term(self) -> float:
        """Gets the initial term of the sequence."""
        return self._func(self._initial_index)

    @property
    def is_invertible(self):
        """Checks if the sequence is invertible."""
        return self._inverse_func

    @classmethod
    def _ensure_indices_are_integers(cls, *indices):
        for index in indices:
            # Raise an exception if the index is not an integer
            if not is_floating_integer(index):
                raise NSequenceException(
                    f"Expect `inverse_fun` to give integers as results but got a float "
                    f"with non-zero decimal {index}"
                )
