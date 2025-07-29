package ratelimits

import (
	"sync"
	"time"
)

// UserLimits stores rate limiting data for a specific user
type UserLimits struct {
	requests     []int64  // Timestamp of requests in the current window
	lastUpdated  int64    // Last time the requests were updated
	mu           sync.Mutex
	gracePeriod  int64    // Duration in nanoseconds before allowing requests after limit exceeded
	lastRejected int64    // Timestamp of last rejected request
}

// RateLimiter implements the distributed rate limiting system
type RateLimiter struct {
	users     map[string]*UserLimits
	mu        sync.RWMutex
	windows   map[int]time.Duration // Time windows for different tiers
	limits    map[int]int          // Request limits for different tiers
}

// NewRateLimiter creates a new instance of RateLimiter
func NewRateLimiter() *RateLimiter {
	windows := make(map[int]time.Duration)
	limits := make(map[int]int)

	// Configure tier-specific windows and limits
	windows[1] = time.Second        // Tier 1: 1 second window 
	windows[2] = time.Second        // Tier 2: 1 second window
	windows[3] = time.Second        // Tier 3: 1 second window
	windows[4] = time.Second        // Tier 4: 1 second window
	windows[5] = time.Second        // Tier 5: 1 second window

	limits[1] = 5                   // Tier 1: 5 requests per second
	limits[2] = 10                  // Tier 2: 10 requests per second
	limits[3] = 15                  // Tier 3: 15 requests per second
	limits[4] = 20                  // Tier 4: 20 requests per second
	limits[5] = 25                  // Tier 5: 25 requests per second

	return &RateLimiter{
		users:   make(map[string]*UserLimits),
		windows: windows,
		limits:  limits,
	}
}

// AllowRequest determines if a request should be allowed based on the rate limit
func (rl *RateLimiter) AllowRequest(userID string, requestTimestamp int64, userTier int) bool {
	// Validate input parameters
	if userID == "" || userTier < 1 || userTier > 5 {
		return false
	}

	// Validate timestamp (shouldn't be too far in the past or future)
	now := time.Now().UnixNano()
	if abs(requestTimestamp-now) > int64(time.Hour) {
		return false
	}

	window, ok := rl.windows[userTier]
	if !ok {
		return false
	}

	limit, ok := rl.limits[userTier]
	if !ok {
		return false
	}

	rl.mu.Lock()
	user, exists := rl.users[userID]
	if !exists {
		user = &UserLimits{
			requests:    make([]int64, 0, limit),
			gracePeriod: int64(window) * 2, // Grace period is twice the window
		}
		rl.users[userID] = user
	}
	rl.mu.Unlock()

	user.mu.Lock()
	defer user.mu.Unlock()

	// Check if user is in grace period
	if user.lastRejected > 0 && requestTimestamp-user.lastRejected < user.gracePeriod {
		return false
	}

	// Clean up old requests
	windowStart := requestTimestamp - int64(window)
	validRequests := make([]int64, 0, len(user.requests))
	for _, req := range user.requests {
		if req >= windowStart {
			validRequests = append(validRequests, req)
		}
	}
	user.requests = validRequests

	// Check if user has exceeded their limit
	if len(user.requests) >= limit {
		user.lastRejected = requestTimestamp
		return false
	}

	// Add new request
	user.requests = append(user.requests, requestTimestamp)
	user.lastUpdated = requestTimestamp
	return true
}

// abs returns the absolute value of x
func abs(x int64) int64 {
	if x < 0 {
		return -x
	}
	return x
}

// cleanup periodically removes old data to prevent memory leaks
func (rl *RateLimiter) cleanup() {
	ticker := time.NewTicker(time.Hour)
	for range ticker.C {
		rl.mu.Lock()
		now := time.Now().UnixNano()
		for userID, user := range rl.users {
			user.mu.Lock()
			if now-user.lastUpdated > int64(24*time.Hour) {
				delete(rl.users, userID)
			}
			user.mu.Unlock()
		}
		rl.mu.Unlock()
	}
}