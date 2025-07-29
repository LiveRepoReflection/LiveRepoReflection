# Distributed Transaction Coordinator

This project implements a simplified distributed transaction coordinator that orchestrates a two-phase commit (2PC) protocol among multiple participants. The coordinator ensures that a transaction across multiple services either fully succeeds or fully fails, maintaining data consistency across services.

## Components

- **Participant Interface**: Defines the contract for participants in the 2PC protocol. Each participant must be able to execute an operation, prepare for a commit, commit, and rollback.
- **Coordinator**: Implements the 2PC protocol to coordinate transactions across multiple participants.

## The Two-Phase Commit Protocol

1. **Execute Phase**: The coordinator sends the operation to all participants for execution.
2. **Prepare Phase**: The coordinator asks all participants if they can commit.
   - If all participants respond "yes", the coordinator proceeds to the commit phase.
   - If any participant responds "no", the coordinator initiates a rollback.
3. **Commit/Rollback Phase**: Based on the prepare phase result, the coordinator either:
   - Sends a commit message to all participants, or
   - Sends a rollback message to all participants.

## Error Handling

The coordinator handles various failure scenarios:
- Execution failures
- Prepare phase failures
- Commit phase failures
- Rollback failures
- Timeouts

## Concurrency

The implementation uses modern C++ concurrency features:
- `std::async` for asynchronous execution
- `std::future` for managing results
- `std::mutex` and `std::atomic` for thread safety

## Usage
