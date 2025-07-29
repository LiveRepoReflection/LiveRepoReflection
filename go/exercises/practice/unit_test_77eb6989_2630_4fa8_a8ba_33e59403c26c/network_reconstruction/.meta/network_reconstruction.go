package network_reconstruction

import (
	"sort"
)

type UnionFind struct {
	parent []int
	rank   []int
}

func NewUnionFind(size int) *UnionFind {
	uf := &UnionFind{
		parent: make([]int, size),
		rank:   make([]int, size),
	}
	for i := range uf.parent {
		uf.parent[i] = i
	}
	return uf
}

func (uf *UnionFind) Find(x int) int {
	if uf.parent[x] != x {
		uf.parent[x] = uf.Find(uf.parent[x])
	}
	return uf.parent[x]
}

func (uf *UnionFind) Union(x, y int) {
	xRoot := uf.Find(x)
	yRoot := uf.Find(y)

	if xRoot == yRoot {
		return
	}

	if uf.rank[xRoot] < uf.rank[yRoot] {
		uf.parent[xRoot] = yRoot
	} else {
		uf.parent[yRoot] = xRoot
		if uf.rank[xRoot] == uf.rank[yRoot] {
			uf.rank[xRoot]++
		}
	}
}

func ReconstructNetwork(n int, log []LogEntry) int {
	if n <= 1 {
		return 0
	}

	// Filter out invalid entries and self-communications
	validLog := make([]LogEntry, 0, len(log))
	for _, entry := range log {
		if entry.Source >= 0 && entry.Source < n &&
			entry.Destination >= 0 && entry.Destination < n &&
			entry.Source != entry.Destination {
			validLog = append(validLog, entry)
		}
	}

	if len(validLog) == 0 {
		return 0
	}

	// Sort log entries by timestamp
	sort.Slice(validLog, func(i, j int) bool {
		return validLog[i].Timestamp < validLog[j].Timestamp
	})

	uf := NewUnionFind(n)
	edges := make(map[[2]int]bool)
	edgeCount := 0

	for _, entry := range validLog {
		src := entry.Source
		dest := entry.Destination

		// Ensure src < dest for undirected edge representation
		if src > dest {
			src, dest = dest, src
		}

		edgeKey := [2]int{src, dest}

		if !edges[edgeKey] {
			if uf.Find(src) != uf.Find(dest) {
				uf.Union(src, dest)
				edges[edgeKey] = true
				edgeCount++
			}
		}
	}

	// Count connected components
	components := make(map[int]bool)
	for i := 0; i < n; i++ {
		components[uf.Find(i)] = true
	}

	// Minimum edges is (nodes - components) + edgeCount
	// But since we've already counted edges between components,
	// we just need to return edgeCount
	return edgeCount
}