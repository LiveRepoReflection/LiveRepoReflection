package decentralized_load

import (
	"math/rand"
	"testing"
)

func TestSingleServer(t *testing.T) {
	// Deterministic behavior for testing using a single server and dispatch node.
	rand.Seed(42)
	N := 1
	M := 1
	C := []int{10}
	batches := []int{5, 3, 2}
	K := 0
	maxLoad := simulate_load_balancing(N, M, C, batches, K)
	expected := 10
	if maxLoad != expected {
		t.Errorf("TestSingleServer: expected max load %d, got %d", expected, maxLoad)
	}
}

func TestMultipleDispatchWithGossip(t *testing.T) {
	// Test scenario with multiple servers and dispatch nodes, with gossip protocol enabled.
	rand.Seed(42)
	N := 3
	M := 2
	C := []int{100, 120, 150}
	batches := []int{50, 80, 60, 40, 70}
	K := 1
	maxLoad := simulate_load_balancing(N, M, C, batches, K)

	// The maximum load observed should be non-negative and no greater than the sum of all requests.
	total := 0
	for _, req := range batches {
		total += req
	}
	if maxLoad < 0 || maxLoad > total {
		t.Errorf("TestMultipleDispatchWithGossip: max load %d is outside valid range [0, %d]", maxLoad, total)
	}
}

func TestMultipleDispatchNoGossip(t *testing.T) {
	// Test multiple dispatch nodes without gossip protocol.
	rand.Seed(42)
	N := 3
	M := 2
	C := []int{100, 120, 150}
	batches := []int{50, 80, 60, 40, 70}
	K := 0
	maxLoad := simulate_load_balancing(N, M, C, batches, K)

	total := 0
	for _, req := range batches {
		total += req
	}
	if maxLoad < 0 || maxLoad > total {
		t.Errorf("TestMultipleDispatchNoGossip: max load %d is outside valid range [0, %d]", maxLoad, total)
	}
}

func TestReproducibility(t *testing.T) {
	// Ensure that with a fixed seed, repeated simulations yield the same maximum load.
	N := 3
	M := 3
	C := []int{200, 220, 250}
	batches := []int{60, 30, 90, 50, 80}
	K := 1

	rand.Seed(42)
	maxLoad1 := simulate_load_balancing(N, M, C, batches, K)

	rand.Seed(42)
	maxLoad2 := simulate_load_balancing(N, M, C, batches, K)

	if maxLoad1 != maxLoad2 {
		t.Errorf("TestReproducibility: expected same max load, got %d and %d", maxLoad1, maxLoad2)
	}
}