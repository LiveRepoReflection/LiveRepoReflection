package txnkvstore

import "errors"

// Error constants for transaction operations
var (
	ErrInvalidNodeID         = errors.New("invalid node ID")
	ErrInsufficientMemory    = errors.New("insufficient memory")
	ErrTransactionCompleted  = errors.New("transaction already committed or aborted")
	ErrNodeFailure           = errors.New("node failure")
	ErrKeyNotFound           = errors.New("key not found")
	ErrEmptyKey              = errors.New("empty key is not allowed")
	ErrPrepareFailed         = errors.New("transaction prepare phase failed")
	ErrCommitFailed          = errors.New("transaction commit phase failed")
)

// Transaction status constants
const (
	StatusActive   = 0
	StatusPrepared = 1
	StatusCommitted = 2
	StatusAborted  = 3
)

// Default maximum number of concurrent transactions
const DefaultMaxTransactions = 1000