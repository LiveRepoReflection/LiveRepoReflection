package sliding_window_rate_limiter

import (
	"sync"
	"testing"
	"time"
)

func TestRateLimiter(t *testing.T) {
	tests := []struct {
		name           string
		requestLimit   int
		windowSize     time.Duration
		clientID       string
		requestPattern []time.Duration // delays between requests
		expectedResults []bool        // whether each request should be allowed
	}{
		{
			name:         "Basic window test",
			requestLimit: 3,
			windowSize:  time.Second,
			clientID:    "client1",
			requestPattern: []time.Duration{
				0,
				0,
				0,
				0,
			},
			expectedResults: []bool{
				true,
				true,
				true,
				false,
			},
		},
		{
			name:         "Sliding window test",
			requestLimit: 2,
			windowSize:  time.Second,
			clientID:    "client2",
			requestPattern: []time.Duration{
				0,
				time.Millisecond * 500,
				time.Second,
				0,
			},
			expectedResults: []bool{
				true,
				true,
				true,
				true,
			},
		},
		{
			name:         "Multiple clients test",
			requestLimit: 2,
			windowSize:  time.Second,
			clientID:    "client3",
			requestPattern: []time.Duration{
				0,
				0,
				0,
			},
			expectedResults: []bool{
				true,
				true,
				false,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limiter := NewRateLimiter(tt.requestLimit, tt.windowSize)
			
			for i, delay := range tt.requestPattern {
				time.Sleep(delay)
				result := limiter.Allow(tt.clientID)
				
				if result != tt.expectedResults[i] {
					t.Errorf("Request %d: got %v, want %v", i+1, result, tt.expectedResults[i])
				}
			}
		})
	}
}

func TestConcurrentAccess(t *testing.T) {
	limiter := NewRateLimiter(1000, time.Second)
	clientID := "concurrent_client"
	
	var wg sync.WaitGroup
	results := make([]bool, 1000)
	
	// Launch 1000 concurrent requests
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()
			results[index] = limiter.Allow(clientID)
		}(i)
	}
	
	wg.Wait()
	
	// Count allowed requests
	allowed := 0
	for _, result := range results {
		if result {
			allowed++
		}
	}
	
	if allowed != 1000 {
		t.Errorf("Expected 1000 requests to be allowed, but got %d", allowed)
	}
}

func TestWindowExpiration(t *testing.T) {
	limiter := NewRateLimiter(1, time.Second)
	clientID := "expiration_client"
	
	// First request should be allowed
	if !limiter.Allow(clientID) {
		t.Error("First request should be allowed")
	}
	
	// Second request should be denied
	if limiter.Allow(clientID) {
		t.Error("Second request should be denied")
	}
	
	// Wait for window to expire
	time.Sleep(time.Second)
	
	// Request after expiration should be allowed
	if !limiter.Allow(clientID) {
		t.Error("Request after window expiration should be allowed")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter := NewRateLimiter(1000000, time.Second)
	clientID := "benchmark_client"
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		limiter.Allow(clientID)
	}
}