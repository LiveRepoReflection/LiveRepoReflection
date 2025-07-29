## Problem: Efficient Median Calculation in a Dynamic Data Stream

### Question Description

You are building a real-time data analysis system that needs to track the median of a continuously flowing stream of numerical data. Due to resource constraints, you need to maintain this median calculation as efficiently as possible, both in terms of time and space complexity.

Specifically, you are given a stream of integers arriving sequentially. After each new integer arrives, your system must be able to report the current median of all integers seen so far.

**Requirements:**

1.  Implement a data structure and associated methods to efficiently:
    *   `add_number(num)`: Add a new integer `num` to the data stream.
    *   `get_median()`: Return the current median of all integers in the data stream. If the number of integers seen so far is even, return the average of the two middle values.

2.  **Efficiency Constraints:**
    *   **Time Complexity:** The `add_number(num)` and `get_median()` operations should strive for an average time complexity of O(log n), where n is the number of integers seen so far.  Solutions with O(n) complexity for either operation will be penalized severely.
    *   **Space Complexity:** Your data structure should use no more than O(n) space.  However, strive to minimize the constant factor in the space usage.

3.  **Handling Duplicates:**  The data stream may contain duplicate numbers. Your solution must handle duplicates correctly.

4.  **Real-world Data Simulation:** Simulate a realistic data stream with potentially large numbers and a non-uniform distribution. Consider edge cases like a stream that is initially sorted, reverse sorted, or contains many repeated values.

5. **Scalability:**  Consider how your solution would scale to handle extremely large data streams (e.g., billions of numbers) that might exceed available memory. *While you don't need to implement a disk-based solution, discuss the potential design changes needed for such a scenario in your comments*.

**Input:**

A stream of integers provided one at a time.

**Output:**

For each integer added to the stream, output the current median after the integer has been added.  The output should have the same number of lines as the input.

**Example:**

**Input Stream:**
```
1
2
3
```

**Output:**

```
1.0
1.5
2.0
```

**Constraints:**

*   Each input number will be within the range of a 64-bit integer.
*   The length of the data stream is not predefined and can be very large.

**Judging Criteria:**

Your solution will be judged based on:

*   **Correctness:** Does it consistently produce the correct median?
*   **Efficiency:** Does it meet the time and space complexity requirements?
*   **Code Clarity:** Is the code well-structured, readable, and commented?
*   **Handling Edge Cases:** Does it handle duplicate numbers, sorted streams, and other edge cases gracefully?
*   **Scalability Discussion:** Does the code contain a meaningful discussion of how to scale the solution to handle very large datasets that exceed available memory? (This discussion should be in the form of code comments).
