package leakybucket

import (
	"sync"
	"time"
)

// bucket represents a leaky bucket for a specific user
type bucket struct {
	lastUpdate time.Time
	tokens     float64
	mu         sync.Mutex
}

// Global map to store buckets for all users
var (
	buckets = make(map[string]*bucket)
	mapMu   sync.RWMutex
)

// AllowRequest determines if a request from the given user should be allowed
// based on the leaky bucket algorithm
func AllowRequest(userID string, capacity int, leakRate float64) bool {
	// Get the current time
	now := getCurrentTime()

	// Get or create bucket for this user
	b := getBucket(userID)

	// Lock the bucket for thread safety
	b.mu.Lock()
	defer b.mu.Unlock()

	// Calculate tokens leaked since last update
	elapsed := now.Sub(b.lastUpdate).Seconds()
	leaked := elapsed * leakRate
	
	// Update current token count
	newTokens := b.tokens - leaked
	if newTokens < 0 {
		newTokens = 0
	}

	// Check if adding a new request would exceed capacity
	if newTokens+1 > float64(capacity) {
		// Update the token count and timestamp even if we're rejecting
		b.tokens = newTokens
		b.lastUpdate = now
		return false
	}

	// Add the new request token and update timestamp
	b.tokens = newTokens + 1
	b.lastUpdate = now
	return true
}

// getBucket returns the bucket for a given user ID, creating it if necessary
func getBucket(userID string) *bucket {
	mapMu.RLock()
	b, exists := buckets[userID]
	mapMu.RUnlock()

	if exists {
		return b
	}

	// If bucket doesn't exist, create it
	mapMu.Lock()
	defer mapMu.Unlock()

	// Double-check existence in case another goroutine created it
	if b, exists = buckets[userID]; exists {
		return b
	}

	// Create new bucket
	b = &bucket{
		lastUpdate: getCurrentTime(),
		tokens:     0,
	}
	buckets[userID] = b
	return b
}

// getCurrentTime returns the current time, allowing for easier testing
func getCurrentTime() time.Time {
	if !mockTime.IsZero() {
		return mockTime
	}
	return time.Now()
}