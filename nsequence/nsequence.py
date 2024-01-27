import functools
from typing import Callable

from math import ceil, floor


# TODO: Doc about funcs monotony and continuity
# TODO: Fix typing

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

    POSITIONS_LIMIT = 1_000_000

    def __init__(
        self,
        *,
        func: Callable[[int], float],
        inverse_func: Callable[[float], float | int] = None,
        indexing_func: Callable[[int], int] = None,
        sum_up_func: Callable[[int], float],
        terms_counting_func: Callable[[int, int], int],
        initial_index=0,
        **kwargs,
    ) -> None:
        super().__init__()

        # Ensure that the provided functions are callables
        for fn in (
            func,
            inverse_func,
            indexing_func,
            sum_up_func,
            terms_counting_func,
        ):
            if fn is not None and not callable(fn):
                raise TypeError(f"Expect a function but got non callable object {fn}")

        # This function may hold the implementation of a recursive sequence.
        # In that case, the client could have cache add caching capability to
        # the function.
        self._func = func

        # The supposed inverse of `self._func`
        self._inverse_func = inverse_func
        # The starting index of the sequence
        self._initial_index = initial_index

        #
        self._sum_up_func = sum_up_func

        self._terms_counting_func = terms_counting_func

        # The indexing function takes a position (of a term in the sequence) and gives
        # its index. Such function maps `{1, 2, 3,.., }` to the sequence indices set
        self._indexing_func = indexing_func or (
            lambda position: self._initial_index + position - 1
        )

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
            raise ValueError(
                f"Expect position to be at least equal to `1`, but got {n}"
            )

        if self._sum_up_func:
            sum_to_return = self._sum_up_func(
                n,
                initial_index=self._initial_index,
            )
        else:
            # No `sum_up_func` defined
            sum_to_return = sum(
                [self.nth_term(position) for position in range(1, n + 1)]
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
                "Cannot calculate `index_of_term` for sequence without `inverse_func`",
            )

        index = self._inverse_func(term)

        if not raise_exception_if_not_exact:
            return index

        self.__validate_integers(index)

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

        self.__validate_integers(term1_index, term2_index)

        # Provide the int versions of indices for the count computation
        return self.count_terms_between(int(term1_index), int(term2_index))

    def count_terms_between(self, index1: int, index2: int):
        """
        Counts the number of terms between two given indices in the sequence.
        The number of terms is the number of valid indices between `index1` and
        `index2` according to `indexing_func`

        Parameters:
        - index1 (int): The first index.
        - index2 (int): The second index.

        Returns:
        int: The number of terms between index1 and index2.
        """

        if self._terms_counting_func:
            return self._terms_counting_func(index1, index2)

        index1_position = self.index_position(index1)
        index2_position = self.index_position(index2)

        return self.__count_positions_between(index1_position, index2_position)

    def terms_between_terms(self, term1: float, term2: float):
        """
        Lists the terms between two given terms in the sequence.

        Parameters:
        - term1 (float): The first term.
        - term2 (float): The second term.

        Returns:
        List[float]: The terms between term1 and term2.

        Raises:
        TypeError: If inverse_func is not defined or not callable.
        """
        if not self.is_invertible:
            raise TypeError(
                f"Expect `inverse_func` to be defined but got {self._inverse_func}"
            )

        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Raise an exception if any index is not integer
        self.__validate_integers(term1_index, term2_index)

        return self.terms_between(int(term1_index), int(term2_index))

    def terms_between(self, index1: int, index2: int):
        """
        Lists the terms between two given indices in the sequence.

        Parameters:
        - index1 (int): The first index.
        - index2 (int): The second index.

        Returns:
        List[float]: The terms between index1 and index2
        """
        index1 = min(index1, index2)
        index2 = max(index1, index2)

        index1_position = self.index_position(index1)
        index2_position = self.index_position(index2)

        return [
            self._func(self._indexing_func(position))
            for position in range(index1_position, index2_position + 1)
        ]

    def nearest_term_index(
        self,
        term_neighbor: float,
        *,
        inversion_technic=True,
        starting_position=1,
        iter_limit=1000,
        prefer_left_term=True,
    ):
        """
        Finds the index of the nearest term in the sequence to a given term.

        !!! Attention: if `inversion_technic=True`, it means that we will use self._func reverse

        Parameters:
        - term_neighbor (float): The term for which to find the nearest index.
        - prefer_left_term (bool): If True, prefers the left term in case of a tie.

        Returns:
        int: The index of the nearest term to term_neighbor.
        """
        if inversion_technic:
            _, nearest_term_index = self.__inversely_get_sequence_nearest_pair(
                term_neighbor,
                prefer_left_term=prefer_left_term,
            )
        else:
            _, nearest_term_index = self.__naively_get_sequence_nearest_pair(
                term_neighbor,
                starting_position=starting_position,
                iter_limit=iter_limit,
                prefer_left_term=prefer_left_term,
            )
        return nearest_term_index

    def nearest_term(
        self,
        term_neighbor: float,
        *,
        inversion_technic=True,
        starting_position=1,
        iter_limit=1000,
        prefer_left_term=True,
    ) -> float:
        """Gets the nearest term in the sequence to the given `term_neighbor`."""

        if not inversion_technic:
            nearest_term, _ = self.__naively_get_sequence_nearest_pair(
                term_neighbor,
                starting_position=starting_position,
                iter_limit=iter_limit,
                prefer_left_term=prefer_left_term,
            )
            return nearest_term

        return self._func(
            self.nearest_term_index(term_neighbor, prefer_left_term=prefer_left_term)
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

    @functools.lru_cache(maxsize=128)
    def index_position(self, index: int) -> int:
        indexing_inverse_func: Callable[[int], int] = self._kwargs(
            "indexing_inverse_func"
        )
        if indexing_inverse_func:
            # The `indexing_inverse_func` is provided
            return indexing_inverse_func(index)
        try:
            position_of_index = next(
                p
                for p in range(1, self.POSITIONS_LIMIT)
                if self._indexing_func(p) == index
            )
        except StopIteration as exc:
            raise NSequenceException(
                f"Index {index} not found within the first {self.POSITIONS_LIMIT} positions of the sequence."
            ) from exc

        return position_of_index

    def __create_sequence_pairs_generator(self, terms_limit=1000, starting_position=1):
        # https://stackoverflow.com/questions/1995418/python-generator-expression-vs-yield
        for position in range(starting_position, starting_position + terms_limit):
            # Index of the position .i.e the `position_th` index
            position_index = self._indexing_func(position)
            yield position_index, self._func(position_index)

    @functools.lru_cache(maxsize=128)
    def __naively_get_sequence_nearest_pair(
        self,
        term_neighbor: float,
        starting_position=1,
        iter_limit=1000,
        prefer_left_term=True,
    ):
        # You have a good/better idea ? Let's discuss it
        lazy_generated_pairs = self.__create_sequence_pairs_generator(
            iter_limit=iter_limit, starting_position=starting_position
        )
        for index, term in lazy_generated_pairs:
            distance = abs(term - term_neighbor)
            if (distance == min_distance and not prefer_left_term) or (
                distance < min_distance
            ):
                min_distance = distance
                nearest_term_index = index
                nearest_term = term
        return nearest_term_index, nearest_term

    @functools.lru_cache(maxsize=128)
    def __inversely_get_sequence_nearest_pair(
        self,
        term_neighbor: float,
        prefer_left_term=True,
    )->tuple[int, float | int]:
        # Here the index of `term_neighbor` can be float because it
        # may not be one of the sequence's terms.
        term_neighbor_index = self._inverse_func(term_neighbor)
        term_neighbor_position = self.index_position(term_neighbor_index)

        # If position is integer then index should too
        if self.__is_integer(term_neighbor_position) and not self.__is_integer(
            term_neighbor_index
        ):
            raise NSequenceException(
                f"Expect index of position {term_neighbor_position} to be an integer "
                f"but it was {term_neighbor_index}"
            )

        if all(
            self.__is_integer(i)
            for i in (
                term_neighbor_position,
                term_neighbor_index,
            )
        ):
            # The provided term is a term of the sequence so do nothing
            return term_neighbor_index, term_neighbor

        left_nearest_term_position = floor(term_neighbor_position)
        right_nearest_term_position = ceil(term_neighbor_position)

        left_nearest_term = self.nth_term(left_nearest_term_position)
        right_nearest_term = self.nth_term(right_nearest_term_position)

        left_distance_to_neighbor = abs(term_neighbor - left_nearest_term)
        right_distance_to_neighbor = abs(term_neighbor - right_nearest_term)

        if (
            not prefer_left_term
            and left_distance_to_neighbor == right_distance_to_neighbor
        ):
            nearest_term_position = right_nearest_term_position
        elif left_distance_to_neighbor > right_distance_to_neighbor:
            nearest_term_position = right_nearest_term_position

        else:
            nearest_term_position = left_nearest_term_position

        return self._inverse_func(nearest_term_position), self.nth_term(
            nearest_term_position
        )

    @staticmethod
    def __count_positions_between(position1: int, position2: int) -> int:
        return abs(position2 - position1) + 1

    @staticmethod
    def __is_integer(value: float) -> bool:
        return value % 1 == 0

    @classmethod
    def __validate_integers(cls, *values_to_validate):
        for value in values_to_validate:
            # Raise an exception if `value` is not an integer
            if not cls.__is_integer(value):
                raise NSequenceException(
                    f"Expect `inverse_fun` to give integers as results but got a float "
                    f"with non-zero decimal {value}"
                )
