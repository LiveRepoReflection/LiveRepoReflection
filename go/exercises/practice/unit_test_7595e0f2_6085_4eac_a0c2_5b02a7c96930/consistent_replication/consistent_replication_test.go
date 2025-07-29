package consistent_replication

import (
	"strconv"
	"sync"
	"testing"
)

func TestWriteNewKey(t *testing.T) {
	store := NewStore()
	// Write to a new key with no parents.
	versionID, err := store.Write("key1", "value1", []string{})
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	if versionID == "" {
		t.Fatalf("Expected non-empty versionID for new write")
	}
	// Read should return the same value and version.
	val, leaf, err := store.Read("key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "value1" {
		t.Errorf("Expected value 'value1', got: %s", val)
	}
	if leaf != versionID {
		t.Errorf("Expected leaf version %s, got: %s", versionID, leaf)
	}
}

func TestWriteWithParents(t *testing.T) {
	store := NewStore()
	// Initial write.
	v1, err := store.Write("key1", "initial", []string{})
	if err != nil {
		t.Fatalf("Initial Write failed: %v", err)
	}
	// Write a new version using v1 as parent.
	v2, err := store.Write("key1", "updated", []string{v1})
	if err != nil {
		t.Fatalf("Write with parent failed: %v", err)
	}
	// Read should now return the updated value.
	val, leaf, err := store.Read("key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "updated" {
		t.Errorf("Expected value 'updated', got: %s", val)
	}
	if leaf != v2 {
		t.Errorf("Expected leaf version %s, got: %s", v2, leaf)
	}
}

func TestWriteInvalidParent(t *testing.T) {
	store := NewStore()
	// Try to write with an invalid parent version id.
	_, err := store.Write("key1", "value", []string{"nonexistent"})
	if err == nil {
		t.Fatalf("Expected error for invalid parent version id, but got nil")
	}
}

func TestReadNonExistentKey(t *testing.T) {
	store := NewStore()
	// Reading a non-existent key must return an error.
	_, _, err := store.Read("nonexistent")
	if err == nil {
		t.Fatalf("Expected error when reading non-existent key, but got nil")
	}
}

func TestCausalConsistency(t *testing.T) {
	store := NewStore()
	// Write an initial version.
	v1, err := store.Write("key2", "version1", []string{})
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	// Write a derived version referencing v1.
	v2, err := store.Write("key2", "version2", []string{v1})
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	// Reading key2 should never return the older version if v2 exists.
	val, leaf, err := store.Read("key2")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if leaf == v1 {
		t.Errorf("Causal consistency violated: returned parent version %s instead of child version %s", v1, v2)
	}
	if val != "version2" {
		t.Errorf("Expected value 'version2', got: %s", val)
	}
}

func TestConcurrentWrites(t *testing.T) {
	store := NewStore()
	// Write an initial version for key3.
	initial, err := store.Write("key3", "init", []string{})
	if err != nil {
		t.Fatalf("Initial Write failed: %v", err)
	}

	var wg sync.WaitGroup
	numGoroutines := 50
	versions := make([]string, numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// Each concurrent write uses the same parent (initial) for simplicity.
			ver, err := store.Write("key3", "value"+strconv.Itoa(i), []string{initial})
			if err != nil {
				t.Errorf("Concurrent Write failed: %v", err)
				return
			}
			versions[i] = ver
		}(i)
	}
	wg.Wait()
	// Read should return one of the concurrently written versions.
	val, leaf, err := store.Read("key3")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	found := false
	for _, v := range versions {
		if v == leaf {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Leaf version %s not among concurrent writes", leaf)
	}
	if val == "init" {
		t.Errorf("Expected value from concurrent writes, but got initial value")
	}
}

func TestMultipleLatestVersions(t *testing.T) {
	store := NewStore()
	// Write a base version.
	base, err := store.Write("key4", "base", []string{})
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	// Create two branches from the base version.
	v2, err := store.Write("key4", "branch1", []string{base})
	if err != nil {
		t.Fatalf("Write for branch1 failed: %v", err)
	}
	v3, err := store.Write("key4", "branch2", []string{base})
	if err != nil {
		t.Fatalf("Write for branch2 failed: %v", err)
	}
	// Read should return one of the branch values.
	val, leaf, err := store.Read("key4")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if leaf != v2 && leaf != v3 {
		t.Errorf("Expected leaf version to be either %s or %s, got: %s", v2, v3, leaf)
	}
	if val != "branch1" && val != "branch2" {
		t.Errorf("Expected value 'branch1' or 'branch2', got: %s", val)
	}
}