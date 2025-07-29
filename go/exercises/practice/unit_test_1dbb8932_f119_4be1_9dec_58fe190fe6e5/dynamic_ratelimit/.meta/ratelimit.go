package ratelimit

import (
	"errors"
	"sync"
	"time"
)

type tokenBucket struct {
	rate         float64       // tokens per second
	capacity     float64       // max tokens
	tokens       float64       // current tokens
	lastUpdate   time.Time     // last token update
	mu           sync.Mutex    // protects the bucket
}

type RateLimiter struct {
	buckets map[string]*tokenBucket
	mu      sync.RWMutex
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		buckets: make(map[string]*tokenBucket),
	}
}

func (rl *RateLimiter) CreateBucket(bucketID string, rateLimit int, burstSize int) error {
	if bucketID == "" {
		return errors.New("bucket ID cannot be empty")
	}
	if rateLimit <= 0 {
		return errors.New("rate limit must be positive")
	}
	if burstSize <= 0 {
		return errors.New("burst size must be positive")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	if _, exists := rl.buckets[bucketID]; exists {
		return errors.New("bucket already exists")
	}

	rl.buckets[bucketID] = &tokenBucket{
		rate:       float64(rateLimit),
		capacity:   float64(burstSize),
		tokens:     float64(burstSize),
		lastUpdate: time.Now(),
	}

	return nil
}

func (rl *RateLimiter) UpdateBucket(bucketID string, rateLimit int, burstSize int) error {
	if rateLimit <= 0 {
		return errors.New("rate limit must be positive")
	}
	if burstSize <= 0 {
		return errors.New("burst size must be positive")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	bucket, exists := rl.buckets[bucketID]
	if !exists {
		return errors.New("bucket does not exist")
	}

	bucket.mu.Lock()
	defer bucket.mu.Unlock()

	bucket.rate = float64(rateLimit)
	bucket.capacity = float64(burstSize)
	// Don't modify current tokens or lastUpdate to maintain rate limiting continuity

	return nil
}

func (rl *RateLimiter) DeleteBucket(bucketID string) error {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if _, exists := rl.buckets[bucketID]; !exists {
		return errors.New("bucket does not exist")
	}

	delete(rl.buckets, bucketID)
	return nil
}

func (rl *RateLimiter) Allow(bucketID string) bool {
	rl.mu.RLock()
	bucket, exists := rl.buckets[bucketID]
	rl.mu.RUnlock()

	if !exists {
		return false
	}

	bucket.mu.Lock()
	defer bucket.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(bucket.lastUpdate).Seconds()
	bucket.lastUpdate = now

	// Add tokens based on elapsed time
	bucket.tokens += elapsed * bucket.rate
	if bucket.tokens > bucket.capacity {
		bucket.tokens = bucket.capacity
	}

	// Check if we can take a token
	if bucket.tokens >= 1 {
		bucket.tokens -= 1
		return true
	}

	return false
}