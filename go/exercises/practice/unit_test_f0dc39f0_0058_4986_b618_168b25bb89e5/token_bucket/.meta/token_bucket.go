package tokenbucket

import (
	"sync"
	"time"
)

// bucket represents a token bucket for a single tenant
type bucket struct {
	mu         sync.Mutex
	tokens     float64
	capacity   int
	refillRate float64
	lastUpdate time.Time
}

// RateLimiter implements a thread-safe, multi-tenant rate limiter
type RateLimiter struct {
	mu      sync.RWMutex
	buckets map[string]*bucket
}

// NewRateLimiter creates a new multi-tenant rate limiter
func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		buckets: make(map[string]*bucket),
	}
}

// SetLimit configures the rate limit for a specific tenant
func (rl *RateLimiter) SetLimit(tenantID string, capacity int, refillRate float64) {
	if capacity < 0 || refillRate < 0 {
		return
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	rl.buckets[tenantID] = &bucket{
		tokens:     float64(capacity),
		capacity:   capacity,
		refillRate: refillRate,
		lastUpdate: time.Now(),
	}
}

// Allow checks if a tenant can consume the specified number of tokens
func (rl *RateLimiter) Allow(tenantID string, tokens int) bool {
	if tokens <= 0 {
		return false
	}

	rl.mu.RLock()
	b, exists := rl.buckets[tenantID]
	rl.mu.RUnlock()

	if !exists {
		return false
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	now := time.Now()
	timePassed := now.Sub(b.lastUpdate).Seconds()
	b.lastUpdate = now

	// Calculate token refill
	newTokens := b.tokens + b.refillRate*timePassed
	if newTokens > float64(b.capacity) {
		newTokens = float64(b.capacity)
	}
	b.tokens = newTokens

	// Check if we have enough tokens
	if b.tokens >= float64(tokens) {
		b.tokens -= float64(tokens)
		return true
	}

	return false
}

// RemoveTenant removes a tenant's rate limit configuration
func (rl *RateLimiter) RemoveTenant(tenantID string) {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	delete(rl.buckets, tenantID)
}

// GetTokens returns the current number of tokens for a tenant
func (rl *RateLimiter) GetTokens(tenantID string) float64 {
	rl.mu.RLock()
	b, exists := rl.buckets[tenantID]
	rl.mu.RUnlock()

	if !exists {
		return 0
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	now := time.Now()
	timePassed := now.Sub(b.lastUpdate).Seconds()
	
	newTokens := b.tokens + b.refillRate*timePassed
	if newTokens > float64(b.capacity) {
		newTokens = float64(b.capacity)
	}
	
	return newTokens
}

// GetTenantConfig returns the current configuration for a tenant
func (rl *RateLimiter) GetTenantConfig(tenantID string) (capacity int, refillRate float64, exists bool) {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	b, exists := rl.buckets[tenantID]
	if !exists {
		return 0, 0, false
	}

	return b.capacity, b.refillRate, true
}

// Reset resets all rate limiters to their initial state
func (rl *RateLimiter) Reset() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	for _, b := range rl.buckets {
		b.mu.Lock()
		b.tokens = float64(b.capacity)
		b.lastUpdate = time.Now()
		b.mu.Unlock()
	}
}