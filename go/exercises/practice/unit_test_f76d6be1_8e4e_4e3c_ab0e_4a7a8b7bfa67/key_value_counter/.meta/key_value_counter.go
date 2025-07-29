package keyvaluecounter

import (
	"fmt"
	"sync"
	"time"
)

// Node represents a single node in the distributed counter system
type Node struct {
	ID           int
	localCounts  map[string]int64
	mutex        sync.RWMutex
	isAvailable  bool
	replicas     map[string]int64
	lastSync     time.Time
}

// DistributedCounter represents the entire distributed counting system
type DistributedCounter struct {
	nodes            []*Node
	numNodes         int
	replicationFactor int
	mutex            sync.RWMutex
	partitioned      bool
}

// NewDistributedCounter creates a new distributed counter system with the specified number of nodes
func NewDistributedCounter(numNodes int) *DistributedCounter {
	dc := &DistributedCounter{
		nodes:            make([]*Node, numNodes),
		numNodes:         numNodes,
		replicationFactor: 3, // Default replication factor
		partitioned:      false,
	}

	// Initialize nodes
	for i := 0; i < numNodes; i++ {
		dc.nodes[i] = &Node{
			ID:          i,
			localCounts: make(map[string]int64),
			replicas:    make(map[string]int64),
			isAvailable: true,
			lastSync:    time.Now(),
		}
	}

	// Start background synchronization
	go dc.backgroundSync()

	return dc
}

// getResponsibleNodes returns the nodes responsible for a given key using consistent hashing
func (dc *DistributedCounter) getResponsibleNodes(key string) []*Node {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()

	result := make([]*Node, 0, dc.replicationFactor)
	hash := SimpleHash(key)
	startIdx := hash % uint32(dc.numNodes)

	// Select primary and replica nodes
	for i := 0; i < dc.replicationFactor && i < dc.numNodes; i++ {
		nodeIdx := (int(startIdx) + i) % dc.numNodes
		if dc.nodes[nodeIdx].isAvailable {
			result = append(result, dc.nodes[nodeIdx])
		}
	}

	return result
}

// Increment atomically increments the counter for the given key
func (dc *DistributedCounter) Increment(key string) error {
	responsibleNodes := dc.getResponsibleNodes(key)
	if len(responsibleNodes) == 0 {
		return fmt.Errorf("no available nodes to handle the increment")
	}

	// Increment on primary node
	primary := responsibleNodes[0]
	primary.mutex.Lock()
	primary.localCounts[key]++
	primaryCount := primary.localCounts[key]
	primary.mutex.Unlock()

	// Async replication to other nodes
	for _, node := range responsibleNodes[1:] {
		go func(n *Node, k string, count int64) {
			n.mutex.Lock()
			n.replicas[k] = count
			n.mutex.Unlock()
		}(node, key, primaryCount)
	}

	return nil
}

// GetCount returns the current count for the given key
func (dc *DistributedCounter) GetCount(key string) (int64, error) {
	responsibleNodes := dc.getResponsibleNodes(key)
	if len(responsibleNodes) == 0 {
		return 0, fmt.Errorf("no available nodes to handle the request")
	}

	// Try to get from primary first
	primary := responsibleNodes[0]
	primary.mutex.RLock()
	count, exists := primary.localCounts[key]
	primary.mutex.RUnlock()

	if exists {
		return count, nil
	}

	// If not found in primary, check replicas
	var maxCount int64
	for _, node := range responsibleNodes[1:] {
		node.mutex.RLock()
		if replicaCount, exists := node.replicas[key]; exists && replicaCount > maxCount {
			maxCount = replicaCount
		}
		node.mutex.RUnlock()
	}

	return maxCount, nil
}

// AddNode adds a new node to the system
func (dc *DistributedCounter) AddNode() error {
	dc.mutex.Lock()
	defer dc.mutex.Unlock()

	newNode := &Node{
		ID:          dc.numNodes,
		localCounts: make(map[string]int64),
		replicas:    make(map[string]int64),
		isAvailable: true,
		lastSync:    time.Now(),
	}

	dc.nodes = append(dc.nodes, newNode)
	dc.numNodes++

	// Trigger rebalancing
	go dc.rebalanceData()

	return nil
}

// SimulateNodeFailure simulates a node failure for testing
func (dc *DistributedCounter) SimulateNodeFailure(nodeID int) {
	if nodeID >= 0 && nodeID < dc.numNodes {
		dc.nodes[nodeID].isAvailable = false
	}
}

// SimulateNetworkPartition simulates a network partition for testing
func (dc *DistributedCounter) SimulateNetworkPartition() {
	dc.mutex.Lock()
	dc.partitioned = true
	dc.mutex.Unlock()
}

// HealNetworkPartition heals a simulated network partition
func (dc *DistributedCounter) HealNetworkPartition() {
	dc.mutex.Lock()
	dc.partitioned = false
	dc.mutex.Unlock()
}

// backgroundSync periodically synchronizes data between nodes
func (dc *DistributedCounter) backgroundSync() {
	ticker := time.NewTicker(1 * time.Second)
	for range ticker.C {
		if dc.partitioned {
			continue
		}

		dc.mutex.RLock()
		for _, node := range dc.nodes {
			if !node.isAvailable {
				continue
			}

			node.mutex.Lock()
			// Sync replicas to local counts if newer
			for key, count := range node.replicas {
				if localCount, exists := node.localCounts[key]; !exists || count > localCount {
					node.localCounts[key] = count
				}
			}
			node.lastSync = time.Now()
			node.mutex.Unlock()
		}
		dc.mutex.RUnlock()
	}
}

// rebalanceData redistributes data after adding new nodes
func (dc *DistributedCounter) rebalanceData() {
	dc.mutex.RLock()
	defer dc.mutex.RUnlock()

	// Simple rebalancing strategy: redistribute some data to new nodes
	for _, node := range dc.nodes[:dc.numNodes-1] {
		node.mutex.RLock()
		for key, count := range node.localCounts {
			if SimpleHash(key)%uint32(dc.numNodes) == uint32(dc.numNodes-1) {
				dc.nodes[dc.numNodes-1].mutex.Lock()
				dc.nodes[dc.numNodes-1].localCounts[key] = count
				dc.nodes[dc.numNodes-1].mutex.Unlock()
			}
		}
		node.mutex.RUnlock()
	}
}

// SimpleHash provides a basic hash function for key distribution
func SimpleHash(key string) uint32 {
	var hash uint32
	for i := 0; i < len(key); i++ {
		hash = hash*31 + uint32(key[i])
	}
	return hash
}