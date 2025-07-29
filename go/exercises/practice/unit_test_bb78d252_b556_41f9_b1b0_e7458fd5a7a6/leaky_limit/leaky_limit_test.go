package leaky_limit

import (
	"sync"
	"testing"
	"time"
)

func TestSingleClientAllowance(t *testing.T) {
	// Create a limiter with a capacity of 10 tokens and a leak rate of 5 tokens per second.
	limiter := NewLimiter(10, 5)
	clientID := "client1"

	// Initially, the bucket should be full.
	// Request 5 tokens; should be allowed.
	if !limiter.Allow(clientID, 5) {
		t.Errorf("Expected to allow a request of 5 tokens when the bucket is full")
	}

	// Immediately request another 6 tokens; should be rejected since only 5 tokens remain.
	if limiter.Allow(clientID, 6) {
		t.Errorf("Expected to reject a request of 6 tokens due to insufficient tokens")
	}

	// Wait for 1.1 seconds to allow tokens to leak into the bucket.
	time.Sleep(1100 * time.Millisecond)

	// Request 4 tokens, which should now be allowed.
	if !limiter.Allow(clientID, 4) {
		t.Errorf("Expected to allow a request of 4 tokens after waiting for token recovery")
	}
}

func TestMultipleClients(t *testing.T) {
	// Create a limiter with a capacity of 15 tokens and a leak rate of 3 tokens per second.
	limiter := NewLimiter(15, 3)
	clients := []string{"clientA", "clientB", "clientC"}

	// Each client should have its own bucket.
	for _, client := range clients {
		// Request 10 tokens for each client; all should be allowed.
		if !limiter.Allow(client, 10) {
			t.Errorf("Expected to allow client %s a request of 10 tokens", client)
		}
	}
}

func TestBucketRecovery(t *testing.T) {
	// Create a limiter with a capacity of 20 tokens and a leak rate of 4 tokens per second.
	limiter := NewLimiter(20, 4)
	clientID := "clientRecovery"

	// Consume the entire bucket.
	if !limiter.Allow(clientID, 20) {
		t.Errorf("Expected to allow consumption of the full bucket (20 tokens)")
	}

	// A subsequent request should be rejected as the bucket is empty.
	if limiter.Allow(clientID, 1) {
		t.Errorf("Expected to reject a request when the bucket is empty")
	}

	// Wait for 2.1 seconds to allow approximately 8 tokens to recover.
	time.Sleep(2100 * time.Millisecond)
	if !limiter.Allow(clientID, 8) {
		t.Errorf("Expected to allow a request of 8 tokens after recovery")
	}

	// A further request that exceeds the remaining tokens should be rejected.
	if limiter.Allow(clientID, 5) {
		t.Errorf("Expected to reject a request exceeding the available tokens")
	}
}

func TestConcurrentAccess(t *testing.T) {
	// Create a limiter with a capacity of 50 tokens and a leak rate of 10 tokens per second.
	limiter := NewLimiter(50, 10)
	clientID := "concurrentClient"
	var wg sync.WaitGroup
	successCount := 0
	mu := sync.Mutex{}

	// Worker function attempting to consume 5 tokens.
	worker := func() {
		defer wg.Done()
		if limiter.Allow(clientID, 5) {
			mu.Lock()
			successCount++
			mu.Unlock()
		}
	}

	// Run 20 concurrent workers.
	numWorkers := 20
	wg.Add(numWorkers)
	for i := 0; i < numWorkers; i++ {
		go worker()
	}
	wg.Wait()

	// Total tokens consumed should not exceed the bucket's capacity.
	if successCount*5 > 50 {
		t.Errorf("Concurrent requests exceeded bucket capacity; successCount=%d", successCount)
	}
}

func TestEdgeCaseExactTokenAvailability(t *testing.T) {
	// Create a limiter with capacity 10 tokens and a leak rate of 2 tokens per second.
	limiter := NewLimiter(10, 2)
	clientID := "edgeCaseClient"

	// Consume tokens exactly to empty the bucket.
	if !limiter.Allow(clientID, 10) {
		t.Errorf("Expected to allow consuming exactly all tokens")
	}
	// The bucket should now be empty.
	if limiter.Allow(clientID, 1) {
		t.Errorf("Expected to reject a request when no tokens remain")
	}

	// Wait just over 0.5 seconds to recover approximately 1 token.
	time.Sleep(510 * time.Millisecond)
	if !limiter.Allow(clientID, 1) {
		t.Errorf("Expected to allow a request after recovering exactly 1 token")
	}
}