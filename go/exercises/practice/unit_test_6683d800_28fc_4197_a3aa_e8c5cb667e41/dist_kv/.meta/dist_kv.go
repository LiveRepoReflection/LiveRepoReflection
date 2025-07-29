package dist_kv

import (
	"errors"
	"hash/fnv"
	"sync"
	"time"
)

type ValueEntry struct {
	value     string
	timestamp time.Time
}

type Node struct {
	alive bool
	mu    sync.RWMutex
	store map[string]ValueEntry
}

func NewNode() *Node {
	return &Node{
		alive: true,
		store: make(map[string]ValueEntry),
	}
}

type Cluster struct {
	nodes             []*Node
	replicationFactor int
	mu                sync.Mutex
}

// NewCluster initializes a new cluster with totalNodes and a given replicationFactor.
func NewCluster(totalNodes int, replicationFactor int) *Cluster {
	nodes := make([]*Node, totalNodes)
	for i := 0; i < totalNodes; i++ {
		nodes[i] = NewNode()
	}
	return &Cluster{
		nodes:             nodes,
		replicationFactor: replicationFactor,
	}
}

// FailNode simulates a failure for the node at index.
func (c *Cluster) FailNode(index int) {
	if index < 0 || index >= len(c.nodes) {
		return
	}
	c.nodes[index].mu.Lock()
	defer c.nodes[index].mu.Unlock()
	c.nodes[index].alive = false
}

// RecoverNode recovers the node at index.
func (c *Cluster) RecoverNode(index int) {
	if index < 0 || index >= len(c.nodes) {
		return
	}
	c.nodes[index].mu.Lock()
	defer c.nodes[index].mu.Unlock()
	c.nodes[index].alive = true
}

// Put stores the key-value pair into the cluster using replication.
// It uses a hash of the key to determine the starting node and then
// replicates the value to the next available alive nodes.
func (c *Cluster) Put(key, value string) error {
	// Generate timestamp for conflict resolution.
	timestamp := time.Now()

	// Determine starting index using hash.
	startIndex := hashKey(key) % uint32(len(c.nodes))
	nodesUpdated := 0

	// Lock cluster to ensure consistent update of replication.
	// We want to decide on the set of nodes in one atomic operation.
	c.mu.Lock()
	defer c.mu.Unlock()

	totalNodes := len(c.nodes)
	// Try to update replicationFactor nodes among alive nodes, scanning full ring if necessary.
	for i := 0; i < totalNodes && nodesUpdated < c.replicationFactor; i++ {
		index := (int(startIndex) + i) % totalNodes
		node := c.nodes[index]
		node.mu.Lock()
		if node.alive {
			// Perform conflict resolution based on existing timestamp.
			currentEntry, exists := node.store[key]
			if !exists || currentEntry.timestamp.Before(timestamp) {
				node.store[key] = ValueEntry{
					value:     value,
					timestamp: timestamp,
				}
			}
			nodesUpdated++
		}
		node.mu.Unlock()
	}
	// If no alive nodes were found, return error.
	if nodesUpdated == 0 {
		return errors.New("no alive nodes for replication")
	}
	return nil
}

// Get returns the current value for the key by reading from all nodes.
// It uses the value with the highest timestamp across available nodes.
func (c *Cluster) Get(key string) (string, error) {
	var bestEntry *ValueEntry
	found := false

	// No global lock needed; each node is locked individually.
	for _, node := range c.nodes {
		node.mu.RLock()
		if node.alive {
			if entry, exists := node.store[key]; exists {
				if !found || entry.timestamp.After(bestEntry.timestamp) {
					temp := entry // local copy
					bestEntry = &temp
					found = true
				}
			}
		}
		node.mu.RUnlock()
	}

	if !found {
		return "", errors.New("key not found")
	}
	return bestEntry.value, nil
}

// hashKey returns a hash for a string using FNV-1a algorithm.
func hashKey(key string) uint32 {
	hasher := fnv.New32a()
	hasher.Write([]byte(key))
	return hasher.Sum32()
}