package dcdn_retrieval

import (
	"math"
	"testing"
)

func floatEqual(a, b float64) bool {
	const epsilon = 1e-6
	return math.Abs(a-b) < epsilon
}

func TestSimpleCase(t *testing.T) {
	// Graph example:
	// A --1-- B --3-- D
	// A --5-- C --2-- D
	graph := map[string]map[string]int{
		"A": {"B": 1, "C": 5},
		"B": {"A": 1, "D": 3},
		"C": {"A": 5, "D": 2},
		"D": {"B": 3, "C": 2},
	}

	// File has two chunks.
	// Chunk 0 is available at nodes A and B.
	// Chunk 1 is available at nodes C and D.
	chunkLocations := map[int][]string{
		0: {"A", "B"},
		1: {"C", "D"},
	}

	// Initiating node is A.
	// For Chunk 0, best is to take from A (cost 0).
	// For Chunk 1, best is to take from D since the shortest distance from D to A is 4 and storage cost is sqrt(1)=1.
	// Total expected cost: 0 + (4+1) = 5.
	initiatingNode := "A"
	numChunks := 2

	expectedCost := 5.0

	cost := CalculateMinimumCost(graph, chunkLocations, initiatingNode, numChunks)
	if !floatEqual(cost, expectedCost) {
		t.Errorf("TestSimpleCase failed: expected %v, got %v", expectedCost, cost)
	}
}

func TestMissingChunk(t *testing.T) {
	// Graph with two nodes
	graph := map[string]map[string]int{
		"A": {"B": 2},
		"B": {"A": 2},
	}

	// File has two chunks, but chunk 1 is missing.
	chunkLocations := map[int][]string{
		0: {"A"},
		// Chunk 1 is not available anywhere.
	}

	initiatingNode := "A"
	numChunks := 2

	expectedCost := -1.0

	cost := CalculateMinimumCost(graph, chunkLocations, initiatingNode, numChunks)
	if !floatEqual(cost, expectedCost) {
		t.Errorf("TestMissingChunk failed: expected %v, got %v", expectedCost, cost)
	}
}

func TestMultipleChunksFromSamePeer(t *testing.T) {
	// Graph: A <-> B <-> C
	graph := map[string]map[string]int{
		"A": {"B": 2},
		"B": {"A": 2, "C": 2},
		"C": {"B": 2},
	}

	// File with three chunks:
	// Chunk 0 and 1 are available only from B.
	// Chunk 2 is available only from C.
	chunkLocations := map[int][]string{
		0: {"B"},
		1: {"B"},
		2: {"C"},
	}

	initiatingNode := "A"
	numChunks := 3

	// For chunks 0 and 1 from B:
	// Transfer cost from B to A = 2 each, plus storage cost for B = sqrt(2)
	// For chunk 2 from C:
	// Best path: C->B->A with cost = 2+2 = 4, plus storage cost for C = sqrt(1)
	// Total cost = (2+2 + sqrt(2)) + (4+1)
	expectedCost := 4.0 + math.Sqrt(2) + 5.0 // 4.0 from transfers for B, sqrt(2) for B storage, and 4+1 for C

	cost := CalculateMinimumCost(graph, chunkLocations, initiatingNode, numChunks)
	if !floatEqual(cost, expectedCost) {
		t.Errorf("TestMultipleChunksFromSamePeer failed: expected %v, got %v", expectedCost, cost)
	}
}

func TestLocalRetrieval(t *testing.T) {
	// Graph with isolated initiating node.
	graph := map[string]map[string]int{
		"A": {"B": 3},
		"B": {"A": 3},
	}

	// File with two chunks, both available at initiating node A.
	chunkLocations := map[int][]string{
		0: {"A"},
		1: {"A"},
	}

	initiatingNode := "A"
	numChunks := 2

	// Since both chunks are locally available, no transfer cost or storage cost should be incurred.
	expectedCost := 0.0

	cost := CalculateMinimumCost(graph, chunkLocations, initiatingNode, numChunks)
	if !floatEqual(cost, expectedCost) {
		t.Errorf("TestLocalRetrieval failed: expected %v, got %v", expectedCost, cost)
	}
}

func TestInvalidInitiatingNode(t *testing.T) {
	// Graph for testing invalid initiating node.
	graph := map[string]map[string]int{
		"A": {"B": 1},
		"B": {"A": 1},
	}

	// File with one chunk available only on A.
	chunkLocations := map[int][]string{
		0: {"A"},
	}

	// Initiating node is not present in the graph.
	initiatingNode := "Z"
	numChunks := 1

	expectedCost := -1.0

	cost := CalculateMinimumCost(graph, chunkLocations, initiatingNode, numChunks)
	if !floatEqual(cost, expectedCost) {
		t.Errorf("TestInvalidInitiatingNode failed: expected %v, got %v", expectedCost, cost)
	}
}