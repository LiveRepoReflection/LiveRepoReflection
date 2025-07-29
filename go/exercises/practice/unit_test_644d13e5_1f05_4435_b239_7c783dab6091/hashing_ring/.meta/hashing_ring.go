package hashing_ring

import (
	"crypto/sha256"
	"encoding/binary"
	"sort"
	"sync"
)

type ConsistentHashingRing struct {
	virtualNodes  int
	ring          map[uint32]string
	nodes         map[string]bool
	sortedHashes  []uint32
	virtualToReal map[uint32]string
	mu            sync.RWMutex
}

func NewConsistentHashingRing(virtualNodes int) *ConsistentHashingRing {
	if virtualNodes <= 0 {
		panic("virtualNodes must be positive")
	}
	return &ConsistentHashingRing{
		virtualNodes:  virtualNodes,
		ring:          make(map[uint32]string),
		nodes:         make(map[string]bool),
		sortedHashes:  make([]uint32, 0),
		virtualToReal: make(map[uint32]string),
	}
}

func (c *ConsistentHashingRing) AddNode(nodeID string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.nodes[nodeID] {
		return
	}

	c.nodes[nodeID] = true

	for i := 0; i < c.virtualNodes; i++ {
		virtualNode := nodeID + "_" + string(rune(i))
		hash := c.hash(virtualNode)
		c.ring[hash] = nodeID
		c.virtualToReal[hash] = nodeID
		c.sortedHashes = append(c.sortedHashes, hash)
	}

	sort.Slice(c.sortedHashes, func(i, j int) bool {
		return c.sortedHashes[i] < c.sortedHashes[j]
	})
}

func (c *ConsistentHashingRing) RemoveNode(nodeID string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if !c.nodes[nodeID] {
		return
	}

	delete(c.nodes, nodeID)

	newHashes := make([]uint32, 0, len(c.sortedHashes))
	for _, hash := range c.sortedHashes {
		if c.virtualToReal[hash] != nodeID {
			newHashes = append(newHashes, hash)
		} else {
			delete(c.ring, hash)
			delete(c.virtualToReal, hash)
		}
	}

	c.sortedHashes = newHashes
}

func (c *ConsistentHashingRing) GetNode(key string) string {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if len(c.sortedHashes) == 0 {
		return ""
	}

	hash := c.hash(key)
	idx := sort.Search(len(c.sortedHashes), func(i int) bool {
		return c.sortedHashes[i] >= hash
	})

	if idx == len(c.sortedHashes) {
		idx = 0
	}

	return c.ring[c.sortedHashes[idx]]
}

func (c *ConsistentHashingRing) ListNodes() []string {
	c.mu.RLock()
	defer c.mu.RUnlock()

	nodes := make([]string, 0, len(c.nodes))
	for node := range c.nodes {
		nodes = append(nodes, node)
	}
	sort.Strings(nodes)
	return nodes
}

func (c *ConsistentHashingRing) hash(key string) uint32 {
	h := sha256.New()
	h.Write([]byte(key))
	sum := h.Sum(nil)
	return binary.BigEndian.Uint32(sum[:4])
}