package sliding_window_rate_limiter

import (
	"sync"
	"time"
)

// RedisStore represents a mock Redis-like storage
type RedisStore struct {
	data map[string][]time.Time
	mu   sync.RWMutex
}

// NewRedisStore creates a new Redis store
func NewRedisStore() *RedisStore {
	return &RedisStore{
		data: make(map[string][]time.Time),
	}
}

// Add adds a timestamp to a client's request list
func (rs *RedisStore) Add(clientID string, timestamp time.Time) {
	rs.mu.Lock()
	defer rs.mu.Unlock()

	if _, exists := rs.data[clientID]; !exists {
		rs.data[clientID] = make([]time.Time, 0)
	}
	rs.data[clientID] = append(rs.data[clientID], timestamp)
}

// GetRequests returns all requests for a client within the window
func (rs *RedisStore) GetRequests(clientID string, windowStart time.Time) []time.Time {
	rs.mu.RLock()
	defer rs.mu.RUnlock()

	if requests, exists := rs.data[clientID]; exists {
		valid := make([]time.Time, 0)
		for _, ts := range requests {
			if ts.After(windowStart) {
				valid = append(valid, ts)
			}
		}
		return valid
	}
	return nil
}

// Cleanup removes expired requests
func (rs *RedisStore) Cleanup(clientID string, cutoff time.Time) {
	rs.mu.Lock()
	defer rs.mu.Unlock()

	if requests, exists := rs.data[clientID]; exists {
		valid := make([]time.Time, 0)
		for _, ts := range requests {
			if ts.After(cutoff) {
				valid = append(valid, ts)
			}
		}
		rs.data[clientID] = valid
	}
}