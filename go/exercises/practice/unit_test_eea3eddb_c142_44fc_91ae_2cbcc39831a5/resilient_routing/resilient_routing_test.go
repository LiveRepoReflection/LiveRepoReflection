package resilient_routing

import (
	"reflect"
	"testing"
)

func TestResilientNetworkRouting_SingleQueryNoFailure(t *testing.T) {
	N := 2
	edges := [][]int{
		{0, 1, 5},
	}
	queries := [][]int{
		{0, 1, 0},
	}
	expected := []int{5}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("SingleQueryNoFailure: expected %v, got %v", expected, result)
	}
}

func TestResilientNetworkRouting_NoResilientPath(t *testing.T) {
	// Graph with a single edge, so any failure makes the route unavailable.
	N := 2
	edges := [][]int{
		{0, 1, 5},
	}
	queries := [][]int{
		{0, 1, 1},
	}
	expected := []int{-1}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("NoResilientPath: expected %v, got %v", expected, result)
	}
}

func TestResilientNetworkRouting_MultipleQueries(t *testing.T) {
	// Example graph:
	// 0-1: 1, 0-2: 5, 1-2: 2, 1-3: 1, 2-3: 4
	N := 4
	edges := [][]int{
		{0, 1, 1},
		{0, 2, 5},
		{1, 2, 2},
		{1, 3, 1},
		{2, 3, 4},
	}
	queries := [][]int{
		{0, 3, 0}, // No failure allowed. Expected shortest cost is 2 (0->1->3)
		{0, 3, 1}, // Resilient to 1 failure. With only one path option, no resilient path exists.
	}
	expected := []int{2, -1}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("MultipleQueries: expected %v, got %v", expected, result)
	}
}

func TestResilientNetworkRouting_DisconnectedGraph(t *testing.T) {
	// Graph where destination is disconnected.
	N := 3
	edges := [][]int{
		{0, 1, 3},
	}
	queries := [][]int{
		{0, 2, 0},
	}
	expected := []int{-1}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("DisconnectedGraph: expected %v, got %v", expected, result)
	}
}

func TestResilientNetworkRouting_CycleGraph(t *testing.T) {
	// Triangle cycle: 0-1: 1, 1-2: 1, 2-0: 1.
	// For k==0, direct edge (if exists) is optimal.
	// For k>=1, although there are cycles, a single chosen path cannot guarantee connectivity if one edge fails.
	N := 3
	edges := [][]int{
		{0, 1, 1},
		{1, 2, 1},
		{2, 0, 1},
	}
	queries := [][]int{
		{0, 2, 0}, // With no failure allowed, the shortest path is direct 0->2, cost 1.
		{0, 2, 1}, // Resiliency requirement forces the answer to be -1.
	}
	expected := []int{1, -1}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("CycleGraph: expected %v, got %v", expected, result)
	}
}

func TestResilientNetworkRouting_ComplexGraph(t *testing.T) {
	// Construct a more complex graph that offers two disjoint routes between some nodes.
	// Graph:
	// 0-1: 1, 1-4: 1, 0-2: 2, 2-4: 2, 1-2: 10, 0-3: 4, 3-4: 4
	// For k==0, shortest path from 0 to 4 is 0->1->4 with cost 2.
	// For k==1, even though two alternative routes exist (0->1->4 and 0->2->4), the requirement
	// is that the selected path remains valid under any one edge failure along it.
	// In this design, both candidate paths lose connectivity if one of their edges fails.
	// Therefore, expected result is -1 for k==1.
	N := 5
	edges := [][]int{
		{0, 1, 1},
		{1, 4, 1},
		{0, 2, 2},
		{2, 4, 2},
		{1, 2, 10},
		{0, 3, 4},
		{3, 4, 4},
	}
	queries := [][]int{
		{0, 4, 0},
		{0, 4, 1},
	}
	expected := []int{2, -1}
	result := ResilientNetworkRouting(N, edges, queries)
	if !reflect.DeepEqual(result, expected) {
		t.Errorf("ComplexGraph: expected %v, got %v", expected, result)
	}
}