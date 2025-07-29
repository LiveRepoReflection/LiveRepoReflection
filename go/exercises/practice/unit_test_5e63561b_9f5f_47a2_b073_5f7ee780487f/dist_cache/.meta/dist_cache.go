package dist_cache

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"hash/fnv"
	"sync"
	"time"
)

type node struct {
	id        int
	data      map[string]*cacheEntry
	lock      sync.RWMutex
	available bool
}

type cacheEntry struct {
	value     string
	timestamp time.Time
	version   uint64
}

type DistributedCache struct {
	nodes            []*node
	replicationFactor int
	nodeCount        int
	globalLock       sync.RWMutex
	vectorClock      map[string][]uint64
	clockLock        sync.RWMutex
}

func NewDistributedCache(nodeCount, replicationFactor int) *DistributedCache {
	if nodeCount < 1 || replicationFactor < 1 || replicationFactor > nodeCount {
		panic("Invalid configuration")
	}

	cache := &DistributedCache{
		nodes:            make([]*node, nodeCount),
		replicationFactor: replicationFactor,
		nodeCount:        nodeCount,
		vectorClock:      make(map[string][]uint64),
	}

	for i := 0; i < nodeCount; i++ {
		cache.nodes[i] = &node{
			id:        i,
			data:      make(map[string]*cacheEntry),
			available: true,
		}
	}

	return cache
}

func (dc *DistributedCache) Put(key, value string) error {
	dc.globalLock.RLock()
	defer dc.globalLock.RUnlock()

	// Update vector clock
	dc.clockLock.Lock()
	if _, exists := dc.vectorClock[key]; !exists {
		dc.vectorClock[key] = make([]uint64, dc.nodeCount)
	}
	dc.vectorClock[key][dc.getPrimaryNode(key)] += 1
	version := dc.vectorClock[key][dc.getPrimaryNode(key)]
	dc.clockLock.Unlock()

	// Get target nodes for replication
	targetNodes := dc.getTargetNodes(key)
	
	// Create entry
	entry := &cacheEntry{
		value:     value,
		timestamp: time.Now(),
		version:   version,
	}

	// Replicate to target nodes
	successCount := 0
	for _, nodeIdx := range targetNodes {
		if dc.nodes[nodeIdx].available {
			dc.nodes[nodeIdx].lock.Lock()
			dc.nodes[nodeIdx].data[key] = entry
			dc.nodes[nodeIdx].lock.Unlock()
			successCount++
		}
	}

	if successCount < dc.replicationFactor/2+1 {
		return errors.New("failed to achieve quorum for write operation")
	}

	return nil
}

func (dc *DistributedCache) Get(key string) (string, bool) {
	dc.globalLock.RLock()
	defer dc.globalLock.RUnlock()

	targetNodes := dc.getTargetNodes(key)
	var latestEntry *cacheEntry
	foundCount := 0

	// Read from all available replicas
	for _, nodeIdx := range targetNodes {
		if !dc.nodes[nodeIdx].available {
			continue
		}

		dc.nodes[nodeIdx].lock.RLock()
		if entry, exists := dc.nodes[nodeIdx].data[key]; exists {
			foundCount++
			if latestEntry == nil || entry.version > latestEntry.version {
				latestEntry = entry
			}
		}
		dc.nodes[nodeIdx].lock.RUnlock()
	}

	// Read repair if inconsistencies found
	if foundCount > 1 && latestEntry != nil {
		go dc.readRepair(key, latestEntry, targetNodes)
	}

	if latestEntry != nil {
		return latestEntry.value, true
	}
	return "", false
}

func (dc *DistributedCache) readRepair(key string, latestEntry *cacheEntry, targetNodes []int) {
	for _, nodeIdx := range targetNodes {
		if !dc.nodes[nodeIdx].available {
			continue
		}

		dc.nodes[nodeIdx].lock.Lock()
		dc.nodes[nodeIdx].data[key] = latestEntry
		dc.nodes[nodeIdx].lock.Unlock()
	}
}

func (dc *DistributedCache) getPrimaryNode(key string) int {
	hash := fnv.New32a()
	hash.Write([]byte(key))
	return int(hash.Sum32()) % dc.nodeCount
}

func (dc *DistributedCache) getTargetNodes(key string) []int {
	primary := dc.getPrimaryNode(key)
	nodes := make([]int, 0, dc.replicationFactor)
	nodes = append(nodes, primary)

	// Use consistent hashing to determine additional replicas
	h := sha256.New()
	h.Write([]byte(key))
	seed := binary.BigEndian.Uint64(h.Sum(nil))

	for len(nodes) < dc.replicationFactor {
		seed = (seed * 2862933555777941757) + 1
		candidate := int(seed % uint64(dc.nodeCount))
		
		// Check if this node is already selected
		found := false
		for _, n := range nodes {
			if n == candidate {
				found = true
				break
			}
		}
		
		if !found {
			nodes = append(nodes, candidate)
		}
	}

	return nodes
}

func (dc *DistributedCache) SimulateNodeFailure(nodeID int) {
	if nodeID >= 0 && nodeID < dc.nodeCount {
		dc.nodes[nodeID].available = false
	}
}

func (dc *DistributedCache) SimulateNetworkPartition() {
	// Simulate network partition by making some nodes unavailable
	for i := 0; i < dc.nodeCount/2; i++ {
		dc.nodes[i].available = false
	}
}

func (dc *DistributedCache) GetResponsibleNode(key string) int {
	return dc.getPrimaryNode(key)
}