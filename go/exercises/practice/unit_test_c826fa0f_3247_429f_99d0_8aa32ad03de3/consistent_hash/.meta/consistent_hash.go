// Package consistent_hash implements a consistent hashing algorithm for distributed systems
package consistent_hash

import (
	"sort"
	"strconv"
	"sync"
)

// ConsistentHashRing represents a consistent hash ring with virtual nodes
type ConsistentHashRing struct {
	// virtualNodes maps hash values to server identifiers
	virtualNodes map[uint32]string
	
	// sortedHashes contains all hash values in sorted order for binary search
	sortedHashes []uint32
	
	// serverToHashes maps server names to their hash values for efficient deletion
	serverToHashes map[string][]uint32
	
	// replicaCount is the number of virtual nodes per physical server
	replicaCount int
	
	// mutex protects concurrent access to the hash ring
	mutex sync.RWMutex
}

// New creates a new consistent hash ring
func New(servers []string, replicas int) *ConsistentHashRing {
	ring := &ConsistentHashRing{
		virtualNodes:   make(map[uint32]string),
		sortedHashes:   make([]uint32, 0),
		serverToHashes: make(map[string][]uint32),
		replicaCount:   replicas,
	}

	// Add all provided servers to the ring
	for _, server := range servers {
		ring.AddServer(server)
	}

	return ring
}

// AddServer adds a server to the hash ring with multiple virtual nodes
func (ring *ConsistentHashRing) AddServer(server string) {
	ring.mutex.Lock()
	defer ring.mutex.Unlock()

	// Check if server already exists
	if _, exists := ring.serverToHashes[server]; exists {
		return // Server already in the ring
	}

	// Create a slice to store this server's hashes
	hashes := make([]uint32, 0, ring.replicaCount)

	// Add virtual nodes for this server
	for i := 0; i < ring.replicaCount; i++ {
		// Create a unique key for each virtual node
		virtualKey := server + ":" + strconv.Itoa(i)
		hash := fnv1aHash(virtualKey)

		// Store the mapping from hash to server
		ring.virtualNodes[hash] = server
		
		// Add to our sorted list of hashes
		ring.sortedHashes = append(ring.sortedHashes, hash)
		
		// Record that this hash belongs to this server
		hashes = append(hashes, hash)
	}

	// Store the server's hashes for easy removal later
	ring.serverToHashes[server] = hashes

	// Re-sort the hashes
	sort.Slice(ring.sortedHashes, func(i, j int) bool {
		return ring.sortedHashes[i] < ring.sortedHashes[j]
	})
}

// RemoveServer removes a server and all its virtual nodes from the hash ring
func (ring *ConsistentHashRing) RemoveServer(server string) {
	ring.mutex.Lock()
	defer ring.mutex.Unlock()

	// Check if server exists
	hashes, exists := ring.serverToHashes[server]
	if !exists {
		return // Server not in the ring
	}

	// Remove all virtual nodes for this server
	for _, hash := range hashes {
		delete(ring.virtualNodes, hash)
	}

	// Remove the server's hash mappings
	delete(ring.serverToHashes, server)

	// Rebuild the sorted hash list
	ring.rebuildSortedHashes()
}

// rebuildSortedHashes rebuilds the sortedHashes slice after server removal
func (ring *ConsistentHashRing) rebuildSortedHashes() {
	ring.sortedHashes = make([]uint32, 0, len(ring.virtualNodes))
	for hash := range ring.virtualNodes {
		ring.sortedHashes = append(ring.sortedHashes, hash)
	}
	
	// Sort the hashes
	sort.Slice(ring.sortedHashes, func(i, j int) bool {
		return ring.sortedHashes[i] < ring.sortedHashes[j]
	})
}

// GetServer returns the server responsible for handling the given key
func (ring *ConsistentHashRing) GetServer(key string) string {
	ring.mutex.RLock()
	defer ring.mutex.RUnlock()

	if len(ring.sortedHashes) == 0 {
		return "" // No servers in the ring
	}

	// Hash the key
	hash := fnv1aHash(key)

	// Binary search to find the closest server in the hash ring
	idx := sort.Search(len(ring.sortedHashes), func(i int) bool {
		return ring.sortedHashes[i] >= hash
	})

	// If we're past the end, wrap around to the first hash
	if idx == len(ring.sortedHashes) {
		idx = 0
	}

	// Get the server corresponding to this hash
	return ring.virtualNodes[ring.sortedHashes[idx]]
}

// Rebalance rebuilds the hash ring with a new set of servers
func (ring *ConsistentHashRing) Rebalance(servers []string) {
	ring.mutex.Lock()
	defer ring.mutex.Unlock()

	// Clear the current hash ring
	ring.virtualNodes = make(map[uint32]string)
	ring.sortedHashes = make([]uint32, 0)
	ring.serverToHashes = make(map[string][]uint32)

	// Add all the new servers
	for _, server := range servers {
		// Create a slice to store this server's hashes
		hashes := make([]uint32, 0, ring.replicaCount)

		// Add virtual nodes for this server
		for i := 0; i < ring.replicaCount; i++ {
			// Create a unique key for each virtual node
			virtualKey := server + ":" + strconv.Itoa(i)
			hash := fnv1aHash(virtualKey)

			// Store the mapping from hash to server
			ring.virtualNodes[hash] = server
			
			// Add to our list of hashes
			ring.sortedHashes = append(ring.sortedHashes, hash)
			
			// Record that this hash belongs to this server
			hashes = append(hashes, hash)
		}

		// Store the server's hashes for easy removal later
		ring.serverToHashes[server] = hashes
	}

	// Sort the hashes
	sort.Slice(ring.sortedHashes, func(i, j int) bool {
		return ring.sortedHashes[i] < ring.sortedHashes[j]
	})
}

// fnv1aHash implements the FNV-1a hash algorithm
func fnv1aHash(s string) uint32 {
	const prime = uint32(16777619)
	const offsetBasis = uint32(2166136261)

	hash := offsetBasis
	for i := 0; i < len(s); i++ {
		hash ^= uint32(s[i])
		hash *= prime
	}
	return hash
}