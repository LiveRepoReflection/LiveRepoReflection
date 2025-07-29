package net_orchestrator

import (
	"testing"
	"sync"
)

func TestAddAndRemoveVM(t *testing.T) {
	no := NewNetworkOrchestrator()
	
	// Test adding a VM
	err := no.AddVM("vm1")
	if err != nil {
		t.Errorf("AddVM failed: %v", err)
	}

	// Test adding duplicate VM
	err = no.AddVM("vm1")
	if err == nil {
		t.Error("Expected error when adding duplicate VM")
	}

	// Test removing VM
	err = no.RemoveVM("vm1")
	if err != nil {
		t.Errorf("RemoveVM failed: %v", err)
	}

	// Test removing non-existent VM
	err = no.RemoveVM("vm2")
	if err == nil {
		t.Error("Expected error when removing non-existent VM")
	}
}

func TestLinkOperations(t *testing.T) {
	no := NewNetworkOrchestrator()
	no.AddVM("vm1")
	no.AddVM("vm2")

	// Test adding link
	err := no.AddLink("vm1", "vm2", 100)
	if err != nil {
		t.Errorf("AddLink failed: %v", err)
	}

	// Test updating bandwidth
	err = no.UpdateLinkBandwidth("vm1", "vm2", 200)
	if err != nil {
		t.Errorf("UpdateLinkBandwidth failed: %v", err)
	}

	// Test removing link
	err = no.RemoveLink("vm1", "vm2")
	if err != nil {
		t.Errorf("RemoveLink failed: %v", err)
	}

	// Test operations on non-existent links
	err = no.UpdateLinkBandwidth("vm1", "vm2", 300)
	if err == nil {
		t.Error("Expected error when updating non-existent link")
	}

	err = no.RemoveLink("vm1", "vm2")
	if err == nil {
		t.Error("Expected error when removing non-existent link")
	}
}

func TestMaxBandwidthPath(t *testing.T) {
	no := NewNetworkOrchestrator()
	no.AddVM("vm1")
	no.AddVM("vm2")
	no.AddVM("vm3")
	no.AddVM("vm4")

	no.AddLink("vm1", "vm2", 100)
	no.AddLink("vm2", "vm3", 200)
	no.AddLink("vm3", "vm4", 50)
	no.AddLink("vm1", "vm4", 300)

	// Test path finding
	path := no.FindMaxBandwidthPath("vm1", "vm4")
	expected := []string{"vm1", "vm4"}
	if !equalSlices(path, expected) {
		t.Errorf("Expected path %v, got %v", expected, path)
	}

	// Test path with higher minimum bandwidth
	path = no.FindMaxBandwidthPath("vm1", "vm3")
	expectedOptions := [][]string{
		{"vm1", "vm2", "vm3"},
		{"vm1", "vm4", "vm3"},
	}
	if !containsPath(expectedOptions, path) {
		t.Errorf("Path %v not in expected options %v", path, expectedOptions)
	}

	// Test non-existent path
	no.AddVM("vm5")
	path = no.FindMaxBandwidthPath("vm1", "vm5")
	if len(path) != 0 {
		t.Errorf("Expected empty path, got %v", path)
	}
}

func TestConcurrency(t *testing.T) {
	no := NewNetworkOrchestrator()
	var wg sync.WaitGroup

	// Concurrent VM operations
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			vmID := string('a' + byte(id%26))
			no.AddVM(vmID)
			no.RemoveVM(vmID)
		}(i)
	}

	// Concurrent link operations
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			vm1 := string('a' + byte(id%26))
			vm2 := string('a' + byte((id+1)%26))
			no.AddLink(vm1, vm2, id%1000)
			no.UpdateLinkBandwidth(vm1, vm2, (id+1)%1000)
			no.RemoveLink(vm1, vm2)
		}(i)
	}

	wg.Wait()
}

func equalSlices(a, b []string) bool {
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

func containsPath(options [][]string, path []string) bool {
	for _, opt := range options {
		if equalSlices(opt, path) {
			return true
		}
	}
	return false
}