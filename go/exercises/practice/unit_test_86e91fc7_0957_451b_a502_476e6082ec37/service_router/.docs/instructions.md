Okay, I'm ready. Here's a challenging Go coding problem designed to test a range of skills.

## Project Name

`HighlyAvailableServiceMesh`

## Question Description

You are tasked with designing and implementing a core component of a highly available service mesh: a dynamic service discovery and routing system. This system needs to handle a large number of services, frequent updates to service availability, and complex routing rules based on service health and request metadata.

**Specifically:**

Imagine a cluster of microservices. Each service instance periodically sends heartbeat signals to the service discovery component to indicate its availability. These heartbeats include metadata like the service name, instance ID, health status (e.g., "healthy", "unhealthy", "degraded"), and potentially custom key-value pairs representing attributes like version, region, or environment.

The routing system must then direct incoming requests to the appropriate service instances based on configurable rules. These rules can consider:

*   **Service Name:** The target service for the request.
*   **Health Status:** Prioritize healthy instances, potentially falling back to degraded instances if no healthy ones are available.  Unhealthy instances should be avoided if possible.
*   **Metadata Matching:** Route requests to instances matching specific metadata criteria (e.g., "version=v2", "region=us-east-1").
*   **Load Balancing:** Distribute requests across available instances of a service using a weighted round-robin approach. The weights should be dynamically adjustable based on instance health and performance metrics (assume these are provided via the heartbeat).

**Your Task:**

Implement a Go package that provides the following functionality:

1.  **Service Registry:**
    *   A data structure to store service instance information (service name, instance ID, health status, metadata, weight).
    *   Methods to:
        *   Register or update service instances (based on heartbeat signals).
        *   Remove service instances.
        *   Retrieve all instances of a given service.
        *   Efficiently query service instances based on service name, health status, and metadata.

2.  **Routing Engine:**
    *   A function that takes a service name and a set of request metadata (key-value pairs) as input.
    *   The function should:
        *   Query the service registry for available instances of the requested service.
        *   Filter the instances based on health status (prioritizing healthy instances, then degraded if no healthy instances exist). Unhealthy instances should only be considered if absolutely no other instances are available.
        *   Further filter the instances based on request metadata, matching instances whose metadata contains all the key-value pairs specified in the request. If no metadata is provided, no filtering is done.
        *   Select an instance for routing based on weighted round-robin load balancing. Weights are assigned to instances.
        *   Return the selected instance ID. If no suitable instance is found, return an appropriate error.

**Constraints and Requirements:**

*   **Concurrency:** The service registry must be thread-safe to handle concurrent updates from multiple sources.
*   **Efficiency:**  The registry should be optimized for read operations (routing requests) as these are expected to be much more frequent than write operations (heartbeats).  Consider the time complexity of your data structure lookups. Minimize locking overhead.
*   **Scalability:**  The design should be scalable to handle a large number of services (tens of thousands) and instances per service (hundreds).
*   **Error Handling:**  Provide clear and informative error messages for cases such as service not found, no healthy instances available, or metadata mismatch.
*   **Weighted Round Robin:** Implement weighted round-robin load balancing correctly, ensuring that instances with higher weights receive proportionally more requests. The weights should be taken into consideration when selecting a suitable server.
*   **Health Status Prioritization:** The system must *always* prioritize healthy instances. Degraded instances are only considered if no healthy instances are available. Unhealthy instances are a last resort.
*   **Metadata Matching:** If metadata matching is required, the system should only return instances that contain *all* of the requested metadata key-value pairs.

This problem emphasizes efficient data structures, concurrent programming, algorithm design, and practical system considerations. Good luck!
