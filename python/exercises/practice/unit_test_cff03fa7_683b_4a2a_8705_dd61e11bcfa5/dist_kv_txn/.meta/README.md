# Distributed Transactional Key-Value Store

This project implements a simplified distributed key-value store with transactional capabilities, including ACID properties (Atomicity, Consistency, Isolation, Durability). The system supports distributed consensus through a simplified two-phase commit protocol and provides snapshot isolation for transactions.

## Architecture

The system consists of:

1. **Node Management**: Each node in the distributed system maintains its own key-value store and transaction state.
2. **Transaction Management**: Transactions are isolated using snapshot isolation, with each transaction seeing a consistent snapshot of the data.
3. **Consensus Protocol**: A simplified two-phase commit protocol ensures all nodes agree on transaction outcomes.
4. **Durability Mechanism**: Transaction logs are maintained for recovery after node failures.
5. **Conflict Detection**: The system detects and resolves conflicts between concurrent transactions.

## Implementation Details

### Key Components:

- **Snapshot Isolation**: Each transaction operates on a snapshot of the data, preventing transactions from seeing each other's uncommitted changes. 
- **Consensus Algorithm**: A simplified two-phase commit protocol ensures that transactions are either committed on all nodes or none.
- **Concurrency Control**: The system detects conflicts when two transactions try to modify the same key.
- **Node Failure Handling**: The system can recover from node failures using transaction logs.

### API:

- `initialize(node_id, all_node_ids)`: Initializes a node in the distributed key-value store
- `begin()`: Starts a new transaction and returns a transaction ID
- `get(tx_id, key)`: Retrieves a value within a transaction
- `put(tx_id, key, value)`: Updates a value within a transaction
- `commit(tx_id)`: Attempts to commit the transaction
- `rollback(tx_id)`: Rolls back the transaction

## Limitations and Future Improvements

This implementation is a simplified version focusing on the core concepts:

1. **Performance Optimization**: The current implementation prioritizes correctness over performance. Future work could include batching, pipelining, and more efficient data structures.
2. **Failure Recovery**: The failure recovery mechanism is basic. A more robust approach would include leader election and automatic recovery.
3. **Scalability**: The current design works best with a small number of nodes. To scale further, partitioning or sharding could be implemented.
4. **Network Communication**: This implementation simulates distributed communication. In a real-world system, network calls would replace this simulation.
5. **Read Optimization**: Read-only transactions could be optimized to avoid the consensus protocol.

## Testing

The system includes tests for:
- Basic transaction operations
- Transaction isolation
- Concurrency
- Conflict detection and resolution
- Failure recovery
- Stress testing with many concurrent transactions