## Problem: Scalable Real-Time Analytics Dashboard

**Description:**

You are tasked with designing and implementing a scalable real-time analytics dashboard for a large e-commerce platform. This platform tracks user interactions (clicks, views, purchases) across millions of products. The goal is to provide near real-time insights into the performance of different product categories.

**Specific Requirements:**

1.  **Data Ingestion:** The system receives a continuous stream of user interaction events. Each event is a JSON object with the following structure:

    ```json
    {
      "timestamp": <long>, // Unix timestamp in milliseconds
      "user_id": <string>,
      "product_id": <string>,
      "category_id": <string>,
      "event_type": <string> // "click", "view", "purchase"
    }
    ```

    The event stream is high-volume (millions of events per minute) and can be noisy (duplicate events, invalid data).

2.  **Real-Time Aggregation:** The system must continuously aggregate event counts for each product category. The aggregation window is a sliding window of the last 5 minutes (300 seconds).  For each category, you need to track the following metrics within the sliding window:
    *   Total clicks
    *   Total views
    *   Total purchases

3.  **Data Storage:** The aggregated metrics must be stored in a way that allows for efficient retrieval for dashboard visualization.

4.  **Dashboard Querying:** The dashboard needs to support the following queries:

    *   Retrieve the current aggregated metrics (clicks, views, purchases) for a single category.
    *   Retrieve the historical aggregated metrics for a single category within a specified time range (e.g., last hour, last day).
    *   Retrieve the top K categories with the highest purchase counts in the last 5 minutes.

5.  **Scalability and Fault Tolerance:** The system must be able to handle increasing data volumes and user load. It should be designed to be fault-tolerant, ensuring minimal data loss in case of failures.

6.  **Optimization:** Minimize latency for both aggregation and querying. The dashboard should display data with minimal delay (ideally within a few seconds of event arrival). Optimize memory usage and CPU consumption.

**Constraints:**

*   You are free to use any appropriate Python libraries or external tools (e.g., databases, message queues, caching systems). Specify your dependencies.
*   Data loss is unacceptable. Even if the aggregation window is 5 minutes, every event must be correctly processed and counted towards the appropriate category within that time frame.
*   Assume the number of distinct categories is large (hundreds of thousands or millions).
*   The system must be able to handle out-of-order events (events arriving with timestamps slightly older than the current window).
*   Consider using a message queue and multiple workers to process the incoming event stream.
*   Consider using an in-memory data store for fast aggregation, with periodic persistence to a durable storage layer.
*   The system should be designed to be easily deployed and scaled on a cloud infrastructure (e.g., AWS, Google Cloud, Azure).

**Deliverables:**

*   Python code implementing the data ingestion, real-time aggregation, and data storage components.
*   A clear description of the chosen data structures and algorithms, with justifications for their suitability.
*   A high-level system architecture diagram illustrating the components and their interactions.
*   A discussion of the scalability and fault tolerance aspects of your design.
*   Instructions on how to deploy and run the system.
*   A brief analysis of the time and space complexity of your solution.
*   Example code demonstrating how to query the system for the different dashboard requirements.
*   Consider the trade-offs between accuracy, latency, and resource consumption when designing the system.

This question challenges the solver to design a system that can handle a high volume of data in real-time, while also providing accurate and up-to-date information for a dashboard. It requires knowledge of data structures, algorithms, system design, and cloud computing concepts. The constraints and requirements make the problem difficult and require careful consideration of performance and scalability.
