package dist_kv_store

import (
	"context"
	"errors"
	"sync"
	"time"
)

var (
	ErrKeyNotFound        = errors.New("key not found")
	ErrInvalidTransaction = errors.New("invalid transaction")
	ErrTransactionConflict = errors.New("transaction conflict")
)

type TransactionID string

type transaction struct {
	id        TransactionID
	startTime time.Time
	changes   map[string]string
	keysLocked map[string]struct{}
}

type KVStore struct {
	mu          sync.RWMutex
	data        map[string]string
	transactions map[TransactionID]*transaction
	nodeID      string
}

func NewKVStore() *KVStore {
	return &KVStore{
		data:        make(map[string]string),
		transactions: make(map[TransactionID]*transaction),
		nodeID:      "node1", // In real implementation, this would be unique per node
	}
}

func (s *KVStore) Get(ctx context.Context, key string, opts ...OperationOption) (string, error) {
	options := &operationOptions{}
	for _, opt := range opts {
		opt(options)
	}

	s.mu.RLock()
	defer s.mu.RUnlock()

	if options.txID != "" {
		tx, exists := s.transactions[options.txID]
		if !exists {
			return "", ErrInvalidTransaction
		}

		if val, ok := tx.changes[key]; ok {
			return val, nil
		}
	}

	val, exists := s.data[key]
	if !exists {
		return "", ErrKeyNotFound
	}
	return val, nil
}

func (s *KVStore) Put(ctx context.Context, key, value string, opts ...OperationOption) error {
	options := &operationOptions{}
	for _, opt := range opts {
		opt(options)
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	if options.txID != "" {
		tx, exists := s.transactions[options.txID]
		if !exists {
			return ErrInvalidTransaction
		}

		if _, locked := tx.keysLocked[key]; !locked {
			if _, exists := s.data[key]; exists {
				tx.keysLocked[key] = struct{}{}
			}
		}

		tx.changes[key] = value
		return nil
	}

	s.data[key] = value
	return nil
}

func (s *KVStore) Delete(ctx context.Context, key string, opts ...OperationOption) error {
	options := &operationOptions{}
	for _, opt := range opts {
		opt(options)
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	if options.txID != "" {
		tx, exists := s.transactions[options.txID]
		if !exists {
			return ErrInvalidTransaction
		}

		if _, locked := tx.keysLocked[key]; !locked {
			if _, exists := s.data[key]; exists {
				tx.keysLocked[key] = struct{}{}
			}
		}

		tx.changes[key] = ""
		return nil
	}

	if _, exists := s.data[key]; !exists {
		return ErrKeyNotFound
	}

	delete(s.data, key)
	return nil
}

func (s *KVStore) BeginTransaction(ctx context.Context) (TransactionID, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	txID := TransactionID(s.nodeID + "-" + time.Now().Format(time.RFC3339Nano))
	s.transactions[txID] = &transaction{
		id:        txID,
		startTime: time.Now(),
		changes:   make(map[string]string),
		keysLocked: make(map[string]struct{}),
	}

	return txID, nil
}

func (s *KVStore) CommitTransaction(ctx context.Context, txID TransactionID) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	tx, exists := s.transactions[txID]
	if !exists {
		return ErrInvalidTransaction
	}

	// Check for conflicts
	for key := range tx.keysLocked {
		if currentVal, exists := s.data[key]; exists {
			if _, changed := tx.changes[key]; changed {
				// If the key was modified in the transaction, we need to check if it was modified by others
				if tx.changes[key] != currentVal {
					return ErrTransactionConflict
				}
			}
		}
	}

	// Apply changes
	for key, val := range tx.changes {
		if val == "" {
			delete(s.data, key)
		} else {
			s.data[key] = val
		}
	}

	delete(s.transactions, txID)
	return nil
}

func (s *KVStore) RollbackTransaction(ctx context.Context, txID TransactionID) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.transactions[txID]; !exists {
		return ErrInvalidTransaction
	}

	delete(s.transactions, txID)
	return nil
}

type operationOptions struct {
	txID TransactionID
}

type OperationOption func(*operationOptions)

func WithTransaction(txID TransactionID) OperationOption {
	return func(o *operationOptions) {
		o.txID = txID
	}
}