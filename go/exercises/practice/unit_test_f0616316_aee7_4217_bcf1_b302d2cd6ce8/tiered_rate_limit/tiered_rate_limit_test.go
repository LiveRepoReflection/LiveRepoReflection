package tiered_rate_limit

import (
	"sync"
	"testing"
	"time"
)

// resetState is a helper function to reset the internal state of the rate limiter between tests.
// It assumes that the implementation exposes a Reset function for testing purposes.
// If such a function is not available, each test should work in isolation.
func resetState() {
	// Assuming an internal reset function exists; if not, simulate by reinitializing state
	// For the purpose of this test file, we assume each test is run independently.
}

// TestFreeTierLimit verifies that a Free tier client is allowed only up to its limit.
func TestFreeTierLimit(t *testing.T) {
	resetState()
	// Set initial global limits: Free: 10, Premium: 100, Enterprise: 1000
	UpdateLimits(10, 100, 1000)

	clientID := "client_free"
	SetTier(clientID, "Free")

	// Make 10 requests in the current window; they should be allowed.
	for i := 0; i < 10; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Free tier", i+1)
		}
	}

	// The 11th request should be denied.
	if Allow(clientID) {
		t.Fatalf("expected 11th request to be denied for Free tier")
	}

	// Wait for the time window to expire.
	time.Sleep(1100 * time.Millisecond)
	// After reset, requests should be allowed again.
	if !Allow(clientID) {
		t.Fatalf("expected request after window reset to be allowed for Free tier")
	}
}

// TestPremiumTierLimit verifies that a Premium tier client can exceed the Free tier limit.
func TestPremiumTierLimit(t *testing.T) {
	resetState()
	UpdateLimits(10, 100, 1000)

	clientID := "client_premium"
	SetTier(clientID, "Premium")

	// Make 100 requests in the current window; they should be allowed.
	for i := 0; i < 100; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Premium tier", i+1)
		}
	}

	// The 101st request should be denied.
	if Allow(clientID) {
		t.Fatalf("expected 101st request to be denied for Premium tier")
	}

	// Wait for the time window to expire.
	time.Sleep(1100 * time.Millisecond)
	if !Allow(clientID) {
		t.Fatalf("expected request after window reset to be allowed for Premium tier")
	}
}

// TestDynamicLimitUpdate verifies that updating the limits at runtime affects the allowance.
func TestDynamicLimitUpdate(t *testing.T) {
	resetState()
	// Initially set Free limit to 5
	UpdateLimits(5, 100, 1000)

	clientID := "client_dynamic"
	SetTier(clientID, "Free")

	// Make 5 requests, all should be allowed.
	for i := 0; i < 5; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Free tier with limit 5", i+1)
		}
	}
	// Next request should be denied.
	if Allow(clientID) {
		t.Fatalf("expected 6th request to be denied for Free tier with limit 5")
	}

	// Update the Free limit to 8 in runtime.
	UpdateLimits(8, 100, 1000)
	// Wait for window reset.
	time.Sleep(1100 * time.Millisecond)
	// Now Free tier should allow up to 8 requests.
	for i := 0; i < 8; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Free tier with updated limit 8", i+1)
		}
	}
	if Allow(clientID) {
		t.Fatalf("expected 9th request to be denied for Free tier with updated limit 8")
	}
}

// TestSetTierAndAllow verifies that setting a client to a different tier immediately applies the new limits.
func TestSetTierAndAllow(t *testing.T) {
	resetState()
	UpdateLimits(10, 100, 1000)

	clientID := "client_switch"
	// Start as Free tier
	SetTier(clientID, "Free")

	// Exhaust Free tier limit.
	for i := 0; i < 10; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Free tier", i+1)
		}
	}
	if Allow(clientID) {
		t.Fatalf("expected request exceeding Free tier limit to be denied")
	}

	// Update the client's tier to Enterprise.
	SetTier(clientID, "Enterprise")
	// After tier switch, the rate limiter should allow up to the Enterprise limit for the new window.
	// Wait for window reset.
	time.Sleep(1100 * time.Millisecond)

	// Now, Enterprise tier should allow up to 1000 requests.
	for i := 0; i < 1000; i++ {
		if !Allow(clientID) {
			t.Fatalf("expected request %d to be allowed for Enterprise tier", i+1)
		}
	}
	if Allow(clientID) {
		t.Fatalf("expected request exceeding Enterprise tier limit to be denied")
	}
}

// TestConcurrentAllow verifies the rate limiter under concurrent request conditions.
func TestConcurrentAllow(t *testing.T) {
	resetState()
	// For this test, we set a moderate limit.
	UpdateLimits(50, 100, 1000)

	clientID := "client_concurrent"
	SetTier(clientID, "Free")

	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0

	// We fire 100 concurrent requests.
	concurrentRequests := 100
	wg.Add(concurrentRequests)
	for i := 0; i < concurrentRequests; i++ {
		go func() {
			defer wg.Done()
			if Allow(clientID) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	// For Free tier, at most 50 requests should be allowed in the window.
	if allowedCount > 50 {
		t.Fatalf("expected at most 50 allowed requests in Free tier concurrently, got %d", allowedCount)
	}
}