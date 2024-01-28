import functools
import inspect
from typing import Callable, Any

from math import ceil, floor


# TODO: Doc about funcs monotony and continuity
# TODO: Fix docstrings
# TODO: Fix typing (some funcs should have float / int or float as return type
# TODO: Some default functions setting

class ArityMismatchError(Exception):
    def __init__(self, func_name, expected_arity, actual_arity):
        super().__init__(
            f"Function {func_name} expected {expected_arity} arguments but got {actual_arity}"
        )


class UnexpectedPositionError(Exception):
    def __init__(self, msg):
        super().__init__(
            msg
        )


class UnexpectedIndexError(Exception):
    def __init__(self, msg):
        super().__init__(
            msg
        )


class InversionError(Exception):
    def __init__(self, msg):
        super().__init__(
            msg
        )


class IndexNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(
            msg
        )


class NSequence(object):
    POSITION_LIMIT = 1_000_000

    def __init__(
            self,
            *,
            func: Callable[[int], float],
            inverse_func: Callable[[float], float | int] = None,
            indexing_func: Callable[[int], int] = None,
            indexing_inverse_func: Callable[[int], int] = None,
            sum_up_func: Callable[[int], float] = None,
            terms_between_counting_func: Callable[[int, int], int] = None,
            initial_index=0,
            **kwargs,
    ) -> None:
        super().__init__()

        self.__validate_func(func, expected_arity=1, is_optional=False)

        _optional_funcs_entries = [
            # (func, expected_arity)
            (inverse_func, 1),
            (indexing_func, 1),
            (indexing_inverse_func, 1),
            (sum_up_func, 1),
            (terms_between_counting_func, 2),
        ]

        for _opt_func, _arity in _optional_funcs_entries:
            self.__validate_func(
                _opt_func,
                expected_arity=_arity,
            )

        # This function may hold the implementation of a recursive sequence.
        # In that case, the client could have cache add caching capability to
        # the function.
        self._func = func

        # The supposed inverse of `self._func`
        self._inverse_func = inverse_func
        self._indexing_inverse_func = indexing_inverse_func
        # The starting index of the sequence
        self._initial_index = initial_index

        #
        self._sum_up_func = sum_up_func

        self._terms_between_counting_func = terms_between_counting_func

        # The indexing function takes a position (of a term in the sequence) and gives
        # its index. Such function maps `{1, 2, 3,.., }` to the sequence indices set
        self._indexing_func = indexing_func or (
            lambda position: self._initial_index + position - 1
        )

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
            raise ValueError(f"Expect position to be at least `1`, but got {n}")

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

    def index_of_term(self, term: float, raise_not_exact_exception=True):
        """
        Computes the index of a given term in the sequence.

        Parameters:
        - term (float): The term for which to find the index.
        - raise_not_exact_exception (bool): If True, raises an exception if the index is not an integer.

        Returns:
        int: The index of the given term in the sequence.

        Raises:
        InversionError: If inverse_func is not defined, or if the index is not an integer.
        """
        if not self.is_invertible:
            raise InversionError(
                "Cannot calculate `index_of_term` for sequence without `inverse_func`. It was not set.",
            )

        index = self._inverse_func(term)

        if not raise_not_exact_exception:
            return index

        self.__validate_indices(index)

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
        InversionError: If inverse_func is not defined or not callable.
        """

        if not self.is_invertible:
            raise InversionError(
                "Cannot calculate `count_terms_between_terms` for sequence "
                "without `inverse_func`. It was not set.",
            )

        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Ensure that all the computed indices are integers

        self.__validate_indices(term1_index, term2_index)

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

        if self._terms_between_counting_func:
            return self._terms_between_counting_func(index1, index2)

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
        self.__validate_indices(term1_index, term2_index)

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

        nearest_term_index, _ = self.nearest_entry(
            term_neighbor,
            inversion_technic=inversion_technic,
            starting_position=starting_position,
            iter_limit=iter_limit,
            prefer_left_term=prefer_left_term,
        )

        return nearest_term_index

    def nearest_term(
            self,
            term_neighbor: float,
            inversion_technic=True,
            starting_position=1,
            iter_limit=1000,
            prefer_left_term=True,
    ) -> float | int:
        """Gets the nearest term in the sequence to the given `term_neighbor`."""

        _, nearest_term = self.nearest_entry(
            term_neighbor,
            inversion_technic=inversion_technic,
            starting_position=starting_position,
            iter_limit=iter_limit,
            prefer_left_term=prefer_left_term,
        )

        return nearest_term

    def nearest_entry(
            self,
            term_neighbor: float,
            inversion_technic=bool,
            starting_position=1,
            iter_limit=1000,
            prefer_left_term=True,
    ):
        # `iter_limit` and `starting_position` are ignored if `inversion_technic` is `True`.

        # We prefer caching the result one level down in other to avoid caching the same
        # entry many times when the developer misuse the method by providing `iter_limit`
        # or `starting_position` while inversion_technic is `True`.

        if inversion_technic:
            nearest_term_index, nearest_term = (
                self.__inversely_get_sequence_nearest_entry(
                    term_neighbor,
                    prefer_left_term=prefer_left_term,
                )
            )
        else:
            nearest_term_index, nearest_term = (
                self.__naively_get_sequence_nearest_entry(
                    term_neighbor,
                    starting_position=starting_position,
                    iter_limit=iter_limit,
                    prefer_left_term=prefer_left_term,
                )
            )
        return nearest_term_index, nearest_term

    @functools.lru_cache(maxsize=128)
    def index_position(self, index: int) -> int:
        if self._indexing_inverse_func:
            # The `indexing_inverse_func` is provided
            return self._indexing_inverse_func(index)
        try:
            position_of_index = next(
                p
                for p in range(1, self.POSITION_LIMIT)
                if self._indexing_func(p) == index
            )
        except StopIteration as exc:
            raise IndexNotFoundError(
                f"Index {index} not found within the first {self.POSITION_LIMIT} positions "
                f"of the sequence."
            ) from exc

        return position_of_index

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

    def __create_sequence_pairs_generator(self, terms_limit=1000, starting_position=1):
        # https://stackoverflow.com/questions/1995418/python-generator-expression-vs-yield
        for position in range(starting_position, starting_position + terms_limit):
            # Index of the position .i.e the `position_th` index
            position_index = self._indexing_func(position)
            yield position_index, self._func(position_index)

    @functools.lru_cache(maxsize=128)
    def __naively_get_sequence_nearest_entry(
            self,
            term_neighbor: float,
            starting_position=1,
            iter_limit=1000,
            prefer_left_term=True,
    ):
        # You have another idea ? Let's discuss it

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

        # Return the index and the corresponding term as a tuple
        return nearest_term_index, nearest_term

    @functools.lru_cache(maxsize=128)
    def __inversely_get_sequence_nearest_entry(
            self,
            term_neighbor: float,
            prefer_left_term=True,
    ) -> tuple[int, float | int]:
        # Here the index of `term_neighbor` can be floated because it
        # may not be one of the sequence's terms.
        term_neighbor_index = self._inverse_func(term_neighbor)
        term_neighbor_position = self.index_position(term_neighbor_index)

        # If position is integer then index should too
        if self.__is_integer(term_neighbor_position) and not self.__is_integer(
                term_neighbor_index
        ):
            raise UnexpectedIndexError(
                f"Expect index of position {term_neighbor_position} to be an integer "
                f"but it was {term_neighbor_index}"
            )

        if all(
                self.__is_integer(val)
                for val in (
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

        # Return the index and the corresponding term as a tuple
        return self._indexing_func(nearest_term_position), self.nth_term(
            nearest_term_position
        )

    @staticmethod
    def __count_positions_between(position1: int, position2: int) -> int:
        return abs(position2 - position1) + 1

    @staticmethod
    def __is_integer(value: float) -> bool:
        return value % 1 == 0

    @classmethod
    def __validate_positions(cls, *values_to_validate):
        try:
            cls.__validate_integers(
                *values_to_validate
            )
        except ValueError as exc:
            raise UnexpectedIndexError(
                f"Expect `indices` to be list of integers (only) but actually "
                f"got a list containing float(s) with non zeros decimals {values_to_validate}"
            ) from exc

    @classmethod
    def __validate_indices(cls, *values_to_validate):
        try:
            cls.__validate_integers(
                *values_to_validate
            )
        except ValueError as exc:
            raise UnexpectedIndexError(
                f"Expect an `indices` to be a list of integers but actually "
                f"got a list containing float(s) with non zeros decimals {values_to_validate}"
            ) from exc

    @classmethod
    def __validate_integers(cls, *values_to_validate):
        # Caller wants to ensure that all provided values are integers
        # or are decimals with zeros after the decimal point
        for value in values_to_validate:
            # Raise an exception if `value` is not an integer
            if not cls.__is_integer(value):
                raise ValueError(
                    f"Expect an integer but got {value}"
                )

    @staticmethod
    def __validate_func(
            func_to_validate: Any, expected_arity: int = 0, is_optional=True
    ):
        """
        Ensure that `func_to_validate` is a function and has the correct number of
        parameters
        """

        if is_optional and func_to_validate is None:
            # Do nothing
            return

        if not inspect.isfunction(func_to_validate):
            raise TypeError(f"Expect a function but got {func_to_validate}")

        func_signature = inspect.signature(func_to_validate)
        func_arity = len(func_signature.parameters)

        if func_arity != expected_arity:
            raise ArityMismatchError(
                func_name=getattr(func_to_validate, "name", ""),
                expected_arity=expected_arity,
                actual_arity=func_arity,
            )
