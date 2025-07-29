package distributed_rate_limiter

import (
	"sync"
	"testing"
	"time"
)

func TestAllowWithinLimit(t *testing.T) {
	user := "user1"
	limit := 3
	window := time.Second

	// First 'limit' requests should be allowed.
	for i := 0; i < limit; i++ {
		if !Allow(user, limit, window) {
			t.Errorf("Iteration %d: expected Allow to return true, got false", i)
		}
	}

	// One additional request should be denied.
	if Allow(user, limit, window) {
		t.Errorf("Expected Allow to return false after reaching the limit, but got true")
	}
}

func TestAllowAfterWindowReset(t *testing.T) {
	user := "user2"
	limit := 2
	window := 200 * time.Millisecond

	// Consume all allowed requests.
	for i := 0; i < limit; i++ {
		if !Allow(user, limit, window) {
			t.Errorf("Iteration %d: expected Allow to return true, got false", i)
		}
	}

	// One additional request should be denied.
	if Allow(user, limit, window) {
		t.Errorf("Expected Allow to return false after limit is reached, but got true")
	}

	// After waiting past the time window, requests should be allowed again.
	time.Sleep(window + 50*time.Millisecond)
	if !Allow(user, limit, window) {
		t.Errorf("Expected Allow to return true after window reset, but got false")
	}
}

func TestConcurrentRequests(t *testing.T) {
	user := "concurrentUser"
	limit := 100
	window := time.Second
	totalRequests := 200

	var wg sync.WaitGroup
	var mu sync.Mutex
	successCount := 0
	failureCount := 0

	wg.Add(totalRequests)
	for i := 0; i < totalRequests; i++ {
		go func() {
			defer wg.Done()
			allowed := Allow(user, limit, window)
			mu.Lock()
			if allowed {
				successCount++
			} else {
				failureCount++
			}
			mu.Unlock()
		}()
	}
	wg.Wait()

	if successCount != limit {
		t.Errorf("Expected %d successful requests but got %d", limit, successCount)
	}
	if failureCount != totalRequests-limit {
		t.Errorf("Expected %d failed requests but got %d", totalRequests-limit, failureCount)
	}
}

func TestEdgeCaseVeryShortWindow(t *testing.T) {
	user := "edgeUser"
	limit := 5
	window := 10 * time.Millisecond

	// Send requests up to the limit.
	successCount := 0
	for i := 0; i < limit; i++ {
		if Allow(user, limit, window) {
			successCount++
		}
	}
	if successCount != limit {
		t.Errorf("Expected %d successful requests, got %d", limit, successCount)
	}

	// Next request in the same window should be denied.
	if Allow(user, limit, window) {
		t.Errorf("Expected request exceeding limit to be denied")
	}

	// Wait for the window to expire, then new request should be allowed.
	time.Sleep(window + 5*time.Millisecond)
	if !Allow(user, limit, window) {
		t.Errorf("Expected request after window expiration to be allowed")
	}
}

func TestMultipleUsers(t *testing.T) {
	users := []string{"userA", "userB", "userC"}
	limit := 10
	window := time.Second

	for _, user := range users {
		// Allow up to the limit per user.
		for i := 0; i < limit; i++ {
			if !Allow(user, limit, window) {
				t.Errorf("User %s: expected Allow true at iteration %d, got false", user, i)
			}
		}
		// One additional request for each user should be denied.
		if Allow(user, limit, window) {
			t.Errorf("User %s: expected Allow false after exceeding limit, but got true", user)
		}
	}
}