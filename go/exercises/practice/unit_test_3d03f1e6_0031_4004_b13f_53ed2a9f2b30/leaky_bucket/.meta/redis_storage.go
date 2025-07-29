package leakybucket

import (
	"sync"
	"time"
)

// Note: This is a simplified in-memory implementation of what would typically
// be Redis-based storage in a production environment. In a real distributed
// system, you would replace this with actual Redis calls.

type bucketState struct {
	Tokens     float64
	LastUpdate time.Time
}

type redisStorage struct {
	store map[string]bucketState
	mu    sync.RWMutex
}

var storage = &redisStorage{
	store: make(map[string]bucketState),
}

func (rs *redisStorage) getBucketState(userID string) (bucketState, bool) {
	rs.mu.RLock()
	defer rs.mu.RUnlock()
	state, exists := rs.store[userID]
	return state, exists
}

func (rs *redisStorage) setBucketState(userID string, state bucketState) {
	rs.mu.Lock()
	defer rs.mu.Unlock()
	rs.store[userID] = state
}

func (rs *redisStorage) clear() {
	rs.mu.Lock()
	defer rs.mu.Unlock()
	rs.store = make(map[string]bucketState)
}