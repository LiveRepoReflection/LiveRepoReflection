package adaptive_limiter

import (
	"sync"
	"testing"
	"time"
)

// TestAllowRequestWithinLimit verifies that allowed requests within the effective limit are accepted.
func TestAllowRequestWithinLimit(t *testing.T) {
	// Create a new rate limiter with windowSize = 1 second.
	rl := NewRateLimiter(1)
	// Set client "client1" with a base limit of 5 requests.
	rl.SetBaseLimit("client1", 5)
	// Global load factor set to 1.0 makes effective limit = 5.
	rl.UpdateGlobalLoadFactor(1.0)

	// Allow 5 requests which should pass.
	for i := 0; i < 5; i++ {
		if !rl.Allow("client1") {
			t.Errorf("expected allowed request for iteration %d, but was rejected", i)
		}
	}

	// The 6th request should be rejected.
	if rl.Allow("client1") {
		t.Errorf("expected request to be rejected when exceeding limit")
	}
}

// TestRejectWhenOverLimit verifies that requests over the effective limit are rejected and window reset works.
func TestRejectWhenOverLimit(t *testing.T) {
	rl := NewRateLimiter(1)
	rl.SetBaseLimit("client2", 3)
	rl.UpdateGlobalLoadFactor(1.0) // effective limit = 3

	// Allow exactly 3 requests.
	for i := 0; i < 3; i++ {
		if !rl.Allow("client2") {
			t.Errorf("expected allowed request for iteration %d, but was rejected", i)
		}
	}

	// Next request should be rejected.
	if rl.Allow("client2") {
		t.Errorf("expected request to be rejected after limit reached")
	}

	// Wait for the window to reset.
	time.Sleep(1100 * time.Millisecond)

	// After the window resets, a new request should be allowed.
	if !rl.Allow("client2") {
		t.Errorf("expected allowed request after window reset, but was rejected")
	}
}

// TestDynamicLoadFactor checks that changes to the global load factor update effective limits dynamically.
func TestDynamicLoadFactor(t *testing.T) {
	rl := NewRateLimiter(1)
	rl.SetBaseLimit("client3", 10)

	// Initially set the load factor to 0.5, so effective limit = 5.
	rl.UpdateGlobalLoadFactor(0.5)
	for i := 0; i < 5; i++ {
		if !rl.Allow("client3") {
			t.Errorf("expected allowed request at iteration %d with load factor 0.5", i)
		}
	}
	if rl.Allow("client3") {
		t.Errorf("expected request to be rejected at current load factor of 0.5")
	}

	// Update the load factor to 1.0, which increases the effective limit to 10.
	// Note that the current window still has 5 used requests.
	rl.UpdateGlobalLoadFactor(1.0)
	for i := 0; i < 5; i++ {
		if !rl.Allow("client3") {
			t.Errorf("expected allowed request after increasing load factor at iteration %d", i)
		}
	}
	if rl.Allow("client3") {
		t.Errorf("expected request to be rejected after exceeding updated limit in the current window")
	}
}

// TestConcurrency ensures that concurrent requests are handled safely.
func TestConcurrency(t *testing.T) {
	rl := NewRateLimiter(1)
	baseLimit := 1000
	clientID := "client_concurrent"
	rl.SetBaseLimit(clientID, baseLimit)
	rl.UpdateGlobalLoadFactor(1.0) // effective limit = 1000

	var wg sync.WaitGroup
	allowedCount := 0
	totalRequests := 1200
	var mutex sync.Mutex

	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.Allow(clientID) {
				mutex.Lock()
				allowedCount++
				mutex.Unlock()
			}
		}()
	}
	wg.Wait()
	// The number of allowed requests must equal the effective limit.
	if allowedCount != baseLimit {
		t.Errorf("expected allowed count to be %d, got %d", baseLimit, allowedCount)
	}
}

// TestMultipleClients verifies that multiple clients are handled independently.
func TestMultipleClients(t *testing.T) {
	rl := NewRateLimiter(1)
	rl.SetBaseLimit("clientA", 5)
	rl.SetBaseLimit("clientB", 10)
	rl.UpdateGlobalLoadFactor(1.0)

	allowedA := 0
	allowedB := 0

	// Issue 15 requests to both clients.
	for i := 0; i < 15; i++ {
		if rl.Allow("clientA") {
			allowedA++
		}
		if rl.Allow("clientB") {
			allowedB++
		}
	}

	if allowedA != 5 {
		t.Errorf("expected clientA allowed requests to be 5, got %d", allowedA)
	}
	if allowedB != 10 {
		t.Errorf("expected clientB allowed requests to be 10, got %d", allowedB)
	}
}