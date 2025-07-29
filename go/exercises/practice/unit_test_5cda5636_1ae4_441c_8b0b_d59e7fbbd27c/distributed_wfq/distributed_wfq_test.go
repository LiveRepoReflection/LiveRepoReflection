package distributed_wfq

import (
	"sync"
	"testing"
	"time"
)

// TestBasicAllow verifies that a client cannot exceed its assigned rate limit.
func TestBasicAllow(t *testing.T) {
	clientID := "client_basic"
	// Set rate limit: 5 requests per 1 second.
	UpdateClientRateLimit(clientID, 5, 1*time.Second)
	// Set weight to 1.
	UpdateClientWeight(clientID, 1)

	// Consume 5 allowed requests.
	allowedCount := 0
	for i := 0; i < 5; i++ {
		if !Allow(clientID) {
			t.Errorf("Expected Allow(%q) to return true on iteration %d", clientID, i)
		} else {
			allowedCount++
		}
	}
	if allowedCount != 5 {
		t.Errorf("Expected 5 allowed requests, got %d", allowedCount)
	}

	// The next immediate request should be rejected.
	if Allow(clientID) {
		t.Errorf("Expected Allow(%q) to return false when rate limit is exceeded", clientID)
	}

	// Wait for the rate limit window to pass.
	time.Sleep(1100 * time.Millisecond)
	// Now it should allow again.
	if !Allow(clientID) {
		t.Errorf("Expected Allow(%q) to return true after rate limit window reset", clientID)
	}
}

// TestRateLimitUpdate verifies that updating a client's rate limit affects the behavior immediately.
func TestRateLimitUpdate(t *testing.T) {
	clientID := "client_rate"
	// Set an initial low rate limit: 2 requests per 1 second.
	UpdateClientRateLimit(clientID, 2, 1*time.Second)
	UpdateClientWeight(clientID, 1)

	// Consume 2 allowed requests.
	if !Allow(clientID) {
		t.Errorf("Expected first request to be allowed for %q", clientID)
	}
	if !Allow(clientID) {
		t.Errorf("Expected second request to be allowed for %q", clientID)
	}

	// Next request should be rejected.
	if Allow(clientID) {
		t.Errorf("Expected third request to be rejected due to low rate limit for %q", clientID)
	}

	// Update the rate limit: 5 requests per 1 second.
	UpdateClientRateLimit(clientID, 5, 1*time.Second)
	// Wait for the previous window to expire.
	time.Sleep(1100 * time.Millisecond)

	// Now, 5 requests should be allowed.
	allowed := 0
	for i := 0; i < 5; i++ {
		if Allow(clientID) {
			allowed++
		} else {
			t.Errorf("Expected request %d to be allowed after rate limit update for %q", i+1, clientID)
		}
	}

	if allowed != 5 {
		t.Errorf("Expected 5 allowed requests after rate limit update, got %d for %q", allowed, clientID)
	}

	// Next request should be rejected.
	if Allow(clientID) {
		t.Errorf("Expected request exceeding new rate limit to be rejected for %q", clientID)
	}
}

// TestWeightUpdate verifies that updating a client's weight is handled atomically.
// For the purpose of this test, we assume that weight affects internal scheduling.
// We simulate by updating the weight and then verifying that the client's behavior changes accordingly.
func TestWeightUpdate(t *testing.T) {
	clientID := "client_weight"
	// Set a moderate rate limit 6 per second.
	UpdateClientRateLimit(clientID, 6, 1*time.Second)
	// Set initial weight to 2.
	UpdateClientWeight(clientID, 2)

	// Consume three requests and expect them to be allowed.
	allowedBefore := 0
	for i := 0; i < 3; i++ {
		if Allow(clientID) {
			allowedBefore++
		}
	}
	if allowedBefore != 3 {
		t.Errorf("Expected 3 allowed requests before weight update for %q, got %d", clientID, allowedBefore)
	}

	// Now update weight to 0 (edge case: zero weight should still allow minimal requests).
	UpdateClientWeight(clientID, 0)
	// Reset the rate limit window.
	time.Sleep(1100 * time.Millisecond)

	// For zero weight we expect only one minimal request to be allowed in a window.
	allowedAfter := 0
	for i := 0; i < 3; i++ {
		if Allow(clientID) {
			allowedAfter++
		}
	}
	if allowedAfter != 1 {
		t.Errorf("Expected 1 allowed request for zero weight client %q in the window, got %d", clientID, allowedAfter)
	}
}

// TestConcurrency simulates a high concurrency scenario with multiple goroutines.
func TestConcurrency(t *testing.T) {
	clientID := "client_concurrent"
	// Set a high rate limit to avoid immediate rejections: 100 requests per 100 milliseconds.
	UpdateClientRateLimit(clientID, 100, 100*time.Millisecond)
	UpdateClientWeight(clientID, 1)

	var wg sync.WaitGroup
	mu := sync.Mutex{}
	allowedCount := 0
	totalRequests := 200

	// Launch concurrent requests.
	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
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

	// The allowedCount should not exceed 100 in the current window.
	if allowedCount > 100 {
		t.Errorf("Allowed count exceeded rate limit: got %d allowed requests, expected at most 100", allowedCount)
	}
}

// TestDynamicUpdates simulates dynamic configuration changes under load.
func TestDynamicUpdates(t *testing.T) {
	clientID := "client_dynamic"
	// Initially set rate limit 5 per 1 second and weight 1.
	UpdateClientRateLimit(clientID, 5, 1*time.Second)
	UpdateClientWeight(clientID, 1)

	// Use goroutines to call Allow while dynamically updating configuration.
	var wg sync.WaitGroup
	mu := sync.Mutex{}
	allowedCount := 0

	// Goroutine to perform dynamic updates.
	wg.Add(1)
	go func() {
		defer wg.Done()
		// After 300ms, update the rate limit and weight.
		time.Sleep(300 * time.Millisecond)
		UpdateClientRateLimit(clientID, 10, 1*time.Second)
		UpdateClientWeight(clientID, 3)
	}()

	// Goroutine to continuously call Allow for 1 second.
	stop := make(chan struct{})
	wg.Add(1)
	go func() {
		defer wg.Done()
		start := time.Now()
		for time.Since(start) < 1*time.Second {
			if Allow(clientID) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
			time.Sleep(50 * time.Millisecond)
		}
		close(stop)
	}()

	<-stop
	wg.Wait()

	// Since configurations were updated dynamically, we expect allowedCount to be at least 5 and at most 10.
	if allowedCount < 5 || allowedCount > 10 {
		t.Errorf("Dynamic updates: allowedCount = %d; expected between 5 and 10 for client %q", allowedCount, clientID)
	}
}