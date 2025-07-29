# Distributed Transactional Key-Value Store

This project implements a simplified distributed transactional key-value store that provides ACID guarantees and fault tolerance through a consensus algorithm.

## Features

- Basic key-value operations: `put(key, value)` and `get(key)`
- ACID transactions with serializable isolation
- Distributed design with consensus-based replication
- Fault tolerance with configurable cluster size
- Linearizable operations
- Optimistic concurrency control for transaction management

## Architecture

The system consists of the following main components:

1. **KeyValueStore** - The main interface for client operations
2. **Transaction** - Represents a transaction with read and write sets
3. **TransactionManager** - Manages transaction lifecycle and conflict detection
4. **Node** - Represents a single node in the distributed cluster
5. **ConsensusModule** - Interface for consensus algorithms (e.g., Raft, Paxos)

## Usage Example
