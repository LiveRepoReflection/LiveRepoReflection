package disttxmanager

import (
	"sync"
	"testing"
)

type mockKeyValueStore struct {
	data      map[string]string
	available bool
	mu        sync.RWMutex
}

func newMockKeyValueStore() *mockKeyValueStore {
	return &mockKeyValueStore{
		data:      make(map[string]string),
		available: true,
	}
}

func (m *mockKeyValueStore) Get(key string) (string, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if !m.available {
		return "", ErrStoreUnavailable
	}
	if val, ok := m.data[key]; ok {
		return val, nil
	}
	return "", ErrKeyNotFound
}

func (m *mockKeyValueStore) Set(key string, value string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if !m.available {
		return ErrStoreUnavailable
	}
	m.data[key] = value
	return nil
}

func (m *mockKeyValueStore) Available() bool {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.available
}

func TestTransactionManager(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Setup
			tm := NewTransactionManager()
			stores := make([]*mockKeyValueStore, 3)
			for i := range stores {
				stores[i] = newMockKeyValueStore()
				tm.RegisterStore(stores[i])
			}

			txs := make(map[int]Transaction)

			// Execute operations
			for _, op := range tc.operations {
				var err error
				switch op.opType {
				case "begin":
					txs[op.txID], err = tm.NewTransaction()
				case "set":
					err = txs[op.txID].Set(op.storeID, op.key, op.value)
				case "get":
					var val string
					val, err = txs[op.txID].Get(op.storeID, op.key)
					if err == nil && val != op.value {
						t.Errorf("Get returned wrong value: got %v, want %v", val, op.value)
					}
				case "commit":
					err = txs[op.txID].Commit()
				case "rollback":
					err = txs[op.txID].Rollback()
				}

				if err != op.expected {
					t.Errorf("Operation %v returned unexpected error: got %v, want %v", op.opType, err, op.expected)
				}
			}

			// Verify final state
			for _, exp := range tc.expected {
				val, err := stores[exp.storeID].Get(exp.key)
				if err != nil && exp.value != "" {
					t.Errorf("Failed to get key %v from store %v: %v", exp.key, exp.storeID, err)
				}
				if val != exp.value {
					t.Errorf("Wrong value for key %v in store %v: got %v, want %v", exp.key, exp.storeID, val, exp.value)
				}
			}
		})
	}
}

func TestConcurrency(t *testing.T) {
	tm := NewTransactionManager()
	store := newMockKeyValueStore()
	tm.RegisterStore(store)

	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			tx, _ := tm.NewTransaction()
			tx.Set(0, "key", "value")
			tx.Commit()
		}(i)
	}
	wg.Wait()
}

func BenchmarkTransactionManager(b *testing.B) {
	tm := NewTransactionManager()
	store := newMockKeyValueStore()
	tm.RegisterStore(store)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tx, _ := tm.NewTransaction()
		tx.Set(0, "key", "value")
		tx.Commit()
	}
}