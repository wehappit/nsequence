# NSequence

NSequence is a Python library designed for handling progressions or sequences, offering various functions and utilities for working with sequences. It allows users to define sequences through functional expressions, offering capabilities for various computations.

## Real-world Usage

Imagine you're developing a complex event reminder system, 
where data is attached to each reminder. For forecasting and planning purposes, you want to retrieve for a given event
 recall data for a given period in the past (or future)

## Key Features

- **Versatile Sequence Handling**: NSequence supports a wide range of sequence types, including linear, quadratic, cubic, and more. It accommodates both direct and inverse calculations.

- **Error Handling**: The library includes robust error handling for scenarios such as arity mismatches, unexpected positions or indices, inversion errors, and index not found situations.

- **Inverse Functionality**: For invertible sequences, NSequence facilitates finding the index of a given term and vice versa. It provides options for different inversion techniques to suit your specific use case.

- **Nearest Term Search**: NSequence allows you to find the index of the nearest term to a given value in the sequence. It provides flexibility in handling tie-breakers and preferences.


## Installation

You can install NSequence using pip:

```bash
pip install nsequence
```

## Getting Started

```python
from NSequence import NSequence

def my_function(x):
    # Do something with x and return what you want
    # ...
    return x * 2

# Create your sequence
my_sequence = NSequence(func=my_function)

# Use the sequence functionalities
term_3 = my_sequence.nth_term(3)
sum_first_5_terms = my_sequence.sum_up_to_nth_term(5)
```

```python
# Create a linear sequence: f(x) = 2x + 3
linear_sequence = NSequence(func=lambda x: 2 * x + 3)

# Compute the 5th term
term_5 = linear_sequence.nth_term(5)

# Find the index of the term 13
index_of_13 = linear_sequence.index_of_term(13)

# Calculate the sum of the first 10 terms
sum_first_10_terms = linear_sequence.sum_up_to_nth_term(10)
```

```python
# Create a quadratic sequence: f(x) = x^2 + 3
quadratic_sequence = NSequence(func=lambda x: x ** 2 + 3)

# Get the nearest term to 20
nearest_term_to_20 = quadratic_sequence.nearest_term(20)

# Count the terms between 10 and 50
count_terms_between_10_and_50 = quadratic_sequence.count_terms_between_terms(10, 50)
```

```python
# Create an invertible sequence with inverse function
invertible_sequence = NSequence(func=lambda x: 2 * x, inverse_func=lambda y: y / 2)

# Find the index of the term 8
index_of_8 = invertible_sequence.index_of_term(8)

# Compute the terms between indices 5 and 10
terms_between_5_and_10 = invertible_sequence.terms_between_indices(5, 10)
```



## Key Methods

### Constructor .i.e `__init__`

Create a sequence instance

#### Parameters

- `func`: The primary function defining the sequence. This function must accept an integer position and return the corresponding sequence term.

- `inverse_func`: An optional inverse function for `func`, allowing for the computation of positions or indices based on sequence term values.

- `indexing_func`: An optional function that maps sequence positions to custom indices, enabling non-standard indexing schemes.

- `indexing_inverse_func`: The inverse of `indexing_func`, allowing for the determination of sequence positions from indices.

- `initial_index`: The starting index for the sequence. This parameter is ignored if `indexing_func` is provided, as the initial index will then be derived from the indexing function.

### `nth_term`
Returns the sequence term at the given position

#### Parameters
- `position`: Position in the sequence to calculate the term for.


### `position_of_index`
Determines the sequence position of a given index, useful when custom indexing is used.

#### Parameters
- `index`: The index for which to find the corresponding sequence position.

### `count_terms_between_indices`
Counts the number of terms between two indices in the sequence.

#### Parameters
- `index1`: The starting index.
- `index2`: The ending index.

### `nearest_entry`
Finds the nearest sequence entry (both the index and the term) to a given term.

#### Parameters
- `term_neighbor`: The term to find the nearest sequence entry for.
- `inversion_technic`: Whether to use the inversion technique for finding the nearest term.
- `starting_position`: The starting position for the iterative search (ignored if `inversion_technic` is True).
- `iter_limit`: The maximum number of iterations for the search (ignored if `inversion_technic` is True).
- `prefer_left_term`: Preference for the left term in case of equidistant terms.

### `terms_between_terms`
Returns a list of sequence terms located between two given terms, inclusive.

#### Parameters
- `term1`: The first term.
- `term2`: The second term.

### `sum_up_to_nth_term`
Calculate the sum of the sequence up to the nth term.

#### Parameters
- `n`: The position up to which the sum is to be calculated. Must be a positive integer.
- 
### `index_of_term`
Returns the sum of the sequence up to the nth term.

#### Parameters
- `term`:  The sequence term to find the index for.
- `naive_technic`: If True and no inverse function is provided, uses a brute-force search to find the index. Defaults to False.
- `exact_exception`:  If True, raises an exception if the term does not exactly match any sequence term. Defaults to True.

### `count_terms_between_terms`
Counts the number of terms between two given terms in the sequence, using 
the sequence's inverse function to find their indices.

This method is meaningful for sequences where a bijective (one-to-one and
onto) relationship exists between terms and their indices.

#### Parameters
- `term1` (float): The first term in the sequence.
- `term2` (float): The second term in the sequence.




Explore more about NSequence and its capabilities in the [documentation](https://github.com/hjisaac/NSequence).

Feel free to contribute, report issues, or suggest enhancements. Happy sequencing! 📈
