package distributed_median

// Package-level documentation
// This package implements a distributed median calculation system
// with worker nodes that maintain limited-size buffers and a coordinator
// that aggregates the data to calculate the global median.

// Exported functions are documented below:

// NewWorkerNode creates a new worker node with the specified buffer size
// NewCoordinatorNode creates a new coordinator node
// WorkerNode.ReceiveNumber processes a new number into the worker's buffer
// WorkerNode.GetBuffer returns the current buffer contents
// CoordinatorNode.ReceiveWorkerBuffer accepts a worker's buffer
// CoordinatorNode.CalculateMedian computes the median from all received buffers