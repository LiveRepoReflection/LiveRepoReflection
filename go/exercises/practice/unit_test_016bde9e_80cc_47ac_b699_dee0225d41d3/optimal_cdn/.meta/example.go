package optimal_cdn

import (
	"fmt"
)

// This file contains an example usage of the OptimalCDNPlacement function

func Example() {
	// Example inputs based on the test case provided in the problem statement
	n, m, k, p := 5, 6, 2, 1      // 5 cities, 6 connections, 2 users, max 1 server
	c, t := 100, 20               // server cost 100, latency threshold 20
	
	connections := [][3]int{
		{0, 1, 5},   // from city 0 to city 1 with latency 5
		{0, 2, 10},  // from city 0 to city 2 with latency 10
		{1, 2, 3},   // from city 1 to city 2 with latency 3
		{1, 3, 8},   // from city 1 to city 3 with latency 8
		{2, 4, 7},   // from city 2 to city 4 with latency 7
		{3, 4, 2},   // from city 3 to city 4 with latency 2
	}
	
	users := [][2]int{
		{1, 50},    // user at city 1 with request rate 50
		{4, 30},    // user at city 4 with request rate 30
	}
	
	originLatencies := []int{0, 12, 15, 18, 9}  // latencies from each city to the origin (city 0)
	
	// Calculate the optimal CDN placement
	minCost, err := OptimalCDNPlacement(
		n, m, k, p,
		c, t,
		connections,
		users,
		originLatencies,
	)
	
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	
	fmt.Printf("Minimum total cost: %d\n", minCost)
	
	// Output analysis:
	// The program will evaluate all possible server placements and return the minimum cost.
	// In this example, it will consider placing a single server at any of the cities
	// and calculate the total cost including server placement and latency costs.
}