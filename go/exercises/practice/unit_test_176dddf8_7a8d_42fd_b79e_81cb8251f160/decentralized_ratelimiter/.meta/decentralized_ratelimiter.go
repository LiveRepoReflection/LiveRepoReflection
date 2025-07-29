package decentralized_ratelimiter

import (
	"sync"
	"time"
)

type entry struct {
	count       int
	windowStart time.Time
}

type node struct {
	lock sync.Mutex
	data map[uint64]*entry
}

// RateLimiter implements the decentralized rate limiter.
type RateLimiter struct {
	nodes    []*node
	rate     int
	window   time.Duration
	numNodes int
}

// NewRateLimiter creates a new RateLimiter with the specified rate limit, time window, and number of nodes.
func NewRateLimiter(rate int, window time.Duration, nodes int) *RateLimiter {
	if nodes < 1 {
		nodes = 1
	}
	rl := &RateLimiter{
		rate:     rate,
		window:   window,
		numNodes: nodes,
		nodes:    make([]*node, nodes),
	}
	for i := 0; i < nodes; i++ {
		rl.nodes[i] = &node{
			data: make(map[uint64]*entry),
		}
	}
	return rl
}

// AdjustRateLimit adjusts the rate limit for all nodes.
func (rl *RateLimiter) AdjustRateLimit(newRate int) {
	rl.rate = newRate
}

// AllowRequest processes a request identified by userID.
// It distributes the user based on userID modulo number of nodes.
// The function returns true if the request is allowed, false otherwise.
func (rl *RateLimiter) AllowRequest(userID uint64) bool {
	nodeIndex := int(userID % uint64(rl.numNodes))
	n := rl.nodes[nodeIndex]
	n.lock.Lock()
	defer n.lock.Unlock()

	now := time.Now()
	e, exists := n.data[userID]
	if !exists {
		n.data[userID] = &entry{
			count:       1,
			windowStart: now,
		}
		return true
	}

	if now.Sub(e.windowStart) >= rl.window {
		// Reset the time window and counter.
		e.count = 1
		e.windowStart = now
		return true
	}

	if e.count < rl.rate {
		e.count++
		return true
	}
	return false
}