package ratelimiter

import (
	"context"
	"errors"
	"sync"
	"time"
)

// RateLimiter implements a distributed rate limiter
// with tiered rate limits using a sliding window algorithm
type RateLimiter struct {
	// Configuration
	limits           map[string]int
	windowDuration   time.Duration
	cleanupInterval  time.Duration
	
	// Data stores
	userWindows      map[string]*slidingWindow
	mu               sync.RWMutex
	
	// Cleanup
	ctx              context.Context
	cancel           context.CancelFunc
	cleanupDone      chan struct{}
}

// slidingWindow represents a sliding window for a specific user
type slidingWindow struct {
	requests   []time.Time // Timestamps of requests in the current window
	mu         sync.Mutex  // Mutex to protect concurrent access to the window
	lastAccess time.Time   // For cleanup purposes
}

// NewRateLimiter creates a new distributed rate limiter
func NewRateLimiter(ctx context.Context) (*RateLimiter, error) {
	if ctx == nil {
		return nil, errors.New("context cannot be nil")
	}
	
	// Create child context for cleanup goroutine
	cleanupCtx, cancel := context.WithCancel(ctx)
	
	limiter := &RateLimiter{
		limits: map[string]int{
			"Free":     5,
			"Standard": 20,
			"Premium":  100,
		},
		windowDuration:  time.Minute,
		cleanupInterval: 5 * time.Minute,
		userWindows:     make(map[string]*slidingWindow),
		ctx:             cleanupCtx,
		cancel:          cancel,
		cleanupDone:     make(chan struct{}),
	}
	
	// Start cleanup goroutine
	go limiter.cleanup()
	
	return limiter, nil
}

// Allow checks if a request from a user with a specific tier is allowed
func (rl *RateLimiter) Allow(userID, tier string) bool {
	// Check if the tier is valid
	limit, ok := rl.limits[tier]
	if !ok {
		return false
	}
	
	// Create a key that combines userID and tier
	key := userID + ":" + tier
	
	// Get or create sliding window for this user+tier
	window := rl.getOrCreateWindow(key)
	
	// Lock the window for this operation
	window.mu.Lock()
	defer window.mu.Unlock()
	
	// Update last access time
	window.lastAccess = time.Now()
	
	// Clean expired requests from the window
	rl.cleanExpiredRequests(window)
	
	// Check if adding this request would exceed the limit
	if len(window.requests) >= limit {
		return false
	}
	
	// Add current request to the window
	window.requests = append(window.requests, time.Now())
	return true
}

// getOrCreateWindow retrieves or creates a sliding window for a user+tier
func (rl *RateLimiter) getOrCreateWindow(key string) *slidingWindow {
	// First try with a read lock
	rl.mu.RLock()
	window, exists := rl.userWindows[key]
	rl.mu.RUnlock()
	
	if exists {
		return window
	}
	
	// If not found, acquire write lock and check again
	rl.mu.Lock()
	defer rl.mu.Unlock()
	
	// Double-check after acquiring write lock
	window, exists = rl.userWindows[key]
	if !exists {
		window = &slidingWindow{
			requests:   make([]time.Time, 0, 100), // Pre-allocate some capacity
			lastAccess: time.Now(),
		}
		rl.userWindows[key] = window
	}
	
	return window
}

// cleanExpiredRequests removes requests that are outside the current window
func (rl *RateLimiter) cleanExpiredRequests(window *slidingWindow) {
	now := time.Now()
	cutoff := now.Add(-rl.windowDuration)
	
	// Find the index of the first request that's still within the window
	i := 0
	for ; i < len(window.requests); i++ {
		if window.requests[i].After(cutoff) {
			break
		}
	}
	
	// Remove all expired requests
	if i > 0 {
		window.requests = window.requests[i:]
	}
}

// cleanup periodically removes windows for users who haven't made requests recently
func (rl *RateLimiter) cleanup() {
	defer close(rl.cleanupDone)
	
	ticker := time.NewTicker(rl.cleanupInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			rl.performCleanup()
		case <-rl.ctx.Done():
			return
		}
	}
}

// performCleanup removes sliding windows for inactive users
func (rl *RateLimiter) performCleanup() {
	now := time.Now()
	inactivityCutoff := now.Add(-rl.cleanupInterval * 2) // Remove after 2 cleanup intervals of inactivity
	
	// Acquire write lock for cleanup
	rl.mu.Lock()
	defer rl.mu.Unlock()
	
	for key, window := range rl.userWindows {
		window.mu.Lock()
		lastAccess := window.lastAccess
		window.mu.Unlock()
		
		if lastAccess.Before(inactivityCutoff) {
			delete(rl.userWindows, key)
		}
	}
}

// Close stops the rate limiter's background processes
func (rl *RateLimiter) Close() error {
	rl.cancel()
	<-rl.cleanupDone
	return nil
}