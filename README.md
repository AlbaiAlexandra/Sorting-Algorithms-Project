# Sorting Algorithms Experiment

This project explores and compares the performance of multiple sorting algorithms under different conditions.
The goal is to understand how algorithm efficiency changes depending on:
* input size
* data type
* data distribution
The experiment measures execution time and evaluates how well each algorithm scales as datasets grow.

##  Algorithms Implemented

The following sorting algorithms were tested:

###  Basic (Quadratic Time Complexity)

* Bubble Sort
* Insertion Sort
* Selection Sort

These algorithms are simple but inefficient for large datasets.

###  Intermediate

* Shell Sort

An improved version of insertion sort that performs better on medium-sized data.

###  Efficient (O(n log n))

* Merge Sort
* Quick Sort
* Heap Sort
* Timsort (Python built-in `sorted()`)

These algorithms are suitable for large datasets and real-world applications.

###  Specialized (Non-comparison)

* Counting Sort (integers only)
* Radix Sort (non-negative integers only)

These can be very fast under specific conditions.

##  Experiment Design

### Input Sizes
The program reads dataset sizes from a text file (e.g. `sizes.txt`) and generates lists of those sizes.

### Data Types

* Integers
* Floats
* Strings
### Data Distributions

Each dataset is generated in different forms:

* **Random** – unordered values
* **Sorted** – already ordered
* **Reversed** – descending order
* **Nearly Sorted** – mostly ordered with small changes
* **Half Sorted** – partially random
* **Flat** – many repeated values

### Benchmarking Process
For each combination of:

* size
* data type
* data distribution
* algorithm

the program:

1. generates a dataset
2. runs the sorting algorithm
3. measures execution time
4. repeats the test multiple times
5. records average and best times
6. verifies correctness of the result

All results are saved to a CSV file.

## Results
The results are stored in a CSV file with the following columns:

* `size` – dataset size
* `case` – data distribution
* `dtype` – data type
* `algorithm` – sorting algorithm used
* `repeats` – number of runs
* `avg_seconds` – average execution time
* `best_seconds` – fastest run
* `status` – correctness (e.g. `ok`, `skipped`, `unsupported`)

##  Key Findings
* Simple algorithms (bubble, insertion, selection) are efficient only for small datasets.
* Their performance degrades rapidly as input size increases.
* Efficient algorithms (merge, quick, heap, timsort) scale much better.
* Input structure (sorted vs random vs reversed) significantly affects performance.
* Python’s built-in Timsort performs very well across most cases.

## Conclusion
This experiment demonstrates that algorithm choice is critical when working with large datasets.
While simple algorithms are useful for learning and small inputs, more advanced algorithms are necessary for efficient real-world applications.
