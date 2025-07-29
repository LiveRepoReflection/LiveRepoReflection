package concurrentkv

import (
	"sync"
	"sync/atomic"
)

type Store struct {
	data    sync.Map
	version uint64
}

type entry struct {
	value   string
	version uint64
}

// New creates a new concurrent key-value store
func New() *Store {
	return &Store{
		data:    sync.Map{},
		version: 0,
	}
}

// Get retrieves a value from the store
func (s *Store) Get(key string) (string, bool) {
	if val, ok := s.data.Load(key); ok {
		entry := val.(entry)
		return entry.value, true
	}
	return "", false
}

// Put stores a value in the store
func (s *Store) Put(key string, value string) {
	version := atomic.AddUint64(&s.version, 1)
	s.data.Store(key, entry{
		value:   value,
		version: version,
	})
}

// Delete removes a key-value pair from the store
func (s *Store) Delete(key string) {
	s.data.Delete(key)
	atomic.AddUint64(&s.version, 1)
}

// Snapshot returns a consistent snapshot of the store
func (s *Store) Snapshot() map[string]string {
	snapshot := make(map[string]string)
	currentVersion := atomic.LoadUint64(&s.version)

	// First pass: collect all entries that existed at the start of snapshot
	temp := make(map[string]entry)
	s.data.Range(func(key, value interface{}) bool {
		k := key.(string)
		v := value.(entry)
		if v.version <= currentVersion {
			temp[k] = v
		}
		return true
	})

	// Second pass: only include entries that haven't changed during snapshot
	for k, v := range temp {
		if val, ok := s.data.Load(k); ok {
			currentEntry := val.(entry)
			if currentEntry.version == v.version {
				snapshot[k] = v.value
			}
		}
	}

	return snapshot
}