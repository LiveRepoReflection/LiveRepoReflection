package dist_kv_range

import (
	"hash/crc32"
	"sort"
	"strconv"
	"sync"
)

type Node struct {
	id   string
	data map[uint64]string
	mu   sync.RWMutex
}

func NewNode(id string) *Node {
	return &Node{
		id:   id,
		data: make(map[uint64]string),
	}
}

func (n *Node) Put(key uint64, value string) {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.data[key] = value
}

func (n *Node) Get(key uint64) string {
	n.mu.RLock()
	defer n.mu.RUnlock()
	return n.data[key]
}

func (n *Node) RangeQuery(startKey, endKey uint64) map[uint64]string {
	result := make(map[uint64]string)
	n.mu.RLock()
	defer n.mu.RUnlock()
	for k, v := range n.data {
		if k >= startKey && k <= endKey {
			result[k] = v
		}
	}
	return result
}

type ConsistentHashRing struct {
	nodes       []*Node
	ring        []uint32
	nodeMap     map[uint32]*Node
	replication int
	mu          sync.RWMutex
}

func newConsistentHashRing(nodes []*Node, replication int) *ConsistentHashRing {
	chr := &ConsistentHashRing{
		nodes:       nodes,
		replication: replication,
		nodeMap:     make(map[uint32]*Node),
	}
	chr.generateRing()
	return chr
}

func (chr *ConsistentHashRing) generateRing() {
	chr.mu.Lock()
	defer chr.mu.Unlock()
	chr.ring = nil
	chr.nodeMap = make(map[uint32]*Node)
	for _, node := range chr.nodes {
		for i := 0; i < chr.replication; i++ {
			vnodeKey := node.id + "#" + strconv.Itoa(i)
			hash := crc32.ChecksumIEEE([]byte(vnodeKey))
			chr.ring = append(chr.ring, hash)
			chr.nodeMap[hash] = node
		}
	}
	sort.Slice(chr.ring, func(i, j int) bool {
		return chr.ring[i] < chr.ring[j]
	})
}

func (chr *ConsistentHashRing) getNode(key uint64) *Node {
	chr.mu.RLock()
	defer chr.mu.RUnlock()
	keyBytes := []byte(strconv.FormatUint(key, 10))
	h := crc32.ChecksumIEEE(keyBytes)
	idx := sort.Search(len(chr.ring), func(i int) bool { return chr.ring[i] >= h })
	if idx == len(chr.ring) {
		idx = 0
	}
	return chr.nodeMap[chr.ring[idx]]
}

type Store struct {
	nodes []*Node
	ring  *ConsistentHashRing
}

func NewStore(nodeCount int) *Store {
	nodes := make([]*Node, nodeCount)
	for i := 0; i < nodeCount; i++ {
		nodes[i] = NewNode("node_" + strconv.Itoa(i))
	}
	ring := newConsistentHashRing(nodes, 3)
	return &Store{
		nodes: nodes,
		ring:  ring,
	}
}

func (s *Store) Put(key uint64, value string) {
	node := s.ring.getNode(key)
	node.Put(key, value)
}

func (s *Store) Get(key uint64) string {
	node := s.ring.getNode(key)
	return node.Get(key)
}

func (s *Store) RangeQuery(startKey, endKey uint64) map[uint64]string {
	result := make(map[uint64]string)
	if startKey > endKey {
		return result
	}
	var wg sync.WaitGroup
	var mu sync.Mutex
	for _, node := range s.nodes {
		wg.Add(1)
		go func(n *Node) {
			defer wg.Done()
			partial := n.RangeQuery(startKey, endKey)
			mu.Lock()
			for k, v := range partial {
				result[k] = v
			}
			mu.Unlock()
		}(node)
	}
	wg.Wait()
	return result
}