package ratelimiter

import (
	"errors"
	"sync"
	"time"
)

// ClientLimitConfig stores rate limit configuration for a client
type ClientLimitConfig struct {
	RequestLimit  int
	TimeWindowSec int
}

// ClientState tracks the current state of a client's rate limiting
type ClientState struct {
	requests    []time.Time
	lastCleanup time.Time
	mu          sync.Mutex
}

// RateLimiter implements a distributed rate limiter
type RateLimiter struct {
	clients     map[string]*ClientState
	configs     map[string]*ClientLimitConfig
	globalMu    sync.RWMutex
	metrics     *Metrics
}

// Metrics tracks various rate limiter statistics
type Metrics struct {
	totalRequests     int64
	allowedRequests   int64
	rejectedRequests  int64
	mu               sync.Mutex
}

// NewRateLimiter creates a new instance of RateLimiter
func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		clients: make(map[string]*ClientState),
		configs: make(map[string]*ClientLimitConfig),
		metrics: &Metrics{},
	}
}

// SetLimit sets or updates the rate limit for a client
func (rl *RateLimiter) SetLimit(clientID string, requestLimit, timeWindowSec int) error {
	if requestLimit < 0 || timeWindowSec <= 0 {
		return errors.New("invalid rate limit parameters")
	}

	rl.globalMu.Lock()
	defer rl.globalMu.Unlock()

	// Update or create config
	rl.configs[clientID] = &ClientLimitConfig{
		RequestLimit:  requestLimit,
		TimeWindowSec: timeWindowSec,
	}

	// Initialize client state if needed
	if _, exists := rl.clients[clientID]; !exists {
		rl.clients[clientID] = &ClientState{
			requests:    make([]time.Time, 0, requestLimit),
			lastCleanup: time.Now(),
		}
	}

	return nil
}

// Allow checks if a request should be allowed based on the rate limit
func (rl *RateLimiter) Allow(clientID string) bool {
	rl.metrics.mu.Lock()
	rl.metrics.totalRequests++
	rl.metrics.mu.Unlock()

	rl.globalMu.RLock()
	config, configExists := rl.configs[clientID]
	client, clientExists := rl.clients[clientID]
	rl.globalMu.RUnlock()

	if !configExists || !clientExists {
		// If no configuration exists, allow the request in degraded mode
		rl.metrics.mu.Lock()
		rl.metrics.allowedRequests++
		rl.metrics.mu.Unlock()
		return true
	}

	client.mu.Lock()
	defer client.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-time.Duration(config.TimeWindowSec) * time.Second)

	// Cleanup old requests if needed
	if now.Sub(client.lastCleanup) > time.Second {
		client.cleanup(windowStart)
		client.lastCleanup = now
	}

	// Check if we're at the limit
	if len(client.requests) >= config.RequestLimit {
		rl.metrics.mu.Lock()
		rl.metrics.rejectedRequests++
		rl.metrics.mu.Unlock()
		return false
	}

	// Allow the request
	client.requests = append(client.requests, now)
	rl.metrics.mu.Lock()
	rl.metrics.allowedRequests++
	rl.metrics.mu.Unlock()
	return true
}

// cleanup removes requests outside the current time window
func (cs *ClientState) cleanup(windowStart time.Time) {
	var valid []time.Time
	for _, t := range cs.requests {
		if t.After(windowStart) {
			valid = append(valid, t)
		}
	}
	cs.requests = valid
}

// GetMetrics returns current metrics
func (rl *RateLimiter) GetMetrics() (int64, int64, int64) {
	rl.metrics.mu.Lock()
	defer rl.metrics.mu.Unlock()
	return rl.metrics.totalRequests, rl.metrics.allowedRequests, rl.metrics.rejectedRequests
}

// RemoveClient removes a client's rate limit configuration and state
func (rl *RateLimiter) RemoveClient(clientID string) {
	rl.globalMu.Lock()
	defer rl.globalMu.Unlock()
	
	delete(rl.configs, clientID)
	delete(rl.clients, clientID)
}

// GetActiveClients returns the number of clients with active configurations
func (rl *RateLimiter) GetActiveClients() int {
	rl.globalMu.RLock()
	defer rl.globalMu.RUnlock()
	return len(rl.configs)
}

// ResetMetrics resets all metrics counters to zero
func (rl *RateLimiter) ResetMetrics() {
	rl.metrics.mu.Lock()
	defer rl.metrics.mu.Unlock()
	
	rl.metrics.totalRequests = 0
	rl.metrics.allowedRequests = 0
	rl.metrics.rejectedRequests = 0
}