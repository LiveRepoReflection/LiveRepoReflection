package distributed_limiter

import (
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// TestBasicRateLimiting verifies that a single client's requests are rate limited according to the specified limit.
func TestBasicRateLimiting(t *testing.T) {
	limit := 2
	window := 100 * time.Millisecond
	client := "client1"

	// First two calls should be allowed.
	if !Allow(client, limit, window) {
		t.Error("expected first call to be allowed")
	}
	if !Allow(client, limit, window) {
		t.Error("expected second call to be allowed")
	}
	// Third call exceeds limit.
	if Allow(client, limit, window) {
		t.Error("expected third call to be rejected")
	}
}

// TestWindowReset verifies that once the time window passes, the rate limit is reset.
func TestWindowReset(t *testing.T) {
	limit := 2
	window := 50 * time.Millisecond
	client := "client2"

	if !Allow(client, limit, window) {
		t.Error("expected first call to be allowed")
	}
	if !Allow(client, limit, window) {
		t.Error("expected second call to be allowed")
	}
	if Allow(client, limit, window) {
		t.Error("expected third call to be rejected before window reset")
	}
	// Wait for the window to expire.
	time.Sleep(60 * time.Millisecond)
	if !Allow(client, limit, window) {
		t.Error("expected call to be allowed after window reset")
	}
}

// TestMultipleClients verifies that different clients maintain independent rate limits.
func TestMultipleClients(t *testing.T) {
	limit := 3
	window := 100 * time.Millisecond
	client1 := "client3"
	client2 := "client4"

	// Each client should be allowed up to the limit independently.
	for i := 0; i < limit; i++ {
		if !Allow(client1, limit, window) {
			t.Errorf("client1 call %d expected to be allowed", i+1)
		}
		if !Allow(client2, limit, window) {
			t.Errorf("client2 call %d expected to be allowed", i+1)
		}
	}
	// One extra call for each client should be rejected.
	if Allow(client1, limit, window) {
		t.Error("client1 extra call should be rejected")
	}
	if Allow(client2, limit, window) {
		t.Error("client2 extra call should be rejected")
	}
}

// TestConcurrency verifies that concurrent calls to the rate limiter are handled correctly.
func TestConcurrency(t *testing.T) {
	limit := 100
	window := 200 * time.Millisecond
	client := "concurrent_client"

	var allowedCount int32
	var wg sync.WaitGroup
	totalRequests := 1000

	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if Allow(client, limit, window) {
				atomic.AddInt32(&allowedCount, 1)
			}
		}()
	}
	wg.Wait()
	if allowedCount != int32(limit) {
		t.Errorf("expected %d allowed calls, but got %d", limit, allowedCount)
	}
}