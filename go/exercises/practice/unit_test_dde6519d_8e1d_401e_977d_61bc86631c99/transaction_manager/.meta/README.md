# Distributed Transaction Manager

This package implements a simplified in-memory distributed transaction manager that uses the Two-Phase Commit (2PC) protocol to ensure atomicity across multiple service nodes.

## Key Features

- Distributed transaction coordination using 2PC protocol
- Thread-safe implementation for concurrent operations
- Service node isolation ensuring a node can only participate in one transaction at a time
- Proper error handling for edge cases and failures
- Support for transaction state tracking and management

## Usage

Here's a basic example of how to use the transaction manager:
