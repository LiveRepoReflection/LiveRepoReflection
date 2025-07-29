package distributed_ratelimit

import (
	"fmt"
	"hash/fnv"
	"sync"
	"time"
)

const evictionThreshold = 5 * time.Minute

type RateLimit struct {
	Requests int
	Window   time.Duration
}

type rateLimitEntry struct {
	windowStart time.Time
	count       int
}

type RateLimiterNode struct {
	mu       sync.Mutex
	clients  map[string]map[string]*rateLimitEntry
	lastSeen map[string]time.Time
}

func NewRateLimiterNode() *RateLimiterNode {
	return &RateLimiterNode{
		clients:  make(map[string]map[string]*rateLimitEntry),
		lastSeen: make(map[string]time.Time),
	}
}

func (n *RateLimiterNode) evictStaleClients(now time.Time) {
	for client, lastTime := range n.lastSeen {
		if now.Sub(lastTime) > evictionThreshold {
			delete(n.clients, client)
			delete(n.lastSeen, client)
		}
	}
}

func ruleKey(rl RateLimit) string {
	return fmt.Sprintf("%d:%d", rl.Requests, int64(rl.Window))
}

func (n *RateLimiterNode) allowRequest(clientID string, rateLimits []RateLimit, requestTime time.Time) bool {
	n.mu.Lock()
	defer n.mu.Unlock()

	// Evict stale client records
	n.evictStaleClients(requestTime)

	// Retrieve or create the client's rate limit state.
	clientState, exists := n.clients[clientID]
	if !exists {
		clientState = make(map[string]*rateLimitEntry)
		n.clients[clientID] = clientState
	}

	// First pass: verify that none of the rate limits would be exceeded.
	for _, rl := range rateLimits {
		key := ruleKey(rl)
		entry, exists := clientState[key]
		var candidate int
		if !exists || requestTime.Sub(entry.windowStart) >= rl.Window {
			candidate = 1
		} else {
			candidate = entry.count + 1
		}
		if candidate > rl.Requests {
			return false
		}
	}

	// Second pass: update the counters for all applicable rate limits.
	for _, rl := range rateLimits {
		key := ruleKey(rl)
		entry, exists := clientState[key]
		if !exists || requestTime.Sub(entry.windowStart) >= rl.Window {
			clientState[key] = &rateLimitEntry{
				windowStart: requestTime,
				count:       1,
			}
		} else {
			entry.count++
		}
	}

	// Update the last seen time for eviction tracking.
	n.lastSeen[clientID] = requestTime

	return true
}

type Cluster struct {
	nodes []*RateLimiterNode
}

func NewCluster(numNodes int) *Cluster {
	nodes := make([]*RateLimiterNode, numNodes)
	for i := 0; i < numNodes; i++ {
		nodes[i] = NewRateLimiterNode()
	}
	return &Cluster{
		nodes: nodes,
	}
}

func (c *Cluster) getNode(clientID string) *RateLimiterNode {
	hash := fnv.New32a()
	hash.Write([]byte(clientID))
	idx := int(hash.Sum32()) % len(c.nodes)
	return c.nodes[idx]
}

var cluster *Cluster

func init() {
	// Initialize the cluster with 3 nodes for simulation.
	cluster = NewCluster(3)
}

// AllowRequest returns true if the request from clientID is allowed based on all the rateLimits,
// or false otherwise.
func AllowRequest(clientID string, rateLimits []RateLimit, requestTime time.Time) bool {
	node := cluster.getNode(clientID)
	return node.allowRequest(clientID, rateLimits, requestTime)
}