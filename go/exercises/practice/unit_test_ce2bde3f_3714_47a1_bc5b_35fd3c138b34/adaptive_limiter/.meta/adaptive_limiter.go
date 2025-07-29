package adaptive_limiter

import (
	"sync"
	"time"
)

// RateLimiter provides distributed rate limiting with adaptive throttling.
type RateLimiter struct {
	windowSize       time.Duration
	globalLoadFactor float64
	clients          map[string]*clientData
	mutex            sync.Mutex
}

type clientData struct {
	baseLimit   int
	currentCount int
	windowStart time.Time
}

// NewRateLimiter initializes a RateLimiter with a given window size (in seconds).
func NewRateLimiter(windowSize int) *RateLimiter {
	return &RateLimiter{
		windowSize:       time.Duration(windowSize) * time.Second,
		globalLoadFactor: 1.0, // default load factor is 1.0
		clients:          make(map[string]*clientData),
	}
}

// SetBaseLimit sets the base limit for a given clientID.
// If the client already exists, its base limit is updated.
func (rl *RateLimiter) SetBaseLimit(clientID string, baseLimit int) {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()
	// If the client does not already exist, initialize it.
	if _, exists := rl.clients[clientID]; !exists {
		rl.clients[clientID] = &clientData{
			baseLimit:    baseLimit,
			windowStart:  time.Now(),
			currentCount: 0,
		}
	} else {
		// Update the base limit, do not alter the current window or count.
		rl.clients[clientID].baseLimit = baseLimit
	}
}

// UpdateGlobalLoadFactor updates the global load factor.
// It affects the effective limits for all clients immediately.
func (rl *RateLimiter) UpdateGlobalLoadFactor(loadFactor float64) {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()
	rl.globalLoadFactor = loadFactor
}

// Allow processes a request for the given clientID.
// It returns true if the request is within the allowed rate limit, false otherwise.
func (rl *RateLimiter) Allow(clientID string) bool {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	client, exists := rl.clients[clientID]
	if !exists {
		// If client is not registered, deny the request.
		return false
	}

	now := time.Now()
	// Reset window if needed.
	if now.Sub(client.windowStart) >= rl.windowSize {
		client.currentCount = 0
		client.windowStart = now
	}

	// Calculate effective limit = baseLimit * globalLoadFactor, rounded down.
	effectiveLimit := int(float64(client.baseLimit) * rl.globalLoadFactor)

	if client.currentCount < effectiveLimit {
		client.currentCount++
		return true
	}
	return false
}