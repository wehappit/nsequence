# NSequence

NSequence is a Python library designed for handling sequences, offering various functions and utilities for working with mathematical sequences. Whether you're dealing with linear, quadratic, or more complex sequences, NSequence provides tools to compute terms, sums, and indices efficiently.

## Key Features

- **Versatile Sequence Handling**: NSequence supports a wide range of sequence types, including linear, quadratic, cubic, and more. It accommodates both direct and inverse calculations.

- **Error Handling**: The library includes robust error handling for scenarios such as arity mismatches, unexpected positions or indices, inversion errors, and index not found situations.

- **Inverse Functionality**: For invertible sequences, NSequence facilitates finding the index of a given term and vice versa. It provides options for different inversion techniques to suit your specific use case.

- **Nearest Term Search**: NSequence allows you to find the index of the nearest term to a given value in the sequence. It provides flexibility in handling tie-breakers and preferences.

## Real-world Examples

### Linear Sequence

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

### Quadratic Sequence

```python
# Create a quadratic sequence: f(x) = x^2 + 3
quadratic_sequence = NSequence(func=lambda x: x ** 2 + 3)

# Get the nearest term to 20
nearest_term_to_20 = quadratic_sequence.nearest_term(20)

# Count the terms between 10 and 50
count_terms_between_10_and_50 = quadratic_sequence.count_terms_between_terms(10, 50)
```

### Invertible Sequence

```python
# Create an invertible sequence with inverse function
invertible_sequence = NSequence(func=lambda x: 2 * x, inverse_func=lambda y: y / 2)

# Find the index of the term 8
index_of_8 = invertible_sequence.index_of_term(8)

# Compute the terms between indices 5 and 10
terms_between_5_and_10 = invertible_sequence.terms_between_indices(5, 10)
```

## Installation

You can install NSequence using pip:

```bash
pip install NSequence
```

## Getting Started

```python
from NSequence import NSequence

# Create your sequence
my_sequence = NSequence(func=lambda x: x * 2)

# Use the sequence functionalities
term_3 = my_sequence.nth_term(3)
sum_first_5_terms = my_sequence.sum_up_to_nth_term(5)
```

Explore more about NSequence and its capabilities in the [documentation](https://github.com/yourusername/NSequence).

Feel free to contribute, report issues, or suggest enhancements. Happy sequencing! 📈
