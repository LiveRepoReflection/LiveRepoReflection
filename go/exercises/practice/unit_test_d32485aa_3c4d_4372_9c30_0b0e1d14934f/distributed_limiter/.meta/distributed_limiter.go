package distributed_limiter

import (
	"sync"
	"time"
)

type clientData struct {
	count       int
	windowStart time.Time
}

var (
	clients = make(map[string]*clientData)
	mu      sync.Mutex
)

// Allow returns true if the client identified by clientID is allowed to make a request
// under the rate limit for the given window duration.
func Allow(clientID string, limit int, window time.Duration) bool {
	now := time.Now()

	mu.Lock()
	defer mu.Unlock()

	data, exists := clients[clientID]
	if !exists {
		clients[clientID] = &clientData{
			count:       1,
			windowStart: now,
		}
		return true
	}

	// Check if the current window has expired.
	if now.Sub(data.windowStart) >= window {
		data.count = 1
		data.windowStart = now
		return true
	}

	// Within the same window, allow if under limit.
	if data.count < limit {
		data.count++
		return true
	}

	// Rate limit exceeded.
	return false
}