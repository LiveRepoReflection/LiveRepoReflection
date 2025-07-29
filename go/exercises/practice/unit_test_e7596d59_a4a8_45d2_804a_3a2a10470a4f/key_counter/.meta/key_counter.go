package key_counter

import (
	"sort"
	"sync"
)

// KeyCount represents a key and its associated count.
type KeyCount struct {
	Key   string
	Count int
}

// KeyCounterService defines the required operations for the key counter.
type KeyCounterService interface {
	Increment(key string, value int) error
	Get(key string) (int, error)
	TopK(k int) ([]KeyCount, error)
}

// keyCounter is the in-memory implementation of the KeyCounterService.
type keyCounter struct {
	mu     sync.RWMutex
	counts map[string]int
}

// NewKeyCounter creates and returns a new instance of the key counter service.
func NewKeyCounter() KeyCounterService {
	return &keyCounter{
		counts: make(map[string]int),
	}
}

// Increment increments the counter for the given key by the specified value.
// It uses a write lock to ensure thread-safety.
func (kc *keyCounter) Increment(key string, value int) error {
	kc.mu.Lock()
	defer kc.mu.Unlock()
	kc.counts[key] += value
	return nil
}

// Get returns the current count associated with the given key.
// If the key does not exist, it returns 0.
func (kc *keyCounter) Get(key string) (int, error) {
	kc.mu.RLock()
	defer kc.mu.RUnlock()
	return kc.counts[key], nil
}

// TopK returns the k keys with the highest counts in descending order.
// If multiple keys have the same count, they are sorted lexicographically.
// If k is greater than the number of keys available, all keys are returned.
func (kc *keyCounter) TopK(k int) ([]KeyCount, error) {
	kc.mu.RLock()
	defer kc.mu.RUnlock()

	// Copy the counts map into a slice.
	keyCounts := make([]KeyCount, 0, len(kc.counts))
	for key, count := range kc.counts {
		keyCounts = append(keyCounts, KeyCount{Key: key, Count: count})
	}

	// Sort the slice first by count descending, then by key lexicographically.
	sort.Slice(keyCounts, func(i, j int) bool {
		if keyCounts[i].Count == keyCounts[j].Count {
			return keyCounts[i].Key < keyCounts[j].Key
		}
		return keyCounts[i].Count > keyCounts[j].Count
	})

	// If k is greater than available keys, adjust k.
	if k > len(keyCounts) {
		k = len(keyCounts)
	}

	return keyCounts[:k], nil
}