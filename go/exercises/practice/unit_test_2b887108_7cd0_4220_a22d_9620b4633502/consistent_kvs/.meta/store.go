package consistent_kvs

import (
	"errors"
	"hash/fnv"
	"sync"
)

var ErrKeyNotFound = errors.New("key not found")
var ErrReplicationFailure = errors.New("no available nodes for replication")

type Node struct {
	id     int
	data   map[string]string
	failed bool
	mu     sync.RWMutex
}

func (n *Node) Put(key, value string) {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.data[key] = value
}

func (n *Node) Get(key string) (string, error) {
	n.mu.RLock()
	defer n.mu.RUnlock()
	if val, ok := n.data[key]; ok {
		return val, nil
	}
	return "", ErrKeyNotFound
}

type Store struct {
	nodes             []*Node
	replicationFactor int
	totalNodes        int
	mu                sync.Mutex
}

func NewStore(totalNodes int, replicationFactor int) (*Store, error) {
	if totalNodes <= 0 || replicationFactor <= 0 || replicationFactor > totalNodes {
		return nil, errors.New("invalid configuration: ensure totalNodes > 0, replicationFactor > 0 and replicationFactor <= totalNodes")
	}
	nodes := make([]*Node, totalNodes)
	for i := 0; i < totalNodes; i++ {
		nodes[i] = &Node{
			id:   i,
			data: make(map[string]string),
		}
	}
	return &Store{
		nodes:             nodes,
		replicationFactor: replicationFactor,
		totalNodes:        totalNodes,
	}, nil
}

func hashKey(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

// getReplicaIndices calculates the nodes responsible for storing a given key.
func (s *Store) getReplicaIndices(key string) []int {
	start := int(hashKey(key)) % s.totalNodes
	indices := make([]int, 0, s.replicationFactor)
	for i := 0; i < s.replicationFactor; i++ {
		indices = append(indices, (start+i)%s.totalNodes)
	}
	return indices
}

// Put writes a key-value pair to available replica nodes in a sequential order.
func (s *Store) Put(key, value string) error {
	// Locking the entire store to emulate consensus ordering for sequential consistency.
	s.mu.Lock()
	defer s.mu.Unlock()

	indices := s.getReplicaIndices(key)
	available := 0
	for _, idx := range indices {
		node := s.nodes[idx]
		node.mu.RLock()
		failed := node.failed
		node.mu.RUnlock()
		if !failed {
			node.Put(key, value)
			available++
		}
	}
	if available == 0 {
		return ErrReplicationFailure
	}
	return nil
}

// Get retrieves the value associated with the key from one of its replica nodes.
func (s *Store) Get(key string) (string, error) {
	indices := s.getReplicaIndices(key)
	for _, idx := range indices {
		node := s.nodes[idx]
		node.mu.RLock()
		failed := node.failed
		node.mu.RUnlock()
		if !failed {
			if val, err := node.Get(key); err == nil {
				return val, nil
			}
		}
	}
	return "", ErrKeyNotFound
}

// SimulateNodeFailure marks a node as failed, so it will not be used in future operations.
func (s *Store) SimulateNodeFailure(nodeIndex int) error {
	if nodeIndex < 0 || nodeIndex >= s.totalNodes {
		return errors.New("invalid node index")
	}
	node := s.nodes[nodeIndex]
	node.mu.Lock()
	defer node.mu.Unlock()
	node.failed = true
	return nil
}