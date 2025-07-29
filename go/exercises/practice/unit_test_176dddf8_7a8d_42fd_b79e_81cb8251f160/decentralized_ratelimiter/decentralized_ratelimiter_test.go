package decentralized_ratelimiter

import (
	"sync"
	"testing"
	"time"
)

// Assume that the RateLimiter struct and its methods are defined in the implementation.
// The assumed API is as follows:
//   NewRateLimiter(rate int, window time.Duration, nodes int) *RateLimiter
//   (rl *RateLimiter) AllowRequest(userID uint64) bool
//   (rl *RateLimiter) AdjustRateLimit(newRate int)
// For testing purposes, we simulate the behavior of the limiter using time.Sleep to allow the time window to expire.

func TestAllowWithinLimit(t *testing.T) {
	// Setup: Allow maximum 3 requests per 1 second window and simulate 5 nodes.
	rate := 3
	window := 1 * time.Second
	nodes := 5
	rl := NewRateLimiter(rate, window, nodes)

	userID := uint64(12345)
	// First 3 requests should be allowed.
	for i := 0; i < rate; i++ {
		if !rl.AllowRequest(userID) {
			t.Fatalf("Request %d: expected allowed but got denied", i+1)
		}
	}

	// 4th request in same window should be denied.
	if rl.AllowRequest(userID) {
		t.Fatalf("Request 4: expected denied but got allowed")
	}
}

func TestResetAfterTimeWindow(t *testing.T) {
	// Setup: Allow maximum 2 requests per 500ms and simulate 3 nodes.
	rate := 2
	window := 500 * time.Millisecond
	nodes := 3
	rl := NewRateLimiter(rate, window, nodes)

	userID := uint64(54321)
	// Use up the limit.
	for i := 0; i < rate; i++ {
		if !rl.AllowRequest(userID) {
			t.Fatalf("Request %d: expected allowed but got denied", i+1)
		}
	}
	if rl.AllowRequest(userID) {
		t.Fatalf("Extra request: expected denied but got allowed")
	}

	// Wait for the time window to expire.
	time.Sleep(window + 100*time.Millisecond)

	// After time window, requests should be allowed again.
	if !rl.AllowRequest(userID) {
		t.Fatalf("After window expired: expected allowed but got denied")
	}
}

func TestMultipleUsers(t *testing.T) {
	// Setup: Allow maximum 4 requests per 1 second window.
	rate := 4
	window := 1 * time.Second
	nodes := 4
	rl := NewRateLimiter(rate, window, nodes)

	// Test with multiple users concurrently.
	userIDs := []uint64{1001, 1002, 1003, 1004, 1005}
	for _, uid := range userIDs {
		// Each user should be able to perform 'rate' allowed requests.
		for i := 0; i < rate; i++ {
			if !rl.AllowRequest(uid) {
				t.Fatalf("User %d, request %d: expected allowed but got denied", uid, i+1)
			}
		}
		// 1 extra request should be denied.
		if rl.AllowRequest(uid) {
			t.Fatalf("User %d: extra request expected denied but got allowed", uid)
		}
	}
}

func TestConcurrentRequests(t *testing.T) {
	// Setup: Allow maximum 10 requests per 1 second window.
	rate := 10
	window := 1 * time.Second
	nodes := 10
	rl := NewRateLimiter(rate, window, nodes)

	userID := uint64(7777)
	var wg sync.WaitGroup
	requests := 20
	allowedCount := 0
	mu := sync.Mutex{}

	wg.Add(requests)
	for i := 0; i < requests; i++ {
		go func() {
			defer wg.Done()
			if rl.AllowRequest(userID) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount > rate {
		t.Fatalf("Concurrent test: allowed requests (%d) exceed limit (%d)", allowedCount, rate)
	}
}

func TestDynamicRateLimitAdjustment(t *testing.T) {
	// Setup: Initial rate limit of 2 requests per 1 second window.
	initialRate := 2
	window := 1 * time.Second
	nodes := 3
	rl := NewRateLimiter(initialRate, window, nodes)

	userID := uint64(8888)
	// Use up initial limit.
	for i := 0; i < initialRate; i++ {
		if !rl.AllowRequest(userID) {
			t.Fatalf("Initial rate: request %d expected allowed but got denied", i+1)
		}
	}
	if rl.AllowRequest(userID) {
		t.Fatalf("Initial rate: extra request expected denied but got allowed")
	}

	// Adjust the rate limit to a higher value.
	newRate := 5
	rl.AdjustRateLimit(newRate)

	// Wait for the time window to expire so that counting resets.
	time.Sleep(window + 100*time.Millisecond)

	// Now, we should be able to allow newRate requests.
	allowed := 0
	for i := 0; i < newRate; i++ {
		if rl.AllowRequest(userID) {
			allowed++
		}
	}
	if allowed != newRate {
		t.Fatalf("After dynamic adjustment: expected %d allowed requests, got %d", newRate, allowed)
	}
}