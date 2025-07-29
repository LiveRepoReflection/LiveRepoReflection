// Package distkvstore implements a distributed key-value store with consistent hashing
// and replication for fault tolerance.
package distkvstore

import (
	"crypto/md5"
	"encoding/binary"
	"fmt"
	"sort"
	"sync"
)

const (
	// Number of virtual nodes per physical node
	virtualNodesPerNode = 200
)

// DistributedStore represents a distributed key-value store
type DistributedStore struct {
	// Replication factor
	replicationFactor int
	// Map of node ID to node instance
	nodes map[string]*node
	// Virtual nodes on the consistent hash ring, sorted by position
	ring []virtualNode
	// Mutex to protect the store during concurrent operations
	mu sync.RWMutex
}

// node represents a physical node in the cluster
type node struct {
	// Node's unique identifier
	id string
	// Data stored on this node
	data map[string]string
	// Mutex to protect node's data during concurrent operations
	mu sync.RWMutex
}

// virtualNode represents a virtual node on the consistent hash ring
type virtualNode struct {
	// Position on the ring (hash value)
	position uint64
	// Reference to the physical node
	nodeID string
}

// NewDistributedStore creates a new distributed key-value store with the given replication factor
func NewDistributedStore(replicationFactor int) *DistributedStore {
	if replicationFactor < 1 {
		replicationFactor = 1
	}
	return &DistributedStore{
		replicationFactor: replicationFactor,
		nodes:             make(map[string]*node),
		ring:              []virtualNode{},
	}
}

// AddNode adds a new node to the cluster
func (s *DistributedStore) AddNode(nodeID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	// Check if the node already exists
	if _, exists := s.nodes[nodeID]; exists {
		return fmt.Errorf("node %s already exists", nodeID)
	}
	
	// Create a new node
	newNode := &node{
		id:   nodeID,
		data: make(map[string]string),
	}
	s.nodes[nodeID] = newNode
	
	// Add virtual nodes to the ring
	for i := 0; i < virtualNodesPerNode; i++ {
		vNodeID := fmt.Sprintf("%s-%d", nodeID, i)
		position := s.hashKey(vNodeID)
		s.ring = append(s.ring, virtualNode{position: position, nodeID: nodeID})
	}
	
	// Sort the ring
	s.sortRing()
	
	// Rebalance data for the new node
	s.rebalanceData()
	
	return nil
}

// RemoveNode removes a node from the cluster
func (s *DistributedStore) RemoveNode(nodeID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	// Check if the node exists
	node, exists := s.nodes[nodeID]
	if !exists {
		return fmt.Errorf("node %s does not exist", nodeID)
	}
	
	// Get all keys from the node being removed
	node.mu.RLock()
	keysToRedistribute := make([]string, 0, len(node.data))
	dataToRedistribute := make(map[string]string)
	for k, v := range node.data {
		keysToRedistribute = append(keysToRedistribute, k)
		dataToRedistribute[k] = v
	}
	node.mu.RUnlock()
	
	// Remove virtual nodes from the ring
	newRing := []virtualNode{}
	for _, vNode := range s.ring {
		if vNode.nodeID != nodeID {
			newRing = append(newRing, vNode)
		}
	}
	s.ring = newRing
	
	// Remove the node
	delete(s.nodes, nodeID)
	
	// Redistribute data to remaining nodes
	for _, key := range keysToRedistribute {
		// Find the new target nodes for this key, ignoring errors
		targetNodes, _ := s.findTargetNodes(key)
		value := dataToRedistribute[key]
		
		// Store the data on the target nodes
		for _, targetNodeID := range targetNodes {
			if targetNode, exists := s.nodes[targetNodeID]; exists {
				targetNode.mu.Lock()
				targetNode.data[key] = value
				targetNode.mu.Unlock()
			}
		}
	}
	
	return nil
}

// Put stores a key-value pair in the cluster
func (s *DistributedStore) Put(key string, value string) error {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	// If no nodes exist, return an error
	if len(s.nodes) == 0 {
		return fmt.Errorf("no nodes in the cluster")
	}
	
	// Find the target nodes for this key
	targetNodes, err := s.findTargetNodes(key)
	if err != nil {
		return err
	}
	
	// Store the data on each target node
	for _, nodeID := range targetNodes {
		node := s.nodes[nodeID]
		node.mu.Lock()
		node.data[key] = value
		node.mu.Unlock()
	}
	
	return nil
}

// Get retrieves the value associated with a given key
func (s *DistributedStore) Get(key string) (string, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	// If no nodes exist, return an error
	if len(s.nodes) == 0 {
		return "", fmt.Errorf("no nodes in the cluster")
	}
	
	// Find the target nodes for this key
	targetNodes, err := s.findTargetNodes(key)
	if err != nil {
		return "", err
	}
	
	// Try to get the value from the primary node first
	primaryNodeID := targetNodes[0]
	primaryNode := s.nodes[primaryNodeID]
	
	primaryNode.mu.RLock()
	value, exists := primaryNode.data[key]
	primaryNode.mu.RUnlock()
	
	if exists {
		// Value found on primary node, check for inconsistencies in replicas
		s.performReadRepair(key, value, targetNodes)
		return value, nil
	}
	
	// Value not found on primary, try replica nodes
	var lastErr error
	for i := 1; i < len(targetNodes); i++ {
		replicaNodeID := targetNodes[i]
		replicaNode := s.nodes[replicaNodeID]
		
		replicaNode.mu.RLock()
		value, exists = replicaNode.data[key]
		replicaNode.mu.RUnlock()
		
		if exists {
			// Found on replica, perform read repair and return
			s.performReadRepair(key, value, targetNodes)
			return value, nil
		}
	}
	
	// Key not found on any node
	if lastErr != nil {
		return "", lastErr
	}
	return "", fmt.Errorf("key %s not found", key)
}

// ListNodes returns a sorted slice of nodeIDs currently in the cluster
func (s *DistributedStore) ListNodes() []string {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	nodeIDs := make([]string, 0, len(s.nodes))
	for nodeID := range s.nodes {
		nodeIDs = append(nodeIDs, nodeID)
	}
	
	sort.Strings(nodeIDs)
	return nodeIDs
}

// findTargetNodes finds the N nodes responsible for storing a key
func (s *DistributedStore) findTargetNodes(key string) ([]string, error) {
	if len(s.ring) == 0 {
		return nil, fmt.Errorf("hash ring is empty")
	}
	
	// Hash the key
	hash := s.hashKey(key)
	
	// Find the first node on the ring
	idx := s.findNodeIdx(hash)
	firstVirtualNode := s.ring[idx]
	
	// Collect unique node IDs, starting with the first node
	targetNodeIDs := []string{firstVirtualNode.nodeID}
	uniqueNodes := map[string]struct{}{firstVirtualNode.nodeID: {}}
	
	// If replication factor is 1 or there's only one node, we're done
	if s.replicationFactor == 1 || len(s.nodes) == 1 {
		return targetNodeIDs, nil
	}
	
	// Find additional unique nodes for replication
	currentIdx := (idx + 1) % len(s.ring)
	for len(targetNodeIDs) < s.replicationFactor && len(targetNodeIDs) < len(s.nodes) {
		nodeID := s.ring[currentIdx].nodeID
		if _, alreadySelected := uniqueNodes[nodeID]; !alreadySelected {
			targetNodeIDs = append(targetNodeIDs, nodeID)
			uniqueNodes[nodeID] = struct{}{}
		}
		currentIdx = (currentIdx + 1) % len(s.ring)
	}
	
	return targetNodeIDs, nil
}

// findNodeIdx finds the index of the node responsible for a given hash
func (s *DistributedStore) findNodeIdx(hash uint64) int {
	// Binary search for the node
	idx := sort.Search(len(s.ring), func(i int) bool {
		return s.ring[i].position >= hash
	})
	
	// Wrap around if needed
	if idx == len(s.ring) {
		idx = 0
	}
	
	return idx
}

// performReadRepair ensures all replicas have the correct value
func (s *DistributedStore) performReadRepair(key string, correctValue string, targetNodes []string) {
	for _, nodeID := range targetNodes {
		node := s.nodes[nodeID]
		
		// Check if repair is needed
		node.mu.RLock()
		storedValue, exists := node.data[key]
		node.mu.RUnlock()
		
		if !exists || storedValue != correctValue {
			// Repair the node
			node.mu.Lock()
			node.data[key] = correctValue
			node.mu.Unlock()
		}
	}
}

// hashKey hashes a key to a position on the ring
func (s *DistributedStore) hashKey(key string) uint64 {
	hash := md5.Sum([]byte(key))
	return binary.BigEndian.Uint64(hash[:8])
}

// sortRing sorts the virtual nodes by position
func (s *DistributedStore) sortRing() {
	sort.Slice(s.ring, func(i, j int) bool {
		return s.ring[i].position < s.ring[j].position
	})
}

// rebalanceData redistributes data after node addition or removal
func (s *DistributedStore) rebalanceData() {
	// Collect all keys from all nodes
	allKeys := make(map[string]string)
	
	for _, node := range s.nodes {
		node.mu.RLock()
		for k, v := range node.data {
			allKeys[k] = v
		}
		node.mu.RUnlock()
	}
	
	// Clear data from all nodes
	for _, node := range s.nodes {
		node.mu.Lock()
		node.data = make(map[string]string)
		node.mu.Unlock()
	}
	
	// Redistribute data according to the new ring
	for key, value := range allKeys {
		// Find the target nodes
		targetNodes, err := s.findTargetNodes(key)
		if err != nil {
			continue
		}
		
		// Store the data on the target nodes
		for _, targetNodeID := range targetNodes {
			targetNode := s.nodes[targetNodeID]
			targetNode.mu.Lock()
			targetNode.data[key] = value
			targetNode.mu.Unlock()
		}
	}
}