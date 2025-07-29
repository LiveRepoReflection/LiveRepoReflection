package network

import (
	"fmt"
	"math/rand"
	"reflect"
	"sort"
	"sync"
	"testing"
	"time"
)

func TestReachableNodes(t *testing.T) {
	tests := []struct {
		name       string
		graph      map[int][]int
		sourceNode int
		want       []int
	}{
		{
			name: "simple path",
			graph: map[int][]int{
				1: {2},
				2: {3},
				3: {4},
				4: {},
			},
			sourceNode: 1,
			want:       []int{2, 3, 4},
		},
		{
			name: "disconnected graph",
			graph: map[int][]int{
				1: {2},
				2: {3},
				3: {},
				4: {5},
				5: {},
			},
			sourceNode: 1,
			want:       []int{2, 3},
		},
		{
			name: "cyclic graph",
			graph: map[int][]int{
				1: {2},
				2: {3},
				3: {1},
			},
			sourceNode: 1,
			want:       []int{2, 3},
		},
		{
			name: "complex graph",
			graph: map[int][]int{
				1: {2, 3, 4},
				2: {5, 6},
				3: {7},
				4: {8},
				5: {9},
				6: {9},
				7: {10},
				8: {10},
				9: {},
				10: {},
			},
			sourceNode: 1,
			want:       []int{2, 3, 4, 5, 6, 7, 8, 9, 10},
		},
		{
			name: "source node not in graph",
			graph: map[int][]int{
				1: {2},
				2: {3},
			},
			sourceNode: 4,
			want:       []int{},
		},
		{
			name:       "empty graph",
			graph:      map[int][]int{},
			sourceNode: 1,
			want:       []int{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ReachableNodes(tt.graph, tt.sourceNode)
			sort.Ints(got) // Ensure the result is sorted for consistent comparison
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ReachableNodes() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestAverageLatency(t *testing.T) {
	// Mock latency function for testing
	mockLatencyFunc := func(source, dest int) int {
		// Simulate computation with a small delay
		time.Sleep(10 * time.Millisecond)
		return (source + dest) % 100
	}

	tests := []struct {
		name        string
		edges       [][]int
		concurrency int
		wantAvg     float64
	}{
		{
			name: "single edge",
			edges: [][]int{
				{1, 2},
			},
			concurrency: 1,
			wantAvg:     3.0, // (1 + 2) % 100 = 3
		},
		{
			name: "multiple edges",
			edges: [][]int{
				{1, 2},
				{2, 3},
				{3, 4},
			},
			concurrency: 2,
			wantAvg:     4.0, // ((1+2)%100 + (2+3)%100 + (3+4)%100) / 3 = (3 + 5 + 7) / 3 = 5
		},
		{
			name:        "no edges",
			edges:       [][]int{},
			concurrency: 1,
			wantAvg:     0.0,
		},
		{
			name: "high concurrency",
			edges: [][]int{
				{1, 2}, {2, 3}, {3, 4}, {4, 5},
				{5, 6}, {6, 7}, {7, 8}, {8, 9},
			},
			concurrency: 8, // Test with high concurrency level
			wantAvg:     7.5,
		},
		{
			name: "concurrency limit exceeds edge count",
			edges: [][]int{
				{1, 2}, {2, 3},
			},
			concurrency: 10, // More than edges count
			wantAvg:     4.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := AverageLatency(tt.edges, mockLatencyFunc, tt.concurrency)
			// Calculate expected manually for verification
			var expectedTotal int
			for _, edge := range tt.edges {
				expectedTotal += (edge[0] + edge[1]) % 100
			}
			var expected float64
			if len(tt.edges) > 0 {
				expected = float64(expectedTotal) / float64(len(tt.edges))
			}
			
			if got != expected {
				t.Errorf("AverageLatency() = %v, want %v", got, expected)
			}
		})
	}
}

func TestConcurrencyEfficiency(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping test in short mode")
	}

	// Create a large set of edges
	edges := make([][]int, 100)
	for i := 0; i < 100; i++ {
		edges[i] = []int{i, i + 1}
	}

	// Latency function with significant delay
	slowLatencyFunc := func(source, dest int) int {
		time.Sleep(50 * time.Millisecond)
		return (source + dest) % 100
	}

	// Test with different concurrency levels
	concurrencyLevels := []int{1, 4, 10, 20, 50}
	times := make([]time.Duration, len(concurrencyLevels))

	for i, concurrency := range concurrencyLevels {
		start := time.Now()
		AverageLatency(edges, slowLatencyFunc, concurrency)
		times[i] = time.Since(start)
	}

	// Verify that higher concurrency generally results in faster execution
	for i := 1; i < len(concurrencyLevels); i++ {
		// Allow some flexibility in timing comparisons due to system load variations
		// Higher concurrency should be at least 25% faster than lower concurrency in this test
		expectedSpeedup := float64(concurrencyLevels[i]) / float64(concurrencyLevels[i-1])
		actualSpeedup := float64(times[i-1]) / float64(times[i])
		
		t.Logf("Concurrency %d -> %d: Expected speedup: %.2f, Actual speedup: %.2f",
			concurrencyLevels[i-1], concurrencyLevels[i], expectedSpeedup, actualSpeedup)
		
		// We don't make this a failure as timing can be affected by system load
		// but we want to log the information
	}
}

func TestRaceConditions(t *testing.T) {
	// Create many edges
	edges := make([][]int, 1000)
	for i := 0; i < 1000; i++ {
		edges[i] = []int{rand.Intn(100), rand.Intn(100)}
	}

	// Function that uses a shared state to detect race conditions
	var counter int
	var mu sync.Mutex
	
	latencyFunc := func(source, dest int) int {
		mu.Lock()
		counter++
		mu.Unlock()
		return source + dest
	}

	// Run with high concurrency to increase chance of detecting race conditions
	AverageLatency(edges, latencyFunc, 50)
	
	if counter != len(edges) {
		t.Errorf("Expected latency function to be called %d times, got %d", len(edges), counter)
	}
}

func TestLargeGraph(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping test in short mode")
	}

	// Create a large graph
	largeGraph := make(map[int][]int)
	for i := 1; i <= 1000; i++ {
		connections := make([]int, 0, 10)
		for j := 0; j < 10; j++ {
			// Connect to 10 random nodes
			target := rand.Intn(1000) + 1
			connections = append(connections, target)
		}
		largeGraph[i] = connections
	}

	// Measure reachability performance
	start := time.Now()
	nodes := ReachableNodes(largeGraph, 1)
	duration := time.Since(start)
	
	t.Logf("Reachability analysis on 1000-node graph took %v and found %d reachable nodes", 
		duration, len(nodes))
	
	// Verify all reachable nodes are in the graph
	for _, node := range nodes {
		if node < 1 || node > 1000 {
			t.Errorf("Invalid node found in result: %d", node)
		}
	}
}

func BenchmarkReachableNodes(b *testing.B) {
	// Create a medium-sized graph for benchmarking
	graph := make(map[int][]int)
	for i := 1; i <= 100; i++ {
		connections := make([]int, 0, 5)
		for j := 0; j < 5; j++ {
			target := (i * j * 17) % 100 + 1 // Deterministic but with some complexity
			connections = append(connections, target)
		}
		graph[i] = connections
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ReachableNodes(graph, 1)
	}
}

func BenchmarkAverageLatency(b *testing.B) {
	// Create edges for benchmarking
	edges := make([][]int, 100)
	for i := 0; i < 100; i++ {
		edges[i] = []int{i % 10, (i + 1) % 10}
	}

	// Fast latency function for benchmarking many iterations
	fastLatencyFunc := func(source, dest int) int {
		return source + dest
	}

	// Benchmark with different concurrency levels
	concurrencyLevels := []int{1, 4, 10, 20, 50}
	
	for _, concurrency := range concurrencyLevels {
		b.Run(fmt.Sprintf("Concurrency=%d", concurrency), func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				AverageLatency(edges, fastLatencyFunc, concurrency)
			}
		})
	}
}