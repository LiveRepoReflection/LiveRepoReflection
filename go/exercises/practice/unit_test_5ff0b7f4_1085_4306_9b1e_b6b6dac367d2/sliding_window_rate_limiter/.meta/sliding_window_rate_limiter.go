package sliding_window_rate_limiter

import (
	"container/heap"
	"sync"
	"time"
)

// RateLimiter represents a distributed rate limiter using sliding window algorithm
type RateLimiter struct {
	requestLimit int
	windowSize   time.Duration
	clients      map[string]*clientWindow
	mu           sync.RWMutex
}

// clientWindow represents the request window for a specific client
type clientWindow struct {
	requests    *requestHeap
	lastCleanup time.Time
}

// requestHeap is a min-heap of request timestamps
type requestHeap []time.Time

// NewRateLimiter creates a new rate limiter with specified limit and window size
func NewRateLimiter(requestLimit int, windowSize time.Duration) *RateLimiter {
	return &RateLimiter{
		requestLimit: requestLimit,
		windowSize:  windowSize,
		clients:     make(map[string]*clientWindow),
	}
}

// Allow checks if a request from a client should be allowed
func (rl *RateLimiter) Allow(clientID string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()

	// Get or create client window
	window, exists := rl.clients[clientID]
	if !exists {
		window = &clientWindow{
			requests:    &requestHeap{},
			lastCleanup: now,
		}
		heap.Init(window.requests)
		rl.clients[clientID] = window
	}

	// Clean up expired requests
	rl.cleanup(window, now)

	// Check if adding this request would exceed the limit
	if window.requests.Len() >= rl.requestLimit {
		return false
	}

	// Add current request to the window
	heap.Push(window.requests, now)
	return true
}

// cleanup removes expired requests from the window
func (rl *RateLimiter) cleanup(window *clientWindow, now time.Time) {
	cutoff := now.Add(-rl.windowSize)
	
	for window.requests.Len() > 0 && window.requests.Peek().Before(cutoff) {
		heap.Pop(window.requests)
	}
	
	window.lastCleanup = now
}

// Heap interface implementation
func (h requestHeap) Len() int           { return len(h) }
func (h requestHeap) Less(i, j int) bool { return h[i].Before(h[j]) }
func (h requestHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *requestHeap) Push(x interface{}) {
	*h = append(*h, x.(time.Time))
}
func (h *requestHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}
func (h requestHeap) Peek() time.Time {
	return h[0]
}