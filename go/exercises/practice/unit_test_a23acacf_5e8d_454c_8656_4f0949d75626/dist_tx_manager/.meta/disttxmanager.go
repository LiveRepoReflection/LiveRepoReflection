package disttxmanager

import (
	"fmt"
	"sync"
	"time"
)

var (
	ErrTransactionNotFound   = fmt.Errorf("transaction not found")
	ErrStoreNotFound        = fmt.Errorf("store not found")
	ErrStoreUnavailable     = fmt.Errorf("store unavailable")
	ErrKeyNotFound          = fmt.Errorf("key not found")
	ErrTransactionCompleted = fmt.Errorf("transaction already completed")
)

type KeyValueStore interface {
	Get(key string) (string, error)
	Set(key string, value string) error
	Available() bool
}

type Transaction interface {
	Begin() error
	Get(storeID int, key string) (string, error)
	Set(storeID int, key string, value string) error
	Commit() error
	Rollback() error
	GetTransactionID() string
}

type TransactionManager struct {
	stores      map[int]KeyValueStore
	nextStoreID int
	nextTxID    int
	mu          sync.RWMutex
}

type transaction struct {
	id           string
	manager      *TransactionManager
	writeBuffer  map[int]map[string]string
	completed    bool
	mu           sync.RWMutex
	involvedKeys map[int]map[string]struct{}
}

func NewTransactionManager() *TransactionManager {
	return &TransactionManager{
		stores:      make(map[int]KeyValueStore),
		nextStoreID: 0,
		nextTxID:    0,
	}
}

func (tm *TransactionManager) RegisterStore(store KeyValueStore) int {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	storeID := tm.nextStoreID
	tm.stores[storeID] = store
	tm.nextStoreID++
	return storeID
}

func (tm *TransactionManager) GetStore(storeID int) (KeyValueStore, error) {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	if store, exists := tm.stores[storeID]; exists {
		return store, nil
	}
	return nil, ErrStoreNotFound
}

func (tm *TransactionManager) NewTransaction() (Transaction, error) {
	tm.mu.Lock()
	txID := tm.nextTxID
	tm.nextTxID++
	tm.mu.Unlock()

	tx := &transaction{
		id:           fmt.Sprintf("tx-%d", txID),
		manager:      tm,
		writeBuffer:  make(map[int]map[string]string),
		involvedKeys: make(map[int]map[string]struct{}),
	}
	return tx, tx.Begin()
}

func (tx *transaction) Begin() error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.completed {
		return ErrTransactionCompleted
	}
	return nil
}

func (tx *transaction) Get(storeID int, key string) (string, error) {
	tx.mu.RLock()
	defer tx.mu.RUnlock()

	if tx.completed {
		return "", ErrTransactionCompleted
	}

	// Check write buffer first
	if storeBuf, exists := tx.writeBuffer[storeID]; exists {
		if val, exists := storeBuf[key]; exists {
			return val, nil
		}
	}

	// If not in write buffer, get from store
	store, err := tx.manager.GetStore(storeID)
	if err != nil {
		return "", err
	}

	if !store.Available() {
		return "", ErrStoreUnavailable
	}

	// Track that this key was accessed
	if _, exists := tx.involvedKeys[storeID]; !exists {
		tx.involvedKeys[storeID] = make(map[string]struct{})
	}
	tx.involvedKeys[storeID][key] = struct{}{}

	return store.Get(key)
}

func (tx *transaction) Set(storeID int, key string, value string) error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.completed {
		return ErrTransactionCompleted
	}

	// Buffer the write
	if _, exists := tx.writeBuffer[storeID]; !exists {
		tx.writeBuffer[storeID] = make(map[string]string)
	}
	tx.writeBuffer[storeID][key] = value

	// Track that this key was modified
	if _, exists := tx.involvedKeys[storeID]; !exists {
		tx.involvedKeys[storeID] = make(map[string]struct{})
	}
	tx.involvedKeys[storeID][key] = struct{}{}

	return nil
}

func (tx *transaction) preparePhase() error {
	// Check if all stores are available
	for storeID := range tx.writeBuffer {
		store, err := tx.manager.GetStore(storeID)
		if err != nil {
			return err
		}
		if !store.Available() {
			return ErrStoreUnavailable
		}
	}
	return nil
}

func (tx *transaction) commitPhase() error {
	// Apply all buffered writes
	for storeID, storeBuf := range tx.writeBuffer {
		store, err := tx.manager.GetStore(storeID)
		if err != nil {
			return err
		}
		for key, value := range storeBuf {
			if err := store.Set(key, value); err != nil {
				return err
			}
			// Simulate some network delay
			time.Sleep(time.Millisecond)
		}
	}
	return nil
}

func (tx *transaction) Commit() error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.completed {
		return ErrTransactionCompleted
	}

	// Two-phase commit
	if err := tx.preparePhase(); err != nil {
		tx.completed = true
		return err
	}

	if err := tx.commitPhase(); err != nil {
		tx.completed = true
		return err
	}

	tx.completed = true
	return nil
}

func (tx *transaction) Rollback() error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.completed {
		return ErrTransactionCompleted
	}

	// Clear write buffer
	tx.writeBuffer = make(map[int]map[string]string)
	tx.completed = true
	return nil
}

func (tx *transaction) GetTransactionID() string {
	return tx.id
}