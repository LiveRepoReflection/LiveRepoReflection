package ratelimit

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type DistributedRateLimiter struct {
	nodes       []string
	rateLimit   int
	nodeStatus  map[string]bool
	counters    map[string]*slidingWindow
	mu          sync.RWMutex
	statusMu    sync.RWMutex
}

type slidingWindow struct {
	timestamps []time.Time
	mu        sync.Mutex
}

func NewDistributedRateLimiter(nodes []string, rateLimit int) (*DistributedRateLimiter, error) {
	if len(nodes) == 0 {
		return nil, fmt.Errorf("at least one node is required")
	}
	if rateLimit <= 0 {
		return nil, fmt.Errorf("rate limit must be positive")
	}

	limiter := &DistributedRateLimiter{
		nodes:      nodes,
		rateLimit:  rateLimit,
		nodeStatus: make(map[string]bool),
		counters:   make(map[string]*slidingWindow),
	}

	// Initialize all nodes as healthy
	for _, node := range nodes {
		limiter.nodeStatus[node] = true
	}

	return limiter, nil
}

func (d *DistributedRateLimiter) Allow(ctx context.Context, clientID string) (bool, error) {
	if err := ctx.Err(); err != nil {
		return false, err
	}

	d.mu.Lock()
	if d.counters[clientID] == nil {
		d.counters[clientID] = &slidingWindow{
			timestamps: make([]time.Time, 0),
		}
	}
	counter := d.counters[clientID]
	d.mu.Unlock()

	counter.mu.Lock()
	defer counter.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-time.Second)

	// Remove expired timestamps
	valid := 0
	for _, ts := range counter.timestamps {
		if ts.After(windowStart) {
			counter.timestamps[valid] = ts
			valid++
		}
	}
	counter.timestamps = counter.timestamps[:valid]

	// Check if we have enough healthy nodes for quorum
	healthyNodes := d.getHealthyNodeCount()
	quorumSize := d.calculateQuorumSize(healthyNodes)

	if quorumSize == 0 {
		return false, fmt.Errorf("not enough healthy nodes for quorum")
	}

	// Check rate limit
	if len(counter.timestamps) >= d.rateLimit {
		return false, nil
	}

	// Add new timestamp
	counter.timestamps = append(counter.timestamps, now)

	// Simulate distributed consensus
	if err := d.simulateConsensus(ctx, quorumSize); err != nil {
		return false, err
	}

	return true, nil
}

func (d *DistributedRateLimiter) simulateConsensus(ctx context.Context, quorumSize int) error {
	// In a real implementation, this would communicate with other nodes
	// For this exercise, we'll simulate consensus success if we have enough healthy nodes
	if d.getHealthyNodeCount() < quorumSize {
		return fmt.Errorf("failed to achieve consensus: not enough healthy nodes")
	}
	return nil
}

func (d *DistributedRateLimiter) getHealthyNodeCount() int {
	d.statusMu.RLock()
	defer d.statusMu.RUnlock()

	count := 0
	for _, healthy := range d.nodeStatus {
		if healthy {
			count++
		}
	}
	return count
}

func (d *DistributedRateLimiter) calculateQuorumSize(healthyNodes int) int {
	totalNodes := len(d.nodes)
	if healthyNodes == 0 {
		return 0
	}

	// If more than 75% nodes are healthy, use majority quorum
	if float64(healthyNodes)/float64(totalNodes) > 0.75 {
		return (healthyNodes / 2) + 1
	}

	// Otherwise, use single-node quorum
	return 1
}

// Test helper methods
func (d *DistributedRateLimiter) SimulateNodeFailure(node string) {
	d.statusMu.Lock()
	defer d.statusMu.Unlock()
	d.nodeStatus[node] = false
}

func (d *DistributedRateLimiter) ResetNodes() {
	d.statusMu.Lock()
	defer d.statusMu.Unlock()
	for node := range d.nodeStatus {
		d.nodeStatus[node] = true
	}
}

func (d *DistributedRateLimiter) GetNodeCounters(clientID string) []int {
	d.mu.RLock()
	defer d.mu.RUnlock()

	counter := d.counters[clientID]
	if counter == nil {
		return make([]int, len(d.nodes))
	}

	counter.mu.Lock()
	defer counter.mu.Unlock()

	counts := make([]int, len(d.nodes))
	for i := range counts {
		counts[i] = len(counter.timestamps)
	}
	return counts
}