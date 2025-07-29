package tiered_rate_limit

import (
	"sync"
	"time"
)

var (
	mu        sync.RWMutex
	clientMap = make(map[string]*ClientInfo)
	limits    = map[string]int{
		"Free":       10,
		"Premium":    100,
		"Enterprise": 1000,
	}
)

// ClientInfo stores the rate limit data for a client.
type ClientInfo struct {
	Tier        string
	WindowStart int64
	Count       int
}

// Reset resets the internal state of the rate limiter.
// This function is intended for testing purposes.
func Reset() {
	mu.Lock()
	defer mu.Unlock()
	clientMap = make(map[string]*ClientInfo)
	limits = map[string]int{
		"Free":       10,
		"Premium":    100,
		"Enterprise": 1000,
	}
}

// Allow verifies if a client's request is within the allowed limit.
// It checks the current window (in seconds), resets if required,
// and atomically increments the request count if allowed.
func Allow(clientID string) bool {
	now := time.Now().Unix()
	mu.Lock()
	defer mu.Unlock()

	info, exists := clientMap[clientID]
	if !exists {
		// If the client does not exist, assume default tier "Free"
		info = &ClientInfo{
			Tier:        "Free",
			WindowStart: now,
			Count:       0,
		}
		clientMap[clientID] = info
	}

	// If the current time window has advanced, reset the count.
	if info.WindowStart != now {
		info.WindowStart = now
		info.Count = 0
	}

	allowedLimit := limits[info.Tier]
	if info.Count < allowedLimit {
		info.Count++
		return true
	}
	return false
}

// SetTier assigns a tier to a client.
// If the client does not exist, it is created with the specified tier.
func SetTier(clientID string, tier string) {
	now := time.Now().Unix()
	mu.Lock()
	defer mu.Unlock()

	info, exists := clientMap[clientID]
	if !exists {
		info = &ClientInfo{
			Tier:        tier,
			WindowStart: now,
			Count:       0,
		}
		clientMap[clientID] = info
	} else {
		info.Tier = tier
		// The request count is maintained until the next time window reset.
	}
}

// UpdateLimits updates the rate limits for each tier during runtime.
func UpdateLimits(freeRPS int, premiumRPS int, enterpriseRPS int) {
	mu.Lock()
	defer mu.Unlock()

	limits["Free"] = freeRPS
	limits["Premium"] = premiumRPS
	limits["Enterprise"] = enterpriseRPS
}