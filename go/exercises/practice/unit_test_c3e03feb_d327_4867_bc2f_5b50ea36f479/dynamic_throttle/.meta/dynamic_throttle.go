package dynamic_throttle

import (
	"sync"
	"time"
)

type RateLimiter struct {
	maxRequests       int
	windowDuration    time.Duration
	currentMaxRequests int
	throttleThreshold int
	throttlePercent   int
	clientRequests    map[string][]time.Time
	mu               sync.Mutex
	nowFunc          func() time.Time
}

func NewRateLimiter(maxRequests int, windowDuration time.Duration) *RateLimiter {
	if windowDuration <= 0 {
		panic("window duration must be positive")
	}

	return &RateLimiter{
		maxRequests:       maxRequests,
		currentMaxRequests: maxRequests,
		windowDuration:    windowDuration,
		throttleThreshold: 80,
		throttlePercent:   50,
		clientRequests:    make(map[string][]time.Time),
		nowFunc:          time.Now,
	}
}

func (rl *RateLimiter) AllowRequest(clientID string, systemLoad int) bool {
	if clientID == "" {
		return false
	}

	rl.UpdateSystemLoad(systemLoad)

	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := rl.nowFunc()
	windowStart := now.Add(-rl.windowDuration)

	// Clean up old requests
	var validRequests []time.Time
	for _, t := range rl.clientRequests[clientID] {
		if t.After(windowStart) {
			validRequests = append(validRequests, t)
		}
	}

	if len(validRequests) >= rl.currentMaxRequests {
		return false
	}

	validRequests = append(validRequests, now)
	rl.clientRequests[clientID] = validRequests
	return true
}

func (rl *RateLimiter) UpdateSystemLoad(load int) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if load >= rl.throttleThreshold {
		// Apply throttling
		rl.currentMaxRequests = rl.maxRequests * rl.throttlePercent / 100
	} else {
		// Return to normal
		rl.currentMaxRequests = rl.maxRequests
	}
}

func (rl *RateLimiter) SetThrottleConfig(threshold, percent int) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if threshold < 0 || threshold > 100 {
		panic("threshold must be between 0 and 100")
	}
	if percent < 0 || percent > 100 {
		panic("percent must be between 0 and 100")
	}

	rl.throttleThreshold = threshold
	rl.throttlePercent = percent
}