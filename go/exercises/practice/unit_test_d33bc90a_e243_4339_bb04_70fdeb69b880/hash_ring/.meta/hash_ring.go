package hashring

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"sort"
	"sync"
)

// Ring represents the consistent hash ring
type Ring struct {
	mutex       sync.RWMutex
	nodes       map[string]*node
	sortedKeys  []uint64
	keyToNode   map[uint64]string
	replicaFunc func(nodeName string, idx int) uint64
}

// node represents a physical node and its virtual nodes
type node struct {
	name         string
	virtualNodes int
	hashKeys     []uint64
}

// New creates a new consistent hash ring
func New() *Ring {
	return &Ring{
		nodes:      make(map[string]*node),
		keyToNode:  make(map[uint64]string),
		sortedKeys: make([]uint64, 0),
		replicaFunc: func(nodeName string, idx int) uint64 {
			hash := sha256.New()
			hash.Write([]byte(fmt.Sprintf("%s-%d", nodeName, idx)))
			hashBytes := hash.Sum(nil)
			return binary.BigEndian.Uint64(hashBytes)
		},
	}
}

// AddNode adds a new node to the hash ring with the specified number of virtual nodes
func (r *Ring) AddNode(nodeName string, virtualNodes int) error {
	if nodeName == "" {
		return fmt.Errorf("node name cannot be empty")
	}
	if virtualNodes <= 0 {
		return fmt.Errorf("virtual nodes must be greater than 0")
	}

	r.mutex.Lock()
	defer r.mutex.Unlock()

	if _, exists := r.nodes[nodeName]; exists {
		return fmt.Errorf("node %s already exists", nodeName)
	}

	newNode := &node{
		name:         nodeName,
		virtualNodes: virtualNodes,
		hashKeys:     make([]uint64, 0, virtualNodes),
	}

	// Generate hash keys for virtual nodes
	for i := 0; i < virtualNodes; i++ {
		hashKey := r.replicaFunc(nodeName, i)
		newNode.hashKeys = append(newNode.hashKeys, hashKey)
		r.keyToNode[hashKey] = nodeName
		r.sortedKeys = append(r.sortedKeys, hashKey)
	}

	// Sort the keys
	sort.Slice(r.sortedKeys, func(i, j int) bool {
		return r.sortedKeys[i] < r.sortedKeys[j]
	})

	r.nodes[nodeName] = newNode
	return nil
}

// RemoveNode removes a node from the hash ring
func (r *Ring) RemoveNode(nodeName string) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	node, exists := r.nodes[nodeName]
	if !exists {
		return fmt.Errorf("node %s does not exist", nodeName)
	}

	// Remove all virtual nodes
	for _, hashKey := range node.hashKeys {
		delete(r.keyToNode, hashKey)
	}

	// Rebuild sorted keys
	newSortedKeys := make([]uint64, 0, len(r.sortedKeys)-node.virtualNodes)
	for _, key := range r.sortedKeys {
		if r.keyToNode[key] != nodeName {
			newSortedKeys = append(newSortedKeys, key)
		}
	}
	r.sortedKeys = newSortedKeys

	delete(r.nodes, nodeName)
	return nil
}

// GetNode returns the node responsible for the given key
func (r *Ring) GetNode(key string) (string, error) {
	if key == "" {
		return "", fmt.Errorf("key cannot be empty")
	}

	r.mutex.RLock()
	defer r.mutex.RUnlock()

	if len(r.sortedKeys) == 0 {
		return "", fmt.Errorf("hash ring is empty")
	}

	hash := r.hash(key)
	idx := r.search(hash)
	if idx >= len(r.sortedKeys) {
		idx = 0
	}
	return r.keyToNode[r.sortedKeys[idx]], nil
}

// Size returns the number of physical nodes in the ring
func (r *Ring) Size() int {
	r.mutex.RLock()
	defer r.mutex.RUnlock()
	return len(r.nodes)
}

// hash generates a hash for the given key
func (r *Ring) hash(key string) uint64 {
	hash := sha256.New()
	hash.Write([]byte(key))
	hashBytes := hash.Sum(nil)
	return binary.BigEndian.Uint64(hashBytes)
}

// search performs binary search to find the appropriate node for a hash
func (r *Ring) search(hash uint64) int {
	idx := sort.Search(len(r.sortedKeys), func(i int) bool {
		return r.sortedKeys[i] >= hash
	})
	return idx
}

// GetNodeDistribution returns a map of node names to their key counts
// This can be used to monitor load distribution
func (r *Ring) GetNodeDistribution(sampleKeys []string) map[string]int {
	r.mutex.RLock()
	defer r.mutex.RUnlock()

	distribution := make(map[string]int)
	for _, key := range sampleKeys {
		if node, err := r.GetNode(key); err == nil {
			distribution[node]++
		}
	}
	return distribution
}

// GetAffectedKeys returns the keys that would need to be remapped if a node is added or removed
func (r *Ring) GetAffectedKeys(keys []string, nodeChange string, isAddition bool) (map[string]string, error) {
	affected := make(map[string]string)

	// Store current mappings
	originalMapping := make(map[string]string)
	for _, key := range keys {
		if node, err := r.GetNode(key); err == nil {
			originalMapping[key] = node
		}
	}

	// Simulate node change
	if isAddition {
		if err := r.AddNode(nodeChange, 10); err != nil {
			return nil, err
		}
		defer r.RemoveNode(nodeChange)
	} else {
		if err := r.RemoveNode(nodeChange); err != nil {
			return nil, err
		}
		defer r.AddNode(nodeChange, 10)
	}

	// Check which keys changed mapping
	for _, key := range keys {
		if newNode, err := r.GetNode(key); err == nil {
			if originalNode, exists := originalMapping[key]; exists && newNode != originalNode {
				affected[key] = newNode
			}
		}
	}

	return affected, nil
}