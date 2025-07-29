package max_flow

import (
	"fmt"
)

func Example() {
	// Define a simple flow network
	n := 4
	edges := []Edge{
		{from: 0, to: 1, capacity: 3},
		{from: 0, to: 2, capacity: 2},
		{from: 1, to: 2, capacity: 1},
		{from: 1, to: 3, capacity: 3},
		{from: 2, to: 3, capacity: 2},
	}
	source := 0
	sink := 3

	// Calculate maximum flow
	maxFlow, err := MaxFlow(n, edges, source, sink)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	fmt.Printf("Maximum flow from node %d to node %d: %d\n", source, sink, maxFlow)
	// Output: Maximum flow from node 0 to node 3: 5
}

func ExampleMaxFlow_advanced() {
	// Define a more complex flow network
	n := 6
	edges := []Edge{
		{from: 0, to: 1, capacity: 10},
		{from: 0, to: 2, capacity: 10},
		{from: 1, to: 2, capacity: 2},
		{from: 1, to: 3, capacity: 4},
		{from: 1, to: 4, capacity: 8},
		{from: 2, to: 4, capacity: 9},
		{from: 3, to: 5, capacity: 10},
		{from: 4, to: 3, capacity: 6},
		{from: 4, to: 5, capacity: 10},
	}
	source := 0
	sink := 5

	// Calculate maximum flow
	maxFlow, err := MaxFlow(n, edges, source, sink)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	fmt.Printf("Maximum flow from node %d to node %d: %d\n", source, sink, maxFlow)
	// Output: Maximum flow from node 0 to node 5: 19
}

func ExampleMaxFlow_errorHandling() {
	// Define a network with invalid parameters
	n := 3
	edges := []Edge{
		{from: 0, to: 1, capacity: 5},
		{from: 1, to: 2, capacity: -1}, // Invalid negative capacity
	}
	source := 0
	sink := 2

	// Calculate maximum flow
	_, err := MaxFlow(n, edges, source, sink)
	fmt.Println("Error:", err != nil)
	// Output: Error: true
}