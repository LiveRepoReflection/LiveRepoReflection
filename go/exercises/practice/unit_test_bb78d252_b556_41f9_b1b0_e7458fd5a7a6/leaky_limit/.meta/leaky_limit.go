package leaky_limit

import (
	"sync"
	"time"
)

type Bucket struct {
	tokens     float64
	lastUpdate time.Time
}

type Limiter struct {
	capacity int
	leakRate float64
	buckets  map[string]*Bucket
	mu       sync.Mutex
}

func NewLimiter(capacity int, leakRate int) *Limiter {
	return &Limiter{
		capacity: capacity,
		leakRate: float64(leakRate),
		buckets:  make(map[string]*Bucket),
	}
}

func (l *Limiter) Allow(clientID string, quantity int) bool {
	l.mu.Lock()
	defer l.mu.Unlock()

	now := time.Now()
	bucket, exists := l.buckets[clientID]
	if !exists {
		// Initialize the bucket with full capacity tokens
		bucket = &Bucket{
			tokens:     float64(l.capacity),
			lastUpdate: now,
		}
		l.buckets[clientID] = bucket
	} else {
		// Refill tokens based on elapsed time
		elapsed := now.Sub(bucket.lastUpdate).Seconds()
		bucket.tokens += elapsed * l.leakRate
		if bucket.tokens > float64(l.capacity) {
			bucket.tokens = float64(l.capacity)
		}
		bucket.lastUpdate = now
	}

	if bucket.tokens >= float64(quantity) {
		bucket.tokens -= float64(quantity)
		return true
	}
	return false
}