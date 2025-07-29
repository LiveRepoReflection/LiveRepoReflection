package distkvstore

import (
	"fmt"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"testing"
	"time"
)

func TestBasicOperations(t *testing.T) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add nodes
	err := store.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	err = store.AddNode("node2")
	if err != nil {
		t.Fatalf("Failed to add node2: %v", err)
	}
	
	err = store.AddNode("node3")
	if err != nil {
		t.Fatalf("Failed to add node3: %v", err)
	}
	
	// Put some data
	err = store.Put("key1", "value1")
	if err != nil {
		t.Fatalf("Failed to put key1: %v", err)
	}
	
	err = store.Put("key2", "value2")
	if err != nil {
		t.Fatalf("Failed to put key2: %v", err)
	}
	
	// Get data
	value, err := store.Get("key1")
	if err != nil {
		t.Fatalf("Failed to get key1: %v", err)
	}
	if value != "value1" {
		t.Errorf("Expected value1 for key1, got %s", value)
	}
	
	value, err = store.Get("key2")
	if err != nil {
		t.Fatalf("Failed to get key2: %v", err)
	}
	if value != "value2" {
		t.Errorf("Expected value2 for key2, got %s", value)
	}
	
	// Check nodes list
	nodes := store.ListNodes()
	expectedNodes := []string{"node1", "node2", "node3"}
	sort.Strings(expectedNodes)
	
	if len(nodes) != len(expectedNodes) {
		t.Errorf("Expected %d nodes, got %d", len(expectedNodes), len(nodes))
	}
	
	for i, node := range nodes {
		if node != expectedNodes[i] {
			t.Errorf("Expected node %s at position %d, got %s", expectedNodes[i], i, node)
		}
	}
}

func TestAddDuplicateNode(t *testing.T) {
	store := NewDistributedStore(3)
	
	err := store.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	// Try to add the same node again
	err = store.AddNode("node1")
	if err == nil {
		t.Errorf("Expected error when adding duplicate node, got nil")
	}
}

func TestRemoveNonExistentNode(t *testing.T) {
	store := NewDistributedStore(3)
	
	err := store.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	// Try to remove a non-existent node
	err = store.RemoveNode("node2")
	if err == nil {
		t.Errorf("Expected error when removing non-existent node, got nil")
	}
}

func TestGetNonExistentKey(t *testing.T) {
	store := NewDistributedStore(3)
	
	err := store.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	// Try to get a non-existent key
	_, err = store.Get("nonexistent")
	if err == nil {
		t.Errorf("Expected error when getting non-existent key, got nil")
	}
}

func TestNodeRemoval(t *testing.T) {
	store := NewDistributedStore(2) // Replication factor of 2
	
	// Add nodes
	err := store.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	err = store.AddNode("node2")
	if err != nil {
		t.Fatalf("Failed to add node2: %v", err)
	}
	
	err = store.AddNode("node3")
	if err != nil {
		t.Fatalf("Failed to add node3: %v", err)
	}
	
	// Put some data
	for i := 0; i < 10; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err = store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put %s: %v", key, err)
		}
	}
	
	// Remove a node
	err = store.RemoveNode("node2")
	if err != nil {
		t.Fatalf("Failed to remove node2: %v", err)
	}
	
	// Verify data is still accessible
	for i := 0; i < 10; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s after node removal: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s after node removal, got %s", expectedValue, key, value)
		}
	}
	
	// Check nodes list
	nodes := store.ListNodes()
	expectedNodes := []string{"node1", "node3"}
	sort.Strings(expectedNodes)
	
	if len(nodes) != len(expectedNodes) {
		t.Errorf("Expected %d nodes after removal, got %d", len(expectedNodes), len(nodes))
	}
	
	for i, node := range nodes {
		if node != expectedNodes[i] {
			t.Errorf("Expected node %s at position %d after removal, got %s", expectedNodes[i], i, node)
		}
	}
}

func TestConcurrentOperations(t *testing.T) {
	store := NewDistributedStore(2) // Replication factor of 2
	
	// Add initial nodes
	for i := 1; i <= 5; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	var wg sync.WaitGroup
	
	// Concurrent puts
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := fmt.Sprintf("key%d", i)
			value := fmt.Sprintf("value%d", i)
			err := store.Put(key, value)
			if err != nil {
				t.Errorf("Failed to put %s concurrently: %v", key, err)
			}
		}(i)
	}
	
	// Concurrent gets
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			time.Sleep(10 * time.Millisecond) // Give puts a chance to complete
			key := fmt.Sprintf("key%d", i)
			_, err := store.Get(key)
			if err != nil {
				// It's possible some gets run before the corresponding put,
				// so we don't consider this an error
			}
		}(i)
	}
	
	// Concurrent node additions and removals
	for i := 6; i <= 10; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			nodeID := fmt.Sprintf("node%d", i)
			err := store.AddNode(nodeID)
			if err != nil {
				t.Errorf("Failed to add %s concurrently: %v", nodeID, err)
			}
		}(i)
	}
	
	// Wait for operations to complete
	wg.Wait()
	
	// Verify data
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s after concurrent operations: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s after concurrent operations, got %s", expectedValue, key, value)
		}
	}
}

func TestReplicationFactor(t *testing.T) {
	// Test with replication factor = 1 (no replication)
	store1 := NewDistributedStore(1)
	
	err := store1.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	err = store1.AddNode("node2")
	if err != nil {
		t.Fatalf("Failed to add node2: %v", err)
	}
	
	err = store1.Put("key1", "value1")
	if err != nil {
		t.Fatalf("Failed to put key1 with N=1: %v", err)
	}
	
	// Test with replication factor = 5, but only 3 nodes
	store2 := NewDistributedStore(5)
	
	err = store2.AddNode("node1")
	if err != nil {
		t.Fatalf("Failed to add node1: %v", err)
	}
	
	err = store2.AddNode("node2")
	if err != nil {
		t.Fatalf("Failed to add node2: %v", err)
	}
	
	err = store2.AddNode("node3")
	if err != nil {
		t.Fatalf("Failed to add node3: %v", err)
	}
	
	err = store2.Put("key1", "value1")
	if err != nil {
		t.Fatalf("Failed to put key1 with N=5 but only 3 nodes: %v", err)
	}
	
	value, err := store2.Get("key1")
	if err != nil {
		t.Fatalf("Failed to get key1 with N=5 but only 3 nodes: %v", err)
	}
	if value != "value1" {
		t.Errorf("Expected value1 for key1, got %s", value)
	}
}

func TestFaultTolerance(t *testing.T) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add nodes
	for i := 1; i <= 5; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	// Put some data
	for i := 0; i < 20; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put %s: %v", key, err)
		}
	}
	
	// Remove nodes to simulate failures
	err := store.RemoveNode("node1")
	if err != nil {
		t.Fatalf("Failed to remove node1: %v", err)
	}
	
	err = store.RemoveNode("node3")
	if err != nil {
		t.Fatalf("Failed to remove node3: %v", err)
	}
	
	// Verify data is still accessible
	for i := 0; i < 20; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s after node failures: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s after node failures, got %s", expectedValue, key, value)
		}
	}
}

func TestReadRepair(t *testing.T) {
	// This is a more advanced test that would require mocking or special hooks
	// into your implementation to verify read repair is happening.
	// For now, we'll just test that reads succeed after updates
	
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add nodes
	for i := 1; i <= 5; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	// Put initial data
	err := store.Put("key1", "initial")
	if err != nil {
		t.Fatalf("Failed to put initial value: %v", err)
	}
	
	// Update the value
	err = store.Put("key1", "updated")
	if err != nil {
		t.Fatalf("Failed to update value: %v", err)
	}
	
	// Read the value (should perform read repair if needed)
	value, err := store.Get("key1")
	if err != nil {
		t.Fatalf("Failed to get key1: %v", err)
	}
	if value != "updated" {
		t.Errorf("Expected updated value, got %s", value)
	}
}

func TestLargeNumberOfNodes(t *testing.T) {
	store := NewDistributedStore(5) // Replication factor of 5
	
	// Add a large number of nodes
	for i := 1; i <= 50; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	// Put some data
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put %s: %v", key, err)
		}
	}
	
	// Verify data
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s with large number of nodes: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s with large number of nodes, got %s", expectedValue, key, value)
		}
	}
}

func TestNodeAdditionAndRemoval(t *testing.T) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add initial nodes
	for i := 1; i <= 5; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	// Put some data
	for i := 0; i < 20; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put %s: %v", key, err)
		}
	}
	
	// Remove a node
	err := store.RemoveNode("node3")
	if err != nil {
		t.Fatalf("Failed to remove node3: %v", err)
	}
	
	// Add a new node
	err = store.AddNode("node6")
	if err != nil {
		t.Fatalf("Failed to add node6: %v", err)
	}
	
	// Verify existing data
	for i := 0; i < 20; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s after node changes: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s after node changes, got %s", expectedValue, key, value)
		}
	}
	
	// Put new data
	for i := 20; i < 40; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put %s after node changes: %v", key, err)
		}
	}
	
	// Verify new data
	for i := 20; i < 40; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get %s after node changes: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for %s after node changes, got %s", expectedValue, key, value)
		}
	}
}

func TestStressTest(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping stress test in short mode")
	}
	
	rand.Seed(time.Now().UnixNano())
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add initial nodes
	for i := 1; i <= 10; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	var wg sync.WaitGroup
	operationCount := 1000
	
	// Concurrent operations
	for i := 0; i < operationCount; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			
			// Random operation: put, get, add node, remove node
			op := rand.Intn(10)
			
			switch {
			case op < 5: // Put
				key := fmt.Sprintf("key%d", rand.Intn(100))
				value := fmt.Sprintf("value%d-%d", i, rand.Intn(1000))
				err := store.Put(key, value)
				if err != nil {
					// Ignore errors as they might be expected due to concurrent node removals
				}
				
			case op < 8: // Get
				key := fmt.Sprintf("key%d", rand.Intn(100))
				_, err := store.Get(key)
				if err != nil {
					// Ignore errors as key might not exist or nodes might be unavailable
				}
				
			case op == 8: // Add node
				nodeID := fmt.Sprintf("node%d", 11+rand.Intn(10))
				store.AddNode(nodeID) // Ignore errors
				
			case op == 9: // Remove node
				nodeID := fmt.Sprintf("node%d", 1+rand.Intn(10))
				store.RemoveNode(nodeID) // Ignore errors
			}
		}(i)
	}
	
	wg.Wait()
	
	// Verify some nodes still exist
	nodes := store.ListNodes()
	if len(nodes) == 0 {
		t.Errorf("Expected some nodes to remain after stress test, got none")
	}
	
	// Try to get some keys
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		_, err := store.Get(key)
		// We don't check the error or value, just want to make sure it doesn't panic
		_ = err
	}
}

func TestVirtualNodesDistribution(t *testing.T) {
	// This is more of an implementation detail, but we want to ensure 
	// that the virtual nodes are well-distributed
	
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add some nodes
	for i := 1; i <= 5; i++ {
		err := store.AddNode(fmt.Sprintf("node%d", i))
		if err != nil {
			t.Fatalf("Failed to add node%d: %v", i, err)
		}
	}
	
	// Put a large number of keys
	keyCount := 1000
	for i := 0; i < keyCount; i++ {
		key := strconv.Itoa(i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			t.Fatalf("Failed to put key %s: %v", key, err)
		}
	}
	
	// Get all keys to ensure they're accessible
	for i := 0; i < keyCount; i++ {
		key := strconv.Itoa(i)
		expectedValue := fmt.Sprintf("value%d", i)
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get key %s: %v", key, err)
			continue
		}
		if value != expectedValue {
			t.Errorf("Expected %s for key %s, got %s", expectedValue, key, value)
		}
	}
}

func BenchmarkPut(b *testing.B) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add some nodes
	for i := 1; i <= 5; i++ {
		store.AddNode(fmt.Sprintf("node%d", i))
	}
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := store.Put(key, value)
		if err != nil {
			b.Fatalf("Failed to put %s: %v", key, err)
		}
	}
}

func BenchmarkGet(b *testing.B) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add some nodes
	for i := 1; i <= 5; i++ {
		store.AddNode(fmt.Sprintf("node%d", i))
	}
	
	// Put some data
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		store.Put(key, value)
	}
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key%d", i%1000)
		_, err := store.Get(key)
		if err != nil {
			b.Fatalf("Failed to get %s: %v", key, err)
		}
	}
}

func BenchmarkAddRemoveNode(b *testing.B) {
	store := NewDistributedStore(3) // Replication factor of 3
	
	// Add initial nodes
	for i := 1; i <= 5; i++ {
		store.AddNode(fmt.Sprintf("initial-node%d", i))
	}
	
	// Put some data
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		store.Put(key, value)
	}
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		// Add a node
		nodeID := fmt.Sprintf("bench-node%d", i)
		err := store.AddNode(nodeID)
		if err != nil {
			b.Fatalf("Failed to add %s: %v", nodeID, err)
		}
		
		// Remove the node
		err = store.RemoveNode(nodeID)
		if err != nil {
			b.Fatalf("Failed to remove %s: %v", nodeID, err)
		}
	}
}