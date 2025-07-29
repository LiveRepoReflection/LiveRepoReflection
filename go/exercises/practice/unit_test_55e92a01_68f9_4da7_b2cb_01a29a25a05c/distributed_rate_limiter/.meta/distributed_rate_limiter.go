package distributed_rate_limiter

import (
	"sync"
	"time"
)

type userRecord struct {
	timestamps []time.Time
}

// RateLimiter handles rate limiting across users.
type RateLimiter struct {
	mu    sync.Mutex
	users map[string]*userRecord
}

// NewRateLimiter creates a new RateLimiter instance.
func NewRateLimiter() *RateLimiter {
	rl := &RateLimiter{
		users: make(map[string]*userRecord),
	}
	return rl
}

// Allow checks if a request for a given user is allowed using the specified limit and window.
// It cleans up expired request timestamps and returns true if the user is within their quota.
func (rl *RateLimiter) Allow(userID string, limit int, window time.Duration) bool {
	now := time.Now()
	rl.mu.Lock()
	defer rl.mu.Unlock()

	rec, exists := rl.users[userID]
	if !exists {
		rec = &userRecord{
			timestamps: make([]time.Time, 0, limit),
		}
		rl.users[userID] = rec
	}

	// Remove timestamps outside of the current window.
	cutoff := now.Add(-window)
	validRequests := rec.timestamps[:0]
	for _, ts := range rec.timestamps {
		if ts.After(cutoff) {
			validRequests = append(validRequests, ts)
		}
	}
	rec.timestamps = validRequests

	// Check if within allowed limit.
	if len(rec.timestamps) < limit {
		rec.timestamps = append(rec.timestamps, now)
		return true
	}
	return false
}

var globalLimiter = NewRateLimiter()

// Allow is the package-level function that wraps the global limiter.
func Allow(userID string, limit int, window time.Duration) bool {
	return globalLimiter.Allow(userID, limit, window)
}