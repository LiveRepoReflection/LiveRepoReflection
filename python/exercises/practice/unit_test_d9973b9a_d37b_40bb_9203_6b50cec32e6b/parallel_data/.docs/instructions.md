## Project Name

`ParallelDataProcessing`

## Question Description

You are given a massive dataset represented as a list of dictionaries. Each dictionary represents a record and contains several key-value pairs. The dataset is too large to fit into memory all at once.

Your task is to implement a parallel data processing pipeline that performs a series of transformations on this dataset and efficiently computes a specific aggregate statistic.

**Specifics:**

1.  **Data Source:** You will receive an iterable (e.g., a generator) that yields dictionaries.  Treat this as a stream of data.  You *cannot* load the entire dataset into a list or other in-memory data structure at any point.  The dataset is potentially infinite.

2.  **Transformations:** You need to apply the following transformations to each record *in order*:

    *   **Filtering:**  Keep only records where the value associated with the key `"status"` is equal to `"active"`.
    *   **Mapping:** For each remaining record, compute a new field `"processed_value"` as the square root of the absolute value of the field `"value"` if `"value"` is present and numerical, otherwise `0.0`. If the `"value"` field is not present, treat it as if it were `0`.
    *   **Deduplication:** Remove duplicate records based on the values of the `"user_id"` and `"processed_value"` fields. Only the first occurrence of a unique (user\_id, processed\_value) pair should be kept.

3.  **Aggregation:** After applying the transformations, calculate the average `"processed_value"` across all remaining records.

4.  **Parallelism:** The filtering, mapping, and aggregation steps should be performed in parallel using multiple processes. The number of processes to use should be configurable.

5.  **Resource Management:**  Minimize memory usage throughout the pipeline.  Intermediate results should be streamed between processes whenever possible to avoid loading large amounts of data into memory.  Avoid unnecessary data copying.

6.  **Error Handling:**  The input data might contain invalid or unexpected values. Your solution should handle these errors gracefully without crashing. For example, non-numerical values for `"value"` should be handled as specified in the mapping stage.

7.  **Efficiency:** Optimize your solution for both speed and memory usage.  Consider using appropriate data structures and algorithms to minimize processing time.

**Input:**

*   `data_source`: An iterable (e.g., a generator) that yields dictionaries representing data records.
*   `num_processes`: An integer representing the number of processes to use for parallel processing.  Must be a positive integer.

**Output:**

*   A float representing the average `"processed_value"` across all remaining records after applying the transformations and deduplication.  Return `0.0` if no records remain after processing.

**Constraints:**

*   The dataset is too large to fit in memory.
*   The `data_source` may yield an infinite stream of data. Your solution must terminate.
*   `num_processes` must be a positive integer.
*   You are not allowed to use external libraries beyond the Python standard library (`math`, `multiprocessing`).
*   Maintain the order of data from the data source throughout the processing pipeline.
*   Aim for optimal CPU utilization across all processes.

**Example Data (Illustrative - the input could be much larger):**

```python
data = [
    {"user_id": 1, "value": "4", "status": "active"},
    {"user_id": 2, "value": "9", "status": "inactive"},
    {"user_id": 1, "value": 4, "status": "active"}, # Duplicate after mapping
    {"user_id": 3, "value": "16", "status": "active"},
    {"user_id": 4, "value": None, "status": "active"},
    {"user_id": 5, "value": "abc", "status": "active"},
    {"user_id": 3, "value": "25", "status": "active"},#Duplicate after mapping
]

# Expected Output (with num_processes=1 for simplicity):
# Filtered: [{"user_id": 1, "value": "4", "status": "active"}, {"user_id": 1, "value": 4, "status": "active"}, {"user_id": 3, "value": "16", "status": "active"}, {"user_id": 4, "value": None, "status": "active"}, {"user_id": 5, "value": "abc", "status": "active"}, {"user_id": 3, "value": "25", "status": "active"}]
# Mapped: [{"user_id": 1, "processed_value": 2.0, "status": "active"}, {"user_id": 1, "processed_value": 2.0, "status": "active"}, {"user_id": 3, "processed_value": 4.0, "status": "active"}, {"user_id": 4, "processed_value": 0.0, "status": "active"}, {"user_id": 5, "processed_value": 0.0, "status": "active"}, {"user_id": 3, "processed_value": 5.0, "status": "active"}]
# Deduplicated: [{"user_id": 1, "processed_value": 2.0, "status": "active"}, {"user_id": 3, "processed_value": 4.0, "status": "active"}, {"user_id": 4, "processed_value": 0.0, "status": "active"}, {"user_id": 5, "processed_value": 0.0, "status": "active"}, {"user_id": 3, "processed_value": 5.0, "status": "active"}]
# Average: (2.0 + 4.0 + 0.0 + 0.0 + 5.0) / 5 = 2.2
# 2.2
```

This problem requires a strong understanding of multiprocessing, data streaming, and efficient algorithm design.  Good luck!
