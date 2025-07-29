package dist_limit

import (
	"sync"
)

// counter holds the state for a particular resource.
type counter struct {
	windowStart int64
	count       int
}

// RateLimiter implements an in-memory distributed rate limiter.
// It controls the number of allowed requests per fixed time window.
// For positive window values, it uses a reset mechanism based on elapsed seconds.
// For zero or negative window values, it treats calls with the same timestamp as the same instantaneous window.
type RateLimiter struct {
	limit    int         // maximum allowed requests per window period
	window   int64       // time window in seconds; if <= 0, treat each distinct timestamp as separate
	mu       sync.Mutex  // protects the counters map
	counters map[string]*counter
}

// NewRateLimiter initializes and returns a new RateLimiter.
// The "limit" parameter specifies the maximum allowed requests per window period.
// The "window" parameter specifies the length of the window in seconds. When window <= 0,
// the limiter treats all calls with the same timestamp as belonging to the same instantaneous window.
func NewRateLimiter(limit int, window int64) *RateLimiter {
	return &RateLimiter{
		limit:    limit,
		window:   window,
		counters: make(map[string]*counter),
	}
}

// Allow determines whether a request from a given resource at a given timestamp is permitted.
// It returns true if the request is allowed or false if it should be rate-limited.
func (rl *RateLimiter) Allow(resource string, ts int64) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	rec, exists := rl.counters[resource]
	if !exists {
		// First request for this resource, create a counter.
		rl.counters[resource] = &counter{
			windowStart: ts,
			count:       1,
		}
		// If limit is set to zero, no requests should be allowed.
		return rl.limit != 0
	}

	if rl.window > 0 {
		// Use fixed-window logic with timer-based reset.
		if ts-rec.windowStart >= rl.window {
			// Reset the window if the current timestamp is outside the current window.
			rec.windowStart = ts
			rec.count = 1
			return true
		}
		if rec.count < rl.limit {
			rec.count++
			return true
		}
		return false
	}

	// For window <= 0, treat each distinct timestamp as a new window.
	if ts != rec.windowStart {
		rec.windowStart = ts
		rec.count = 1
		return true
	}
	if rec.count < rl.limit {
		rec.count++
		return true
	}
	return false
}