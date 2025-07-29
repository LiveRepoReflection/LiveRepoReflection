package traffic_control

import (
	"math"
	"math/rand"
	"testing"
	"time"
)

// TestOptimalTrafficLightControl tests the OptimalTrafficLightControl function
func TestOptimalTrafficLightControl(t *testing.T) {
	tests := []struct {
		name         string
		n            int
		m            int
		roads        [][]int
		k            int
		trips        [][]int
		cycleLength  int
		maxTravelTime float64 // To verify solution is reasonable
	}{
		{
			name:        "Simple Linear Road",
			n:           3,
			m:           2,
			roads:       [][]int{{0, 1, 10}, {1, 2, 10}},
			k:           1,
			trips:       [][]int{{0, 2}},
			cycleLength: 50,
			maxTravelTime: 30, // 10 + 10 + potential waiting time
		},
		{
			name:        "Small Grid Network",
			n:           4,
			m:           4,
			roads:       [][]int{{0, 1, 5}, {1, 3, 5}, {0, 2, 5}, {2, 3, 5}},
			k:           2,
			trips:       [][]int{{0, 3}, {3, 0}},
			cycleLength: 50,
			maxTravelTime: 20, // 5 + 5 + potential waiting time
		},
		{
			name:        "Complex Network",
			n:           5,
			m:           8,
			roads:       [][]int{
				{0, 1, 5}, {0, 2, 8}, {1, 2, 3}, 
				{1, 3, 6}, {2, 3, 7}, {2, 4, 10}, 
				{3, 4, 4}, {0, 4, 15},
			},
			k:           3,
			trips:       [][]int{{0, 4}, {4, 0}, {2, 3}},
			cycleLength: 60,
			maxTravelTime: 30, // Reasonable upper bound for these routes
		},
		{
			name:        "Large Network",
			n:           10,
			m:           20,
			roads:       generateRandomRoads(10, 20, 100),
			k:           5,
			trips:       [][]int{{0, 9}, {9, 0}, {3, 7}, {2, 8}, {5, 1}},
			cycleLength: 80,
			maxTravelTime: 500, // Large upper bound for random network
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			schedule := OptimalTrafficLightControl(tt.n, tt.m, tt.roads, tt.k, tt.trips, tt.cycleLength)
			
			// Check if schedule has correct length
			if len(schedule) != tt.n {
				t.Errorf("Expected schedule length %d, got %d", tt.n, len(schedule))
			}
			
			// Check if all values are within valid range
			for i, greenTime := range schedule {
				if greenTime < 1 || greenTime > tt.cycleLength-1 {
					t.Errorf("Invalid green time %d at intersection %d, should be between 1 and %d", 
						greenTime, i, tt.cycleLength-1)
				}
			}
			
			// Simulate the traffic flow with the given schedule to check if it's reasonable
			avgTravelTime := simulateTrafficFlow(tt.n, tt.roads, tt.trips, schedule, tt.cycleLength)
			if avgTravelTime > tt.maxTravelTime {
				t.Errorf("Average travel time too high: %f (max expected: %f)", 
					avgTravelTime, tt.maxTravelTime)
			}
			
			t.Logf("Average travel time with optimized schedule: %f", avgTravelTime)
		})
	}
}

// Helper function to simulate traffic flow and calculate average travel time
func simulateTrafficFlow(n int, roads [][]int, trips [][]int, schedule []int, cycleLength int) float64 {
	// Build adjacency list
	graph := make([][][]int, n)
	for _, road := range roads {
		u, v, t := road[0], road[1], road[2]
		graph[u] = append(graph[u], []int{v, t})
		graph[v] = append(graph[v], []int{u, t})
	}
	
	totalTravelTime := 0.0
	
	for _, trip := range trips {
		start, end := trip[0], trip[1]
		
		// Calculate shortest path (simplified version)
		travelTime := calculateShortestPathWithLights(n, graph, start, end, schedule, cycleLength)
		totalTravelTime += travelTime
	}
	
	return totalTravelTime / float64(len(trips))
}

// Simplified Dijkstra's algorithm to find shortest path with traffic light delays
func calculateShortestPathWithLights(n int, graph [][][]int, start, end int, schedule []int, cycleLength int) float64 {
	// Initialize distances
	dist := make([]float64, n)
	for i := range dist {
		dist[i] = math.Inf(1)
	}
	dist[start] = 0
	
	// Keep track of visited nodes
	visited := make([]bool, n)
	
	for i := 0; i < n; i++ {
		// Find the minimum distance vertex from the set of vertices not yet processed
		u := -1
		minDist := math.Inf(1)
		for v := 0; v < n; v++ {
			if !visited[v] && dist[v] < minDist {
				minDist = dist[v]
				u = v
			}
		}
		
		// If we've reached the destination, we're done
		if u == end {
			break
		}
		
		// Mark the picked vertex as processed
		visited[u] = true
		
		// Update dist value of the adjacent vertices
		for _, edge := range graph[u] {
			v, weight := edge[0], float64(edge[1])
			
			// Calculate waiting time at traffic light (simplified)
			waitTime := 0.0
			arrivalTime := dist[u] + weight
			
			// Only wait at traffic light if we're not at the destination
			if v != end {
				cycle := int(arrivalTime) % cycleLength
				greenTime := schedule[v]
				
				if cycle >= greenTime {
					// We arrived during red light, wait for next green
					waitTime = float64(cycleLength - cycle + greenTime)
				}
			}
			
			if dist[u]+weight+waitTime < dist[v] {
				dist[v] = dist[u] + weight + waitTime
			}
		}
	}
	
	return dist[end]
}

// Helper function to generate random roads for testing
func generateRandomRoads(n, m, maxWeight int) [][]int {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	
	// Make sure all nodes are connected (generate a minimal spanning tree first)
	roads := make([][]int, 0, m)
	connected := make([]bool, n)
	connected[0] = true
	
	for i := 1; i < n; i++ {
		u := r.Intn(i)
		for !connected[u] {
			u = r.Intn(i)
		}
		
		weight := r.Intn(maxWeight) + 1
		roads = append(roads, []int{u, i, weight})
		connected[i] = true
	}
	
	// Add remaining random edges up to m
	for len(roads) < m {
		u := r.Intn(n)
		v := r.Intn(n)
		
		// Ensure we don't have loops or duplicate edges
		if u != v {
			isDuplicate := false
			for _, road := range roads {
				if (road[0] == u && road[1] == v) || (road[0] == v && road[1] == u) {
					isDuplicate = true
					break
				}
			}
			
			if !isDuplicate {
				weight := r.Intn(maxWeight) + 1
				roads = append(roads, []int{u, v, weight})
			}
		}
	}
	
	return roads
}

// TestCornerCases tests edge cases of the function
func TestCornerCases(t *testing.T) {
	// Single intersection, no roads
	t.Run("Single Intersection", func(t *testing.T) {
		n := 1
		m := 0
		roads := [][]int{}
		k := 0
		trips := [][]int{}
		cycleLength := 50
		
		schedule := OptimalTrafficLightControl(n, m, roads, k, trips, cycleLength)
		
		if len(schedule) != n {
			t.Errorf("Expected schedule length %d, got %d", n, len(schedule))
		}
	})
	
	// Two intersections, one road, but no trips
	t.Run("No Trips", func(t *testing.T) {
		n := 2
		m := 1
		roads := [][]int{{0, 1, 10}}
		k := 0
		trips := [][]int{}
		cycleLength := 50
		
		schedule := OptimalTrafficLightControl(n, m, roads, k, trips, cycleLength)
		
		if len(schedule) != n {
			t.Errorf("Expected schedule length %d, got %d", n, len(schedule))
		}
	})
	
	// Minimum cycle length
	t.Run("Minimum Cycle Length", func(t *testing.T) {
		n := 2
		m := 1
		roads := [][]int{{0, 1, 10}}
		k := 1
		trips := [][]int{{0, 1}}
		cycleLength := 2
		
		schedule := OptimalTrafficLightControl(n, m, roads, k, trips, cycleLength)
		
		for i, greenTime := range schedule {
			if greenTime < 1 || greenTime > cycleLength-1 {
				t.Errorf("Invalid green time %d at intersection %d, should be between 1 and %d", 
					greenTime, i, cycleLength-1)
			}
		}
	})
}

// Benchmark the OptimalTrafficLightControl function
func BenchmarkOptimalTrafficLightControl(b *testing.B) {
	n := 20
	m := 40
	roads := generateRandomRoads(n, m, 100)
	k := 10
	trips := make([][]int, k)
	
	// Generate random trips
	for i := 0; i < k; i++ {
		start := rand.Intn(n)
		end := rand.Intn(n)
		for end == start {
			end = rand.Intn(n)
		}
		trips[i] = []int{start, end}
	}
	
	cycleLength := 80
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalTrafficLightControl(n, m, roads, k, trips, cycleLength)
	}
}