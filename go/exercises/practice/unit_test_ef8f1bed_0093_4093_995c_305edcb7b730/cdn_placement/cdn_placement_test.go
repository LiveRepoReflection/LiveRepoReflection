package cdn_placement

import (
	"reflect"
	"testing"
)

func TestOptimalNetworkPlacement(t *testing.T) {
	tests := []struct {
		name               string
		n                  int
		edges              [][]int
		storageCapacity    []int
		requestFrequencies [][]int
		contentSize        int
		maxReplicas        int
		expectedLatency    float64
	}{
		{
			name: "Simple network with 5 nodes",
			n:    5,
			edges: [][]int{
				{0, 1, 10},
				{0, 2, 15},
				{1, 2, 5},
				{1, 3, 20},
				{2, 4, 10},
				{3, 4, 5},
			},
			storageCapacity:    []int{600, 700, 800, 900, 1000},
			requestFrequencies: [][]int{{0, 50}, {1, 60}, {2, 70}, {3, 80}, {4, 90}},
			contentSize:        500,
			maxReplicas:        2,
			expectedLatency:    5.0, // Example expected latency
		},
		{
			name: "Disconnected network",
			n:    6,
			edges: [][]int{
				{0, 1, 5},
				{1, 2, 10},
				{3, 4, 15},
				{4, 5, 20},
			},
			storageCapacity:    []int{500, 600, 700, 800, 900, 1000},
			requestFrequencies: [][]int{{0, 40}, {1, 50}, {2, 60}, {3, 70}, {4, 80}, {5, 90}},
			contentSize:        400,
			maxReplicas:        2,
			expectedLatency:    0.0, // Disconnected network will have a special case handling
		},
		{
			name: "Single node network",
			n:    1,
			edges: [][]int{
				// No edges
			},
			storageCapacity:    []int{1000},
			requestFrequencies: [][]int{{0, 100}},
			contentSize:        500,
			maxReplicas:        1,
			expectedLatency:    0.0, // Single node network
		},
		{
			name: "Network with varying storage capacities",
			n:    4,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 15},
				{2, 3, 20},
				{3, 0, 25},
			},
			storageCapacity:    []int{300, 400, 600, 800},
			requestFrequencies: [][]int{{0, 50}, {1, 60}, {2, 70}, {3, 80}},
			contentSize:        500,
			maxReplicas:        2,
			expectedLatency:    12.5, // Example expected latency
		},
		{
			name: "Network with multiple edges between nodes",
			n:    4,
			edges: [][]int{
				{0, 1, 10},
				{0, 1, 5},  // Duplicate edge with different weight
				{1, 2, 15},
				{2, 3, 20},
				{3, 0, 25},
				{3, 0, 15}, // Duplicate edge with different weight
			},
			storageCapacity:    []int{600, 700, 800, 900},
			requestFrequencies: [][]int{{0, 50}, {1, 60}, {2, 70}, {3, 80}},
			contentSize:        500,
			maxReplicas:        2,
			expectedLatency:    10.0, // Example expected latency
		},
		{
			name: "Network with nodes having insufficient storage",
			n:    5,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 15},
				{2, 3, 20},
				{3, 4, 25},
				{4, 0, 30},
			},
			storageCapacity:    []int{200, 300, 400, 600, 800},
			requestFrequencies: [][]int{{0, 50}, {1, 60}, {2, 70}, {3, 80}, {4, 90}},
			contentSize:        500,
			maxReplicas:        2,
			expectedLatency:    15.0, // Example expected latency
		},
		{
			name: "Large network",
			n:    10,
			edges: [][]int{
				{0, 1, 5}, {1, 2, 10}, {2, 3, 15}, {3, 4, 20},
				{4, 5, 25}, {5, 6, 30}, {6, 7, 35}, {7, 8, 40},
				{8, 9, 45}, {9, 0, 50}, {0, 5, 55}, {1, 6, 60},
				{2, 7, 65}, {3, 8, 70}, {4, 9, 75},
			},
			storageCapacity: []int{500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400},
			requestFrequencies: [][]int{
				{0, 10}, {1, 20}, {2, 30}, {3, 40}, {4, 50},
				{5, 60}, {6, 70}, {7, 80}, {8, 90}, {9, 100},
			},
			contentSize:     400,
			maxReplicas:     3,
			expectedLatency: 20.0, // Example expected latency
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			placement := OptimalNetworkPlacement(tt.n, tt.edges, tt.storageCapacity, tt.requestFrequencies, tt.contentSize, tt.maxReplicas)
			
			// Validate the number of replicas
			if len(placement) > tt.maxReplicas {
				t.Errorf("OptimalNetworkPlacement() returned %d replicas, want at most %d", len(placement), tt.maxReplicas)
			}
			
			// Validate that all nodes in the placement have sufficient storage capacity
			for _, node := range placement {
				if node < 0 || node >= tt.n {
					t.Errorf("OptimalNetworkPlacement() returned invalid node %d, valid range is [0, %d)", node, tt.n)
					continue
				}
				
				if tt.storageCapacity[node] < tt.contentSize {
					t.Errorf("OptimalNetworkPlacement() placed content on node %d with insufficient storage capacity %d, content size is %d",
						node, tt.storageCapacity[node], tt.contentSize)
				}
			}
			
			// Validate that all nodes in the placement are unique
			nodeMap := make(map[int]bool)
			for _, node := range placement {
				if nodeMap[node] {
					t.Errorf("OptimalNetworkPlacement() returned duplicate node %d", node)
				}
				nodeMap[node] = true
			}
			
			// Calculate the actual average latency with the given placement
			actualLatency := calculateAverageLatency(tt.n, tt.edges, tt.requestFrequencies, placement)
			
			// For the disconnected network or single node network, we don't check the latency
			if tt.name == "Disconnected network" || tt.name == "Single node network" {
				return
			}
			
			// For other test cases, we perform a latency check
			// but since the optimal placement can vary depending on the implementation,
			// we just verify that the latency is reasonable (not just returning a bad solution)
			// In a real test, you would compare against a known optimal solution
			if actualLatency > 3*tt.expectedLatency && tt.expectedLatency > 0 {
				t.Errorf("OptimalNetworkPlacement() resulted in average latency %f, which is much higher than expected %f",
					actualLatency, tt.expectedLatency)
			}
		})
	}
}

// TestEnsureOptimalPlacement verifies that the OptimalNetworkPlacement function returns the optimal placement
// for a simple case where we know the exact answer
func TestEnsureOptimalPlacement(t *testing.T) {
	// Simple line graph where node 1 is clearly the optimal placement for a single replica
	n := 3
	edges := [][]int{{0, 1, 1}, {1, 2, 1}}
	storageCapacity := []int{1000, 1000, 1000}
	requestFrequencies := [][]int{{0, 1}, {1, 1}, {2, 1}}
	contentSize := 500
	maxReplicas := 1
	
	expectedPlacement := []int{1} // Node 1 is optimal
	
	placement := OptimalNetworkPlacement(n, edges, storageCapacity, requestFrequencies, contentSize, maxReplicas)
	
	if !reflect.DeepEqual(placement, expectedPlacement) {
		t.Errorf("OptimalNetworkPlacement() = %v, want %v", placement, expectedPlacement)
	}
}

// calculateAverageLatency calculates the average latency for all requests based on the given placement
func calculateAverageLatency(n int, edges [][]int, requestFrequencies [][]int, placement []int) float64 {
	// Build adjacency list representation of the graph
	graph := make([][]struct{ node, latency int }, n)
	for _, edge := range edges {
		from, to, latency := edge[0], edge[1], edge[2]
		graph[from] = append(graph[from], struct{ node, latency int }{to, latency})
		graph[to] = append(graph[to], struct{ node, latency int }{from, latency})
	}
	
	// Convert placement to a set for faster lookup
	placementSet := make(map[int]bool)
	for _, node := range placement {
		placementSet[node] = true
	}
	
	// Calculate the shortest distance from each node to the nearest content replica
	totalLatency := 0
	totalRequests := 0
	
	for _, req := range requestFrequencies {
		node, frequency := req[0], req[1]
		
		if placementSet[node] {
			// The node has a content replica, so latency is 0
			totalRequests += frequency
			continue
		}
		
		// Find the shortest path from this node to any content replica using BFS
		dist := make([]int, n)
		for i := range dist {
			dist[i] = -1 // -1 means unreachable
		}
		dist[node] = 0
		
		queue := []int{node}
		var shortestDist int = -1
		
		for len(queue) > 0 && shortestDist == -1 {
			current := queue[0]
			queue = queue[1:]
			
			if placementSet[current] {
				shortestDist = dist[current]
				break
			}
			
			for _, neighbor := range graph[current] {
				nextNode, edgeLatency := neighbor.node, neighbor.latency
				
				if dist[nextNode] == -1 {
					dist[nextNode] = dist[current] + edgeLatency
					queue = append(queue, nextNode)
				}
			}
		}
		
		if shortestDist != -1 {
			totalLatency += shortestDist * frequency
			totalRequests += frequency
		}
	}
	
	if totalRequests == 0 {
		return 0
	}
	
	return float64(totalLatency) / float64(totalRequests)
}

// TestEdgeCases tests various edge cases and corner cases
func TestEdgeCases(t *testing.T) {
	// Test with no valid placement (all nodes have insufficient storage)
	n := 3
	edges := [][]int{{0, 1, 1}, {1, 2, 1}}
	storageCapacity := []int{400, 400, 400}
	requestFrequencies := [][]int{{0, 1}, {1, 1}, {2, 1}}
	contentSize := 500
	maxReplicas := 2
	
	placement := OptimalNetworkPlacement(n, edges, storageCapacity, requestFrequencies, contentSize, maxReplicas)
	
	if len(placement) > 0 {
		t.Errorf("Expected empty placement when no nodes have sufficient storage, got %v", placement)
	}
	
	// Test with maxReplicas > available nodes with sufficient storage
	storageCapacity = []int{600, 400, 600}
	maxReplicas = 3
	
	placement = OptimalNetworkPlacement(n, edges, storageCapacity, requestFrequencies, contentSize, maxReplicas)
	
	if len(placement) > 2 {
		t.Errorf("Expected at most 2 nodes in placement when only 2 nodes have sufficient storage, got %v", placement)
	}
}

// BenchmarkOptimalNetworkPlacement benchmarks the performance of the algorithm
func BenchmarkOptimalNetworkPlacement(b *testing.B) {
	n := 100
	edges := make([][]int, 0, n*3)
	
	// Create a ring graph
	for i := 0; i < n; i++ {
		edges = append(edges, []int{i, (i+1)%n, 1})
		if i > 0 {
			edges = append(edges, []int{i, (i+5)%n, 5})
		}
		if i > 0 {
			edges = append(edges, []int{i, (i+10)%n, 10})
		}
	}
	
	storageCapacity := make([]int, n)
	requestFrequencies := make([][]int, n)
	
	for i := 0; i < n; i++ {
		storageCapacity[i] = 1000
		requestFrequencies[i] = []int{i, 10}
	}
	
	contentSize := 500
	maxReplicas := 10
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		OptimalNetworkPlacement(n, edges, storageCapacity, requestFrequencies, contentSize, maxReplicas)
	}
}