package rideshare_network

import (
	"reflect"
	"sort"
	"testing"
)

func TestNodeDiscovery(t *testing.T) {
	for _, tt := range nodeDiscoveryTests {
		t.Run(tt.name, func(t *testing.T) {
			got := NodeDiscovery(tt.adjacencyList, tt.startNode, tt.maxDistance)
			sort.Ints(got)
			sort.Ints(tt.expected)
			if !reflect.DeepEqual(got, tt.expected) {
				t.Errorf("NodeDiscovery() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestRideMatching(t *testing.T) {
	for _, tt := range rideMatchingTests {
		t.Run(tt.name, func(t *testing.T) {
			got := RideMatching(tt.adjacencyList, tt.riderNode, tt.driverNodes, tt.riderDestination)
			if got != tt.expected {
				t.Errorf("RideMatching() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestNetworkPartitioning(t *testing.T) {
	for _, tt := range networkPartitionTests {
		t.Run(tt.name, func(t *testing.T) {
			got := NetworkPartitioning(tt.adjacencyList)
			if got != tt.expected {
				t.Errorf("NetworkPartitioning() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkNodeDiscovery(b *testing.B) {
	adjList := map[int][]int{
		1: {2, 3},
		2: {1, 4},
		3: {1, 5},
		4: {2, 6},
		5: {3, 7},
		6: {4, 8},
		7: {5, 9},
		8: {6, 10},
		9: {7},
		10: {8},
	}
	for i := 0; i < b.N; i++ {
		NodeDiscovery(adjList, 1, 5)
	}
}

func BenchmarkRideMatching(b *testing.B) {
	adjList := map[int][]int{
		1: {2, 3},
		2: {1, 4},
		3: {1, 5},
		4: {2, 6},
		5: {3, 7},
		6: {4, 8},
		7: {5, 9},
		8: {6, 10},
		9: {7},
		10: {8},
	}
	drivers := []int{4, 6, 8, 10}
	for i := 0; i < b.N; i++ {
		RideMatching(adjList, 1, drivers, 9)
	}
}

func BenchmarkNetworkPartitioning(b *testing.B) {
	adjList := map[int][]int{
		1: {2, 3},
		2: {1, 4},
		3: {1, 5},
		4: {2, 6},
		5: {3, 7},
		6: {4, 8},
		7: {5, 9},
		8: {6, 10},
		9: {7},
		10: {8},
	}
	for i := 0; i < b.N; i++ {
		NetworkPartitioning(adjList)
	}
}