package consensus

import (
	"testing"
)

func TestSingleNodeCommit(t *testing.T) {
	n := 1
	proposals := []bool{true}
	expected := true
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestSingleNodeRollback(t *testing.T) {
	n := 1
	proposals := []bool{false}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestAllCommit(t *testing.T) {
	n := 5
	proposals := []bool{true, true, true, true, true}
	expected := true
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestAllRollback(t *testing.T) {
	n := 4
	proposals := []bool{false, false, false, false}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestMajorityRollback(t *testing.T) {
	n := 7
	proposals := []bool{true, true, false, false, false, false, false}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestTieVote(t *testing.T) {
	n := 6
	proposals := []bool{true, true, true, false, false, false}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestLargeNumberOfNodes(t *testing.T) {
	n := 100000
	proposals := make([]bool, n)
	for i := 0; i < n/2; i++ {
		proposals[i] = true
	}
	for i := n / 2; i < n; i++ {
		proposals[i] = false
	}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestEdgeCaseOneCommit(t *testing.T) {
	n := 5
	proposals := []bool{true, false, false, false, false}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}

func TestEdgeCaseOneRollback(t *testing.T) {
	n := 5
	proposals := []bool{false, true, true, true, true}
	expected := false
	result := DecideConsensus(n, proposals)
	if result != expected {
		t.Errorf("Expected %v, got %v", expected, result)
	}
}