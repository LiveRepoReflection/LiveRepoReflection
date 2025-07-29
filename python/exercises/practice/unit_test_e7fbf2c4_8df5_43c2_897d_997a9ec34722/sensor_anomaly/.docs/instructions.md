Okay, here's a challenging problem description, designed to be at a LeetCode Hard level.

## Problem: Real-Time Anomaly Detection in a Distributed System

**Description:**

You are tasked with designing and implementing a real-time anomaly detection system for a distributed network of sensors. These sensors continuously generate time-series data (numerical values with timestamps) representing various environmental parameters (e.g., temperature, pressure, humidity). The data is streamed to a central processing unit (CPU).

Your goal is to identify anomalies in the sensor data as quickly and accurately as possible. An anomaly is defined as a data point that deviates significantly from the expected behavior based on historical data and the current context.

**Input:**

*   **Stream of Sensor Data:**  A continuous stream of sensor readings. Each reading is a tuple: `(sensor_id, timestamp, value)`, where:
    *   `sensor_id` is a unique identifier for the sensor (string).
    *   `timestamp` is the time of the reading (Unix timestamp in seconds, integer).
    *   `value` is the sensor reading (floating-point number).
*   **Historical Data:** A limited window of past sensor readings for each sensor is available. This window is used to train a model of "normal" behavior. You can assume this data is pre-loaded into your system. The window size can be configured for each sensor.
*   **System Capacity:** The system must handle a large number of sensors (potentially thousands), each generating readings at varying rates. The rate can vary from 1 reading/minute to 100 readings/second for each sensor.

**Output:**

*   **Anomaly Alerts:**  Whenever an anomaly is detected, your system should generate an alert containing the following information: `(sensor_id, timestamp, value, anomaly_score)`.
    *   `sensor_id`, `timestamp`, and `value` are the same as in the input.
    *   `anomaly_score` is a numerical score representing the degree of anomaly (higher score means more anomalous). The anomaly score should be a non-negative float.

**Constraints and Requirements:**

1.  **Real-Time Processing:** The system must process the sensor data with minimal latency. The maximum acceptable delay between receiving a sensor reading and generating an anomaly alert (if applicable) should be less than 100 milliseconds on average.

2.  **Scalability:** The system should be able to scale to handle a large number of sensors and high data throughput.

3.  **Accuracy:** The anomaly detection algorithm should have a high precision and recall. False positives and false negatives should be minimized.

4.  **Resource Constraints:** The system has limited memory and CPU resources. The memory footprint should be minimized, and the CPU usage should be kept within reasonable limits.

5.  **Dynamic Adaptation:** The system should be able to adapt to changes in the sensor data distribution over time. For example, the system should be able to detect seasonal patterns or gradual drifts in the sensor readings.

6.  **Configuration:** The system should be configurable, allowing users to adjust parameters such as the window size for historical data, the anomaly detection threshold, and the anomaly scoring function.

7. **Cold Start:** Consider the "cold start" problem. How does your system perform anomaly detection when there is very little or no historical data available for a sensor? How do you bootstrap the anomaly detection process?

8. **Handling Missing Data**: Sensors may intermittently fail or drop readings. The solution must be robust against missing data and avoid generating spurious alerts.

**Considerations:**

*   You need to choose an appropriate anomaly detection algorithm.  Consider algorithms like: Exponential Smoothing, ARIMA, Kalman Filters, One-Class SVM, Isolation Forests, or Autoencoders.  You are free to research and implement any suitable algorithm.
*   Think about how to efficiently store and access historical data.
*   Consider using appropriate data structures to optimize performance.
*   Consider how to handle different sensor types with different data characteristics.
*   Think about how to parallelize the anomaly detection process to improve throughput.
*   Think about how to evaluate the performance of your system (e.g., using metrics like precision, recall, F1-score, and latency).
*   Think about how to handle the trade-off between anomaly detection accuracy and processing speed.

This problem requires a strong understanding of data structures, algorithms, system design, and real-time processing. Good luck!
