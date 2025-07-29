# Transaction Validator

This project implements a validator for transactions in a distributed database system. The validator's purpose is to determine whether a transaction that spans multiple nodes can be safely committed based on the logs from various participating nodes.

## Overview

In this distributed database system:

- A transaction involves multiple operations on resources across different nodes
- Each resource has a version, and operations can read and/or write resources
- Operations form a directed acyclic graph (DAG) with dependencies
- Nodes execute operations and log the resource versions they observe

The validator determines if a transaction should be committed or aborted based on several criteria:

1. **Version Consistency**: Operations must see the expected resource versions
2. **Acyclicity**: The transaction graph must be a DAG (no cycles)
3. **Atomicity**: If any operation fails, the entire transaction must be aborted
4. **Completeness**: All operations must be executed
5. **Real-time**: The validator must complete within a time limit

## Implementation Details

### Key Components

- `Operation`: Represents an action on a resource (read/write)
- `Dependency`: Defines ordering requirements between operations
- `TransactionGraph`: Contains all operations and their dependencies
- `LogEntry`: Records the actual execution of an operation at a node

### Validation Algorithm

The validator performs several key checks:

1. **Cycle Detection**: Uses topological sorting to ensure the transaction graph is a DAG
2. **Completeness Check**: Ensures all operations in the graph were executed
3. **Version Consistency**: Verifies each operation read the expected resource version
4. **Dependency Validation**: Confirms operations were executed in an order respecting dependencies
5. **Time Limit**: Monitors execution time to stay within the required time constraint

## Usage

The main function is:
