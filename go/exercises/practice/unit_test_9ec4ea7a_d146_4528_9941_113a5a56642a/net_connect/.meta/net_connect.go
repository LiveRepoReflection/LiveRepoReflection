package net_connect

import (
	"sync"
)

const MaxNodes = 1000000

type edgeKey struct {
	a, b int
}

func newEdgeKey(a, b int) edgeKey {
	if a > b {
		a, b = b, a
	}
	return edgeKey{a: a, b: b}
}

type DSU struct {
	parent []int
	size   []int
}

func NewDSU() *DSU {
	parent := make([]int, MaxNodes)
	size := make([]int, MaxNodes)
	for i := 0; i < MaxNodes; i++ {
		parent[i] = i
		size[i] = 1
	}
	return &DSU{
		parent: parent,
		size:   size,
	}
}

func (d *DSU) Find(x int) int {
	if d.parent[x] != x {
		d.parent[x] = d.Find(d.parent[x])
	}
	return d.parent[x]
}

func (d *DSU) Union(x, y int) {
	rootX := d.Find(x)
	rootY := d.Find(y)
	if rootX == rootY {
		return
	}
	// Union by size
	if d.size[rootX] < d.size[rootY] {
		d.parent[rootX] = rootY
		d.size[rootY] += d.size[rootX]
	} else {
		d.parent[rootY] = rootX
		d.size[rootX] += d.size[rootY]
	}
}

type Network struct {
	lock     sync.RWMutex
	edges    map[edgeKey]bool
	degree   map[int]int
	active   map[int]bool
	dsu      *DSU
	dsuValid bool
}

// NewNetwork returns a new instance of Network.
func NewNetwork() *Network {
	return &Network{
		edges:    make(map[edgeKey]bool),
		degree:   make(map[int]int),
		active:   make(map[int]bool),
		dsu:      NewDSU(),
		dsuValid: true,
	}
}

// AddConnection adds a bidirectional connection between node1 and node2.
func (n *Network) AddConnection(node1, node2 int) {
	if node1 < 0 || node1 >= MaxNodes || node2 < 0 || node2 >= MaxNodes {
		return
	}
	if node1 == node2 {
		return
	}
	key := newEdgeKey(node1, node2)

	n.lock.Lock()
	defer n.lock.Unlock()

	// if the connection already exists, do nothing
	if n.edges[key] {
		return
	}
	n.edges[key] = true

	// update degree and active nodes for node1
	n.degree[node1]++
	n.active[node1] = true

	// update degree and active nodes for node2
	n.degree[node2]++
	n.active[node2] = true

	// If DSU is valid, update it with the new connection.
	if n.dsuValid {
		n.dsu.Union(node1, node2)
	}
}

// RemoveConnection removes the bidirectional connection between node1 and node2.
func (n *Network) RemoveConnection(node1, node2 int) {
	if node1 < 0 || node1 >= MaxNodes || node2 < 0 || node2 >= MaxNodes {
		return
	}
	if node1 == node2 {
		return
	}
	key := newEdgeKey(node1, node2)

	n.lock.Lock()
	defer n.lock.Unlock()

	// if the connection doesn't exist, do nothing
	if !n.edges[key] {
		return
	}
	delete(n.edges, key)

	// update degree and active nodes for node1
	n.degree[node1]--
	if n.degree[node1] <= 0 {
		delete(n.degree, node1)
		delete(n.active, node1)
	}

	// update degree and active nodes for node2
	n.degree[node2]--
	if n.degree[node2] <= 0 {
		delete(n.degree, node2)
		delete(n.active, node2)
	}

	// Mark DSU as stale; we need to rebuild it on next query.
	n.dsuValid = false
}

// AreConnected returns true if node1 and node2 are connected by any path.
func (n *Network) AreConnected(node1, node2 int) bool {
	if node1 < 0 || node1 >= MaxNodes || node2 < 0 || node2 >= MaxNodes {
		return false
	}
	// Rebuild DSU if needed.
	n.ensureDSU()

	n.lock.RLock()
	defer n.lock.RUnlock()
	return n.dsu.Find(node1) == n.dsu.Find(node2)
}

// FindLargestConnectedComponent returns the size of the largest connected component.
func (n *Network) FindLargestConnectedComponent() int {
	n.ensureDSU()

	n.lock.RLock()
	defer n.lock.RUnlock()

	if len(n.active) == 0 {
		return 0
	}

	compSize := make(map[int]int)
	maxSize := 0
	for node := range n.active {
		parent := n.dsu.Find(node)
		compSize[parent]++
		if compSize[parent] > maxSize {
			maxSize = compSize[parent]
		}
	}
	return maxSize
}

// ensureDSU rebuilds the DSU structure if it is marked as stale.
func (n *Network) ensureDSU() {
	n.lock.RLock()
	stale := !n.dsuValid
	n.lock.RUnlock()
	if !stale {
		return
	}

	n.lock.Lock()
	defer n.lock.Unlock()

	// Double-check after acquiring write lock.
	if n.dsuValid {
		return
	}
	n.dsu = NewDSU()
	for key := range n.edges {
		n.dsu.Union(key.a, key.b)
	}
	n.dsuValid = true
}