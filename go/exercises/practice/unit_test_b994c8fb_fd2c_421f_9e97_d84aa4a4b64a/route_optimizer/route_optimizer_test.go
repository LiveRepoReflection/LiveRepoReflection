package route_optimizer

import (
	"testing"
	"reflect"
)

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		name           string
		graph          map[string][]Connection
		source         string
		destination    string
		minBandwidth   int
		expectedPath   []string
	}{
		{
			name: "simple path with sufficient bandwidth",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 50}, {Dest: "C", Latency: 15, Bandwidth: 20}},
				"B": {{Dest: "D", Latency: 5, Bandwidth: 30}},
				"C": {{Dest: "D", Latency: 20, Bandwidth: 40}},
				"D": {},
			},
			source:       "A",
			destination:  "D",
			minBandwidth: 30,
			expectedPath: []string{"A", "B", "D"},
		},
		{
			name: "multiple paths with different bandwidths",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 30}, {Dest: "C", Latency: 5, Bandwidth: 25}},
				"B": {{Dest: "D", Latency: 5, Bandwidth: 30}},
				"C": {{Dest: "D", Latency: 10, Bandwidth: 20}},
				"D": {},
			},
			source:       "A",
			destination:  "D",
			minBandwidth: 20,
			expectedPath: []string{"A", "C", "D"},
		},
		{
			name: "no path meets bandwidth requirement",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 30}},
				"B": {{Dest: "C", Latency: 5, Bandwidth: 20}},
				"C": {},
			},
			source:       "A",
			destination:  "C",
			minBandwidth: 40,
			expectedPath: []string{},
		},
		{
			name: "graph with cycle but valid path exists",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 50}},
				"B": {{Dest: "C", Latency: 5, Bandwidth: 40}},
				"C": {{Dest: "A", Latency: 1, Bandwidth: 100}, {Dest: "D", Latency: 20, Bandwidth: 30}},
				"D": {},
			},
			source:       "A",
			destination:  "D",
			minBandwidth: 30,
			expectedPath: []string{"A", "B", "C", "D"},
		},
		{
			name: "disconnected graph",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 50}},
				"B": {},
				"C": {{Dest: "D", Latency: 5, Bandwidth: 30}},
				"D": {},
			},
			source:       "A",
			destination:  "D",
			minBandwidth: 20,
			expectedPath: []string{},
		},
		{
			name: "same source and destination",
			graph: map[string][]Connection{
				"A": {{Dest: "B", Latency: 10, Bandwidth: 50}},
				"B": {},
			},
			source:       "A",
			destination:  "A",
			minBandwidth: 10,
			expectedPath: []string{"A"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotPath := FindOptimalPath(tt.graph, tt.source, tt.destination, tt.minBandwidth)
			if !reflect.DeepEqual(gotPath, tt.expectedPath) {
				t.Errorf("FindOptimalPath() = %v, want %v", gotPath, tt.expectedPath)
			}
		})
	}
}

func BenchmarkFindOptimalPath(b *testing.B) {
	largeGraph := generateLargeGraph(1000, 10)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		FindOptimalPath(largeGraph, "0", "999", 50)
	}
}

func generateLargeGraph(nodeCount, connectionsPerNode int) map[string][]Connection {
	graph := make(map[string][]Connection)
	for i := 0; i < nodeCount; i++ {
		node := string(rune('0' + i%10)) + string(rune('0' + (i/10)%10)) + string(rune('0' + (i/100)%10))
		for j := 0; j < connectionsPerNode; j++ {
			dest := (i + j + 1) % nodeCount
			destNode := string(rune('0' + dest%10)) + string(rune('0' + (dest/10)%10)) + string(rune('0' + (dest/100)%10))
			graph[node] = append(graph[node], Connection{
				Dest:      destNode,
				Latency:   (i + j) % 100 + 1,
				Bandwidth: (i + j) % 100 + 1,
			})
		}
	}
	return graph
}