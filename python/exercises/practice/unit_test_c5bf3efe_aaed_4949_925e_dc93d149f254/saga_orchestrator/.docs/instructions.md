## Question: Distributed Transaction Orchestrator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction orchestrator. This orchestrator manages transactions that span multiple independent services. Due to network latency and potential service failures, maintaining atomicity, consistency, isolation, and durability (ACID) in a distributed environment is challenging.

Your orchestrator will manage transactions using the Saga pattern with compensation.  A Saga is a sequence of local transactions. Each local transaction updates data within a single service. If one transaction in the Saga fails, the orchestrator executes a series of *compensating transactions* that undo the changes made by the preceding transactions.

**System Architecture:**

You are given a list of services, each responsible for a specific domain. Each service exposes two endpoints:

*   `commit(transaction_id, data)`:  Attempts to perform a local transaction.  It returns `True` on success, `False` on failure.  The `data` payload is specific to each service and will contain all information needed to perform the local transaction.
*   `compensate(transaction_id, data)`: Attempts to undo the changes made by a previous `commit` operation.  It returns `True` on success, `False` on failure. The `data` payload here will be the same as the `data` used for the commit operation.

**Orchestrator Requirements:**

Your task is to implement the `execute_saga` function that takes a list of `TransactionStep` objects representing the saga and attempts to execute the saga.

A `TransactionStep` has the following attributes:

*   `service_name`: The name of the service to interact with.
*   `commit_endpoint`: The URL endpoint for the `commit` operation of the service (string).
*   `compensate_endpoint`: The URL endpoint for the `compensate` operation of the service (string).
*   `data`: A dictionary containing the data required for the `commit` and `compensate` operations.

**`execute_saga` Function Details:**

The `execute_saga` function should:

1.  Iterate through the list of `TransactionStep` objects.
2.  For each step, call the `commit_endpoint` with the provided `transaction_id` and `data`. You can assume a simple HTTP POST request with JSON data.  If the request fails (e.g., connection error, timeout) or the service returns `False`, the saga has failed and needs to be compensated.
3.  If any `commit` operation fails, the orchestrator must execute the compensating transactions in *reverse order* for all successfully committed steps.
4.  For each compensating transaction, call the `compensate_endpoint` with the `transaction_id` and `data` that was originally used for the `commit` operation. If the request fails or the service returns `False`, log the error but continue compensating the remaining transactions.  Compensation failures should *not* halt the compensation process.
5.  The `execute_saga` function must return `True` if the entire saga (all commits) completes successfully. If any commit fails and the compensation process completes (even with compensation failures), the function must return `False`.

**Constraints:**

*   **Concurrency:** The services are independent and the orchestrator can execute multiple sagas concurrently. However, within a single saga, transactions must be executed serially (one after another).
*   **Idempotency:**  Assume the `commit` and `compensate` operations are *not* inherently idempotent. Your orchestrator *cannot* retry failed `commit` or `compensate` operations during the initial execution or during compensation. The external services will handle idempotency if required.
*   **Network Reliability:** Network connections are unreliable.  Requests to services can fail due to timeouts, connection errors, etc. You need to handle these failures gracefully.
*   **Service Failures:** Services can be temporarily unavailable.
*   **Logging:** Implement basic logging to track the progress of the saga and any errors encountered.
*   **Optimization:** Minimize the time spent waiting for responses from services. While serial execution within a saga is required, consider how you might improve the overall efficiency of the orchestrator when handling multiple concurrent sagas (though this isn't the primary focus, it's a bonus).
*   **Error Handling:** Implement robust error handling to catch exceptions and log them appropriately. Ensure that failures during compensation do not prevent the remaining compensation steps from being executed.
*   **Scalability:**  While you don't need to implement a fully distributed system, consider how your design could be scaled to handle a large number of concurrent sagas and services. (This is a design consideration, not an implementation requirement.)

**Input:**

*   `saga`: A list of `TransactionStep` objects.
*   `transaction_id`: A unique identifier for the saga (string).

**Output:**

*   `True` if the entire saga completes successfully.
*   `False` if any commit fails and the compensation process completes (even with compensation failures).

**Example `TransactionStep`:**

```python
class TransactionStep:
    def __init__(self, service_name, commit_endpoint, compensate_endpoint, data):
        self.service_name = service_name
        self.commit_endpoint = commit_endpoint
        self.compensate_endpoint = compensate_endpoint
        self.data = data
```

**Your task is to implement the `execute_saga` function in Python, adhering to the above requirements and constraints.**
