package intergalactic_network

import (
	"sort"
)

// DSU represents a union-find structure.
type DSU struct {
	parent []int
	rank   []int
}

// NewDSU initializes a new DSU for n elements.
func NewDSU(n int) *DSU {
	parent := make([]int, n)
	rank := make([]int, n)
	for i := 0; i < n; i++ {
		parent[i] = i
		rank[i] = 0
	}
	return &DSU{
		parent: parent,
		rank:   rank,
	}
}

// find returns the representative of the given element.
func (d *DSU) find(x int) int {
	if d.parent[x] != x {
		d.parent[x] = d.find(d.parent[x])
	}
	return d.parent[x]
}

// union merges the sets of x and y, returns false if already in same set.
func (d *DSU) union(x, y int) bool {
	rootX := d.find(x)
	rootY := d.find(y)
	if rootX == rootY {
		return false
	}
	if d.rank[rootX] < d.rank[rootY] {
		d.parent[rootX] = rootY
	} else if d.rank[rootX] > d.rank[rootY] {
		d.parent[rootY] = rootX
	} else {
		d.parent[rootY] = rootX
		d.rank[rootX]++
	}
	return true
}

// Edge represents an edge in the graph.
type Edge struct {
	u, v   int
	weight float64
}

// MinimumCost calculates the minimum total cost to connect all N planets
// using at most K wormholes. The cost matrix provides the precomputed cost
// between any two planets. Wormholes can effectively remove the highest cost
// edges in the spanning tree.
func MinimumCost(N int, K int, coordinates [][]int, cost [][]float64) float64 {
	if N <= 1 {
		return 0
	}

	// Build list of edges for the complete graph.
	edges := make([]Edge, 0, N*(N-1)/2)
	for i := 0; i < N; i++ {
		for j := i + 1; j < N; j++ {
			edges = append(edges, Edge{
				u:      i,
				v:      j,
				weight: cost[i][j],
			})
		}
	}

	// Sort edges in ascending order based on weight.
	sort.Slice(edges, func(i, j int) bool {
		return edges[i].weight < edges[j].weight
	})

	// Use Kruskal's algorithm to form the MST.
	dsu := NewDSU(N)
	mstEdges := make([]float64, 0, N-1)
	totalCost := 0.0
	for _, edge := range edges {
		if dsu.union(edge.u, edge.v) {
			mstEdges = append(mstEdges, edge.weight)
			totalCost += edge.weight
			if len(mstEdges) == N-1 {
				break
			}
		}
	}

	// Remove the K most expensive edges from the MST using wormholes.
	sort.Slice(mstEdges, func(i, j int) bool {
		return mstEdges[i] > mstEdges[j]
	})
	removedCost := 0.0
	for i := 0; i < K && i < len(mstEdges); i++ {
		removedCost += mstEdges[i]
	}

	finalCost := totalCost - removedCost
	return finalCost
}