package optimal_path

import (
	"reflect"
	"testing"
)

func TestFindOptimalPathBasic(t *testing.T) {
	// Graph with two available routes:
	// Route 1: 0 -> 1 -> 3 (latency: 1+1 = 2; max capacity: max(5,2,4)=5)
	// Route 2: 0 -> 2 -> 3 (latency: 2+1 = 3; max capacity: max(5,3,4)=5)
	// Optimal route should be [0, 1, 3] as it has lower total latency.
	n := 4
	edges := [][]int{
		{0, 1, 1},
		{1, 3, 1},
		{0, 2, 2},
		{2, 3, 1},
	}
	capacities := []int{5, 2, 3, 4}
	s, d := 0, 3
	expected := []int{0, 1, 3}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath returned %v, expected %v", got, expected)
	}
}

func TestFindOptimalPathNoPath(t *testing.T) {
	// Graph with no valid path from s to d.
	n := 3
	edges := [][]int{
		{0, 1, 5},
		{1, 0, 5},
	}
	capacities := []int{1, 1, 1}
	s, d := 0, 2
	expected := []int{}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath returned %v, expected empty slice", got)
	}
}

func TestFindOptimalPathMultipleEdges(t *testing.T) {
	// Graph with parallel edges between nodes.
	// There are two edges from 0 to 1. The one with lower latency should be preferred.
	n := 5
	edges := [][]int{
		{0, 1, 10},
		{0, 1, 2}, // duplicate edge with lower latency
		{1, 2, 5},
		{2, 3, 2},
		{3, 4, 1},
		{0, 2, 15},
		{2, 4, 10},
	}
	capacities := []int{3, 5, 2, 4, 1}
	s, d := 0, 4
	// Two candidate paths:
	// Option 1: [0, 1, 2, 3, 4] with max capacity = max(3,5,2,4,1)=5 and total latency = 2+5+2+1 = 10.
	// Option 2: [0, 2, 4] with max capacity = max(3,2,1)=3 and total latency = 15+10 = 25.
	// Optimal path is [0, 2, 4] because it minimizes the maximum capacity.
	expected := []int{0, 2, 4}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath returned %v, expected %v", got, expected)
	}
}

func TestFindOptimalPathCycle(t *testing.T) {
	// Graph containing a cycle between nodes 1 and 2.
	n := 4
	edges := [][]int{
		{0, 1, 1},
		{1, 2, 1},
		{2, 1, 1}, // cycle back edge
		{2, 3, 1},
		{1, 3, 4},
	}
	capacities := []int{4, 2, 3, 1}
	s, d := 0, 3
	// Two candidate routes:
	// Route 1: [0,1,3] with max capacity = max(4,2,1)=4 and total latency = 1+4 = 5.
	// Route 2: [0,1,2,3] with max capacity = max(4,2,3,1)=4 and total latency = 1+1+1 = 3.
	// Optimal route is [0,1,2,3] due to lower total latency.
	expected := []int{0, 1, 2, 3}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath returned %v, expected %v", got, expected)
	}
}

func TestFindOptimalPathInvalidNodes(t *testing.T) {
	// Test with invalid source and destination indices.
	n := 3
	edges := [][]int{
		{0, 1, 3},
		{1, 2, 3},
	}
	capacities := []int{1, 2, 3}
	
	// Test with invalid source: s = -1.
	s, d := -1, 2
	expected := []int{}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath with invalid source returned %v, expected empty slice", got)
	}
	
	// Test with invalid destination: d = 3.
	s, d = 0, 3
	expected = []int{}
	got = FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath with invalid destination returned %v, expected empty slice", got)
	}
}

func TestFindOptimalPathTieBreaker(t *testing.T) {
	// Test to verify the tie-breaker based on total latency when paths have equal maximum capacities.
	n := 4
	edges := [][]int{
		// Two routes from 0 to 3:
		{0, 1, 5},
		{1, 3, 5},
		{0, 2, 2},
		{2, 3, 10},
	}
	capacities := []int{5, 3, 3, 5}
	s, d := 0, 3
	// Both potential paths have maximum capacity 5. 
	// Route 1: total latency = 5+5 = 10, Route 2: total latency = 2+10 = 12.
	// Expected optimal route is [0, 1, 3].
	expected := []int{0, 1, 3}
	got := FindOptimalPath(n, edges, capacities, s, d)
	if !reflect.DeepEqual(got, expected) {
		t.Errorf("FindOptimalPath returned %v, expected %v", got, expected)
	}
}

func BenchmarkFindOptimalPath(b *testing.B) {
	// Benchmark on a chain-like graph of 1000 nodes.
	n := 1000
	var edges [][]int
	capacities := make([]int, n)
	for i := 0; i < n-1; i++ {
		edges = append(edges, []int{i, i + 1, 1})
		capacities[i] = i % 100
	}
	capacities[n-1] = (n - 1) % 100
	s, d := 0, n-1

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = FindOptimalPath(n, edges, capacities, s, d)
	}
}