package paxos

import (
	"testing"
	"time"
)

func TestBasicConsensus(t *testing.T) {
	nodes := make([]*Node, 3)
	for i := 0; i < 3; i++ {
		nodes[i] = NewNode(i, 3, 100*time.Millisecond)
		go nodes[i].Run()
	}

	// Propose value from node 0
	nodes[0].Propose(42)

	// Wait for consensus
	time.Sleep(500 * time.Millisecond)

	// Verify all nodes learned the same value
	expected := nodes[0].LearnedValue()
	for i := 1; i < 3; i++ {
		if nodes[i].LearnedValue() != expected {
			t.Errorf("Node %d learned %v, expected %v", i, nodes[i].LearnedValue(), expected)
		}
	}
}

func TestQuorumAfterFailure(t *testing.T) {
	nodes := make([]*Node, 5)
	for i := 0; i < 5; i++ {
		nodes[i] = NewNode(i, 5, 100*time.Millisecond)
		go nodes[i].Run()
	}

	// Crash two nodes
	nodes[1].Crash()
	nodes[2].Crash()

	// Propose value from node 0
	nodes[0].Propose(42)

	// Wait for consensus
	time.Sleep(500 * time.Millisecond)

	// Verify remaining nodes learned the same value
	expected := nodes[0].LearnedValue()
	for i := 3; i < 5; i++ {
		if nodes[i].LearnedValue() != expected {
			t.Errorf("Node %d learned %v, expected %v", i, nodes[i].LearnedValue(), expected)
		}
	}
}

func TestMessageLoss(t *testing.T) {
	nodes := make([]*Node, 3)
	for i := 0; i < 3; i++ {
		n := NewNode(i, 3, 100*time.Millisecond)
		n.SetMessageLossProbability(0.3) // 30% message loss
		nodes[i] = n
		go nodes[i].Run()
	}

	// Propose value from node 0
	nodes[0].Propose(42)

	// Wait longer due to potential message loss
	time.Sleep(1 * time.Second)

	// Verify all nodes eventually learned the same value
	expected := nodes[0].LearnedValue()
	for i := 1; i < 3; i++ {
		if nodes[i].LearnedValue() != expected {
			t.Errorf("Node %d learned %v, expected %v", i, nodes[i].LearnedValue(), expected)
		}
	}
}

func TestConcurrentProposals(t *testing.T) {
	nodes := make([]*Node, 5)
	for i := 0; i < 5; i++ {
		nodes[i] = NewNode(i, 5, 100*time.Millisecond)
		go nodes[i].Run()
	}

	// Concurrent proposals from different nodes
	nodes[0].Propose(42)
	nodes[1].Propose(24)
	nodes[2].Propose(99)

	// Wait for consensus
	time.Sleep(1 * time.Second)

	// Verify all nodes learned the same value
	expected := nodes[0].LearnedValue()
	for i := 1; i < 5; i++ {
		if nodes[i].LearnedValue() != expected {
			t.Errorf("Node %d learned %v, expected %v", i, nodes[i].LearnedValue(), expected)
		}
	}
}

func TestRecoveryAfterCrash(t *testing.T) {
	nodes := make([]*Node, 3)
	for i := 0; i < 3; i++ {
		nodes[i] = NewNode(i, 3, 100*time.Millisecond)
		go nodes[i].Run()
	}

	// Crash node 1
	nodes[1].Crash()

	// Propose value from node 0
	nodes[0].Propose(42)

	// Wait a bit
	time.Sleep(300 * time.Millisecond)

	// Recover node 1
	nodes[1].Recover()
	go nodes[1].Run()

	// Wait for consensus
	time.Sleep(500 * time.Millisecond)

	// Verify all nodes learned the same value
	expected := nodes[0].LearnedValue()
	for i := 1; i < 3; i++ {
		if nodes[i].LearnedValue() != expected {
			t.Errorf("Node %d learned %v, expected %v", i, nodes[i].LearnedValue(), expected)
		}
	}
}