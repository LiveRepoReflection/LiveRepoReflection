package tiered_limiter

import (
	"sync"
	"time"
)

type requestCounter struct {
	count    int
	lastTime time.Time
}

type RateLimiter struct {
	store      RateLimitStore
	counters   map[string]map[string]*requestCounter
	countersMu sync.RWMutex
	cleanup    *time.Ticker
	stop       chan struct{}
}

func NewRateLimiter(store RateLimitStore) *RateLimiter {
	rl := &RateLimiter{
		store:    store,
		counters: make(map[string]map[string]*requestCounter),
		cleanup:  time.NewTicker(time.Minute),
		stop:     make(chan struct{}),
	}

	go rl.cleanupExpiredCounters()
	return rl
}

func (rl *RateLimiter) Allow(userID, tier string) bool {
	limit, duration, err := rl.store.GetRateLimit(tier)
	if err != nil {
		return false
	}

	rl.countersMu.Lock()
	defer rl.countersMu.Unlock()

	now := time.Now()

	// Initialize user counters if needed
	if _, exists := rl.counters[tier]; !exists {
		rl.counters[tier] = make(map[string]*requestCounter)
	}

	counter, exists := rl.counters[tier][userID]
	if !exists {
		rl.counters[tier][userID] = &requestCounter{
			count:    1,
			lastTime: now,
		}
		return true
	}

	// Reset counter if window has expired
	if now.Sub(counter.lastTime) > duration {
		counter.count = 1
		counter.lastTime = now
		return true
	}

	// Check if within limit
	if counter.count < limit {
		counter.count++
		return true
	}

	return false
}

func (rl *RateLimiter) cleanupExpiredCounters() {
	for {
		select {
		case <-rl.cleanup.C:
			rl.countersMu.Lock()
			now := time.Now()
			for tier, users := range rl.counters {
				for userID, counter := range users {
					if now.Sub(counter.lastTime) > 24*time.Hour {
						delete(rl.counters[tier], userID)
					}
				}
				if len(rl.counters[tier]) == 0 {
					delete(rl.counters, tier)
				}
			}
			rl.countersMu.Unlock()
		case <-rl.stop:
			rl.cleanup.Stop()
			return
		}
	}
}

func (rl *RateLimiter) Stop() {
	close(rl.stop)
}