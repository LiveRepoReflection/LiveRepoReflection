package network_latency

import "testing"

func TestMaxNetworkLatency(t *testing.T) {
	tests := []struct {
		name         string
		N            int
		graph        [][][2]int
		serviceNodes []int
		expected     int
	}{
		{
			name: "sample case",
			N:    5,
			graph: [][][2]int{
				// Node 0 connections: {neighbor, cost}
				{{1, 5}, {2, 2}},
				// Node 1 connections
				{{0, 5}, {3, 1}},
				// Node 2 connections
				{{0, 2}, {4, 8}},
				// Node 3 connections
				{{1, 1}, {4, 7}},
				// Node 4 connections
				{{2, 8}, {3, 7}},
			},
			serviceNodes: []int{0, 4},
			expected:     6,
		},
		{
			name: "all nodes service",
			N:    4,
			graph: [][][2]int{
				{{1, 3}},
				{{0, 3}, {2, 4}},
				{{1, 4}, {3, 2}},
				{{2, 2}},
			},
			serviceNodes: []int{0, 1, 2, 3},
			expected:     0,
		},
		{
			name: "single node network",
			N:    1,
			graph: [][][2]int{
				{},
			},
			serviceNodes: []int{0},
			expected:     0,
		},
		{
			name: "chain graph service at one end",
			N:    6,
			graph: [][][2]int{
				{{1, 2}},
				{{0, 2}, {2, 3}},
				{{1, 3}, {3, 4}},
				{{2, 4}, {4, 5}},
				{{3, 5}, {5, 6}},
				{{4, 6}},
			},
			serviceNodes: []int{0},
			// Distances: Node0=0, Node1=2, Node2=5, Node3=9, Node4=14, Node5=20.
			expected: 20,
		},
		{
			name: "multiple service nodes spread out",
			N:    7,
			graph: [][][2]int{
				{{1, 4}, {2, 1}},
				{{0, 4}, {3, 2}},
				{{0, 1}, {3, 5}, {4, 8}},
				{{1, 2}, {2, 5}, {5, 3}},
				{{2, 8}, {6, 7}},
				{{3, 3}, {6, 2}},
				{{4, 7}, {5, 2}},
			},
			serviceNodes: []int{2, 5},
			// Compute distances manually:
			// Node0: min(distance from Node0->2 = 1, via 0->1->3->5 = 4+2+3=9) = 1
			// Node1: min(distance via 1->0->2 = 4+1=5, 1->3->5 = 2+3=5) = 5
			// Node2: 0 since service node.
			// Node3: min(distance: 3->5=3, 3->2=5)=3
			// Node4: min(distance: 4->2=8, 4->6->5=7+2=9)=8
			// Node5: 0 since service node.
			// Node6: min(distance: 6->5=2, 6->4->2=7+8=15)=2
			// Maximum distance is 8.
			expected: 8,
		},
		{
			name: "star topology with central service",
			N:    5,
			graph: [][][2]int{
				{{1, 3}, {2, 4}, {3, 2}, {4, 6}},
				{{0, 3}},
				{{0, 4}},
				{{0, 2}},
				{{0, 6}},
			},
			serviceNodes: []int{0},
			// Distances: Node0=0, Node1=3, Node2=4, Node3=2, Node4=6. Maximum=6.
			expected: 6,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := MaxNetworkLatency(tc.N, tc.graph, tc.serviceNodes)
			if result != tc.expected {
				t.Errorf("Test %q failed: expected %d but got %d", tc.name, tc.expected, result)
			}
		})
	}
}

func BenchmarkMaxNetworkLatency(b *testing.B) {
	// Construct a moderately sized chain graph for benchmarking.
	N := 10000
	graph := make([][][2]int, N)
	for i := 0; i < N-1; i++ {
		graph[i] = append(graph[i], [2]int{i + 1, 1})
		graph[i+1] = append(graph[i+1], [2]int{i, 1})
	}
	// Mark one end as service.
	serviceNodes := []int{0}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = MaxNetworkLatency(N, graph, serviceNodes)
	}
}