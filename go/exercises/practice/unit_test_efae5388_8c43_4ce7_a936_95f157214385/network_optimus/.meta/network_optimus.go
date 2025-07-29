package networkoptimus

import (
	"sort"
)

type Edge struct {
	u, v, w int
}

type UnionFind struct {
	parent []int
	rank   []int
}

func NewUnionFind(n int) *UnionFind {
	parent := make([]int, n)
	rank := make([]int, n)
	for i := 0; i < n; i++ {
		parent[i] = i
	}
	return &UnionFind{parent: parent, rank: rank}
}

func (uf *UnionFind) Find(x int) int {
	if uf.parent[x] != x {
		uf.parent[x] = uf.Find(uf.parent[x])
	}
	return uf.parent[x]
}

func (uf *UnionFind) Union(x, y int) bool {
	rx, ry := uf.Find(x), uf.Find(y)
	if rx == ry {
		return false
	}
	if uf.rank[rx] < uf.rank[ry] {
		uf.parent[rx] = ry
	} else if uf.rank[rx] > uf.rank[ry] {
		uf.parent[ry] = rx
	} else {
		uf.parent[ry] = rx
		uf.rank[rx]++
	}
	return true
}

func OptimizeNetwork(n int, connections [][]int, maxLatency int) int {
	if n == 1 {
		return 0
	}

	// Build edges and ignore self loops.
	var edges []Edge
	for _, conn := range connections {
		u, v, w := conn[0], conn[1], conn[2]
		if u == v {
			continue
		}
		edges = append(edges, Edge{u: u, v: v, w: w})
	}

	// Sort edges by latency.
	sort.Slice(edges, func(i, j int) bool {
		return edges[i].w < edges[j].w
	})

	uf := NewUnionFind(n)
	var mstEdges []Edge
	totalCost := 0
	for _, e := range edges {
		if uf.Union(e.u, e.v) {
			mstEdges = append(mstEdges, e)
			totalCost += e.w
			if len(mstEdges) == n-1 {
				break
			}
		}
	}

	// Check if the MST connects all nodes.
	if len(mstEdges) != n-1 {
		return -1
	}

	// Build tree adjacency list from MST.
	tree := make([][]Edge, n)
	for _, e := range mstEdges {
		// For tree, add both directions.
		tree[e.u] = append(tree[e.u], Edge{u: e.u, v: e.v, w: e.w})
		tree[e.v] = append(tree[e.v], Edge{u: e.v, v: e.u, w: e.w})
	}

	// DFS helper returns the farthest node and the corresponding distance.
	var dfs func(node, parent, dist int) (int, int)
	dfs = func(node, parent, dist int) (int, int) {
		farthestNode := node
		maxDist := dist
		for _, edge := range tree[node] {
			if edge.v == parent {
				continue
			}
			nextNode, d := dfs(edge.v, node, dist+edge.w)
			if d > maxDist {
				maxDist = d
				farthestNode = nextNode
			}
		}
		return farthestNode, maxDist
	}

	// Find diameter of the MST.
	startNode, _ := dfs(0, -1, 0)
	_, diameter := dfs(startNode, -1, 0)

	if diameter <= maxLatency {
		return totalCost
	}
	return -1
}