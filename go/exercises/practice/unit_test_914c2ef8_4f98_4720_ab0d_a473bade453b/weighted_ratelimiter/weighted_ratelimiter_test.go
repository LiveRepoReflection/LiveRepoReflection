package weighted_ratelimiter

import (
	"sync"
	"sync/atomic"
	"testing"
)

func TestUpdateUserLimits_Valid(t *testing.T) {
	err := UpdateUserLimits("user_valid", 3, []int{30, 30, 40}, 100)
	if err != nil {
		t.Fatalf("expected no error for valid bucket weights, got: %v", err)
	}
}

func TestUpdateUserLimits_Invalid(t *testing.T) {
	// Sum of weights is 80, which is invalid as it should be 100.
	err := UpdateUserLimits("user_invalid", 2, []int{50, 30}, 80)
	if err == nil {
		t.Fatal("expected error for invalid bucket weights sum, got none")
	}
}

func TestAllow_Basic(t *testing.T) {
	userID := "user_basic"
	// 2 buckets with equal weights [50, 50] and totalLimit 20 results in each bucket having 10 tokens.
	err := UpdateUserLimits(userID, 2, []int{50, 50}, 20)
	if err != nil {
		t.Fatalf("UpdateUserLimits failed: %v", err)
	}

	allowedCount := 0
	totalRequests := 50
	for i := 0; i < totalRequests; i++ {
		if Allow(userID, 1) {
			allowedCount++
		}
	}
	if allowedCount > 20 {
		t.Fatalf("allowedCount %d exceeds total limit of 20", allowedCount)
	}
	// In case allowedCount is less than 20 due to random bucket selection,
	// the test logs the count rather than failing.
	t.Logf("Basic Allow test: allowed %d requests out of %d attempts", allowedCount, totalRequests)
}

func TestAllow_WithCost(t *testing.T) {
	userID := "user_cost"
	// 1 bucket, weight 100, totalLimit 50, so full capacity is 50.
	err := UpdateUserLimits(userID, 1, []int{100}, 50)
	if err != nil {
		t.Fatalf("UpdateUserLimits failed: %v", err)
	}

	// Using cost 5 per request, the maximum allowed requests should be 10.
	allowedCount := 0
	totalRequests := 20
	for i := 0; i < totalRequests; i++ {
		if Allow(userID, 5) {
			allowedCount++
		}
	}
	if allowedCount != 10 {
		t.Fatalf("expected 10 allowed requests with cost 5, got %d", allowedCount)
	}

	// Further request with cost greater than remaining tokens should be rejected.
	if Allow(userID, 6) {
		t.Fatal("expected cost 6 request to be rejected after tokens are exhausted")
	}
}

func TestAllow_Concurrent(t *testing.T) {
	userID := "user_concurrent"
	// 4 buckets with equal distribution [25, 25, 25, 25] leading to a totalLimit of 40 (each bucket gets 10 tokens).
	err := UpdateUserLimits(userID, 4, []int{25, 25, 25, 25}, 40)
	if err != nil {
		t.Fatalf("UpdateUserLimits failed: %v", err)
	}

	var allowedCount int32 = 0
	totalRequests := 1000
	var wg sync.WaitGroup
	wg.Add(totalRequests)

	for i := 0; i < totalRequests; i++ {
		go func() {
			if Allow(userID, 1) {
				atomic.AddInt32(&allowedCount, 1)
			}
			wg.Done()
		}()
	}
	wg.Wait()

	if allowedCount > 40 {
		t.Fatalf("allowedCount %d exceeds total limit of 40", allowedCount)
	} else {
		t.Logf("Concurrent Allow test: allowed %d requests out of %d attempts", allowedCount, totalRequests)
	}
}