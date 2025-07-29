package net_route_opt

import (
	"testing"
	"fmt"
	"math"
)

// Helper: build a map for minimum weight between two connected nodes.
// The key is "u_v" string with u <= v.
func buildEdgeMap(edges [][]int) map[string]int {
	edgeMap := make(map[string]int)
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		var key string
		if u <= v {
			key = fmt.Sprintf("%d_%d", u, v)
		} else {
			key = fmt.Sprintf("%d_%d", v, u)
		}
		if current, exists := edgeMap[key]; !exists || w < current {
			edgeMap[key] = w
		}
	}
	return edgeMap
}

// Helper: Given a path and the edge map, calculate the latency of the path.
// It uses the minimum weight edge between consecutive nodes.
func calcLatency(path []int, edgeMap map[string]int) int {
	total := 0
	for i := 0; i < len(path)-1; i++ {
		u, v := path[i], path[i+1]
		var key string
		if u <= v {
			key = fmt.Sprintf("%d_%d", u, v)
		} else {
			key = fmt.Sprintf("%d_%d", v, u)
		}
		weight, exists := edgeMap[key]
		if !exists {
			// edge not found, return a high value
			return math.MaxInt32
		}
		total += weight
	}
	return total
}

// Helper: Validate that a path meets the criteria:
// 1. Starts with src and ends with dest.
// 2. The sum of latencies along the path is <= maxLatency.
// 3. Intermediate nodes (excluding src and dest) are unique.
func validPath(path []int, edgeMap map[string]int, src, dest, maxLatency int) bool {
	if len(path) < 2 || path[0] != src || path[len(path)-1] != dest {
		return false
	}
	seen := make(map[int]bool)
	// Checking intermediate nodes uniqueness.
	for i := 1; i < len(path)-1; i++ {
		if seen[path[i]] {
			return false
		}
		seen[path[i]] = true
	}
	latency := calcLatency(path, edgeMap)
	return latency <= maxLatency
}

// Helper: Validate that the set of paths are node-disjoint except at src and dest.
func disjointPaths(paths [][]int, src, dest int) bool {
	usedNodes := make(map[int]bool)
	for _, path := range paths {
		// check intermediate nodes only
		for i := 1; i < len(path)-1; i++ {
			if usedNodes[path[i]] {
				return false
			}
			usedNodes[path[i]] = true
		}
	}
	return true
}

// Test cases for FindDisjointPaths function.
func TestFindDisjointPaths(t *testing.T) {
	tests := []struct{
		name        string
		n           int
		edges       [][]int
		src         int
		dest        int
		maxLatency  int
		expectedK   int
	}{
		{
			name: "sample graph with two valid paths",
			n: 5,
			edges: [][]int{
				{0, 1, 5},
				{0, 2, 3},
				{1, 3, 6},
				{2, 3, 2},
				{3, 4, 4},
				{1, 4, 8},
				{2, 4, 7},
			},
			src: 0,
			dest: 4,
			maxLatency: 15,
			expectedK: 2,
		},
		{
			name: "no valid path due to low maxLatency",
			n: 4,
			edges: [][]int{
				{0, 1, 3},
				{1, 2, 3},
				{2, 3, 3},
				{0, 3, 10},
			},
			src: 0,
			dest: 3,
			maxLatency: 8,
			expectedK: 0,
		},
		{
			name: "multiple potential paths but only disjoint subset allowed",
			n: 6,
			edges: [][]int{
				{0, 1, 2},
				{1, 3, 2},
				{3, 5, 2},
				{0, 2, 2},
				{2, 3, 3},
				{0, 4, 5},
				{4, 5, 2},
				{1, 4, 2},
				{4, 3, 2},
			},
			src: 0,
			dest: 5,
			maxLatency: 8,
			expectedK: 2,
		},
		{
			name: "graph with multiple edges between nodes",
			n: 4,
			edges: [][]int{
				{0, 1, 1},
				{0, 1, 2},
				{1, 2, 2},
				{1, 2, 1},
				{2, 3, 3},
			},
			src: 0,
			dest: 3,
			maxLatency: 6,
			expectedK: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			edgeMap := buildEdgeMap(tt.edges)
			paths := FindDisjointPaths(tt.n, tt.edges, tt.src, tt.dest, tt.maxLatency)
			
			if len(paths) != tt.expectedK {
				t.Errorf("Expected %d disjoint paths, got %d", tt.expectedK, len(paths))
			}
			// Validate each returned path.
			for i, path := range paths {
				if !validPath(path, edgeMap, tt.src, tt.dest, tt.maxLatency) {
					t.Errorf("Path %d is invalid: %v", i, path)
				}
			}
			// Check disjointness for intermediate nodes.
			if !disjointPaths(paths, tt.src, tt.dest) {
				t.Errorf("Returned paths are not node-disjoint (excluding src and dest): %v", paths)
			}
		})
	}
}

func BenchmarkFindDisjointPaths(b *testing.B) {
	// Benchmark with a moderately sized graph.
	n := 300
	// Construct a graph: linear chain and some extra edges to create alternative paths.
	var edges [][]int
	// Linear chain edges.
	for i := 0; i < n-1; i++ {
		edges = append(edges, []int{i, i+1, 1})
	}
	// Add some extra shortcut edges.
	for i := 0; i < n-3; i += 3 {
		edges = append(edges, []int{i, i+3, 2})
	}

	src := 0
	dest := n - 1
	maxLatency := n

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = FindDisjointPaths(n, edges, src, dest, maxLatency)
	}
}