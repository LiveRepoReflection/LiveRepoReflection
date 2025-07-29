package dist_ratelimit

import (
	"sync"
	"time"
)

// RateLimiter is an interface for rate limiting.
type RateLimiter interface {
	Allow(clientID string) bool
}

// bucket holds the token bucket state for a client.
type bucket struct {
	tokens     float64
	lastRefill time.Time
}

// rateLimiter implements a token bucket rate limiter.
type rateLimiter struct {
	limit        float64
	window       time.Duration
	tokenRate    float64
	buckets      map[string]*bucket
	mu           sync.Mutex
	redisAddress string
}

// NewRateLimiter returns an instance of RateLimiter.
// If redisAddress is non-empty, it could be used to integrate a distributed system.
// For this implementation, an in-memory token bucket is used regardless of redisAddress.
func NewRateLimiter(limit int, window time.Duration, redisAddress string) RateLimiter {
	rl := &rateLimiter{
		limit:        float64(limit),
		window:       window,
		tokenRate:    float64(limit) / window.Seconds(),
		buckets:      make(map[string]*bucket),
		redisAddress: redisAddress,
	}
	return rl
}

// Allow checks if a request from the given clientID is allowed.
// It implements the token bucket algorithm, refilling tokens based on the elapsed time.
func (r *rateLimiter) Allow(clientID string) bool {
	now := time.Now()
	r.mu.Lock()
	b, exists := r.buckets[clientID]
	if !exists {
		b = &bucket{
			tokens:     r.limit,
			lastRefill: now,
		}
		r.buckets[clientID] = b
	}
	// Calculate elapsed time since last refill.
	elapsed := now.Sub(b.lastRefill).Seconds()
	// Refill tokens based on the elapsed time.
	b.tokens += elapsed * r.tokenRate
	if b.tokens > r.limit {
		b.tokens = r.limit
	}
	// Update the last refill time.
	b.lastRefill = now

	// If there is at least 1 token, allow the request.
	if b.tokens >= 1 {
		b.tokens -= 1
		r.mu.Unlock()
		return true
	}
	r.mu.Unlock()
	return false
}