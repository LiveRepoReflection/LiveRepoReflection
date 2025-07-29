package network_bridges

import (
	"sync"
)

type Network struct {
	n      int
	parent []int
	rank   []int
	adj    [][]int
	bridges [][]int
	mu     sync.RWMutex
}

func NewNetwork(n int, edges [][]int) *Network {
	net := &Network{
		n:      n,
		parent: make([]int, n),
		rank:   make([]int, n),
		adj:    make([][]int, n),
	}

	for i := 0; i < n; i++ {
		net.parent[i] = i
		net.rank[i] = 1
	}

	net.mu.Lock()
	defer net.mu.Unlock()

	// Build adjacency list and union nodes
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		if u >= 0 && u < n && v >= 0 && v < n && u != v {
			net.adj[u] = append(net.adj[u], v)
			net.adj[v] = append(net.adj[v], u)
			net.union(u, v)
		}
	}

	// Find bridges using Tarjan's algorithm
	net.findBridges()

	return net
}

func (net *Network) find(u int) int {
	if net.parent[u] != u {
		net.parent[u] = net.find(net.parent[u])
	}
	return net.parent[u]
}

func (net *Network) union(u, v int) {
	rootU := net.find(u)
	rootV := net.find(v)

	if rootU != rootV {
		if net.rank[rootU] > net.rank[rootV] {
			net.parent[rootV] = rootU
		} else if net.rank[rootU] < net.rank[rootV] {
			net.parent[rootU] = rootV
		} else {
			net.parent[rootV] = rootU
			net.rank[rootU]++
		}
	}
}

func (net *Network) findBridges() {
	visited := make([]bool, net.n)
	disc := make([]int, net.n)
	low := make([]int, net.n)
	time := 0

	var dfs func(u, parent int)
	dfs = func(u, parent int) {
		visited[u] = true
		disc[u] = time
		low[u] = time
		time++

		for _, v := range net.adj[u] {
			if !visited[v] {
				dfs(v, u)
				low[u] = min(low[u], low[v])
				if low[v] > disc[u] {
					net.bridges = append(net.bridges, []int{u, v})
				}
			} else if v != parent {
				low[u] = min(low[u], disc[v])
			}
		}
	}

	for i := 0; i < net.n; i++ {
		if !visited[i] {
			dfs(i, -1)
		}
	}
}

func (net *Network) isConnected(u, v int) bool {
	net.mu.RLock()
	defer net.mu.RUnlock()

	if u < 0 || u >= net.n || v < 0 || v >= net.n {
		return false
	}
	return net.find(u) == net.find(v)
}

func (net *Network) getCriticalLinks() [][]int {
	net.mu.RLock()
	defer net.mu.RUnlock()

	cpy := make([][]int, len(net.bridges))
	copy(cpy, net.bridges)
	return cpy
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}