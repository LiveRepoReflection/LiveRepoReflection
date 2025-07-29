## Question: Data Stream Median with Limited Memory

**Description:**

You are building a real-time analytics system that needs to track the median of a continuously flowing stream of numerical data. However, due to resource constraints in your embedded environment, you have a strict limit on the amount of memory you can use. Your task is to implement a data structure that efficiently maintains an approximate median of the data stream while adhering to the memory limitations.

Specifically, you need to implement a `LimitedMemoryMedian` struct with the following functionalities:

1.  **`NewLimitedMemoryMedian(capacity int, epsilon float64) *LimitedMemoryMedian`**: Constructor that initializes the data structure with a maximum `capacity` (number of data points to store) and an `epsilon` value. The `epsilon` value represents the allowed relative error for the median approximation.

2.  **`Add(value float64)`**:  Adds a new data point to the stream. The data structure should update its internal state to reflect the inclusion of this new value.

3.  **`Median() float64`**:  Returns an *approximate* median of the data stream seen so far. The returned value should be within a relative error of `epsilon` from the true median.  That is if `M` is the returned median value and `T` is the true median value calculated from all added values, then `|M - T| <= epsilon * T`.

**Constraints:**

*   **Memory Limit:**  The data structure must use no more than `capacity` number of floats in memory.
*   **Real-time Performance:**  `Add` and `Median` operations should be reasonably efficient. Excessive computational complexity will lead to timeouts.
*   **Epsilon Accuracy:** The approximate median returned by `Median()` should satisfy the relative error constraint with respect to the true median of the *entire* data seen so far.
*   **Positive Data:** The input data stream will consist of only positive floating-point numbers. `value > 0`.
*   **Non-Empty Stream:** The `Median()` function will only be called after at least one number has been added to the stream.
*   **Capacity Significance:** Capacity will always be larger than 1.
*   **Epsilon Significance:** 0 < Epsilon < 1
*   **Consider edge case**: Consider the situation where all the data comes in is very similar, for example, from 10000 to 10001.

**Challenge:**

The main challenge lies in maintaining a good balance between accuracy and memory usage. You can't simply store all the data points because of the memory limit. Explore techniques like:

*   **Reservoir Sampling:**  Keep a random subset of the data.
*   **Histograms:**  Maintain a histogram of the data distribution.
*   **Quantiles:** Track specific quantiles of the data.
*   **Data Compression:**  Employ compression techniques to store more information within the memory limit.

Consider the trade-offs between the complexity of these techniques and their impact on the accuracy of the median approximation. Choose the best approach for the given constraints.

**Note:** Your solution will be judged on its correctness, efficiency, and adherence to the memory limitations.
