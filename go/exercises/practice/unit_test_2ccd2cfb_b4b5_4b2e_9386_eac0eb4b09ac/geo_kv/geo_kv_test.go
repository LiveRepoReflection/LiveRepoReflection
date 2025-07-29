package geo_kv

import (
	"testing"
	"time"
)

func TestKeyValueStore(t *testing.T) {
	config := Config{
		DataCenters: []DataCenterConfig{
			{
				ID: "dc1",
				Nodes: []string{"node1:8080", "node2:8080"},
			},
			{
				ID: "dc2",
				Nodes: []string{"node3:8080", "node4:8080"},
			},
		},
		ReplicationFactor: 3,
		ConsistencyLevel: ConsistencyLevelQuorum,
	}

	store, err := NewKeyValueStore(config)
	if err != nil {
		t.Fatalf("Failed to create key-value store: %v", err)
	}

	// Basic put and get
	key := "test_key"
	value := "test_value"
	err = store.Put(key, value)
	if err != nil {
		t.Errorf("Put failed: %v", err)
	}

	retrievedValue, exists, err := store.Get(key)
	if err != nil {
		t.Errorf("Get failed: %v", err)
	}
	if !exists {
		t.Error("Key should exist but doesn't")
	}
	if retrievedValue != value {
		t.Errorf("Expected value %s, got %s", value, retrievedValue)
	}

	// Test non-existent key
	_, exists, err = store.Get("non_existent_key")
	if err != nil {
		t.Errorf("Get failed: %v", err)
	}
	if exists {
		t.Error("Key should not exist but does")
	}

	// Test concurrent writes
	concurrency := 10
	done := make(chan bool)
	for i := 0; i < concurrency; i++ {
		go func(i int) {
			err := store.Put("concurrent_key", string(rune(i)))
			if err != nil {
				t.Errorf("Concurrent put failed: %v", err)
			}
			done <- true
		}(i)
	}

	for i := 0; i < concurrency; i++ {
		<-done
	}

	// Test quorum consistency
	// This would require mocking network partitions in a real implementation
	// For now just verify we can still read after write
	err = store.Put("quorum_key", "quorum_value")
	if err != nil {
		t.Errorf("Put failed during quorum test: %v", err)
	}

	// Test data center failure simulation
	// In a real implementation, we would simulate a DC going down
	// Here we just verify the store still operates
	err = store.Put("dc_failure_key", "dc_failure_value")
	if err != nil {
		t.Errorf("Put failed during DC failure test: %v", err)
	}

	// Test large value
	largeValue := make([]byte, 1024*1024) // 1MB
	err = store.Put("large_key", string(largeValue))
	if err != nil {
		t.Errorf("Failed to store large value: %v", err)
	}

	// Test timeout handling
	// This would require mocking slow responses in a real implementation
	// For now just verify basic timeout behavior
	timeout := time.Second
	doneChan := make(chan bool)
	go func() {
		_, _, _ = store.Get("timeout_key")
		doneChan <- true
	}()

	select {
	case <-doneChan:
		// Success
	case <-time.After(timeout):
		t.Error("Operation timed out")
	}
}

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name        string
		config      Config
		expectError bool
	}{
		{
			name: "Valid config",
			config: Config{
				DataCenters: []DataCenterConfig{
					{ID: "dc1", Nodes: []string{"node1:8080"}},
				},
				ReplicationFactor: 1,
				ConsistencyLevel: ConsistencyLevelQuorum,
			},
			expectError: false,
		},
		{
			name: "No data centers",
			config: Config{
				DataCenters:       []DataCenterConfig{},
				ReplicationFactor: 1,
			},
			expectError: true,
		},
		{
			name: "Replication factor too high",
			config: Config{
				DataCenters: []DataCenterConfig{
					{ID: "dc1", Nodes: []string{"node1:8080"}},
				},
				ReplicationFactor: 2,
			},
			expectError: true,
		},
		{
			name: "Invalid consistency level",
			config: Config{
				DataCenters: []DataCenterConfig{
					{ID: "dc1", Nodes: []string{"node1:8080"}},
				},
				ReplicationFactor: 1,
				ConsistencyLevel: "invalid",
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := NewKeyValueStore(tt.config)
			if tt.expectError && err == nil {
				t.Error("Expected error but got none")
			}
			if !tt.expectError && err != nil {
				t.Errorf("Unexpected error: %v", err)
			}
		})
	}
}