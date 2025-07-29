package flow_scheduler

import (
	"testing"
)

func TestEmptyNetwork(t *testing.T) {
	n := 2
	m := 1
	edges := [][3]int{{0, 1, 10}}
	k := 1
	requests := [][3]int{{0, 1, 5}}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 1 {
		t.Errorf("Expected 1 satisfied request, got %d", result)
	}
}

func TestNoPossibleRequests(t *testing.T) {
	n := 3
	m := 1
	edges := [][3]int{{0, 1, 10}}
	k := 2
	requests := [][3]int{{0, 2, 5}, {1, 2, 5}}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 0 {
		t.Errorf("Expected 0 satisfied requests, got %d", result)
	}
}

func TestMultiplePaths(t *testing.T) {
	n := 4
	m := 5
	edges := [][3]int{
		{0, 1, 10},
		{0, 2, 5},
		{1, 2, 4},
		{1, 3, 7},
		{2, 3, 6},
	}
	k := 3
	requests := [][3]int{
		{0, 3, 5},
		{0, 3, 3},
		{1, 3, 2},
	}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 3 {
		t.Errorf("Expected 3 satisfied requests, got %d", result)
	}
}

func TestCapacityConstraints(t *testing.T) {
	n := 3
	m := 2
	edges := [][3]int{
		{0, 1, 5},
		{1, 2, 5},
	}
	k := 2
	requests := [][3]int{
		{0, 2, 5},
		{0, 2, 1},
	}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 1 {
		t.Errorf("Expected 1 satisfied request, got %d", result)
	}
}

func TestSameSourceTarget(t *testing.T) {
	n := 2
	m := 1
	edges := [][3]int{{0, 1, 10}}
	k := 2
	requests := [][3]int{
		{0, 0, 5},
		{1, 1, 5},
	}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 2 {
		t.Errorf("Expected 2 satisfied requests, got %d", result)
	}
}

func TestMultipleEdgesSameNodes(t *testing.T) {
	n := 2
	m := 3
	edges := [][3]int{
		{0, 1, 3},
		{0, 1, 2},
		{0, 1, 5},
	}
	k := 3
	requests := [][3]int{
		{0, 1, 3},
		{0, 1, 2},
		{0, 1, 5},
	}
	
	result := MaxSatisfiedRequests(n, m, edges, k, requests)
	if result != 3 {
		t.Errorf("Expected 3 satisfied requests, got %d", result)
	}
}

func BenchmarkLargeNetwork(b *testing.B) {
	n := 50
	m := 200
	edges := make([][3]int, m)
	for i := 0; i < m; i++ {
		edges[i] = [3]int{i % n, (i + 1) % n, 10}
	}
	k := 20
	requests := make([][3]int, k)
	for i := 0; i < k; i++ {
		requests[i] = [3]int{i % n, (i + 5) % n, 1}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MaxSatisfiedRequests(n, m, edges, k, requests)
	}
}