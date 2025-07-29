package leakybucket

import (
	"testing"
	"time"
)

func TestLeakyBucket(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			for i, req := range tc.requests {
				// Mock the current time for testing
				mockTime = time.Unix(0, req.timestamp*int64(time.Millisecond))
				
				result := AllowRequest(tc.userID, tc.capacity, tc.leakRate)
				if result != req.expected {
					t.Errorf("Request %d failed: %s\nexpected: %v, got: %v",
						i+1, req.comment, req.expected, result)
				}
			}
		})
	}
}

func BenchmarkLeakyBucket(b *testing.B) {
	testCase := testCases[0]
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		mockTime = time.Unix(0, int64(i)*int64(time.Millisecond))
		AllowRequest(testCase.userID, testCase.capacity, testCase.leakRate)
	}
}

// Mock time for testing
var mockTime time.Time

func init() {
	// Initialize mock time
	mockTime = time.Now()
}