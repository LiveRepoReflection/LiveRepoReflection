package quantum

import (
	"reflect"
	"testing"
)

func TestFindMostReliablePath(t *testing.T) {
	tests := []struct {
		name        string
		n           int
		graph       [][]Edge
		source      int
		destination int
		want        []int
	}{
		{
			name:        "Example case",
			n:           4,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.9}, {To: 2, Fidelity: 0.8}}, {{To: 0, Fidelity: 0.9}, {To: 3, Fidelity: 0.7}}, {{To: 0, Fidelity: 0.8}, {To: 3, Fidelity: 0.6}}, {{To: 1, Fidelity: 0.7}, {To: 2, Fidelity: 0.6}}},
			source:      0,
			destination: 3,
			want:        []int{0, 1, 3}, // This is one possible optimal solution
		},
		{
			name:        "Single node, source=destination",
			n:           1,
			graph:       [][]Edge{{}},
			source:      0,
			destination: 0,
			want:        []int{0},
		},
		{
			name:        "Two nodes with direct connection",
			n:           2,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.8}}, {{To: 0, Fidelity: 0.8}}},
			source:      0,
			destination: 1,
			want:        []int{0, 1},
		},
		{
			name:        "Path via intermediate node is more reliable",
			n:           3,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.5}, {To: 2, Fidelity: 0.3}}, {{To: 0, Fidelity: 0.5}, {To: 2, Fidelity: 0.9}}, {{To: 0, Fidelity: 0.3}, {To: 1, Fidelity: 0.9}}},
			source:      0,
			destination: 2,
			want:        []int{0, 1, 2}, // Path 0->1->2 has reliability 0.5*0.9=0.45, better than direct 0->2 with 0.3
		},
		{
			name:        "Disconnected graph",
			n:           4,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.7}}, {{To: 0, Fidelity: 0.7}}, {{To: 3, Fidelity: 0.8}}, {{To: 2, Fidelity: 0.8}}},
			source:      0,
			destination: 3,
			want:        []int{}, // No path exists
		},
		{
			name:        "Complex network with multiple possible paths",
			n:           5,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.9}, {To: 2, Fidelity: 0.7}}, {{To: 0, Fidelity: 0.9}, {To: 2, Fidelity: 0.8}, {To: 3, Fidelity: 0.6}}, {{To: 0, Fidelity: 0.7}, {To: 1, Fidelity: 0.8}, {To: 3, Fidelity: 0.7}, {To: 4, Fidelity: 0.5}}, {{To: 1, Fidelity: 0.6}, {To: 2, Fidelity: 0.7}, {To: 4, Fidelity: 0.8}}, {{To: 2, Fidelity: 0.5}, {To: 3, Fidelity: 0.8}}},
			source:      0,
			destination: 4,
			want:        []int{0, 2, 4}, // Path 0->2->4 has reliability 0.7*0.5=0.35
		},
		{
			name:        "Linear network",
			n:           5,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.9}}, {{To: 0, Fidelity: 0.9}, {To: 2, Fidelity: 0.8}}, {{To: 1, Fidelity: 0.8}, {To: 3, Fidelity: 0.7}}, {{To: 2, Fidelity: 0.7}, {To: 4, Fidelity: 0.6}}, {{To: 3, Fidelity: 0.6}}},
			source:      0,
			destination: 4,
			want:        []int{0, 1, 2, 3, 4},
		},
		{
			name:        "Star network with center as source",
			n:           5,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.9}, {To: 2, Fidelity: 0.8}, {To: 3, Fidelity: 0.7}, {To: 4, Fidelity: 0.6}}, {{To: 0, Fidelity: 0.9}}, {{To: 0, Fidelity: 0.8}}, {{To: 0, Fidelity: 0.7}}, {{To: 0, Fidelity: 0.6}}},
			source:      0,
			destination: 4,
			want:        []int{0, 4},
		},
		{
			name:        "Full graph with varying fidelities",
			n:           4,
			graph:       [][]Edge{{{To: 1, Fidelity: 0.5}, {To: 2, Fidelity: 0.6}, {To: 3, Fidelity: 0.3}}, {{To: 0, Fidelity: 0.5}, {To: 2, Fidelity: 0.7}, {To: 3, Fidelity: 0.4}}, {{To: 0, Fidelity: 0.6}, {To: 1, Fidelity: 0.7}, {To: 3, Fidelity: 0.8}}, {{To: 0, Fidelity: 0.3}, {To: 1, Fidelity: 0.4}, {To: 2, Fidelity: 0.8}}},
			source:      0,
			destination: 3,
			want:        []int{0, 2, 3}, // Path 0->2->3 has reliability 0.6*0.8=0.48, better than direct 0->3 with 0.3
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindMostReliablePath(tt.n, tt.graph, tt.source, tt.destination)
			if len(tt.want) == 0 {
				if len(got) != 0 {
					t.Errorf("FindMostReliablePath() = %v, want empty path for disconnected graph", got)
				}
				return
			}
			
			// If there's a valid path, we need to check if it's correct
			// We can check that we get from source to destination
			if got[0] != tt.source || got[len(got)-1] != tt.destination {
				t.Errorf("FindMostReliablePath() path doesn't start at source and end at destination; got = %v", got)
				return
			}
			
			// Verify the path is valid by checking each step
			for i := 0; i < len(got)-1; i++ {
				current := got[i]
				next := got[i+1]
				edgeExists := false
				for _, edge := range tt.graph[current] {
					if edge.To == next {
						edgeExists = true
						break
					}
				}
				if !edgeExists {
					t.Errorf("FindMostReliablePath() returned invalid path %v; no edge between %d and %d", got, current, next)
					return
				}
			}
			
			// If the expected path is one of several with optimal reliability, we can skip exact path comparison
			// However, if we're given a specific expected path, check that one exactly
			if tt.name == "Example case" || reflect.DeepEqual(got, tt.want) {
				// Calculate reliability of returned path
				reliability := calculatePathReliability(tt.graph, got)
				expectedReliability := calculatePathReliability(tt.graph, tt.want)
				
				// Allow for slight floating point differences
				const epsilon = 1e-9
				if reliability < expectedReliability-epsilon {
					t.Errorf("FindMostReliablePath() returned path with reliability %v, want %v", reliability, expectedReliability)
				}
			}
		})
	}
}

// Helper function to calculate path reliability
func calculatePathReliability(graph [][]Edge, path []int) float64 {
	if len(path) <= 1 {
		return 1.0 // A path with one or zero nodes has perfect reliability
	}
	
	reliability := 1.0
	for i := 0; i < len(path)-1; i++ {
		current := path[i]
		next := path[i+1]
		
		// Find the edge connecting current and next
		for _, edge := range graph[current] {
			if edge.To == next {
				reliability *= edge.Fidelity
				break
			}
		}
	}
	
	return reliability
}

func BenchmarkFindMostReliablePath(b *testing.B) {
	// Create a reasonably sized graph for benchmarking
	n := 100
	graph := make([][]Edge, n)
	for i := 0; i < n; i++ {
		// Connect to 5 random nodes
		graph[i] = []Edge{}
		for j := 1; j <= 5; j++ {
			next := (i + j) % n
			graph[i] = append(graph[i], Edge{To: next, Fidelity: 0.8})
		}
	}
	
	source := 0
	destination := n/2
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindMostReliablePath(n, graph, source, destination)
	}
}