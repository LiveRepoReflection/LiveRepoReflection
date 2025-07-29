package optimal_paths

import (
	"reflect"
	"sync"
	"testing"
)

// Assume that the candidate's solution defines the following exported types:
// - type Graph map[int][]Edge
// - type Edge struct { Dest int; Cost int }
// - func FindOptimalPath(graph Graph, startServerID int, endServerID int, unavailableServerIDs []int) ([]int, int)
//
// For the purpose of these tests, we will construct sample graphs using these types.

var sampleGraph Graph = Graph{
	1: {
		{Dest: 2, Cost: 1},
		{Dest: 3, Cost: 4},
	},
	2: {
		{Dest: 3, Cost: 2},
		{Dest: 4, Cost: 5},
	},
	3: {
		{Dest: 4, Cost: 1},
	},
	4: {},
}

var disconnectedGraph Graph = Graph{
	1: {
		{Dest: 2, Cost: 3},
	},
	2: {
		{Dest: 3, Cost: 4},
	},
	3: {},
	4: {
		{Dest: 5, Cost: 1},
	},
	5: {},
}

var alternativeGraph Graph = Graph{
	1: {
		{Dest: 2, Cost: 1},
		{Dest: 3, Cost: 10},
	},
	2: {
		{Dest: 3, Cost: 1},
		{Dest: 4, Cost: 5},
	},
	3: {
		{Dest: 4, Cost: 1},
	},
	4: {},
}

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		description         string
		graph               Graph
		start               int
		end                 int
		unavailable         []int
		expectedPath        []int
		expectedTotalCost   int
	}{
		{
			description:       "Basic valid path on sampleGraph",
			graph:             sampleGraph,
			start:             1,
			end:               4,
			unavailable:       []int{},
			expectedPath:      []int{1, 2, 3, 4},
			expectedTotalCost: 4, // 1 (1->2) + 2 (2->3) + 1 (3->4)
		},
		{
			description:       "Direct unavailable start",
			graph:             sampleGraph,
			start:             1,
			end:               4,
			unavailable:       []int{1},
			expectedPath:      []int{},
			expectedTotalCost: -1,
		},
		{
			description:       "Direct unavailable end",
			graph:             sampleGraph,
			start:             1,
			end:               4,
			unavailable:       []int{4},
			expectedPath:      []int{},
			expectedTotalCost: -1,
		},
		{
			description:       "Start and end are same and available",
			graph:             sampleGraph,
			start:             1,
			end:               1,
			unavailable:       []int{},
			expectedPath:      []int{1},
			expectedTotalCost: 0,
		},
		{
			description:       "No available path due to intermediate removals",
			graph:             sampleGraph,
			start:             1,
			end:               4,
			unavailable:       []int{2, 3},
			expectedPath:      []int{},
			expectedTotalCost: -1,
		},
		{
			description:       "Path exists with alternative route using alternativeGraph",
			graph:             alternativeGraph,
			start:             1,
			end:               4,
			unavailable:       []int{},
			expectedPath:      []int{1, 2, 3, 4},
			expectedTotalCost: 3, // 1 (1->2) + 1 (2->3) + 1 (3->4)
		},
		{
			description:       "No path exists in disconnectedGraph",
			graph:             disconnectedGraph,
			start:             1,
			end:               5,
			unavailable:       []int{},
			expectedPath:      []int{},
			expectedTotalCost: -1,
		},
		{
			description:       "Unavailable node splits alternativeGraph path forcing different route",
			graph:             alternativeGraph,
			start:             1,
			end:               4,
			unavailable:       []int{2},
			expectedPath:      []int{1, 3, 4},
			expectedTotalCost: 11, // 10 (1->3) + 1 (3->4)
		},
	}

	for _, tc := range tests {
		t.Run(tc.description, func(t *testing.T) {
			path, cost := FindOptimalPath(tc.graph, tc.start, tc.end, tc.unavailable)
			if cost != tc.expectedTotalCost {
				t.Fatalf("Test '%s' failed: expected cost %d, got %d", tc.description, tc.expectedTotalCost, cost)
			}
			if !reflect.DeepEqual(path, tc.expectedPath) {
				t.Fatalf("Test '%s' failed: expected path %v, got %v", tc.description, tc.expectedPath, path)
			}
		})
	}
}

func TestConcurrencySafety(t *testing.T) {
	// Test that FindOptimalPath is safe to be used concurrently.
	var wg sync.WaitGroup
	numGoroutines := 10
	runFunc := func(id int) {
		defer wg.Done()
		path, cost := FindOptimalPath(alternativeGraph, 1, 4, []int{})
		// In alternativeGraph, the optimal path is [1,2,3,4] with total cost 3.
		if cost != 3 || !reflect.DeepEqual(path, []int{1, 2, 3, 4}) {
			t.Errorf("Goroutine %d: expected path [1,2,3,4] with cost 3, got path %v and cost %d", id, path, cost)
		}
	}

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go runFunc(i)
	}

	wg.Wait()
}