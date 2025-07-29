// Package txnkvstore provides a distributed transactional key-value store
// that supports ACID transactions across multiple nodes.
package txnkvstore

// This file serves as the main entry point for the package.
// The actual implementation is split into multiple files for better organization:
// - node.go: Implementation of the Node struct and its methods
// - transaction.go: Implementation of the Transaction struct and its methods
// - coordinator.go: Implementation of the Coordinator struct and its methods
// - constants.go: Error constants and other global constants