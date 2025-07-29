package distributed_wfq

import (
	"sync"
	"time"
)

type clientInfo struct {
	rate        int           // Base rate: allowed requests per duration.
	duration    time.Duration // Duration for the rate limit window.
	weight      int           // Weight for WFQ. Zero or positive.
	tokens      int           // Remaining tokens in the current window.
	windowStart time.Time     // Start time of the current window.
}

var (
	clients   = make(map[string]*clientInfo)
	clientsMu sync.Mutex
)

// getEffectiveLimit calculates the effective allowed requests for a client based on its rate and weight.
// If weight is 0, return 1 as minimal allowed requests.
// Otherwise, return rate / weight, but at least 1.
func getEffectiveLimit(rate, weight int) int {
	if weight <= 0 {
		return 1
	}
	limit := rate / weight
	if limit < 1 {
		return 1
	}
	return limit
}

// Allow checks if a request from the given clientID is allowed based on the rate limit and WFQ.
// It returns true if the request is allowed, false otherwise.
func Allow(clientID string) bool {
	clientsMu.Lock()
	defer clientsMu.Unlock()

	client, exists := clients[clientID]
	if !exists {
		// If the client is not registered, deny the request.
		return false
	}

	now := time.Now()
	// Check if the current window has expired.
	if now.Sub(client.windowStart) >= client.duration {
		// Reset the window.
		client.windowStart = now
		client.tokens = getEffectiveLimit(client.rate, client.weight)
	}

	// If tokens are available, allow the request and decrement.
	if client.tokens > 0 {
		client.tokens--
		return true
	}
	return false
}

// UpdateClientWeight updates the weight for the given clientID.
// If the client does not exist, it is created with default rate limit of 1 request per second.
func UpdateClientWeight(clientID string, weight int) {
	clientsMu.Lock()
	defer clientsMu.Unlock()

	client, exists := clients[clientID]
	if !exists {
		// Default rate limit: 1 request per second.
		client = &clientInfo{
			rate:        1,
			duration:    time.Second,
			weight:      weight,
			windowStart: time.Now(),
			tokens:      getEffectiveLimit(1, weight),
		}
		clients[clientID] = client
		return
	}
	// Update the weight.
	client.weight = weight
	// Adjust the current tokens if they exceed the new effective limit.
	limit := getEffectiveLimit(client.rate, client.weight)
	if client.tokens > limit {
		client.tokens = limit
	}
}

// UpdateClientRateLimit updates the rate limit for given clientID.
// The rate limit is defined as 'rate' requests per 'duration'.
// If the client does not exist, it is created with weight 1.
func UpdateClientRateLimit(clientID string, rate int, duration time.Duration) {
	clientsMu.Lock()
	defer clientsMu.Unlock()

	client, exists := clients[clientID]
	if !exists {
		client = &clientInfo{
			rate:        rate,
			duration:    duration,
			weight:      1,
			windowStart: time.Now(),
			tokens:      getEffectiveLimit(rate, 1),
		}
		clients[clientID] = client
		return
	}
	// Update the rate and duration.
	client.rate = rate
	client.duration = duration
	// Adjust the current tokens if they exceed the new effective limit.
	limit := getEffectiveLimit(client.rate, client.weight)
	if client.tokens > limit {
		client.tokens = limit
	}
}