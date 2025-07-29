package bft_network

import (
	"reflect"
	"testing"
	"time"
)

// The following tests assume that the implementation provides an exported function with the signature:
//   func StartBFTConsensus(proposals []string, faultyIndices []int, timeout time.Duration) ([]string, error)
// which simulates a PBFT consensus network using n = 3f + 1 nodes where f is the tolerated maximum number of faulty nodes.
// Node 0 is always the leader. The function returns the committed operations sequence when consensus is reached,
// or an error if consensus fails (for example, when too many nodes are faulty).

func TestConsensusNoFaults(t *testing.T) {
	// For a fault tolerant network, f must be at least 1.
	// For no faulty nodes, set f = 1 (i.e. n = 4) and supply an empty slice for faultyIndices.
	proposals := []string{"op1", "op2", "op3"}
	var faultyIndices []int // No faulty nodes.

	committed, err := StartBFTConsensus(proposals, faultyIndices, 3*time.Second)
	if err != nil {
		t.Fatalf("Expected consensus with no faults, but got error: %v", err)
	}
	if !reflect.DeepEqual(committed, proposals) {
		t.Errorf("Consensus failed: expected %v, got %v", proposals, committed)
	}
}

func TestConsensusWithFaults(t *testing.T) {
	// For this test, we assume f = 1, so n should be 4.
	// We simulate one faulty node (non-leader) by specifying its index in faultyIndices.
	proposals := []string{"txn1", "txn2", "txn3", "txn4"}
	faultyIndices := []int{2} // Node 2 will behave in a Byzantine manner.

	committed, err := StartBFTConsensus(proposals, faultyIndices, 3*time.Second)
	if err != nil {
		t.Fatalf("Expected consensus with f=1 faulty node, but got error: %v", err)
	}
	if !reflect.DeepEqual(committed, proposals) {
		t.Errorf("Consensus with faults failed: expected %v, got %v", proposals, committed)
	}
}

func TestConsensusTooManyFaults(t *testing.T) {
	// For PBFT, the maximum tolerated number of faulty nodes is f, with total nodes n = 3f + 1.
	// If the number of faulty nodes exceeds f, then consensus should fail.
	// Here we simulate f = 1 by design (n = 4) and supply 2 faulty nodes.
	proposals := []string{"cmdA", "cmdB"}
	// Intentionally exceed the tolerated fault threshold.
	faultyIndices := []int{1, 2} // 2 faults in a network that can only tolerate 1.

	_, err := StartBFTConsensus(proposals, faultyIndices, 3*time.Second)
	if err == nil {
		t.Fatalf("Expected consensus to fail when too many faults are present, but it succeeded")
	}
}

func TestMultipleRounds(t *testing.T) {
	// Test consensus over multiple sequential rounds.
	// In each round, a new operation is proposed; nodes must commit them in the correct sequence.
	proposalsRound1 := []string{"init"}
	proposalsRound2 := []string{"update1", "update2"}
	proposalsRound3 := []string{"finalize"}

	// Use f = 1 network (n = 4) without any faults.
	var faultyIndices []int

	// Run round 1.
	committed1, err := StartBFTConsensus(proposalsRound1, faultyIndices, 3*time.Second)
	if err != nil {
		t.Fatalf("Round 1 consensus failed: %v", err)
	}
	if !reflect.DeepEqual(committed1, proposalsRound1) {
		t.Errorf("Round 1 consensus incorrect: expected %v, got %v", proposalsRound1, committed1)
	}

	// Run round 2.
	committed2, err := StartBFTConsensus(proposalsRound2, faultyIndices, 3*time.Second)
	if err != nil {
		t.Fatalf("Round 2 consensus failed: %v", err)
	}
	if !reflect.DeepEqual(committed2, proposalsRound2) {
		t.Errorf("Round 2 consensus incorrect: expected %v, got %v", proposalsRound2, committed2)
	}

	// Run round 3.
	committed3, err := StartBFTConsensus(proposalsRound3, faultyIndices, 3*time.Second)
	if err != nil {
		t.Fatalf("Round 3 consensus failed: %v", err)
	}
	if !reflect.DeepEqual(committed3, proposalsRound3) {
		t.Errorf("Round 3 consensus incorrect: expected %v, got %v", proposalsRound3, committed3)
	}
}