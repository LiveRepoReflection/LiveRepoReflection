package rate_limit

import (
	"sync"
	"testing"
	"time"
)

// TestAllowUnderLimit checks that requests under the limit are allowed.
func TestAllowUnderLimit(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          5,
		Window:         2 * time.Second,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}
	defer rl.Close()

	key := "user1"
	for i := 0; i < config.Limit; i++ {
		allowed, err := rl.Allow(key)
		if err != nil {
			t.Fatalf("Allow returned error: %v", err)
		}
		if !allowed {
			t.Fatalf("Expected request %d to be allowed for key %s", i+1, key)
		}
	}
}

// TestAllowOverLimit verifies that requests over the limit are disallowed.
func TestAllowOverLimit(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          3,
		Window:         1 * time.Second,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}
	defer rl.Close()

	key := "user2"
	for i := 0; i < config.Limit; i++ {
		allowed, err := rl.Allow(key)
		if err != nil {
			t.Fatalf("Unexpected error on request %d: %v", i+1, err)
		}
		if !allowed {
			t.Fatalf("Expected request %d to be allowed for key %s", i+1, key)
		}
	}
	// Next request should be disallowed.
	allowed, err := rl.Allow(key)
	if err != nil {
		t.Fatalf("Unexpected error on extra request: %v", err)
	}
	if allowed {
		t.Fatalf("Expected request over limit for key %s to be disallowed", key)
	}
}

// TestReset verifies that the rate limiter resets the counter for a given key.
func TestReset(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          2,
		Window:         1 * time.Second,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}
	defer rl.Close()

	key := "user3"
	for i := 0; i < config.Limit; i++ {
		allowed, err := rl.Allow(key)
		if err != nil {
			t.Fatalf("Unexpected error on request %d: %v", i+1, err)
		}
		if !allowed {
			t.Fatalf("Expected request %d to be allowed for key %s", i+1, key)
		}
	}
	// A further request should be blocked.
	allowed, err := rl.Allow(key)
	if err != nil {
		t.Fatalf("Unexpected error on extra request: %v", err)
	}
	if allowed {
		t.Fatalf("Expected request over limit for key %s to be disallowed", key)
	}
	// Reset the key.
	err = rl.Reset(key)
	if err != nil {
		t.Fatalf("Failed to reset rate limiter for key %s: %v", key, err)
	}
	// After reset, a new request should be allowed.
	allowed, err = rl.Allow(key)
	if err != nil {
		t.Fatalf("Unexpected error after reset: %v", err)
	}
	if !allowed {
		t.Fatalf("Expected request after reset for key %s to be allowed", key)
	}
}

// TestAllowAfterWindowExpiration ensures that after the time window has expired, requests are allowed again.
func TestAllowAfterWindowExpiration(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          2,
		Window:         500 * time.Millisecond,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}
	defer rl.Close()

	key := "user4"
	for i := 0; i < config.Limit; i++ {
		allowed, err := rl.Allow(key)
		if err != nil {
			t.Fatalf("Unexpected error on request %d: %v", i+1, err)
		}
		if !allowed {
			t.Fatalf("Expected request %d to be allowed for key %s", i+1, key)
		}
	}

	// Extra call should be disallowed.
	allowed, err := rl.Allow(key)
	if err != nil {
		t.Fatalf("Unexpected error on extra request: %v", err)
	}
	if allowed {
		t.Fatalf("Expected request over limit for key %s to be disallowed", key)
	}

	// Wait for the window to expire.
	time.Sleep(config.Window)
	allowed, err = rl.Allow(key)
	if err != nil {
		t.Fatalf("Unexpected error after window expiration: %v", err)
	}
	if !allowed {
		t.Fatalf("Expected request after window expiration for key %s to be allowed", key)
	}
}

// TestConcurrency tests the rate limiter under concurrent requests.
func TestConcurrency(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          50,
		Window:         2 * time.Second,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}
	defer rl.Close()

	key := "user5"
	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0
	totalRequests := 100

	wg.Add(totalRequests)
	for i := 0; i < totalRequests; i++ {
		go func() {
			defer wg.Done()
			allowed, err := rl.Allow(key)
			if err != nil {
				t.Errorf("Unexpected error in concurrent Allow: %v", err)
				return
			}
			if allowed {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount != config.Limit {
		t.Fatalf("Expected allowed count to be %d, got %d", config.Limit, allowedCount)
	}
}

// TestClose verifies that after closing the rate limiter, further operations return an error.
func TestClose(t *testing.T) {
	config := RateLimiterConfig{
		Limit:          5,
		Window:         1 * time.Second,
		StorageType:    "inmemory",
		StorageAddress: "",
	}
	rl, err := NewRateLimiter(config)
	if err != nil {
		t.Fatalf("Failed to create RateLimiter: %v", err)
	}

	err = rl.Close()
	if err != nil {
		t.Fatalf("Failed to close RateLimiter: %v", err)
	}
	// After closing, further Allow calls should return an error.
	_, err = rl.Allow("user6")
	if err == nil {
		t.Fatalf("Expected error after calling Allow on a closed RateLimiter")
	}
}