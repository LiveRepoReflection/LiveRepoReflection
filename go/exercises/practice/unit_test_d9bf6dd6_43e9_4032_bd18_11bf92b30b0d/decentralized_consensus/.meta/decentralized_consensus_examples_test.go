package decentralized_consensus

import (
	"fmt"
	"math/rand"
)

// This file provides examples of how to use the decentralized consensus simulation

func Example_basicUsage() {
	// Set a fixed seed for reproducible results
	rand.Seed(42)
	
	// Parameters for the simulation
	n := 5                         // Number of nodes
	k := 2                         // Number of random nodes to communicate with per round
	r := 10                        // Maximum number of rounds
	messageLossProbability := 0.1  // 10% chance of message loss
	
	// Initial values for each node
	initialValues := []int64{10, 20, 30, 40, 50}
	
	// Run the simulation
	result := SimulateConsensus(n, k, r, initialValues, messageLossProbability)
	
	fmt.Printf("Reached consensus: %v\n", result)
	// Output: Reached consensus: true
}

func Example_largeNetwork() {
	// Set a fixed seed for reproducible results
	rand.Seed(42)
	
	// Generate 100 nodes with random initial values between 1 and 1000
	n := 100
	initialValues := make([]int64, n)
	for i := 0; i < n; i++ {
		initialValues[i] = int64(rand.Intn(1000) + 1)
	}
	
	// Parameters for the simulation
	k := 10                        // Each node communicates with 10 others
	r := 20                        // Maximum of 20 rounds
	messageLossProbability := 0.2  // 20% chance of message loss
	
	// Run the simulation
	result := SimulateConsensus(n, k, r, initialValues, messageLossProbability)
	
	fmt.Printf("Large network consensus: %v\n", result)
	// Output: Large network consensus: true
}