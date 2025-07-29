package consistent_kv

import (
	"sync"
	"testing"
)

// TestBasicPutGet verifies that a basic Put followed by a Get returns the expected value.
func TestBasicPutGet(t *testing.T) {
	nodes := []string{"node1", "node2", "node3"}
	cluster := NewCluster(nodes, 2) // replication factor 2

	if err := cluster.Put("key1", "value1"); err != nil {
		t.Fatalf("Put failed: %v", err)
	}

	value, err := cluster.Get("key1")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}

	if value != "value1" {
		t.Fatalf("Expected %q, got %q", "value1", value)
	}
}

// TestGetNonExistentKey verifies that a Get on a missing key returns an error.
func TestGetNonExistentKey(t *testing.T) {
	nodes := []string{"node1", "node2", "node3"}
	cluster := NewCluster(nodes, 2)

	_, err := cluster.Get("nonexistent")
	if err == nil {
		t.Fatalf("Expected error for nonexistent key, got none")
	}
}

// TestConcurrentOperations ensures that concurrent Put and Get operations work correctly.
func TestConcurrentOperations(t *testing.T) {
	nodes := []string{"node1", "node2", "node3", "node4"}
	cluster := NewCluster(nodes, 2)
	var wg sync.WaitGroup
	keys := []string{"a", "b", "c", "d", "e", "f", "g", "h"}

	// Perform concurrent Put operations.
	for _, key := range keys {
		wg.Add(1)
		go func(k string) {
			defer wg.Done()
			if err := cluster.Put(k, "val_"+k); err != nil {
				t.Errorf("Put failed for key %s: %v", k, err)
			}
		}(key)
	}
	wg.Wait()

	// Perform concurrent Get operations.
	for _, key := range keys {
		wg.Add(1)
		go func(k string) {
			defer wg.Done()
			value, err := cluster.Get(k)
			if err != nil {
				t.Errorf("Get failed for key %s: %v", k, err)
				return
			}
			if value != "val_"+k {
				t.Errorf("Expected %q for key %s, got %q", "val_"+k, k, value)
			}
		}(key)
	}
	wg.Wait()
}

// TestReplicationAndNodeFailure simulates a node failure and verifies that Get still returns the correct value.
func TestReplicationAndNodeFailure(t *testing.T) {
	nodes := []string{"node1", "node2", "node3", "node4"}
	cluster := NewCluster(nodes, 3) // replication factor 3

	if err := cluster.Put("failTest", "replicaValue"); err != nil {
		t.Fatalf("Put failed: %v", err)
	}

	// Retrieve the primary node for the key.
	primaryNode, err := cluster.GetPrimaryNode("failTest")
	if err != nil {
		t.Fatalf("GetPrimaryNode failed: %v", err)
	}

	// Simulate failure of the primary node.
	if err := cluster.FailNode(primaryNode); err != nil {
		t.Fatalf("FailNode failed for %s: %v", primaryNode, err)
	}

	// The Get operation should succeed by retrieving from a replica.
	value, err := cluster.Get("failTest")
	if err != nil {
		t.Fatalf("Get failed after node failure: %v", err)
	}
	if value != "replicaValue" {
		t.Fatalf("Expected %q, got %q", "replicaValue", value)
	}

	// Recover the failed node.
	if err := cluster.RecoverNode(primaryNode); err != nil {
		t.Fatalf("RecoverNode failed for %s: %v", primaryNode, err)
	}

	// Verify that the value remains consistent after recovery.
	value, err = cluster.Get("failTest")
	if err != nil {
		t.Fatalf("Get failed after node recovery: %v", err)
	}
	if value != "replicaValue" {
		t.Fatalf("Expected %q, got %q", "replicaValue", value)
	}
}

// TestConsistentHashingDistribution verifies that the keys are distributed across multiple nodes.
func TestConsistentHashingDistribution(t *testing.T) {
	nodes := []string{"node1", "node2", "node3", "node4", "node5"}
	cluster := NewCluster(nodes, 2)
	keys := []string{"alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"}

	// Insert keys into the cluster.
	for _, key := range keys {
		if err := cluster.Put(key, "val_"+key); err != nil {
			t.Fatalf("Put failed for key %s: %v", key, err)
		}
	}

	// Count key distribution across primary nodes.
	distribution := make(map[string]int)
	for _, key := range keys {
		primary, err := cluster.GetPrimaryNode(key)
		if err != nil {
			t.Fatalf("GetPrimaryNode failed for key %s: %v", key, err)
		}
		distribution[primary]++
	}

	if len(distribution) < 2 {
		t.Fatalf("Expected keys to be distributed over multiple nodes, got distribution: %v", distribution)
	}
}