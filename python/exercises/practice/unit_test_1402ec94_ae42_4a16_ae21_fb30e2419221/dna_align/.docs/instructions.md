## The DNA Alignment Problem

**Problem Description:**

In the rapidly evolving field of bioinformatics, accurate and efficient DNA sequence alignment is crucial for tasks like identifying genetic diseases, understanding evolutionary relationships, and developing personalized medicine. You are tasked with developing a highly optimized DNA alignment algorithm.

Given two DNA sequences, `sequence1` and `sequence2`, consisting of the characters 'A', 'C', 'G', and 'T', your goal is to find the optimal alignment between them. Alignment is achieved by introducing gaps ('-') into the sequences to maximize a scoring function.

The scoring function is defined as follows:

*   **Match:**  +2 points for each position where the characters in the aligned sequences are identical (excluding gaps).
*   **Mismatch:** -1 point for each position where the characters in the aligned sequences are different (excluding gaps).
*   **Gap Penalty:** -2 points for each gap introduced in either sequence.

Your task is to write a function that takes `sequence1` and `sequence2` as input and returns the *maximum possible alignment score* between them.
The sequences can have lengths up to 5000.

**Constraints and Considerations:**

1.  **Memory Usage:**  Due to the potential length of the sequences, memory usage should be carefully managed. Storing the entire alignment matrix in memory might lead to `MemoryError` for larger inputs. Aim for a space-efficient solution.
2.  **Time Complexity:**  A naive implementation might result in a time complexity that is too high for the given sequence lengths.  Optimize your algorithm to achieve the best possible time complexity. Solutions with O(n\*m) time complexity are expected, where n and m are the lengths of the sequences.
3.  **Edge Cases:**  Handle edge cases gracefully, such as empty sequences or sequences with only one character.
4.  **Large Inputs:** The algorithm should be able to produce an answer within reasonable time for sequences with lengths close to the maximum allowed length.
5.  **Correctness:** The returned score MUST be the optimal score. Suboptimal solutions might pass some test cases, but will fail on others.

**Input:**

*   `sequence1` (string): The first DNA sequence.
*   `sequence2` (string): The second DNA sequence.

**Output:**

*   (int): The maximum possible alignment score between the two sequences.
