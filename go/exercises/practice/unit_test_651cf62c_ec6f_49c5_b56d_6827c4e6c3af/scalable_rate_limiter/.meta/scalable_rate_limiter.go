package scalable_rate_limiter

import (
	"sync"
	"time"
)

type RateLimiter struct {
	globalLimit int
	window      time.Duration
	mu          sync.Mutex
	records     map[string]*record
}

type record struct {
	count       int
	windowStart time.Time
}

// NewRateLimiter creates a new instance of RateLimiter.
// globalLimit specifies the default maximum number of requests allowed per client per window.
// window specifies the duration of each rate limiting window.
func NewRateLimiter(globalLimit int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		globalLimit: globalLimit,
		window:      window,
		records:     make(map[string]*record),
	}
}

// AllowRequest processes a request for a specific client and endpoint.
// For a given (clientID, endpoint) pair, it allows up to a predefined number of requests in the current window.
// For "api_premium" endpoint, the limit is set to double the globalLimit.
func (rl *RateLimiter) AllowRequest(clientID, endpoint string) bool {
	// Determine the limit based on the endpoint.
	limit := rl.globalLimit
	if endpoint == "api_premium" {
		limit = rl.globalLimit * 2
	}
	
	key := clientID + "_" + endpoint
	now := time.Now()

	rl.mu.Lock()
	defer rl.mu.Unlock()

	rec, exists := rl.records[key]
	if !exists {
		// No record exists for the key; create one.
		rl.records[key] = &record{
			count:       1,
			windowStart: now,
		}
		return true
	}
	// If the time window has passed, reset the counter.
	if now.Sub(rec.windowStart) >= rl.window {
		rec.count = 1
		rec.windowStart = now
		return true
	}
	// If the count is below the limit, allow the request.
	if rec.count < limit {
		rec.count++
		return true
	}
	// Otherwise, reject the request.
	return false
}