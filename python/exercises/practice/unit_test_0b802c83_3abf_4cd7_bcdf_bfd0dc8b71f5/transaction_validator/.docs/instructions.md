## Question: Distributed Transaction Validator

### Question Description

You are building a distributed transaction system. A transaction consists of a series of operations performed across multiple independent services. To ensure data consistency, all operations within a transaction must either succeed completely (commit) or fail completely (rollback).

Your task is to implement a transaction validator that can determine whether a proposed transaction, represented by a log of operations, is valid given the known state of the services involved.

**Input:**

The input consists of two parts:

1.  **Service State:** A dictionary representing the initial state of each service. The keys are service IDs (strings), and the values are dictionaries representing the state of that service. The state dictionary contains key-value pairs where keys are data identifiers within the service (strings) and values are their current values (integers).

    ```python
    service_state = {
        "service_A": {"item1": 10, "item2": 20},
        "service_B": {"item3": 30, "item4": 40},
    }
    ```

2.  **Transaction Log:** A list of operations representing the proposed transaction. Each operation is a dictionary with the following keys:

    *   `service_id`: The ID of the service the operation targets (string).
    *   `operation_type`: The type of operation: `"update"`, `"delete"`, or `"create"` (string).
    *   `data_id`: The identifier of the data being operated on within the service (string).
    *   `new_value`: (Only for "update" and "create" operations) The new value to be set (integer).
    *   `expected_value`: (Only for "update" and "delete" operations) The expected current value of the data (integer).

    ```python
    transaction_log = [
        {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
        {"service_id": "service_B", "operation_type": "delete", "data_id": "item3", "expected_value": 30},
        {"service_id": "service_C", "operation_type": "create", "data_id": "item5", "new_value": 50}
    ]
    ```

**Output:**

Return `True` if the transaction is valid, meaning all operations can be successfully applied in the order they appear in the log based on the initial `service_state`. Return `False` if any operation fails due to a conflict in the service state.

**Constraints:**

*   The transaction must be atomic. If any operation fails, the entire transaction is considered invalid.
*   Operations must be validated in the order they appear in the `transaction_log`.
*   The `service_state` represents the *initial* state. Operations, if valid, should be applied *sequentially* to this state as you validate.
*   If a service doesn't exist in the initial `service_state`, it should be created when a "create" operation targets it.
*   "Update" operations should fail if the `data_id` does not exist or the `expected_value` does not match the current value.
*   "Delete" operations should fail if the `data_id` does not exist or the `expected_value` does not match the current value.
*   "Create" operations should fail if the `data_id` already exists in the targeted service.
*   The services can be scaled to a large number. Optimize your implementation to handle a large number of services and operations efficiently.

**Example:**

```python
service_state = {
    "service_A": {"item1": 10, "item2": 20},
    "service_B": {"item3": 30, "item4": 40},
}

transaction_log = [
    {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 10},
    {"service_id": "service_B", "operation_type": "delete", "data_id": "item3", "expected_value": 30},
    {"service_id": "service_C", "operation_type": "create", "data_id": "item5", "new_value": 50}
]

# Expected Output: True

service_state = {
    "service_A": {"item1": 10, "item2": 20}
}

transaction_log = [
    {"service_id": "service_A", "operation_type": "update", "data_id": "item1", "new_value": 15, "expected_value": 12} # Invalid expected value
]

# Expected Output: False
```
