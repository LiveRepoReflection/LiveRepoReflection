package range_store

import (
	"errors"
	"sort"
	"sync"
)

type KeyValue struct {
	Key   uint64
	Value string
}

type Node struct {
	startKey uint64
	endKey   uint64
	data     map[uint64]string
	mu       sync.RWMutex
	failed   bool
}

type RangeStore struct {
	nodes          []*Node
	replication    int
	nodeRanges     []struct{ start, end uint64 }
	consistentHash []uint64
}

func NewRangeStore(numNodes, replicationFactor int) *RangeStore {
	store := &RangeStore{
		nodes:       make([]*Node, numNodes),
		replication: replicationFactor,
	}

	// Calculate key ranges for each node
	rangeSize := ^uint64(0) / uint64(numNodes)
	for i := 0; i < numNodes; i++ {
		start := uint64(i) * rangeSize
		end := start + rangeSize - 1
		if i == numNodes-1 {
			end = ^uint64(0)
		}

		store.nodes[i] = &Node{
			startKey: start,
			endKey:   end,
			data:     make(map[uint64]string),
		}

		store.nodeRanges = append(store.nodeRanges, struct{ start, end uint64 }{start, end})
	}

	return store
}

func (rs *RangeStore) findNodesForKey(key uint64) []*Node {
	var nodes []*Node
	for i := 0; i < rs.replication; i++ {
		// Simple consistent hashing by finding the first node that covers the key
		// and then wrapping around for replication
		nodeIndex := 0
		for j, r := range rs.nodeRanges {
			if key >= r.start && key <= r.end {
				nodeIndex = j
				break
			}
		}

		// Get the next nodes in sequence for replication
		replicaIndex := (nodeIndex + i) % len(rs.nodes)
		nodes = append(nodes, rs.nodes[replicaIndex])
	}
	return nodes
}

func (rs *RangeStore) Put(key uint64, value string) error {
	nodes := rs.findNodesForKey(key)

	var lastError error
	successCount := 0

	for _, node := range nodes {
		node.mu.Lock()
		if !node.failed {
			node.data[key] = value
			successCount++
		} else {
			lastError = errors.New("node failed")
		}
		node.mu.Unlock()
	}

	if successCount == 0 {
		return lastError
	}
	return nil
}

func (rs *RangeStore) Get(key uint64) (string, error) {
	nodes := rs.findNodesForKey(key)

	for _, node := range nodes {
		node.mu.RLock()
		if !node.failed {
			if value, exists := node.data[key]; exists {
				node.mu.RUnlock()
				return value, nil
			}
		}
		node.mu.RUnlock()
	}

	return "", errors.New("key not found")
}

func (rs *RangeStore) RangeQuery(startKey, endKey uint64) ([]KeyValue, error) {
	if startKey > endKey {
		return nil, nil
	}

	var results []KeyValue
	var mu sync.Mutex
	var wg sync.WaitGroup

	for _, node := range rs.nodes {
		wg.Add(1)
		go func(n *Node) {
			defer wg.Done()

			n.mu.RLock()
			defer n.mu.RUnlock()

			if n.failed {
				return
			}

			var nodeResults []KeyValue
			for key, value := range n.data {
				if key >= startKey && key <= endKey {
					nodeResults = append(nodeResults, KeyValue{Key: key, Value: value})
				}
			}

			mu.Lock()
			results = append(results, nodeResults...)
			mu.Unlock()
		}(node)
	}

	wg.Wait()

	// Sort results by key
	sort.Slice(results, func(i, j int) bool {
		return results[i].Key < results[j].Key
	})

	return results, nil
}

func (rs *RangeStore) NodeStatus() []struct{ Start, End uint64 } {
	var status []struct{ Start, End uint64 }
	for _, node := range rs.nodes {
		status = append(status, struct{ Start, End uint64 }{node.startKey, node.endKey})
	}
	return status
}