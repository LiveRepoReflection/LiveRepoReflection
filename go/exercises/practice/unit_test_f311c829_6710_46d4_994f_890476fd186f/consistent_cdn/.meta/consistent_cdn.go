package consistentcdn

import (
	"crypto/md5"
	"encoding/binary"
	"sort"
	"sync"
)

type CDN struct {
	replicationFactor int
	ring             *hashRing
	mu               sync.RWMutex
}

type hashRing struct {
	nodes     []uint64       // Sorted hash values
	nodeMap   map[uint64]string // Map from hash to server ID
	serverMap map[string]bool   // Map of server availability
}

func NewCDN(replicationFactor int) *CDN {
	if replicationFactor < 1 {
		replicationFactor = 1
	}
	return &CDN{
		replicationFactor: replicationFactor,
		ring: &hashRing{
			nodes:     make([]uint64, 0),
			nodeMap:   make(map[uint64]string),
			serverMap: make(map[string]bool),
		},
	}
}

func (cdn *CDN) AddServer(serverID string) {
	cdn.mu.Lock()
	defer cdn.mu.Unlock()

	// Generate multiple hash values for each server for better distribution
	for i := 0; i < 100; i++ {
		hash := cdn.hashKey(serverID + string(rune(i)))
		cdn.ring.nodes = append(cdn.ring.nodes, hash)
		cdn.ring.nodeMap[hash] = serverID
	}

	sort.Slice(cdn.ring.nodes, func(i, j int) bool {
		return cdn.ring.nodes[i] < cdn.ring.nodes[j]
	})

	cdn.ring.serverMap[serverID] = true
}

func (cdn *CDN) RemoveServer(serverID string) {
	cdn.mu.Lock()
	defer cdn.mu.Unlock()

	newNodes := make([]uint64, 0)
	for _, hash := range cdn.ring.nodes {
		if cdn.ring.nodeMap[hash] != serverID {
			newNodes = append(newNodes, hash)
		} else {
			delete(cdn.ring.nodeMap, hash)
		}
	}
	cdn.ring.nodes = newNodes
	delete(cdn.ring.serverMap, serverID)
}

func (cdn *CDN) SetServerAvailability(serverID string, available bool) {
	cdn.mu.Lock()
	defer cdn.mu.Unlock()

	cdn.ring.serverMap[serverID] = available
}

func (cdn *CDN) GetServerForKey(key string) string {
	cdn.mu.RLock()
	defer cdn.mu.RUnlock()

	if len(cdn.ring.nodes) == 0 {
		return ""
	}

	hash := cdn.hashKey(key)
	idx := cdn.findNextNode(hash)
	
	// Find the first available server
	for i := 0; i < len(cdn.ring.nodes); i++ {
		serverID := cdn.ring.nodeMap[cdn.ring.nodes[idx]]
		if cdn.ring.serverMap[serverID] {
			return serverID
		}
		idx = (idx + 1) % len(cdn.ring.nodes)
	}

	return ""
}

func (cdn *CDN) GetReplicasForKey(key string) []string {
	cdn.mu.RLock()
	defer cdn.mu.RUnlock()

	if len(cdn.ring.nodes) == 0 {
		return nil
	}

	hash := cdn.hashKey(key)
	idx := cdn.findNextNode(hash)
	
	seen := make(map[string]bool)
	replicas := make([]string, 0, cdn.replicationFactor)

	// Find k available unique servers
	for i := 0; i < len(cdn.ring.nodes) && len(replicas) < cdn.replicationFactor; i++ {
		serverID := cdn.ring.nodeMap[cdn.ring.nodes[idx]]
		if cdn.ring.serverMap[serverID] && !seen[serverID] {
			replicas = append(replicas, serverID)
			seen[serverID] = true
		}
		idx = (idx + 1) % len(cdn.ring.nodes)
	}

	return replicas
}

func (cdn *CDN) hashKey(key string) uint64 {
	hash := md5.Sum([]byte(key))
	return binary.BigEndian.Uint64(hash[:8])
}

func (cdn *CDN) findNextNode(hash uint64) int {
	nodes := cdn.ring.nodes
	n := len(nodes)
	idx := sort.Search(n, func(i int) bool {
		return nodes[i] >= hash
	})
	if idx == n {
		idx = 0
	}
	return idx
}