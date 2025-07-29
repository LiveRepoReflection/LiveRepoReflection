package distributed_commit

import (
	"strings"
	"testing"
	"time"
)

// helper function to parse the simulation result string into a slice of states.
func parseResult(result string, n int) []string {
	// Expected format:
	// "Node 0: <state>, Node 1: <state>, ..., Node n-1: <state>"
	parts := strings.Split(result, ",")
	if len(parts) != n {
		return nil
	}
	states := make([]string, n)
	for i, part := range parts {
		part = strings.TrimSpace(part)
		// part should be "Node i: State"
		subparts := strings.Split(part, ":")
		if len(subparts) != 2 {
			return nil
		}
		state := strings.TrimSpace(subparts[1])
		states[i] = state
	}
	return states
}

func TestSimulateCommit(t *testing.T) {
	// All nodes have 0 failure probability.
	n := 5
	failureProbabilities := []float64{0.0, 0.0, 0.0, 0.0, 0.0}
	timeoutDuration := 1000 // in milliseconds

	result := SimulateTransaction(n, failureProbabilities, timeoutDuration)
	expectedState := "Committed"

	states := parseResult(result, n)
	if states == nil {
		t.Fatalf("Failed to parse simulation result: %q", result)
	}
	for i, state := range states {
		if state != expectedState {
			t.Fatalf("Node %d expected state %q, got %q", i, expectedState, state)
		}
	}
}

func TestSimulateAbortDueToVoteFailure(t *testing.T) {
	// Node 2 has 100% chance to fail during voting phase.
	n := 5
	// For deterministic behavior, node 2's failure causes no vote.
	failureProbabilities := []float64{0.0, 0.0, 1.0, 0.0, 0.0}
	timeoutDuration := 1000

	result := SimulateTransaction(n, failureProbabilities, timeoutDuration)
	// Expect coordinator to decide "abort" because of missing vote.
	// For nodes that did not fail in commit/rollback phase,
	// expect "Aborted". The node that failed in voting phase remains "Undecided".
	states := parseResult(result, n)
	if states == nil {
		t.Fatalf("Failed to parse simulation result: %q", result)
	}
	// Node 0 is the coordinator and should have processed rollback.
	expectedStates := []string{"Aborted", "Aborted", "Undecided", "Aborted", "Aborted"}
	for i, expected := range expectedStates {
		if states[i] != expected {
			t.Fatalf("Node %d expected state %q, got %q", i, expected, states[i])
		}
	}
}

func TestSimulateTimeout(t *testing.T) {
	// To simulate timeout, set a very short timeout.
	// Even if nodes are reliable, the coordinator might not receive all votes in time.
	n := 5
	// All nodes reliable.
	failureProbabilities := []float64{0.0, 0.0, 0.0, 0.0, 0.0}
	// Set timeoutDuration very short to force timeout.
	timeoutDuration := 1

	// Note: Because of concurrency, this test might occasionally pass as commit.
	// To account for this, we retry simulation until we get an abort.
	// We'll allow up to 5 attempts.
	var result string
	var states []string
	var foundAbort bool
	for i := 0; i < 5; i++ {
		result = SimulateTransaction(n, failureProbabilities, timeoutDuration)
		states = parseResult(result, n)
		if states == nil {
			t.Fatalf("Failed to parse simulation result: %q", result)
		}
		// If timeout occurs, the coordinator will abort.
		if states[0] == "Aborted" {
			foundAbort = true
			break
		}
		// Sleep a bit before next attempt to avoid racing overhead.
		time.Sleep(10 * time.Millisecond)
	}
	if !foundAbort {
		t.Fatalf("Expected an abort due to timeout condition, but got: %q", result)
	}
}

func TestInvalidInput(t *testing.T) {
	// If the length of failureProbabilities does not match n, the simulation
	// function should handle it gracefully. For this test, we expect a panic.
	n := 5
	// Provide only 3 failure probabilities.
	failureProbabilities := []float64{0.0, 0.0, 0.0}
	timeoutDuration := 1000

	defer func() {
		if r := recover(); r == nil {
			t.Fatalf("Expected panic due to invalid input lengths, but no panic occurred")
		}
	}()

	// This call should cause a panic.
	_ = SimulateTransaction(n, failureProbabilities, timeoutDuration)
}