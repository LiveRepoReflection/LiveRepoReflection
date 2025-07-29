package distributed_limit

import (
	"sync"
	"time"
)

// TokenBucket implements the token bucket algorithm for rate limiting
type TokenBucket struct {
	mu            sync.RWMutex
	store         Store
	defaultLimit  int
	defaultWindow time.Duration
	lastCleanup   time.Time
	cleanupInterval time.Duration
}

// bucket represents a token bucket for a specific identifier
type bucket struct {
	Tokens        float64   `json:"tokens"`
	LastRefill    time.Time `json:"lastRefill"`
	Limit         int       `json:"limit"`
	WindowSeconds int64     `json:"windowSeconds"`
}

// NewTokenBucket creates a new token bucket rate limiter
func NewTokenBucket(store Store, defaultLimit int, defaultWindow time.Duration) *TokenBucket {
	tb := &TokenBucket{
		store:         store,
		defaultLimit:  defaultLimit,
		defaultWindow: defaultWindow,
		lastCleanup:   time.Now(),
		cleanupInterval: 10 * time.Minute,
	}
	
	go tb.periodicCleanup()
	
	return tb
}

// periodicCleanup periodically cleans up expired buckets
func (tb *TokenBucket) periodicCleanup() {
	ticker := time.NewTicker(tb.cleanupInterval)
	defer ticker.Stop()
	
	for range ticker.C {
		tb.cleanup()
	}
}

// cleanup removes expired buckets from the store
func (tb *TokenBucket) cleanup() {
	tb.mu.Lock()
	defer tb.mu.Unlock()
	
	// Only perform cleanup if enough time has passed
	if time.Since(tb.lastCleanup) < tb.cleanupInterval {
		return
	}
	
	tb.lastCleanup = time.Now()
	tb.store.Cleanup()
}

// Allow checks if a request with the given identifier should be allowed
func (tb *TokenBucket) Allow(identifier string) (bool, time.Duration) {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	
	// Get or create bucket for this identifier
	b, err := tb.getBucket(identifier)
	if err != nil {
		// In case of error, we default to allowing the request
		return true, 0
	}

	// Calculate token refill since last request
	windowDuration := time.Duration(b.WindowSeconds) * time.Second
	tokenRate := float64(b.Limit) / float64(windowDuration.Seconds())
	
	timePassed := now.Sub(b.LastRefill).Seconds()
	newTokens := timePassed * tokenRate
	
	// Add new tokens up to the limit
	b.Tokens = min(float64(b.Limit), b.Tokens+newTokens)
	b.LastRefill = now
	
	// Check if we have enough tokens for this request
	if b.Tokens >= 1.0 {
		b.Tokens--
		err := tb.storeBucket(identifier, b)
		if err != nil {
			return true, 0
		}
		return true, 0
	}
	
	// Calculate time until next token is available
	waitTime := time.Duration((1.0 - b.Tokens) / tokenRate * float64(time.Second))
	err = tb.storeBucket(identifier, b)
	if err != nil {
		return true, 0
	}
	
	return false, waitTime
}

// ConfigureLimit sets a custom limit and window for a specific identifier
func (tb *TokenBucket) ConfigureLimit(identifier string, limit int, window time.Duration) {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	b, err := tb.getBucket(identifier)
	if err != nil {
		// Create a new bucket with full tokens
		b = &bucket{
			Tokens:        float64(limit),
			LastRefill:    time.Now(),
			Limit:         limit,
			WindowSeconds: int64(window.Seconds()),
		}
	} else {
		// Adjust token count proportionally when changing limits
		oldLimit := b.Limit
		oldTokens := b.Tokens
		
		if oldLimit > 0 {
			b.Tokens = (oldTokens / float64(oldLimit)) * float64(limit)
		} else {
			b.Tokens = float64(limit)
		}
		
		b.Limit = limit
		b.WindowSeconds = int64(window.Seconds())
	}

	tb.storeBucket(identifier, b)
}

// GetLimit retrieves the current limit and window for a specific identifier
func (tb *TokenBucket) GetLimit(identifier string) (int, time.Duration) {
	tb.mu.RLock()
	defer tb.mu.RUnlock()

	b, err := tb.getBucket(identifier)
	if err != nil || b == nil {
		return tb.defaultLimit, tb.defaultWindow
	}

	return b.Limit, time.Duration(b.WindowSeconds) * time.Second
}

// getBucket retrieves a bucket for the given identifier from the store
func (tb *TokenBucket) getBucket(identifier string) (*bucket, error) {
	data, err := tb.store.Get(identifier)
	if err != nil {
		if err == ErrKeyNotFound {
			// Create a new bucket with default settings and full tokens
			return &bucket{
				Tokens:        float64(tb.defaultLimit),
				LastRefill:    time.Now(),
				Limit:         tb.defaultLimit,
				WindowSeconds: int64(tb.defaultWindow.Seconds()),
			}, nil
		}
		return nil, err
	}

	var b bucket
	if err := decode(data, &b); err != nil {
		return nil, err
	}
	
	return &b, nil
}

// storeBucket stores a bucket for the given identifier in the store
func (tb *TokenBucket) storeBucket(identifier string, b *bucket) error {
	data, err := encode(b)
	if err != nil {
		return err
	}
	
	return tb.store.Set(identifier, data, time.Duration(b.WindowSeconds)*time.Second*2)
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}