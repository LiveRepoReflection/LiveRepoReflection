package distrolimiter

import (
	"context"
	"errors"
	"sync"
	"time"
)

// RateLimiter represents a distributed rate limiter
type RateLimiter struct {
	ratePerSecond  int
	burstCapacity  int
	tokens         map[string]*tokenBucket
	mu            sync.RWMutex
	lastCleanup   time.Time
	cleanupPeriod time.Duration
}

// tokenBucket represents a token bucket for rate limiting
type tokenBucket struct {
	tokens        float64
	lastRefill    time.Time
	ratePerSecond int
	burstCapacity int
}

var (
	ErrInvalidRate          = errors.New("rate must be positive")
	ErrInvalidBurstCapacity = errors.New("burst capacity must be positive")
	ErrInvalidKey           = errors.New("key cannot be empty")
)

// NewRateLimiter creates a new distributed rate limiter
func NewRateLimiter(ratePerSecond, burstCapacity int) (*RateLimiter, error) {
	if ratePerSecond <= 0 {
		return nil, ErrInvalidRate
	}
	if burstCapacity <= 0 {
		return nil, ErrInvalidBurstCapacity
	}

	return &RateLimiter{
		ratePerSecond:  ratePerSecond,
		burstCapacity:  burstCapacity,
		tokens:         make(map[string]*tokenBucket),
		cleanupPeriod:  time.Hour,
		lastCleanup:    time.Now(),
	}, nil
}

// Allow checks if a request should be allowed based on the rate limit
func (rl *RateLimiter) Allow(ctx context.Context, key string) (bool, error) {
	if key == "" {
		return false, ErrInvalidKey
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	// Cleanup expired buckets
	rl.cleanup()

	bucket, exists := rl.tokens[key]
	if !exists {
		bucket = &tokenBucket{
			tokens:        float64(rl.burstCapacity),
			lastRefill:    time.Now(),
			ratePerSecond: rl.ratePerSecond,
			burstCapacity: rl.burstCapacity,
		}
		rl.tokens[key] = bucket
	}

	// Refill tokens based on time elapsed
	now := time.Now()
	elapsed := now.Sub(bucket.lastRefill).Seconds()
	bucket.tokens = min(float64(bucket.burstCapacity),
		bucket.tokens+float64(bucket.ratePerSecond)*elapsed)
	bucket.lastRefill = now

	if bucket.tokens >= 1 {
		bucket.tokens--
		return true, nil
	}

	return false, nil
}

// UpdateRate updates the rate limit for a specific key
func (rl *RateLimiter) UpdateRate(key string, newRate int) error {
	if newRate <= 0 {
		return ErrInvalidRate
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	if bucket, exists := rl.tokens[key]; exists {
		bucket.ratePerSecond = newRate
	} else {
		rl.tokens[key] = &tokenBucket{
			tokens:        float64(rl.burstCapacity),
			lastRefill:    time.Now(),
			ratePerSecond: newRate,
			burstCapacity: rl.burstCapacity,
		}
	}

	return nil
}

// cleanup removes expired token buckets
func (rl *RateLimiter) cleanup() {
	now := time.Now()
	if now.Sub(rl.lastCleanup) < rl.cleanupPeriod {
		return
	}

	for key, bucket := range rl.tokens {
		if now.Sub(bucket.lastRefill) > rl.cleanupPeriod {
			delete(rl.tokens, key)
		}
	}
	rl.lastCleanup = now
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}