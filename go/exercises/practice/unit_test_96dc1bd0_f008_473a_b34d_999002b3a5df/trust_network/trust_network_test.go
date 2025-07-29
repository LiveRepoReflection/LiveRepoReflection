package trust_network

import (
	"math"
	"testing"
)

func TestAddUser(t *testing.T) {
	tn := NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")

	if !tn.HasUser("alice") || !tn.HasUser("bob") {
		t.Error("Failed to add users")
	}
}

func TestAddTrustEdge(t *testing.T) {
	tn := NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")

	err := tn.AddTrustEdge("alice", "bob", 0.8)
	if err != nil {
		t.Errorf("AddTrustEdge failed: %v", err)
	}

	err = tn.AddTrustEdge("alice", "nonexistent", 0.5)
	if err == nil {
		t.Error("Expected error when adding edge to nonexistent user")
	}

	err = tn.AddTrustEdge("alice", "bob", 1.1)
	if err == nil {
		t.Error("Expected error when adding invalid trust score > 1.0")
	}
}

func TestGetTrustworthiness(t *testing.T) {
	tn := NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")
	tn.AddUser("charlie")

	tn.AddTrustEdge("alice", "bob", 0.8)
	tn.AddTrustEdge("charlie", "bob", 0.6)

	trust := tn.GetTrustworthiness("bob")
	expected := (0.8 + 0.6) / 2
	if math.Abs(trust-expected) > 1e-9 {
		t.Errorf("Expected trustworthiness %.2f, got %.2f", expected, trust)
	}

	trust = tn.GetTrustworthiness("alice")
	if trust != 0.0 {
		t.Errorf("Expected trustworthiness 0.0 for user with no incoming edges, got %.2f", trust)
	}
}

func TestFindBestTrustPath(t *testing.T) {
	tn := NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")
	tn.AddUser("charlie")
	tn.AddUser("dave")

	tn.AddTrustEdge("alice", "bob", 0.9)
	tn.AddTrustEdge("bob", "charlie", 0.8)
	tn.AddTrustEdge("alice", "dave", 0.7)
	tn.AddTrustEdge("dave", "charlie", 0.6)

	path := tn.FindBestTrustPath("alice", "charlie")
	expected := []string{"alice", "bob", "charlie"}
	if !equalPaths(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}

	path = tn.FindBestTrustPath("alice", "nonexistent")
	if len(path) != 0 {
		t.Errorf("Expected empty path for nonexistent user, got %v", path)
	}
}

func TestGetUsersInCycles(t *testing.T) {
	tn := NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")
	tn.AddUser("charlie")

	tn.AddTrustEdge("alice", "bob", 0.5)
	tn.AddTrustEdge("bob", "charlie", 0.5)
	tn.AddTrustEdge("charlie", "alice", 0.5)

	cycles := tn.GetUsersInCycles()
	if len(cycles) != 3 {
		t.Errorf("Expected 3 users in cycles, got %d", len(cycles))
	}

	tn = NewTrustNetwork()
	tn.AddUser("alice")
	tn.AddUser("bob")
	cycles = tn.GetUsersInCycles()
	if len(cycles) != 0 {
		t.Errorf("Expected no cycles, got %d", len(cycles))
	}
}

func equalPaths(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}