package distributed_limit

import (
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"
)

var (
	// ErrKeyNotFound is returned when a key is not found in the store
	ErrKeyNotFound = errors.New("key not found")
)

// Store is an interface for key-value storage with expiration
type Store interface {
	// Get retrieves a value for the given key
	Get(key string) ([]byte, error)
	
	// Set stores a value for the given key with an optional expiration
	Set(key string, value []byte, expiration time.Duration) error
	
	// Delete removes a key from the store
	Delete(key string) error
	
	// Cleanup removes expired keys from the store
	Cleanup()
}

// MemoryStoreItem represents an item in the MemoryStore
type MemoryStoreItem struct {
	Value      []byte
	Expiration time.Time
}

// MemoryStore is an in-memory implementation of the Store interface
type MemoryStore struct {
	mu    sync.RWMutex
	items map[string]MemoryStoreItem
}

// NewMemoryStore creates a new in-memory store
func NewMemoryStore() *MemoryStore {
	return &MemoryStore{
		items: make(map[string]MemoryStoreItem),
	}
}

// Get retrieves a value for the given key from memory
func (s *MemoryStore) Get(key string) ([]byte, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	item, found := s.items[key]
	if !found {
		return nil, ErrKeyNotFound
	}
	
	// Check if the item has expired
	if !item.Expiration.IsZero() && item.Expiration.Before(time.Now()) {
		return nil, ErrKeyNotFound
	}
	
	return item.Value, nil
}

// Set stores a value for the given key in memory with an optional expiration
func (s *MemoryStore) Set(key string, value []byte, expiration time.Duration) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	var expirationTime time.Time
	if expiration > 0 {
		expirationTime = time.Now().Add(expiration)
	}
	
	s.items[key] = MemoryStoreItem{
		Value:      value,
		Expiration: expirationTime,
	}
	
	return nil
}

// Delete removes a key from memory
func (s *MemoryStore) Delete(key string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	delete(s.items, key)
	return nil
}

// Cleanup removes expired items from memory
func (s *MemoryStore) Cleanup() {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	now := time.Now()
	for key, item := range s.items {
		if !item.Expiration.IsZero() && item.Expiration.Before(now) {
			delete(s.items, key)
		}
	}
}

// encode encodes a value to JSON
func encode(v interface{}) ([]byte, error) {
	return json.Marshal(v)
}

// decode decodes a JSON value
func decode(data []byte, v interface{}) error {
	if len(data) == 0 {
		return fmt.Errorf("empty data")
	}
	return json.Unmarshal(data, v)
}