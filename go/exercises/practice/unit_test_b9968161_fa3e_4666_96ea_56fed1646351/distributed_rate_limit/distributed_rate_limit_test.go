package distributed_rate_limit

import (
	"os"
	"sync"
	"testing"
	"time"
)

// Helper function to reset rate limiter state for tests.
// It is assumed that the implementation uses a Redis key prefix "rl:" for user keys.
// For comprehensive tests, you might need to flush these keys from Redis.
func flushTestKeys(userIDs ...string) {
	for _, id := range userIDs {
		// Assumes the existence of a function flushKey in the implementation to assist testing.
		// If not available, this test may require a direct Redis connection to delete the keys.
		// For testing purposes, we call AllowRequest with zero window to force key expiration.
		_, _ = AllowRequest(id, 0, 0)
	}
}

func TestAllowRequestSingleServer(t *testing.T) {
	userID := "test_user_single"
	N := 3
	T := 2 // seconds

	// Flush any previous state
	flushTestKeys(userID)

	// First N calls should be allowed.
	for i := 0; i < N; i++ {
		allowed, err := AllowRequest(userID, N, T)
		if err != nil {
			t.Fatalf("Unexpected error for user %s on call %d: %v", userID, i+1, err)
		}
		if !allowed {
			t.Fatalf("Expected request %d to be allowed, but it was rejected", i+1)
		}
	}

	// Next call within the time window should be rejected.
	allowed, err := AllowRequest(userID, N, T)
	if err != nil {
		t.Fatalf("Unexpected error for user %s on call %d: %v", userID, N+1, err)
	}
	if allowed {
		t.Fatalf("Expected request %d to be rate limited, but it was allowed", N+1)
	}

	// Wait for the time window to expire.
	time.Sleep(time.Duration(T+1) * time.Second)

	// After window expiration, requests should be allowed again.
	allowed, err = AllowRequest(userID, N, T)
	if err != nil {
		t.Fatalf("Unexpected error after time window expired for user %s: %v", userID, err)
	}
	if !allowed {
		t.Fatalf("Expected request after time window expiration to be allowed, but it was rejected")
	}

	flushTestKeys(userID)
}

func TestDistributedRateLimit(t *testing.T) {
	userID := "test_user_distributed"
	N := 5
	T := 3 // seconds

	flushTestKeys(userID)

	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0
	totalRequests := 20

	// Simulate requests coming from multiple "servers" concurrently.
	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			allowed, err := AllowRequest(userID, N, T)
			if err != nil {
				// For the purpose of this test, if an error occurs, we consider the request as not allowed.
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

	if allowedCount > N {
		t.Fatalf("Distributed rate limiter allowed %d requests but maximum allowed is %d", allowedCount, N)
	}

	flushTestKeys(userID)
}

func TestConcurrency(t *testing.T) {
	userID := "test_user_concurrent"
	N := 10
	T := 4 // seconds

	flushTestKeys(userID)

	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0
	numGoroutines := 50

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			allowed, err := AllowRequest(userID, N, T)
			if err != nil {
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

	if allowedCount > N {
		t.Fatalf("Concurrency test: allowed %d requests but maximum allowed is %d", allowedCount, N)
	}

	flushTestKeys(userID)
}

func TestEdgeCases(t *testing.T) {
	// Test with N = 0, no requests should be allowed.
	userIDZero := "edge_case_zero"
	NZero := 0
	T := 5

	flushTestKeys(userIDZero)

	allowed, err := AllowRequest(userIDZero, NZero, T)
	if err != nil {
		t.Fatalf("Unexpected error for user %s with zero rate limit: %v", userIDZero, err)
	}
	if allowed {
		t.Fatalf("Expected request to be rejected when N = 0, but it was allowed")
	}

	// Test with empty userID. Behavior could be to treat it as a valid key or reject.
	emptyUserID := ""
	N := 3

	flushTestKeys(emptyUserID)

	allowed, err = AllowRequest(emptyUserID, N, T)
	if err != nil {
		t.Fatalf("Unexpected error for empty userID: %v", err)
	}
	// In this test, we assume that an empty userID is invalid and should be rejected.
	if allowed {
		t.Fatalf("Expected empty userID request to be rejected, but it was allowed")
	}

	flushTestKeys(userIDZero, emptyUserID)
}

func TestRedisFailure(t *testing.T) {
	// This test attempts to simulate a Redis failure scenario.
	// It temporarily sets an environment variable that the implementation is expected to use
	// for the Redis server address. The test expects AllowRequest to return an error.
	// It is assumed that the implementation reads "REDIS_ADDR" from the environment.
	originalAddr := os.Getenv("REDIS_ADDR")
	defer func() {
		// Restore the original Redis address after the test.
		os.Setenv("REDIS_ADDR", originalAddr)
	}()

	// Set an invalid Redis address to simulate failure.
	os.Setenv("REDIS_ADDR", "127.0.0.1:9999")

	userID := "test_redis_failure"
	N := 3
	T := 5

	allowed, err := AllowRequest(userID, N, T)
	if err == nil {
		t.Fatalf("Expected an error due to Redis failure simulation, but got none (allowed=%v)", allowed)
	}
}