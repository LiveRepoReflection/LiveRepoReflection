package adaptive_rate_limit

import (
	"sync"
	"time"
)

type clientInfo struct {
	count       int
	windowStart time.Time
}

type RateLimiter struct {
	baseLimit        int
	window           time.Duration
	globalAdjustment float64
	clientLimits     map[string]int
	clientRecords    map[string]*clientInfo
	mu               sync.Mutex
}

func NewRateLimiter(baseLimit int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		baseLimit:        baseLimit,
		window:           window,
		globalAdjustment: 1.0,
		clientLimits:     make(map[string]int),
		clientRecords:    make(map[string]*clientInfo),
	}
}

func (rl *RateLimiter) Allow(clientID string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	ci, exists := rl.clientRecords[clientID]
	if !exists {
		ci = &clientInfo{
			count:       0,
			windowStart: now,
		}
		rl.clientRecords[clientID] = ci
	}

	if now.Sub(ci.windowStart) >= rl.window {
		ci.count = 0
		ci.windowStart = now
	}

	effectiveLimit := rl.effectiveLimit(clientID)
	if ci.count < effectiveLimit {
		ci.count++
		return true
	}
	return false
}

func (rl *RateLimiter) effectiveLimit(clientID string) int {
	if override, ok := rl.clientLimits[clientID]; ok {
		return override
	}
	limit := int(float64(rl.baseLimit) * rl.globalAdjustment)
	if limit < 1 {
		limit = 1
	}
	return limit
}

func (rl *RateLimiter) UpdateBackendMetrics(latency time.Duration, errorRate float64) {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	if latency > 200*time.Millisecond || errorRate > 0.3 {
		rl.globalAdjustment = 0.5
	} else if latency < 100*time.Millisecond && errorRate < 0.1 {
		rl.globalAdjustment = 1.0
	}
}

func (rl *RateLimiter) UpdateClientRateLimit(clientID string, newLimit int) {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	rl.clientLimits[clientID] = newLimit
	if ci, exists := rl.clientRecords[clientID]; exists {
		ci.count = 0
		ci.windowStart = time.Now()
	}
}