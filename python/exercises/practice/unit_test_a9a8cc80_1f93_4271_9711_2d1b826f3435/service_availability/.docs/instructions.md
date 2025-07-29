## Question: Optimizing Inter-Service Communication in a Microservices Architecture

### Problem Description

You are designing a critical component for a large-scale e-commerce platform built using a microservices architecture. This component is responsible for handling product availability checks across multiple independent services. When a user attempts to add an item to their cart, this component needs to query the inventory service, the pricing service, and the promotions service to determine if the item is in stock, its current price, and if any promotions apply.

The system is under heavy load, especially during peak hours.  The goal is to minimize the overall latency of the availability check, ensuring a smooth user experience while maintaining data consistency.

**Constraints and Requirements:**

1.  **Service Dependencies:** The component relies on three distinct microservices:
    *   `InventoryService.checkAvailability(productID)`: Returns a boolean indicating if the product is in stock.
    *   `PricingService.getPrice(productID)`: Returns the current price of the product.
    *   `PromotionService.getPromotions(productID)`: Returns a list of applicable promotions for the product.

2.  **Latency Sensitivity:** The overall latency for checking availability *must* be minimized.  Exceeding a 200ms threshold will result in a degraded user experience.

3.  **Concurrency:** The system handles thousands of concurrent requests.  Your solution must be thread-safe and highly concurrent.  Avoid blocking operations where possible.

4.  **Data Consistency:** While eventual consistency is acceptable, the system must avoid displaying stale data that significantly deviates from the actual state.  For example, showing a product as available when it is actually out of stock is unacceptable.

5.  **Service Unavailability:** The services are prone to occasional failures or temporary unavailability. Your component must be resilient and handle such scenarios gracefully without crashing or significantly impacting performance. A failed service call should not immediately fail the entire request; instead, implement a retry mechanism with exponential backoff.

6.  **Optimization Focus:** Prioritize minimizing the *critical path* - the longest sequence of dependent operations.

7.  **Scalability:** The solution should be designed to easily scale as the number of products and users increases.  Consider the impact of your design on system resources like CPU, memory, and network bandwidth.

8.  **Resource Constraints:** The component is deployed on a resource-constrained environment (e.g., limited memory and CPU). Memory leaks and excessive CPU usage are strictly prohibited.

9. **Caching:** Implement an efficient caching strategy to reduce the load on backend services.  The cache should be designed to minimize cache invalidation issues and data staleness. The cache TTL should be configurable and adaptable.

10. **Circuit Breaker Pattern:** Implement a circuit breaker pattern for each service dependency to prevent cascading failures. The circuit breaker should automatically open when a service becomes unhealthy and close when the service recovers.

**Task:**

Implement a function `check_product_availability(product_id)` that takes a `product_id` as input and returns a tuple containing:

*   A boolean indicating if the product is available (considering inventory, price, and promotions). Availability requires being in stock.
*   The final price of the product after applying all applicable promotions.
*   A list of promotion names applied to the product.

Your implementation must adhere to all the constraints and requirements outlined above. You are free to use any Python libraries necessary, but justify your choices in terms of performance, reliability, and maintainability.  Consider the trade-offs between different approaches and document your design decisions.  Pay close attention to algorithmic efficiency, concurrency, fault tolerance, and resource utilization. Provide your design choices in docstrings.
