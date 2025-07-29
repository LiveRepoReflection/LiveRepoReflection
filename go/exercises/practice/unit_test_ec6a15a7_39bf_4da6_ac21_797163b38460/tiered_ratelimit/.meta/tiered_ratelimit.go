package tiered_ratelimit

import (
	"errors"
	"sync"
	"time"
)

type requestInfo struct {
	windowStart time.Time
	count       int
}

// RateLimiter implements a tiered rate limiter.
type RateLimiter struct {
	mu         sync.Mutex
	store      map[string]*requestInfo
	tierLimits map[string]int
}

// NewRateLimiter creates a new instance of RateLimiter.
func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		store: make(map[string]*requestInfo),
		tierLimits: map[string]int{
			"free":    10,
			"basic":   100,
			"premium": 1000,
			"admin":   -1, // -1 indicates no limit.
		},
	}
}

// Allow checks if a request identified by key and tier should be allowed.
func (rl *RateLimiter) Allow(key string, tier string) bool {
	if key == "" {
		return false
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	limit, exists := rl.tierLimits[tier]
	if !exists {
		return false
	}

	// Admin tier has no limits.
	if tier == "admin" {
		return true
	}

	now := time.Now()
	currentWindow := now.Truncate(time.Minute)
	identifier := tier + "_" + key

	ri, found := rl.store[identifier]
	if !found || currentWindow.After(ri.windowStart) {
		rl.store[identifier] = &requestInfo{
			windowStart: currentWindow,
			count:       1,
		}
		return true
	}

	if ri.count < limit {
		ri.count++
		return true
	}

	return false
}

// UpdateTierLimit dynamically updates the rate limit for a given tier.
func (rl *RateLimiter) UpdateTierLimit(tier string, newLimit int) error {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	_, exists := rl.tierLimits[tier]
	if !exists {
		return errors.New("unknown tier")
	}

	rl.tierLimits[tier] = newLimit
	return nil
}