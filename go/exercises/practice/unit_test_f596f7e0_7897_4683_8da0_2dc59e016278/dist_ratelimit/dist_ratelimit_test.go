package dist_ratelimit

import (
	"sync"
	"testing"
	"time"
)

// Assume that the RateLimiter interface and NewRateLimiter function are defined in the dist_ratelimit package.
// The RateLimiter interface is defined as:
//    type RateLimiter interface {
//        Allow(clientID string) bool
//    }
// And NewRateLimiter is assumed to initialize an instance with the following signature:
//    func NewRateLimiter(limit int, window time.Duration, redisAddress string) RateLimiter

func TestRateLimiterAllowSingleClient(t *testing.T) {
	limit := 5
	window := 1 * time.Second
	// Initialize the rate limiter. For testing purposes, redisAddress is empty.
	rl := NewRateLimiter(limit, window, "")
	clientID := "client1"

	// Allow exactly 'limit' number of requests.
	for i := 0; i < limit; i++ {
		if !rl.Allow(clientID) {
			t.Errorf("expected request %d to be allowed", i+1)
		}
	}

	// The next request should be rejected.
	if rl.Allow(clientID) {
		t.Errorf("expected request number %d to be rejected", limit+1)
	}

	// Wait for the window to pass to check if the rate limiter resets.
	time.Sleep(window)

	// After the window, the request should be allowed again.
	if !rl.Allow(clientID) {
		t.Errorf("expected rate limiter to reset after window, but request was rejected")
	}
}

func TestRateLimiterMultipleClients(t *testing.T) {
	limit := 3
	window := 1 * time.Second
	rl := NewRateLimiter(limit, window, "")
	clients := []string{"client1", "client2", "client3"}

	// Each client should be allowed up to 'limit' requests independently.
	for _, client := range clients {
		for i := 0; i < limit; i++ {
			if !rl.Allow(client) {
				t.Errorf("expected request %d for %s to be allowed", i+1, client)
			}
		}
		// Next request should be rejected.
		if rl.Allow(client) {
			t.Errorf("expected request for %s to be rejected after reaching limit", client)
		}
	}
}

func TestRateLimiterConcurrency(t *testing.T) {
	limit := 100
	window := 2 * time.Second
	rl := NewRateLimiter(limit, window, "")
	clientID := "concurrent_client"
	var wg sync.WaitGroup
	allowedCount := 0
	mu := sync.Mutex{}

	totalRequests := limit * 2
	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.Allow(clientID) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount > limit {
		t.Errorf("allowedCount %d exceeds limit %d", allowedCount, limit)
	}
}

func TestRateLimiterReset(t *testing.T) {
	limit := 2
	window := 500 * time.Millisecond
	rl := NewRateLimiter(limit, window, "")
	clientID := "reset_client"

	// Use up the limit.
	for i := 0; i < limit; i++ {
		if !rl.Allow(clientID) {
			t.Errorf("expected request %d to be allowed", i+1)
		}
	}

	// Next request should be rejected.
	if rl.Allow(clientID) {
		t.Errorf("expected request to be rejected after limit is reached")
	}

	// Wait for the window to expire.
	time.Sleep(window)

	// After the window, the limiter should allow new requests.
	if !rl.Allow(clientID) {
		t.Errorf("expected rate limiter to reset after window, but request was rejected")
	}
}