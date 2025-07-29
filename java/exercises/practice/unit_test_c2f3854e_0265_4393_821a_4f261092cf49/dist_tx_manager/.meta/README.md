# Distributed Transaction Manager

This project implements a distributed transaction manager (DTM) using the two-phase commit (2PC) protocol to coordinate transactions across multiple database shards in a distributed system.

## Overview

The DTM ensures ACID properties (Atomicity, Consistency, Isolation, Durability) for transactions that span multiple shards. The implementation focuses on:

1. **Atomicity**: Using the two-phase commit protocol to ensure all-or-nothing execution
2. **Isolation**: Managing concurrent transactions through proper locking and conflict detection
3. **Optimization**: Batching operations and skipping prepare phase for read-only operations

## Components

The system consists of:

- `Operation`: Represents a read or write operation on a specific shard
- `OperationType`: Enum for the types of operations (READ, WRITE)
- `Shard`: Interface defining the contract for database shards
- `DistributedTransactionManager`: The main implementation of the DTM

## Key Features

1. **Two-Phase Commit Protocol**:
   - Prepare phase: Validates operations can be executed successfully
   - Commit phase: Finalizes the execution if all shards are prepared

2. **Conflict Resolution**:
   - Detects conflicts during the prepare phase
   - Rolls back transactions if conflicts occur

3. **Optimizations**:
   - Read-only shards skip the prepare phase
   - Batches operations for the same shard

4. **Concurrency Control**:
   - Thread-safe implementation using locks
   - Proper transaction state management

## Usage
