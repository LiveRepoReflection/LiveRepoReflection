## Project Name

`DistributedMedianTracker`

## Question Description

You are tasked with designing and implementing a distributed system for tracking the median of a continuous stream of numerical data arriving from multiple sources in real-time. The system must be scalable, fault-tolerant, and provide accurate median estimates with minimal latency.

Specifically, imagine a network of sensors continuously reporting temperature readings. Your system needs to maintain a running estimate of the median temperature across all sensors.

**Input:**

The system receives a stream of numerical data points from `N` different sources (sensors). Each source sends data points asynchronously. The system does not know the number of sources (`N`) in advance and must handle sources dynamically joining and leaving the system.

**Requirements:**

1.  **Real-time Median Tracking:** The system must continuously update its estimate of the median as new data points arrive.
2.  **Scalability:** The system should be able to handle a large number of data sources and a high data ingestion rate.
3.  **Fault Tolerance:** The system should be resilient to failures of individual data sources or processing nodes.
4.  **Accuracy:**  The system should provide an accurate estimate of the median.  Define a configurable tolerance level `T` (e.g., 0.01 or 1%). The estimated median must be within `T` of the true median of the data seen so far.
5.  **Latency:** Minimize the latency between data arrival and the availability of an updated median estimate. Define a maximum acceptable latency `L` (e.g., 100ms). The estimated median must be available within `L` milliseconds of the arrival of a new data point.
6.  **Dynamic Source Management:** The system must be able to handle data sources dynamically joining and leaving the system without requiring a full system restart or significant performance degradation.
7.  **Resource Efficiency:** Minimize the memory and CPU usage of the system.  Discuss the trade-offs between resource consumption, accuracy, and latency.

**Constraints:**

*   You are free to choose the data structures and algorithms used, but justify your choices in terms of scalability, accuracy, and latency.
*   Assume that data points are real numbers.
*   You are not allowed to store all the data points.  The system must maintain a summary of the data that requires significantly less storage than the entire dataset.
*   Consider the impact of network latency and communication overhead between distributed components.
*   While implementing the core median tracking logic is crucial, you also need to address the distributed system design aspects, including data distribution, aggregation, and fault tolerance.

**Output:**

The system should provide an API (a Javascript function) to retrieve the current estimated median.

**Evaluation Criteria:**

The solution will be evaluated based on:

*   **Correctness:** The accuracy of the median estimate.
*   **Performance:** The latency of updates and the system's throughput.
*   **Scalability:** The ability to handle a large number of data sources and a high data ingestion rate.
*   **Fault Tolerance:** The ability to handle failures of data sources or processing nodes.
*   **Code Quality:** The clarity, maintainability, and testability of the code.
*   **Design Justification:** A clear explanation of the design choices made and the trade-offs considered.  Specifically, address the choice of data structures, algorithms, and distributed system architecture.  Explain how the design meets the requirements for scalability, accuracy, fault tolerance, and latency.

This problem requires a deep understanding of data structures, algorithms, and distributed systems concepts. A successful solution will demonstrate the ability to design and implement a robust and efficient system for real-time median tracking. The challenge lies in balancing accuracy, latency, scalability, fault tolerance, and resource efficiency in a distributed environment.
