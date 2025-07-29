package dist_rate_limit

import (
	"sync"
	"testing"
	"time"
)

func TestNewRateLimiter(t *testing.T) {
	tests := []struct {
		name              string
		maxRequests       int
		timeWindowSeconds int64
		wantErr          bool
	}{
		{
			name:              "valid parameters",
			maxRequests:       100,
			timeWindowSeconds: 60,
			wantErr:          false,
		},
		{
			name:              "invalid max requests",
			maxRequests:       0,
			timeWindowSeconds: 60,
			wantErr:          true,
		},
		{
			name:              "invalid time window",
			maxRequests:       100,
			timeWindowSeconds: 0,
			wantErr:          true,
		},
		{
			name:              "negative max requests",
			maxRequests:       -1,
			timeWindowSeconds: 60,
			wantErr:          true,
		},
		{
			name:              "negative time window",
			maxRequests:       100,
			timeWindowSeconds: -1,
			wantErr:          true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := NewRateLimiter(tt.maxRequests, tt.timeWindowSeconds)
			if (err != nil) != tt.wantErr {
				t.Errorf("NewRateLimiter() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestRateLimiter_Allow(t *testing.T) {
	tests := []struct {
		name              string
		maxRequests       int
		timeWindowSeconds int64
		clientID          string
		requestCount      int
		sleepBetween     time.Duration
		expectedResults   []bool
	}{
		{
			name:              "basic rate limiting",
			maxRequests:       3,
			timeWindowSeconds: 1,
			clientID:          "client1",
			requestCount:      5,
			sleepBetween:     0,
			expectedResults:   []bool{true, true, true, false, false},
		},
		{
			name:              "window reset",
			maxRequests:       2,
			timeWindowSeconds: 1,
			clientID:          "client2",
			requestCount:      4,
			sleepBetween:     time.Second,
			expectedResults:   []bool{true, true, true, true},
		},
		{
			name:              "empty client ID",
			maxRequests:       2,
			timeWindowSeconds: 1,
			clientID:          "",
			requestCount:      1,
			sleepBetween:     0,
			expectedResults:   []bool{false},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			rl, err := NewRateLimiter(tt.maxRequests, tt.timeWindowSeconds)
			if err != nil {
				t.Fatalf("Failed to create rate limiter: %v", err)
			}

			results := make([]bool, tt.requestCount)
			for i := 0; i < tt.requestCount; i++ {
				results[i] = rl.Allow(tt.clientID, time.Now().Unix())
				if tt.sleepBetween > 0 {
					time.Sleep(tt.sleepBetween)
				}
			}

			if len(results) != len(tt.expectedResults) {
				t.Fatalf("Got %d results, want %d", len(results), len(tt.expectedResults))
			}

			for i, want := range tt.expectedResults {
				if results[i] != want {
					t.Errorf("Request %d: got %v, want %v", i+1, results[i], want)
				}
			}
		})
	}
}

func TestRateLimiter_Concurrent(t *testing.T) {
	rl, err := NewRateLimiter(100, 1)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	const (
		numGoroutines = 10
		numRequests   = 200
	)

	var wg sync.WaitGroup
	results := make([]int, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			allowed := 0
			for j := 0; j < numRequests; j++ {
				if rl.Allow("shared-client", time.Now().Unix()) {
					allowed++
				}
			}
			results[idx] = allowed
		}(i)
	}

	wg.Wait()

	totalAllowed := 0
	for _, count := range results {
		totalAllowed += count
	}

	if totalAllowed > 100 {
		t.Errorf("Rate limit exceeded: got %d allowed requests, want <= 100", totalAllowed)
	}
}

func TestRateLimiter_TimestampValidation(t *testing.T) {
	rl, err := NewRateLimiter(10, 60)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	tests := []struct {
		name      string
		timestamp int64
		want      bool
	}{
		{
			name:      "current time",
			timestamp: time.Now().Unix(),
			want:      true,
		},
		{
			name:      "past time",
			timestamp: time.Now().Add(-24 * time.Hour).Unix(),
			want:      false,
		},
		{
			name:      "future time",
			timestamp: time.Now().Add(24 * time.Hour).Unix(),
			want:      false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := rl.Allow("client1", tt.timestamp); got != tt.want {
				t.Errorf("Allow() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkRateLimiter_Allow(b *testing.B) {
	rl, err := NewRateLimiter(1000, 1)
	if err != nil {
		b.Fatalf("Failed to create rate limiter: %v", err)
	}

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			rl.Allow("benchmark-client", time.Now().Unix())
		}
	})
}