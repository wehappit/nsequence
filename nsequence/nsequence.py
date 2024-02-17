import functools
import inspect

from typing import Callable, Any
from math import ceil, floor
from collections.abc import Iterator, Sequence

from .exceptions import (
    ArityMismatchError,
    UnexpectedIndexError,
    UnexpectedPositionError,
    InversionError,
    IndexNotFoundError,
)

# DOCME: Doc about functions monotony and continuity impact

number = int | float

LRU_CACHE_MAX_SIZE = 128

POSITION_LIMIT = 1_000_000

DEFAULT_INITIAL_INDEX = 0

INITIAL_POSITION = 1


class NSequence(Iterator, Sequence):
    def __init__(
        self,
        *,
        func: Callable[[int], Any],
        inverse_func: Callable[[Any], number] = None,
        indexing_func: Callable[[number], number] = None,
        indexing_inverse_func: Callable[[number], number] = None,
        initial_index=None,
        position_limit=None,
    ) -> None:
        super().__init__()

        self._validate_func(func, expected_arity=1, is_optional=False)

        _optional_funcs_entries = [
            # (function, expected_arity)
            (inverse_func, 1),
            (indexing_func, 1),
            (indexing_inverse_func, 1),
        ]

        for _opt_func, _arity in _optional_funcs_entries:
            self._validate_func(_opt_func, expected_arity=_arity)

        self._validate_mutually_exclusive_params(
            "When `indexing_func` is defined, `initial_index` becomes automatically "
            "`indexing_func` image by the first position that is always 1. The intend "
            "of this is to help you better to be aware of what you're doing.",
            initial_index=initial_index,
            indexing_func=indexing_func,
        )

        # This function may hold the implementation of a recursive sequence.
        # In that case, the client could have added caching capability to the
        # function.
        self._func = func

        # The supposed inverse of `self._func`
        self._inverse_func = inverse_func
        self._indexing_inverse_func = indexing_inverse_func

        # The indexing function takes a position (of a term in the sequence) and gives
        # its index. Such function maps `{1, 2, 3,.., }` to the sequence indices set

        # NOTE: `indexing_func` is supposed to be bijective
        if indexing_func:
            # If `indexing_func` is provided, we should ignore the provided
            # `initial_index` and use the one computed from the `indexing_func`

            self._indexing_func = indexing_func
            # Set the starting index of the sequence
            self._initial_index = self._indexing_func(INITIAL_POSITION)
        else:
            # Use the default indexing func and its inverse
            self._indexing_func = lambda position: self._initial_index + position - 1
            self._indexing_inverse_func = lambda index: index - self._initial_index + 1
            # Set the starting index of the sequence
            self._initial_index = initial_index or DEFAULT_INITIAL_INDEX

        self._position_limit = position_limit or POSITION_LIMIT

    def __iter__(self):
        self._iter_position = INITIAL_POSITION
        return self

    def __next__(self):
        if not hasattr(self, "_iter_position"):
            # When `next` is called on the sequence directly
            self._iter_position = INITIAL_POSITION

        if self._iter_position > self._position_limit:
            # "position" can take the right value of the bounds
            raise StopIteration

        _position = self._iter_position
        self._iter_position += 1
        return self.nth_term(_position)

    def __len__(self):
        return self._position_limit

    def __getitem__(self, position: int | slice) -> Any:
        if isinstance(position, int):
            _position = position
            if _position < 0:
                # Convert negative position to positive position to ensure
                # that we support list-like negative indexing.
                _position = len(self) + _position

            if _position < 0 or _position >= self._position_limit:
                raise IndexError("NSequence instance out of range")
            return self.nth_term(_position + 1)
        elif isinstance(position, slice):
            # Add support for slices
            start, stop, step = position.indices(self._position_limit)
            return [self.nth_term(i + 1) for i in range(start, stop, step)]
        else:
            raise TypeError(
                f"Invalid argument type. int or slice expected, but got {position}"
            )

    def nth_term(self, n: int) -> Any:
        """
        Computes the nth term of the sequence using a predefined function.

        This method applies the function `_func` to the result of `_indexing_func(n)`,
        effectively calculating the nth term of the sequence. `_func` is the main
        function defining the sequence's behavior, while `_indexing_func` maps indices
        to inputs for `_func`.

        Args:
            n (int): Position in the sequence to calculate the term for. Must be
                    a positive integer.

        Returns:
            Any: The nth term of the sequence. It depends on the sequence function.

        """

        self._validate_positions(n)

        return self._func(self._indexing_func(n))

    def sum_up_to_nth_term(self, n: int) -> Any:
        """
        Calculate the sum of the sequence up to the nth term.

        This method computes the cumulative sum of the sequence from the first term up
        to the nth term by individually calculating each term's value and summing them up.

        It should be overridden if the return type of the sequence's function does not
        implement `__add__`.

        Args:
            n (int): .The position up to which the sum is to be calculated. Must be a
            positive integer

        Returns:
            Any: The sum of the sequence's terms up to the nth term.

        Raises:
            NotImplementedError: If the sum cannot be computed with the default summing function.
            This indicates that a custom `sum_up_func` needs to be provided.
        """
        self._validate_positions(n)

        try:
            sum_to_return = sum(self.nth_term(position) for position in range(1, n + 1))
        except (TypeError, ValueError, ArithmeticError) as exc:
            raise NotImplementedError(
                "Failed to compute the sequence's n first terms sum with the default `sump_up_func`."
                "The default `sump_up_func` implementation seems not appropriate for your use case."
                "You should override the default `sum_up_func` implementation."
            ) from exc

        return sum_to_return

    # METHODS FOR INVERTIBLE SEQUENCES

    @functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE)
    def index_of_term(
        self, term: Any, inversion_technic=True, exact_exception=True
    ) -> number:
        """
        Finds the index of a given term in the sequence.

        Args:
            term (Any): The sequence term to find the index for.
            inversion_technic (bool): If False uses a brute-force search to find the index.
                                Defaults to True.
            exact_exception (bool): If True, raises an exception if the term does
                                    not exactly match any sequence term. Defaults
                                    to True.

        Returns:
            int: The index of the term in the sequence.

        Raises:
            InversionError: If `inversion_technic` is True and no inverse function is
                            provided.
            ValueError: If `exact_exception` is True and the term is not found.
        """
        if not self._inverse_func and inversion_technic:
            raise InversionError(
                "Cannot calculate `index_of_term` for sequence without `inverse_func` and with "
                "`inversion_technic` set to `True`. You need either to provide `inverse_func` or set "
                "`inversion_technic` to `False`"
            )

        if self._inverse_func:
            index = self._inverse_func(term)

        else:
            # We will (kinda) brute-force to get the wanted index.
            # The first index that brings that term will be returned

            position_of_index = next(
                (
                    position
                    for position in range(1, POSITION_LIMIT)
                    if self.nth_term(position) == term
                ),
                None,
            )

            # Raising an exception depends on the value of `exact_exception`
            # So, if the `position_of_index` is `None`, `_validate_indices` will raise
            # the exception for us in the next lines if `exact_exception` is True
            index = (
                self._indexing_func(position_of_index) if position_of_index else None
            )

        if not exact_exception:
            # `index` might not be an integer here but the client code prefers
            # us to not raise an exception.
            return index

        self._validate_indices(index)

        return int(index)

    def count_terms_between_terms(self, term1: Any, term2: Any) -> int:
        """
        Counts the number of terms between two given terms in the sequence, using
        the sequence's inverse function to find their indices.

        This method is meaningful for sequences where a bijective (one-to-one and
        onto) relationship exists between terms and their indices.

        Parameters:
        - term1 (Any): The first term in the sequence.
        - term2 (Any): The second term in the sequence.

        Returns:
        - int: The number of terms between `term1` and `term2`, exclusive.

        Raises:
        - InversionError: If an inverse function has not been defined or is not
        applicable, indicating that term indices cannot be accurately determined.
        """

        if not self._inverse_func:
            raise InversionError(
                "Cannot calculate `count_terms_between_indices_terms` for sequence "
                "without `inverse_func`. It was not set.",
            )

        # Find indices of the given terms using the inverse function
        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Ensure that all the computed indices are integers
        self._validate_indices(term1_index, term2_index)

        # Provide the int versions of indices for the count computation
        return self.count_terms_between_indices(int(term1_index), int(term2_index))

    def count_terms_between_indices(self, index1: int, index2: int):
        """
        Counts the number of terms between two indices in the sequence.

        Assumes the indexing function is bijective, allowing for direct mapping
        between indices and sequence positions. Validates the positions of the
        indices before computing the difference to ensure they're within the
        acceptable range of the sequence.

        Parameters:
        - index1 (int): The first index.
        - index2 (int): The second index.

        Returns:
        - int: The count of terms between the two indices.

        Raises:
        - Any validation errors raised by `_validate_positions` or
        `position_of_index`.
        """

        # Convert indices to positions in the sequence
        index1_position = self.position_of_index(index1)
        index2_position = self.position_of_index(index2)

        self._validate_positions(index1_position, index2_position)

        return self._count_positions_between(index1_position, index2_position)

    def count_terms_between_terms_neighbors(self, neighbor1, neighbor2):
        # Let's do this only for invertible sequences
        return self.count_terms_between_terms(
            self.nearest_term(neighbor1, prefer_left_term=False),
            self.nearest_term(neighbor2, prefer_left_term=True),
        )

    def terms_between_terms(self, term1: Any, term2: Any):
        """
        Returns the terms located between two given terms in the sequence.

        Utilizes the inverse function to convert `term1` and `term2` into their
        respective indices, then retrieves all terms between these indices.

        Parameters:
        - term1 (Any): The first term in the sequence.
        - term2 (Any): The second term in the sequence.

        Returns:
        - A list of terms between `term1` and `term2`.

        Raises:
        - InversionError: If `inverse_func` is not defined.
        - ValueError: If calculated indices are not valid or if `term1_index` or
        `term2_index` are not integers.
        """

        if not self._inverse_func:
            raise InversionError(
                f"Expect `inverse_func` to be defined but got {self._inverse_func}"
            )

        term1_index = self._inverse_func(term1)
        term2_index = self._inverse_func(term2)

        # Raise an exception if any index is not integer
        self._validate_indices(term1_index, term2_index)

        return self.terms_between_indices(int(term1_index), int(term2_index))

    def terms_between_indices(self, index1: int, index2: int):
        """
        Returns the terms between two given indices, inclusive.

        Parameters:
        - index1 (int): The first index.
        - index2 (int): The second index.

        Returns:
        - list[Any]: A list of terms between the two indices, inclusive.
        """
        index1 = min(index1, index2)
        index2 = max(index1, index2)

        index1_position = self.position_of_index(index1)
        index2_position = self.position_of_index(index2)

        return [
            self.nth_term(position)
            for position in range(index1_position, index2_position + 1)
        ]

    def nearest_term_index(
        self,
        term_neighbor: Any,
        inversion_technic=True,
        starting_position=None,
        iter_limit=None,
        prefer_left_term=True,
    ):
        """
        Finds the index of the nearest term to a given value in the sequence.

        Depending on the `inversion_technic` flag, this function either utilizes
        the sequence's inverse function for an efficient lookup or conducts an
        iterative search. For iterative searches, `starting_position` and
        `iter_limit` define the search's start and the maximum iterations.
        `prefer_left_term` dictates the preference for the left or right term
        when two are equally distant from `term_neighbor`.

        Parameters:
            term_neighbor (Any): The value to find the nearest sequence term to.
            inversion_technic (bool): If True, uses inversion for efficient search.
            starting_position (int): Starting point for the search (ignored if
                                    `inversion_technic` is True).
            iter_limit (int): Max iterations for the search (ignored if
                            `inversion_technic` is True).
            prefer_left_term (bool): If True, prefers the left term in case of
                                    equidistant terms.

        Returns:
            int: Index of the nearest term to `term_neighbor`.
        """

        iter_limit = iter_limit or self._position_limit
        starting_position = starting_position or INITIAL_POSITION

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
        term_neighbor: Any,
        inversion_technic=True,
        starting_position=None,
        iter_limit=None,
        prefer_left_term=True,
    ) -> number:
        """
        Retrieves the term in the sequence that is nearest to a specified value.

        Depending on the `inversion_technic` parameter, this function will either use
        the sequence's inverse function for an efficient determination of the nearest term
        or perform an iterative search starting from `starting_position` up to a limit
        defined by `iter_limit`. When two terms are equally distant from `term_neighbor`,
        `prefer_left_term` decides whether the term on the left (if True) or on the right
        (if False) is selected as the nearest.

        Parameters:
            term_neighbor (Any): The value to find the nearest sequence term for.
            inversion_technic (bool): If True, uses the inversion technique for finding
                                    the nearest term, otherwise uses iterative search.
            starting_position (int): The starting position for iterative search, ignored
                                    if `inversion_technic` is True.
            iter_limit (int): The iteration limit for the search, ignored if
                            `inversion_technic` is True.
            prefer_left_term (bool): Indicates preference for the left term in case of
                                    equidistant terms from `term_neighbor`.

        Returns:
            Any: The term in the sequence nearest to the specified `term_neighbor`.
        """

        iter_limit = iter_limit or self._position_limit
        starting_position = starting_position or INITIAL_POSITION

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
        term_neighbor: Any,
        inversion_technic=True,
        starting_position=None,
        iter_limit=None,
        prefer_left_term=True,
    ):
        """
        Finds the nearest term in the sequence to a given term, using either
        an inversion technique or a naive search approach.

        Parameters:
        - term_neighbor (Any): The term to find the nearest for.
        - inversion_technic (bool): If True, uses inversion function for finding
        the nearest term. If False, performs a naive search. Default is True.
        - starting_position (int): The starting position for the naive search.
        Ignored if inversion_technic is True. Default is 1.
        - iter_limit (int): The iteration limit for the naive search. Ignored if
        inversion_technic is True. Default is position_limit.
        - prefer_left_term (bool): Preference for the left the nearest term if distances
        are equal. Default is True.

        Returns:
        - A tuple (nearest_term_index, nearest_term) representing the index and the
        value of the nearest term found.

        Note:
        `iter_limit` and `starting_position` are ignored when `inversion_technic` is True.
        Caching is applied at a lower level to avoid duplicate entries when `iter_limit`
        or `starting_position` are provided with `inversion_technic` set to True.
        """

        if inversion_technic:
            if not self._inverse_func:
                raise InversionError(
                    "Cannot calculate `nearest_entry` for sequence without `inverse_func` and with "
                    "`inversion_technic` set to `True`. You need either to provide `inverse_func` or set "
                    "`inversion_technic` to `False` to use the naive approach"
                )

            (
                nearest_term_index,
                nearest_term,
            ) = self._inversely_get_sequence_nearest_entry(
                term_neighbor,
                prefer_left_term=prefer_left_term,
            )
        else:
            iter_limit = iter_limit or self._position_limit
            starting_position = starting_position or INITIAL_POSITION

            try:
                (
                    nearest_term_index,
                    nearest_term,
                ) = self._naively_get_sequence_nearest_entry(
                    term_neighbor,
                    starting_position=starting_position,
                    iter_limit=iter_limit,
                    prefer_left_term=prefer_left_term,
                )
            except (TypeError, ValueError, ArithmeticError) as exc:
                raise NotImplementedError(
                    f"Failed to compute the `nearest_entry` for {term_neighbor} "
                    "May be you should override the default `nearest_entry` implementation."
                ) from exc
        return nearest_term_index, nearest_term

    @functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE)
    def position_of_index(self, index: int) -> int:
        """
        Finds the position in the sequence corresponding to the given index using
        the sequence's indexing function or its inverse if provided.

        Utilizes caching to enhance performance for repeated queries.

        Parameters:
        - index (int): The index for which the corresponding position is sought.

        Returns:
        - int: The position within the sequence that corresponds to the given index.

        Raises:
        - IndexNotFoundError: If the index is not found within the bounds set by
        `POSITION_LIMIT`.
        """

        if self._indexing_inverse_func:
            # Return the position if an inverse indexing function is available
            return self._indexing_inverse_func(index)
        try:
            _position_of_index = next(
                p
                for p in range(1, POSITION_LIMIT)
                if self._indexing_func(p) == index
            )
        except StopIteration as exc:
            raise IndexNotFoundError(
                f"Index {index} not found within {POSITION_LIMIT} positions "
                f"of the sequence."
            ) from exc

        return _position_of_index

    # PROPERTIES

    @property
    def initial_index(self) -> int:
        """The initial index provided while creating the sequence."""
        return self._initial_index

    @property
    def initial_term(self) -> Any:
        """The initial term of the sequence."""
        return self._func(self._initial_index)

    @property
    def position_limit(self) -> int:
        """The length of the sequence."""
        return self._position_limit

    def _create_sequence_pairs_generator(self, iter_limit=None, starting_position=None):
        iter_limit = iter_limit or self._position_limit
        starting_position = starting_position or INITIAL_POSITION
        for position in range(starting_position, starting_position + iter_limit):
            # Index of the position .i.e the `position_th` index
            position_index = self._indexing_func(position)
            yield position_index, self._func(position_index)

    @functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE)
    def _naively_get_sequence_nearest_entry(
        self,
        term_neighbor: Any,
        starting_position=None,
        iter_limit=None,
        prefer_left_term=True,
    ):
        """
        Finds the sequence entry nearest to a given term, using a naive approach.

        Parameters:
        - term_neighbor (Any): The term to find the nearest neighbor for.
        - starting_position (int, optional): The sequence position to start searching from. Defaults to 1.
        - iter_limit (int, optional): The maximum number of terms to consider in the search. Defaults to 1000.
        - prefer_left_term (bool, optional): Whether to prefer the left term. Defaults to True.

        Returns:
        - A tuple (nearest_term_index, nearest_term) representing the index and value of the nearest term found.

        This method naively iterates through the sequence, comparing each term's distance to the target term
        and updating the nearest term accordingly. It's optimized for sequences where terms are not sorted or
        where no faster lookup method is available.
        """

        # This implementation makes sens only if the return type of the sequence's function is a float

        iter_limit = iter_limit or self._position_limit
        starting_position = starting_position or INITIAL_POSITION

        lazy_generated_pairs = self._create_sequence_pairs_generator(
            iter_limit=iter_limit, starting_position=starting_position
        )

        min_distance = float("inf")
        nearest_term_index, nearest_term = None, None

        for index, term in lazy_generated_pairs:
            distance = abs(term - term_neighbor)

            if (distance == min_distance and not prefer_left_term) or (
                distance < min_distance
            ):
                min_distance = distance
                nearest_term_index = index
                nearest_term = term

            if prefer_left_term and distance == 0:
                # Early exit if an exact match is found and `prefer_left_term`.
                # The term provided is actually a term of the sequence. We could
                # have just returned if the distance is zero. But the client code
                # may provide an one-to-one function for the sequence and wants the
                # last most indices that is giving zero as distance.
                break

        # Return the index and the corresponding term as a tuple
        return nearest_term_index, nearest_term

    @functools.lru_cache(maxsize=LRU_CACHE_MAX_SIZE)
    def _inversely_get_sequence_nearest_entry(
        self,
        term_neighbor: Any,
        prefer_left_term=True,
    ) -> tuple[int, number]:
        """
        Finds the nearest sequence entry to a given term using inverse function.

        This method utilizes the inverse function of the sequence to estimate the
        position of a term close to `term_neighbor`, then identifies the nearest
        actual term in the sequence.

        Parameters:
        - term_neighbor (Any): The term to find the nearest neighbor for.
        - prefer_left_term (bool, optional): Prefers the left term in case of equal
        distances. Defaults to True.

        Returns:
        - A tuple (index, term) representing the index and value of the nearest term.

        Raises:
        - UnexpectedIndexError: If the calculated index or position is not consistent.
        """

        term_neighbor_index = self._inverse_func(term_neighbor)
        term_neighbor_position = self.position_of_index(term_neighbor_index)

        # If position is integer then index should too
        if self._is_integer(term_neighbor_position) and not self._is_integer(
            term_neighbor_index
        ):
            raise UnexpectedIndexError(
                f"Expect index of position {term_neighbor_position} to be an integer, "
                f"but it was {term_neighbor_index}"
            )

        if all(
            self._is_integer(val)
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

    # (WANTED) PROTECTED METHODS

    @staticmethod
    def _count_positions_between(position1: int, position2: int) -> int:
        return abs(position2 - position1) + 1

    @staticmethod
    def _is_integer(value: number | None) -> bool:
        return isinstance(value, number) and value % 1 == 0

    @classmethod
    def _validate_positions(cls, *values_to_validate, min_value=None, max_value=None):
        min_value = min_value or INITIAL_POSITION
        try:
            cls._validate_integers(
                *values_to_validate, min_value=min_value, max_value=max_value
            )
        except ValueError as exc:
            raise UnexpectedPositionError(
                f"Expect `positions` to be tuple of integers (strictly greater than 0 and less than the "
                f"specified position_limit), but actually got `{values_to_validate}`"
            ) from exc

    @classmethod
    def _validate_indices(cls, *values_to_validate):
        try:
            cls._validate_integers(*values_to_validate)
        except ValueError as exc:
            raise UnexpectedIndexError(
                f"Expect an `indices` to be a tuple of integers, but actually got a "
                f"tuple containing None or float(s) with non zero decimal(s) {values_to_validate}"
            ) from exc

    @classmethod
    def _validate_integers(cls, *values_to_validate, **constraints):
        # Caller wants to ensure that all provided values are integers
        # or are decimals with zeros after the decimal point

        # Add more constraints if needed
        min_value = constraints.get("min_value", -float("inf"))
        if min_value is None:
            min_value = -float("inf")

        max_value = constraints.get("max_value", float("inf"))
        if max_value is None:
            max_value = float("inf")

        for value in values_to_validate:
            # Raise an exception if `value` is not an integer or does not respect the constraints
            if not cls._is_integer(value) or min_value > value or max_value < value:
                constraints_msg = (
                    f" with constraints {constraints}" if constraints else ""
                )
                raise ValueError(f"Expect an integer{constraints_msg}, but got {value}")

    @staticmethod
    def _validate_func(
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
            raise TypeError(f"Expect a function, but got `{func_to_validate}`")

        func_signature = inspect.signature(func_to_validate)
        func_arity = len(func_signature.parameters)

        if func_arity != expected_arity:
            raise ArityMismatchError(
                f"Function {getattr(func_to_validate, '__name__', '')} is expected to have "
                f"{expected_arity} as arity (.i.e the number of parameters) "
                f"but it actually has {func_arity}"
            )

    @staticmethod
    def _validate_mutually_exclusive_params(msg: str, **kwargs):
        not_none_kwargs = {}
        for param, value in kwargs.items():
            if value is None:
                continue
            # Either uncomment the next statement in the nest release
            # or delete this function
            # assert not not_none_kwargs, msg # TBD
            not_none_kwargs[param] = value
