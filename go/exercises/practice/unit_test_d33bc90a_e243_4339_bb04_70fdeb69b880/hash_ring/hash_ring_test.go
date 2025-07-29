package hashring

import (
	"fmt"
	"sync"
	"testing"
)

func TestAddNode(t *testing.T) {
	tests := []struct {
		name          string
		nodes         []string
		virtualNodes  int
		expectedSize  int
		expectedError bool
	}{
		{
			name:          "add single node",
			nodes:         []string{"node1"},
			virtualNodes:  10,
			expectedSize:  1,
			expectedError: false,
		},
		{
			name:          "add multiple nodes",
			nodes:         []string{"node1", "node2", "node3"},
			virtualNodes:  10,
			expectedSize:  3,
			expectedError: false,
		},
		{
			name:          "add duplicate node",
			nodes:         []string{"node1", "node1"},
			virtualNodes:  10,
			expectedSize:  1,
			expectedError: true,
		},
		{
			name:          "add empty node name",
			nodes:         []string{""},
			virtualNodes:  10,
			expectedSize:  0,
			expectedError: true,
		},
		{
			name:          "add node with zero virtual nodes",
			nodes:         []string{"node1"},
			virtualNodes:  0,
			expectedSize:  0,
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ring := New()
			var lastErr error
			for _, node := range tt.nodes {
				err := ring.AddNode(node, tt.virtualNodes)
				if err != nil {
					lastErr = err
				}
			}

			if tt.expectedError && lastErr == nil {
				t.Error("expected error but got none")
			}
			if !tt.expectedError && lastErr != nil {
				t.Errorf("unexpected error: %v", lastErr)
			}

			if ring.Size() != tt.expectedSize {
				t.Errorf("expected size %d, got %d", tt.expectedSize, ring.Size())
			}
		})
	}
}

func TestRemoveNode(t *testing.T) {
	tests := []struct {
		name          string
		setupNodes    []string
		removeNode    string
		expectedSize  int
		expectedError bool
	}{
		{
			name:          "remove existing node",
			setupNodes:    []string{"node1", "node2"},
			removeNode:    "node1",
			expectedSize:  1,
			expectedError: false,
		},
		{
			name:          "remove non-existing node",
			setupNodes:    []string{"node1"},
			removeNode:    "node2",
			expectedSize:  1,
			expectedError: true,
		},
		{
			name:          "remove from empty ring",
			setupNodes:    []string{},
			removeNode:    "node1",
			expectedSize:  0,
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ring := New()
			for _, node := range tt.setupNodes {
				_ = ring.AddNode(node, 10)
			}

			err := ring.RemoveNode(tt.removeNode)
			if tt.expectedError && err == nil {
				t.Error("expected error but got none")
			}
			if !tt.expectedError && err != nil {
				t.Errorf("unexpected error: %v", err)
			}

			if ring.Size() != tt.expectedSize {
				t.Errorf("expected size %d, got %d", tt.expectedSize, ring.Size())
			}
		})
	}
}

func TestGetNode(t *testing.T) {
	tests := []struct {
		name          string
		setupNodes    []string
		keys         []string
		expectedError bool
	}{
		{
			name:          "get node for keys with multiple nodes",
			setupNodes:    []string{"node1", "node2", "node3"},
			keys:         []string{"key1", "key2", "key3"},
			expectedError: false,
		},
		{
			name:          "get node with empty ring",
			setupNodes:    []string{},
			keys:         []string{"key1"},
			expectedError: true,
		},
		{
			name:          "get node with empty key",
			setupNodes:    []string{"node1"},
			keys:         []string{""},
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ring := New()
			for _, node := range tt.setupNodes {
				_ = ring.AddNode(node, 10)
			}

			for _, key := range tt.keys {
				node, err := ring.GetNode(key)
				if tt.expectedError && err == nil {
					t.Error("expected error but got none")
				}
				if !tt.expectedError && err != nil {
					t.Errorf("unexpected error: %v", err)
				}
				if !tt.expectedError && node == "" {
					t.Error("expected non-empty node but got empty string")
				}
			}
		})
	}
}

func TestConcurrency(t *testing.T) {
	ring := New()
	var wg sync.WaitGroup
	numOperations := 1000

	// Test concurrent additions
	wg.Add(numOperations)
	for i := 0; i < numOperations; i++ {
		go func(i int) {
			defer wg.Done()
			_ = ring.AddNode(fmt.Sprintf("node%d", i), 10)
		}(i)
	}
	wg.Wait()

	// Test concurrent lookups
	wg.Add(numOperations)
	for i := 0; i < numOperations; i++ {
		go func(i int) {
			defer wg.Done()
			_, _ = ring.GetNode(fmt.Sprintf("key%d", i))
		}(i)
	}
	wg.Wait()

	// Test concurrent removals
	wg.Add(numOperations)
	for i := 0; i < numOperations; i++ {
		go func(i int) {
			defer wg.Done()
			_ = ring.RemoveNode(fmt.Sprintf("node%d", i))
		}(i)
	}
	wg.Wait()
}

func BenchmarkAddNode(b *testing.B) {
	ring := New()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ring.AddNode(fmt.Sprintf("node%d", i), 10)
	}
}

func BenchmarkGetNode(b *testing.B) {
	ring := New()
	for i := 0; i < 1000; i++ {
		_ = ring.AddNode(fmt.Sprintf("node%d", i), 10)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = ring.GetNode(fmt.Sprintf("key%d", i))
	}
}

func BenchmarkRemoveNode(b *testing.B) {
	ring := New()
	nodes := make([]string, b.N)
	for i := 0; i < b.N; i++ {
		nodeName := fmt.Sprintf("node%d", i)
		nodes[i] = nodeName
		_ = ring.AddNode(nodeName, 10)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ring.RemoveNode(nodes[i])
	}
}