# Transactional Key-Value Store with Snapshot Isolation

This project implements an in-memory distributed transactional key-value store with snapshot isolation guarantees. It provides a consistent view of data for each transaction regardless of concurrent modifications by other transactions.

## Features

- **Snapshot Isolation**: Each transaction operates on a consistent snapshot of the data
- **ACID Properties**: Provides atomicity, consistency, isolation, and reasonable durability
- **Optimized for Reads**: Designed for read-heavy workloads
- **Concurrency**: Supports multiple concurrent transactions with proper synchronization
- **Extensible**: Design considerations for distributed deployment

## API

The store provides the following operations:

- `begin_transaction()`: Starts a new transaction and returns a unique transaction ID
- `read(TID, key)`: Reads a value within the transaction context
- `write(TID, key, value)`: Writes a value within the transaction context
- `commit_transaction(TID)`: Attempts to commit all changes made in the transaction
- `abort_transaction(TID)`: Discards all changes made in the transaction

## Implementation Details

The implementation uses Multi-Version Concurrency Control (MVCC) to provide snapshot isolation:

- Each key maintains a list of versioned values
- Transactions read from a consistent snapshot based on their start time
- Write-write conflicts are detected at commit time
- Thread synchronization is handled through locks
- Uses UUID for transaction ID generation

## Scaling Considerations

The code includes comments on how to extend this implementation to a distributed environment, covering:

- Sharding
- Replication
- Distributed transaction coordination
- Consensus algorithms
- Failure handling
- Recovery mechanisms

## Running Tests

The implementation includes comprehensive test cases that verify:

- Basic read/write functionality
- Snapshot isolation guarantees
- Concurrent transaction handling
- Edge cases like write skew prevention
- Performance with large values and many keys

Run the tests with:
