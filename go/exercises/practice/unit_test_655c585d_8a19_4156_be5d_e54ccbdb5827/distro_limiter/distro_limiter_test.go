package distrolimiter

import (
	"context"
	"sync"
	"testing"
	"time"
)

func TestRateLimiter(t *testing.T) {
	tests := []struct {
		name           string
		ratePerSecond  int
		burstCapacity  int
		requests       int
		concurrent     int
		expectedAllow  int
		expectedDeny   int
		executionTime  time.Duration
	}{
		{
			name:          "Basic rate limiting",
			ratePerSecond: 10,
			burstCapacity: 10,
			requests:      20,
			concurrent:    1,
			expectedAllow: 10,
			expectedDeny:  10,
			executionTime: time.Second,
		},
		{
			name:          "Burst capacity test",
			ratePerSecond: 5,
			burstCapacity: 10,
			requests:      15,
			concurrent:    1,
			expectedAllow: 10,
			expectedDeny:  5,
			executionTime: time.Second,
		},
		{
			name:          "Concurrent requests",
			ratePerSecond: 50,
			burstCapacity: 50,
			requests:      100,
			concurrent:    10,
			expectedAllow: 50,
			expectedDeny:  50,
			executionTime: time.Second,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limiter, err := NewRateLimiter(tt.ratePerSecond, tt.burstCapacity)
			if err != nil {
				t.Fatalf("Failed to create rate limiter: %v", err)
			}

			ctx := context.Background()
			var wg sync.WaitGroup
			allowed := int32(0)
			denied := int32(0)
			var mu sync.Mutex

			// Start concurrent workers
			for i := 0; i < tt.concurrent; i++ {
				wg.Add(1)
				go func() {
					defer wg.Done()
					requests := tt.requests / tt.concurrent
					for j := 0; j < requests; j++ {
						isAllowed, err := limiter.Allow(ctx, "test-key")
						if err != nil {
							t.Errorf("Error during Allow check: %v", err)
							return
						}
						mu.Lock()
						if isAllowed {
							allowed++
						} else {
							denied++
						}
						mu.Unlock()
					}
				}()
			}

			wg.Wait()

			if int(allowed) != tt.expectedAllow {
				t.Errorf("Expected %d allowed requests, got %d", tt.expectedAllow, allowed)
			}
			if int(denied) != tt.expectedDeny {
				t.Errorf("Expected %d denied requests, got %d", tt.expectedDeny, denied)
			}
		})
	}
}

func TestDynamicRateUpdate(t *testing.T) {
	limiter, err := NewRateLimiter(10, 10)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	ctx := context.Background()

	// Test initial rate
	for i := 0; i < 10; i++ {
		allowed, err := limiter.Allow(ctx, "test-key")
		if err != nil {
			t.Fatalf("Error during Allow check: %v", err)
		}
		if !allowed {
			t.Errorf("Expected request to be allowed")
		}
	}

	// Update rate limit
	err = limiter.UpdateRate("test-key", 5)
	if err != nil {
		t.Fatalf("Failed to update rate: %v", err)
	}

	time.Sleep(time.Second) // Wait for bucket to refill

	allowed := 0
	denied := 0
	for i := 0; i < 10; i++ {
		isAllowed, err := limiter.Allow(ctx, "test-key")
		if err != nil {
			t.Fatalf("Error during Allow check: %v", err)
		}
		if isAllowed {
			allowed++
		} else {
			denied++
		}
	}

	if allowed != 5 {
		t.Errorf("Expected 5 allowed requests after rate update, got %d", allowed)
	}
	if denied != 5 {
		t.Errorf("Expected 5 denied requests after rate update, got %d", denied)
	}
}

func TestErrorHandling(t *testing.T) {
	// Test with invalid configuration
	_, err := NewRateLimiter(0, 10)
	if err == nil {
		t.Error("Expected error for invalid rate, got nil")
	}

	_, err = NewRateLimiter(10, 0)
	if err == nil {
		t.Error("Expected error for invalid burst capacity, got nil")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter, err := NewRateLimiter(1000, 1000)
	if err != nil {
		b.Fatalf("Failed to create rate limiter: %v", err)
	}

	ctx := context.Background()
	b.ResetTimer()

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			_, err := limiter.Allow(ctx, "bench-key")
			if err != nil {
				b.Errorf("Error during Allow check: %v", err)
			}
		}
	})
}