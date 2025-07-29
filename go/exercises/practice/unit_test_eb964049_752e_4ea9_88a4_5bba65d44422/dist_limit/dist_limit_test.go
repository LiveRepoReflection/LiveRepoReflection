package dist_limit

import (
	"sync"
	"testing"
	"time"
)

func TestAllowWithinLimit(t *testing.T) {
	// Create a rate limiter allowing 3 requests per 1 second.
	rl := NewRateLimiter(3, 1)
	resource := "user1"
	now := time.Now().Unix()

	// The first three requests should be allowed.
	for i := 0; i < 3; i++ {
		if !rl.Allow(resource, now) {
			t.Errorf("Expected request %d to be allowed, but it was rejected", i+1)
		}
	}
	// The fourth request should be rejected.
	if rl.Allow(resource, now) {
		t.Errorf("Expected the fourth request to be rejected after reaching the rate limit")
	}
}

func TestAllowAfterWindow(t *testing.T) {
	// Create a rate limiter allowing 2 requests per 1 second.
	rl := NewRateLimiter(2, 1)
	resource := "user2"
	now := time.Now().Unix()

	// Two consecutive requests at the same timestamp.
	if !rl.Allow(resource, now) {
		t.Errorf("Expected the first request to be allowed")
	}
	if !rl.Allow(resource, now) {
		t.Errorf("Expected the second request to be allowed")
	}
	// Simulate passage of time: after waiting for two seconds, the window should have expired.
	later := now + 2
	if !rl.Allow(resource, later) {
		t.Errorf("Expected request after time window to be allowed")
	}
}

func TestMultipleResources(t *testing.T) {
	// Create a rate limiter allowing 2 requests per 1 second.
	rl := NewRateLimiter(2, 1)
	now := time.Now().Unix()
	users := []string{"userA", "userB", "userC"}

	for _, user := range users {
		// Each user makes two allowed requests.
		if !rl.Allow(user, now) {
			t.Errorf("Expected first request for %s to be allowed", user)
		}
		if !rl.Allow(user, now) {
			t.Errorf("Expected second request for %s to be allowed", user)
		}
		// Third request should be rejected.
		if rl.Allow(user, now) {
			t.Errorf("Expected third request for %s to be rejected", user)
		}
	}
}

func TestConcurrency(t *testing.T) {
	// Create a rate limiter allowing 100 requests per 1 second.
	rl := NewRateLimiter(100, 1)
	resource := "concurrentUser"
	now := time.Now().Unix()

	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0
	totalRequests := 200

	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.Allow(resource, now) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount != 100 {
		t.Errorf("Expected 100 allowed requests for concurrent access, got %d", allowedCount)
	}
}

func TestEdgeCaseZeroLimit(t *testing.T) {
	// Create a rate limiter with a limit of 0 requests per 1 second.
	rl := NewRateLimiter(0, 1)
	resource := "userZero"
	now := time.Now().Unix()

	// All requests should be rejected.
	if rl.Allow(resource, now) {
		t.Errorf("Expected the request to be rejected for a zero limit rate limiter")
	}
}

func TestEdgeCaseNegativeWindow(t *testing.T) {
	// Create a rate limiter with a negative time window.
	// In this hypothetical behavior, treat negative window as an immediate reset between calls,
	// resulting in allowed requests up to the configured limit per instantaneous timestamp.
	rl := NewRateLimiter(5, -1)
	resource := "userNeg"
	now := time.Now().Unix()

	allowed := 0
	for i := 0; i < 10; i++ {
		if rl.Allow(resource, now) {
			allowed++
		}
	}
	if allowed != 5 {
		t.Errorf("Expected 5 allowed requests for negative window, got %d", allowed)
	}
}