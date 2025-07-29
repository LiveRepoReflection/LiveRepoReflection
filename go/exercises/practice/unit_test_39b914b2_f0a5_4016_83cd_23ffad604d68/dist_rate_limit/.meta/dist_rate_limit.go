package dist_rate_limit

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

const (
	maxTimestampDrift = 300 // Maximum allowed timestamp drift in seconds (5 minutes)
)

type ClientWindow struct {
	requestCount int
	startTime    int64
}

// RateLimiter implements a thread-safe, distributed rate limiter
// using a sliding window algorithm with in-memory storage
type RateLimiter struct {
	maxRequests       int
	timeWindowSeconds int64
	mu               sync.RWMutex
	clients          map[string]*ClientWindow
}

// NewRateLimiter creates a new distributed rate limiter
func NewRateLimiter(maxRequests int, timeWindowSeconds int64) (*RateLimiter, error) {
	if maxRequests <= 0 {
		return nil, errors.New("maxRequests must be greater than 0")
	}
	if timeWindowSeconds <= 0 {
		return nil, errors.New("timeWindowSeconds must be greater than 0")
	}

	return &RateLimiter{
		maxRequests:       maxRequests,
		timeWindowSeconds: timeWindowSeconds,
		clients:          make(map[string]*ClientWindow),
	}, nil
}

// Allow checks if a client is allowed to make a request at the given timestamp
func (rl *RateLimiter) Allow(clientID string, timestamp int64) bool {
	if !rl.validateInput(clientID, timestamp) {
		return false
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	// Get or create client window
	window, exists := rl.clients[clientID]
	if !exists {
		window = &ClientWindow{
			requestCount: 0,
			startTime:    timestamp,
		}
		rl.clients[clientID] = window
	}

	// Clean up expired windows
	rl.cleanupExpiredWindows(timestamp)

	// Check if current window has expired
	if timestamp-window.startTime >= rl.timeWindowSeconds {
		window.requestCount = 0
		window.startTime = timestamp
	}

	// Check if client has exceeded rate limit
	if window.requestCount >= rl.maxRequests {
		return false
	}

	// Increment request count and allow request
	window.requestCount++
	return true
}

// validateInput checks if the input parameters are valid
func (rl *RateLimiter) validateInput(clientID string, timestamp int64) bool {
	if clientID == "" {
		return false
	}

	currentTime := time.Now().Unix()
	if timestamp < currentTime-maxTimestampDrift || timestamp > currentTime+maxTimestampDrift {
		return false
	}

	return true
}

// cleanupExpiredWindows removes expired client windows to prevent memory leaks
func (rl *RateLimiter) cleanupExpiredWindows(currentTimestamp int64) {
	for clientID, window := range rl.clients {
		if currentTimestamp-window.startTime >= rl.timeWindowSeconds*2 {
			delete(rl.clients, clientID)
		}
	}
}

// GetClientStats returns the current request count and window start time for a client
// This method is primarily used for testing and monitoring
func (rl *RateLimiter) GetClientStats(clientID string) (int, int64, error) {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	window, exists := rl.clients[clientID]
	if !exists {
		return 0, 0, fmt.Errorf("client %s not found", clientID)
	}

	return window.requestCount, window.startTime, nil
}

// Reset clears all rate limiting data
// This method is primarily used for testing
func (rl *RateLimiter) Reset() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	rl.clients = make(map[string]*ClientWindow)
}

// UpdateLimits updates the rate limiting parameters
func (rl *RateLimiter) UpdateLimits(maxRequests int, timeWindowSeconds int64) error {
	if maxRequests <= 0 || timeWindowSeconds <= 0 {
		return errors.New("invalid rate limit parameters")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	rl.maxRequests = maxRequests
	rl.timeWindowSeconds = timeWindowSeconds
	return nil
}

// GetLimits returns the current rate limiting parameters
func (rl *RateLimiter) GetLimits() (int, int64) {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	return rl.maxRequests, rl.timeWindowSeconds
}