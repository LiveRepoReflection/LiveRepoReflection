package consistent_hashlb

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"fmt"
	"net"
	"sort"
	"sync"
)

// LoadBalancer represents the consistent hashing load balancer
type LoadBalancer struct {
	ring        map[uint64]string    // hash ring mapping
	servers     map[string]struct{}  // set of physical servers
	sortedHashes []uint64           // sorted list of hash values
	virtualNodes int                // number of virtual nodes per server
	ringSize     uint64            // size of the hash ring
	mu          sync.RWMutex       // mutex for thread safety
}

// NewLoadBalancer creates a new load balancer instance
func NewLoadBalancer(ringSize uint64, virtualNodes int) (*LoadBalancer, error) {
	if ringSize == 0 {
		return nil, errors.New("ring size must be greater than 0")
	}
	if virtualNodes <= 0 {
		return nil, errors.New("number of virtual nodes must be greater than 0")
	}

	return &LoadBalancer{
		ring:         make(map[uint64]string),
		servers:      make(map[string]struct{}),
		sortedHashes: make([]uint64, 0),
		virtualNodes: virtualNodes,
		ringSize:     ringSize,
	}, nil
}

// validateServerAddress checks if the server address is valid
func validateServerAddress(address string) error {
	if address == "" {
		return errors.New("server address cannot be empty")
	}
	host, port, err := net.SplitHostPort(address)
	if err != nil {
		return fmt.Errorf("invalid address format: %v", err)
	}
	if host == "" || port == "" {
		return errors.New("invalid address: host and port required")
	}
	return nil
}

// hash generates a hash value for a given key
func (lb *LoadBalancer) hash(key string) uint64 {
	hasher := sha256.New()
	hasher.Write([]byte(key))
	hash := hasher.Sum(nil)
	return binary.BigEndian.Uint64(hash) % lb.ringSize
}

// AddServer adds a new server to the load balancer
func (lb *LoadBalancer) AddServer(address string) error {
	if err := validateServerAddress(address); err != nil {
		return err
	}

	lb.mu.Lock()
	defer lb.mu.Unlock()

	if _, exists := lb.servers[address]; exists {
		return fmt.Errorf("server %s already exists", address)
	}

	// Add server to the set of physical servers
	lb.servers[address] = struct{}{}

	// Add virtual nodes to the hash ring
	for i := 0; i < lb.virtualNodes; i++ {
		virtualNode := fmt.Sprintf("%s-%d", address, i)
		hash := lb.hash(virtualNode)
		lb.ring[hash] = address
		lb.sortedHashes = append(lb.sortedHashes, hash)
	}

	// Sort the hashes
	sort.Slice(lb.sortedHashes, func(i, j int) bool {
		return lb.sortedHashes[i] < lb.sortedHashes[j]
	})

	return nil
}

// RemoveServer removes a server from the load balancer
func (lb *LoadBalancer) RemoveServer(address string) error {
	if err := validateServerAddress(address); err != nil {
		return err
	}

	lb.mu.Lock()
	defer lb.mu.Unlock()

	if _, exists := lb.servers[address]; !exists {
		return fmt.Errorf("server %s does not exist", address)
	}

	// Remove server from the set of physical servers
	delete(lb.servers, address)

	// Remove virtual nodes from the hash ring
	newSortedHashes := make([]uint64, 0, len(lb.sortedHashes))
	for _, hash := range lb.sortedHashes {
		if lb.ring[hash] != address {
			newSortedHashes = append(newSortedHashes, hash)
		}
		if lb.ring[hash] == address {
			delete(lb.ring, hash)
		}
	}
	lb.sortedHashes = newSortedHashes

	return nil
}

// GetServer returns the server that should handle the given key
func (lb *LoadBalancer) GetServer(key string) (string, error) {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	if len(lb.servers) == 0 {
		return "", errors.New("no servers available")
	}

	hash := lb.hash(key)
	
	// Binary search to find the first hash greater than or equal to the key hash
	idx := sort.Search(len(lb.sortedHashes), func(i int) bool {
		return lb.sortedHashes[i] >= hash
	})

	// Wrap around to the first hash if necessary
	if idx >= len(lb.sortedHashes) {
		idx = 0
	}

	return lb.ring[lb.sortedHashes[idx]], nil
}

// GetServerLoad returns the current load (number of keys) for each server
func (lb *LoadBalancer) GetServerLoad() map[string]int {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	load := make(map[string]int)
	for _, server := range lb.servers {
		load[fmt.Sprint(server)] = 0
	}

	for hash := uint64(0); hash < lb.ringSize; hash++ {
		server, err := lb.GetServer(fmt.Sprint(hash))
		if err == nil {
			load[server]++
		}
	}

	return load
}

// GetServerCount returns the number of servers in the load balancer
func (lb *LoadBalancer) GetServerCount() int {
	lb.mu.RLock()
	defer lb.mu.RUnlock()
	return len(lb.servers)
}

// GetVirtualNodeCount returns the total number of virtual nodes in the system
func (lb *LoadBalancer) GetVirtualNodeCount() int {
	lb.mu.RLock()
	defer lb.mu.RUnlock()
	return len(lb.sortedHashes)
}