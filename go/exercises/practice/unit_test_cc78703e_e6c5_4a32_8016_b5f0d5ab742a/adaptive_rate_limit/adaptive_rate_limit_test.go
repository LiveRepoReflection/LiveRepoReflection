package adaptive_rate_limit

import (
	"sync"
	"testing"
	"time"
)

func TestRateLimiter_BasicEnforcement(t *testing.T) {
	// Create a rate limiter with limit 5 requests per window (200ms window for test purposes)
	rl := NewRateLimiter(5, 200*time.Millisecond)
	clientID := "client_basic"

	// Allow 5 consecutive requests within the same window.
	for i := 0; i < 5; i++ {
		if !rl.Allow(clientID) {
			t.Errorf("expected request %d to be allowed", i+1)
		}
	}
	// The 6th request within the same window should be rejected.
	if rl.Allow(clientID) {
		t.Errorf("expected 6th request to be rejected, but it was allowed")
	}

	// Wait for the time window to reset.
	time.Sleep(250 * time.Millisecond)
	if !rl.Allow(clientID) {
		t.Errorf("expected request after window reset to be allowed")
	}
}

func TestRateLimiter_ConcurrentAccess(t *testing.T) {
	// Create a rate limiter with a higher limit to test concurrent access.
	rl := NewRateLimiter(100, 400*time.Millisecond)
	clientID := "client_concurrent"

	var allowed int
	var wg sync.WaitGroup
	var mu sync.Mutex

	numGoroutines := 20
	requestsPerGoroutine := 10
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func() {
			defer wg.Done()
			for j := 0; j < requestsPerGoroutine; j++ {
				if rl.Allow(clientID) {
					mu.Lock()
					allowed++
					mu.Unlock()
				}
			}
		}()
	}
	wg.Wait()

	// Ensure that the total allowed requests do not exceed the defined limit.
	if allowed > 100 {
		t.Errorf("allowed requests exceeded limit: got %d, expected at most 100", allowed)
	}
}

func TestRateLimiter_AdaptiveThrottling(t *testing.T) {
	// Create a rate limiter with an initial limit of 10 requests per window.
	rl := NewRateLimiter(10, 200*time.Millisecond)
	clientID := "client_adaptive"

	// Under normal conditions, ensure 10 requests are allowed.
	normalCount := 0
	for i := 0; i < 10; i++ {
		if rl.Allow(clientID) {
			normalCount++
		}
	}
	if normalCount != 10 {
		t.Errorf("expected 10 allowed requests under normal conditions, got %d", normalCount)
	}

	// Simulate backend overload by reporting high latency and error rate.
	rl.UpdateBackendMetrics(300*time.Millisecond, 0.5)
	// Allow time for the adaptive mechanism to adjust.
	time.Sleep(220 * time.Millisecond)

	// Now, the rate limiter should reduce the allowed number of requests.
	allowedAfterOverload := 0
	for i := 0; i < 20; i++ {
		if rl.Allow(clientID) {
			allowedAfterOverload++
		}
	}
	if allowedAfterOverload >= 10 {
		t.Errorf("expected adaptive throttling to lower the allowed request count under overload, got %d", allowedAfterOverload)
	}

	// Simulate backend recovery with low latency and zero errors.
	rl.UpdateBackendMetrics(50*time.Millisecond, 0.0)
	time.Sleep(220 * time.Millisecond)

	// After recovery, the rate limiter should increase the allowed number.
	allowedAfterRecovery := 0
	for i := 0; i < 20; i++ {
		if rl.Allow(clientID) {
			allowedAfterRecovery++
		}
	}
	if allowedAfterRecovery <= allowedAfterOverload {
		t.Errorf("expected increased allowance after backend recovery; got %d allowed (previously %d)", allowedAfterRecovery, allowedAfterOverload)
	}
}

func TestRateLimiter_UpdateClientConfig(t *testing.T) {
	// Create a rate limiter with a default limit of 5 requests per window.
	rl := NewRateLimiter(5, 200*time.Millisecond)
	clientID := "client_config"

	// Allow 5 consecutive requests and expect them to pass.
	for i := 0; i < 5; i++ {
		if !rl.Allow(clientID) {
			t.Errorf("expected request %d to be allowed", i+1)
		}
	}
	// The 6th request should be rejected.
	if rl.Allow(clientID) {
		t.Errorf("expected 6th request to be rejected")
	}

	// Dynamically update the rate limit for this client to 10.
	rl.UpdateClientRateLimit(clientID, 10)
	// Wait for a new window.
	time.Sleep(250 * time.Millisecond)

	// Now, 10 requests should be allowed.
	allowedCount := 0
	for i := 0; i < 10; i++ {
		if rl.Allow(clientID) {
			allowedCount++
		}
	}
	if allowedCount != 10 {
		t.Errorf("expected 10 allowed requests after configuration update, got %d", allowedCount)
	}
}

func TestRateLimiter_EdgeCases(t *testing.T) {
	// Test edge case for burst traffic and window boundaries.
	rl := NewRateLimiter(3, 200*time.Millisecond)
	clientID := "client_edge"

	// Send 3 immediate requests first.
	burstCount := 0
	for i := 0; i < 3; i++ {
		if rl.Allow(clientID) {
			burstCount++
		}
	}
	if burstCount != 3 {
		t.Errorf("expected 3 allowed requests in burst, got %d", burstCount)
	}

	// Wait almost till the end of the window, then send another request.
	time.Sleep(180 * time.Millisecond)
	_ = rl.Allow(clientID) // The outcome may vary due to timing within the window.

	// Wait for the complete window reset and verify that a new request is allowed.
	time.Sleep(50 * time.Millisecond)
	if !rl.Allow(clientID) {
		t.Errorf("expected request after complete window reset to be allowed")
	}
}