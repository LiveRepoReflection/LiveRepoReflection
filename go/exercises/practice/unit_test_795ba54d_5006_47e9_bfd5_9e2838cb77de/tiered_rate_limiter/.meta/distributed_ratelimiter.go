package ratelimiter

import (
	"context"
	"errors"
	"sync"
	"time"
)

// DistributedRateLimiter extends the basic RateLimiter to work in a distributed environment.
// This implementation uses a simple in-memory approach with thread safety,
// but in a real distributed system, you would replace this with Redis or another shared storage.
type DistributedRateLimiter struct {
	// Configuration
	limits          map[string]int
	windowDuration  time.Duration
	cleanupInterval time.Duration
	
	// Data store that would be replaced with Redis or similar in production
	store           *distributedStore
	
	// Context for cleanup
	ctx             context.Context
	cancel          context.CancelFunc
	cleanupDone     chan struct{}
}

// distributedStore is a thread-safe store that simulates a distributed storage
// In a real implementation, this would be replaced with Redis or similar
type distributedStore struct {
	windows map[string][]time.Time
	lastAccess map[string]time.Time
	mu      sync.RWMutex
}

// NewDistributedRateLimiter creates a new distributed rate limiter
func NewDistributedRateLimiter(ctx context.Context) (*DistributedRateLimiter, error) {
	if ctx == nil {
		return nil, errors.New("context cannot be nil")
	}
	
	cleanupCtx, cancel := context.WithCancel(ctx)
	
	limiter := &DistributedRateLimiter{
		limits: map[string]int{
			"Free":     5,
			"Standard": 20,
			"Premium":  100,
		},
		windowDuration:  time.Minute,
		cleanupInterval: 5 * time.Minute,
		store: &distributedStore{
			windows: make(map[string][]time.Time),
			lastAccess: make(map[string]time.Time),
		},
		ctx:            cleanupCtx,
		cancel:         cancel,
		cleanupDone:    make(chan struct{}),
	}
	
	// Start cleanup goroutine
	go limiter.cleanup()
	
	return limiter, nil
}

// Allow checks if a request from a user with a specific tier is allowed
func (drl *DistributedRateLimiter) Allow(userID, tier string) bool {
	// Check if the tier is valid
	limit, ok := drl.limits[tier]
	if !ok {
		return false
	}
	
	// Create a key that combines userID and tier
	key := userID + ":" + tier
	
	// Acquire lock for this operation (in a real Redis implementation, 
	// this would be a MULTI/EXEC or Lua script for atomicity)
	drl.store.mu.Lock()
	defer drl.store.mu.Unlock()
	
	// Update last access time
	drl.store.lastAccess[key] = time.Now()
	
	// Get current window
	window, exists := drl.store.windows[key]
	if !exists {
		window = make([]time.Time, 0, 100) // Pre-allocate some capacity
		drl.store.windows[key] = window
	}
	
	// Clean expired requests
	now := time.Now()
	cutoff := now.Add(-drl.windowDuration)
	
	i := 0
	for ; i < len(window); i++ {
		if window[i].After(cutoff) {
			break
		}
	}
	
	// Remove expired requests
	if i > 0 {
		window = window[i:]
		drl.store.windows[key] = window
	}
	
	// Check if adding this request would exceed the limit
	if len(window) >= limit {
		return false
	}
	
	// Add current request to the window
	drl.store.windows[key] = append(window, now)
	return true
}

// cleanup periodically removes windows for users who haven't made requests recently
func (drl *DistributedRateLimiter) cleanup() {
	defer close(drl.cleanupDone)
	
	ticker := time.NewTicker(drl.cleanupInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			drl.performCleanup()
		case <-drl.ctx.Done():
			return
		}
	}
}

// performCleanup removes sliding windows for inactive users
func (drl *DistributedRateLimiter) performCleanup() {
	now := time.Now()
	inactivityCutoff := now.Add(-drl.cleanupInterval * 2)
	
	drl.store.mu.Lock()
	defer drl.store.mu.Unlock()
	
	for key, lastAccess := range drl.store.lastAccess {
		if lastAccess.Before(inactivityCutoff) {
			delete(drl.store.windows, key)
			delete(drl.store.lastAccess, key)
		}
	}
}

// Close stops the rate limiter's background processes
func (drl *DistributedRateLimiter) Close() error {
	drl.cancel()
	<-drl.cleanupDone
	return nil
}