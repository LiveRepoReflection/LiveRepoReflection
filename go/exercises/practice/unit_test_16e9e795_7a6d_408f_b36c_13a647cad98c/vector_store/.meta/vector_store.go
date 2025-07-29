package vectorstore

import (
	"errors"
	"fmt"
	"sync"
)

// ValueVersion represents a value with its associated vector clock
type ValueVersion struct {
	Value       string
	VectorClock []int
}

// VectorStore is a distributed key-value store that uses vector clocks for conflict resolution
type VectorStore struct {
	data     map[string][]ValueVersion
	numNodes int
	mu       sync.RWMutex
}

// NewVectorStore creates a new VectorStore with the specified number of nodes
func NewVectorStore(numNodes int) *VectorStore {
	return &VectorStore{
		data:     make(map[string][]ValueVersion),
		numNodes: numNodes,
	}
}

// Put adds or updates a key-value pair with the given vector clock
func (vs *VectorStore) Put(key string, value string, vectorClock []int) error {
	// Validate the vector clock
	if vectorClock == nil {
		return errors.New("vector clock cannot be nil")
	}
	if len(vectorClock) != vs.numNodes {
		return fmt.Errorf("vector clock must have %d elements", vs.numNodes)
	}

	vs.mu.Lock()
	defer vs.mu.Unlock()

	// Check if the key exists
	currentVersions, exists := vs.data[key]
	if !exists {
		// Key doesn't exist, add the value as the first version
		vs.data[key] = []ValueVersion{
			{
				Value:       value,
				VectorClock: cloneVectorClock(vectorClock),
			},
		}
		return nil
	}

	// Apply conflict resolution for existing versions
	newVersions := vs.resolveConflicts(currentVersions, value, vectorClock)
	vs.data[key] = newVersions
	
	return nil
}

// Get retrieves all non-conflicting versions of a value for the given key
func (vs *VectorStore) Get(key string) ([]ValueVersion, error) {
	vs.mu.RLock()
	defer vs.mu.RUnlock()

	versions, exists := vs.data[key]
	if !exists {
		return []ValueVersion{}, nil
	}

	// Return a copy of the versions to prevent modification of the store's data
	result := make([]ValueVersion, len(versions))
	for i, v := range versions {
		result[i] = ValueVersion{
			Value:       v.Value,
			VectorClock: cloneVectorClock(v.VectorClock),
		}
	}

	return result, nil
}

// resolveConflicts applies vector clock conflict resolution logic to determine
// which versions to keep and returns the new set of versions
func (vs *VectorStore) resolveConflicts(currentVersions []ValueVersion, newValue string, newVectorClock []int) []ValueVersion {
	// Create a new value version with a copy of the vector clock
	newVersion := ValueVersion{
		Value:       newValue,
		VectorClock: cloneVectorClock(newVectorClock),
	}

	// Check if the new version is a descendant of any existing versions
	// or if any existing version is a descendant of the new version
	var newVersions []ValueVersion
	var supersededByNew bool
	var supersededByExisting bool

	for _, existingVersion := range currentVersions {
		relationship := compareVectorClocks(newVersion.VectorClock, existingVersion.VectorClock)

		switch relationship {
		case descendant:
			// New version descends from existing, so existing is superseded
			supersededByNew = true
		case ancestor:
			// New version is an ancestor of existing, so new is superseded
			supersededByExisting = true
			newVersions = append(newVersions, existingVersion)
		case concurrent:
			// Versions are concurrent, keep both
			newVersions = append(newVersions, existingVersion)
		case equal:
			// Versions are identical, replace with new value
			supersededByNew = true
		}
	}

	// If the new version wasn't superseded by an existing version, add it
	if !supersededByExisting {
		// If the new version supersedes all existing versions, it's the only one to keep
		if supersededByNew {
			newVersions = []ValueVersion{newVersion}
		} else {
			// Otherwise append it to the versions we're keeping
			newVersions = append(newVersions, newVersion)
		}
	}

	return newVersions
}

// Relationship between vector clocks
type clockRelationship int

const (
	ancestor   clockRelationship = iota // A is an ancestor of B
	descendant                          // A is a descendant of B
	concurrent                          // A and B are concurrent
	equal                               // A and B are equal
)

// compareVectorClocks compares two vector clocks and returns their relationship
func compareVectorClocks(a, b []int) clockRelationship {
	if len(a) != len(b) {
		panic("Vector clocks have different dimensions")
	}

	// Check if the vector clocks are equal
	isEqual := true
	for i := 0; i < len(a); i++ {
		if a[i] != b[i] {
			isEqual = false
			break
		}
	}
	if isEqual {
		return equal
	}

	// Check if A is a descendant of B (A[i] >= B[i] for all i, with at least one A[j] > B[j])
	aDescendant := true
	aGreaterAtLeastOnce := false
	for i := 0; i < len(a); i++ {
		if a[i] < b[i] {
			aDescendant = false
			break
		}
		if a[i] > b[i] {
			aGreaterAtLeastOnce = true
		}
	}
	if aDescendant && aGreaterAtLeastOnce {
		return descendant
	}

	// Check if B is a descendant of A (B[i] >= A[i] for all i, with at least one B[j] > A[j])
	bDescendant := true
	bGreaterAtLeastOnce := false
	for i := 0; i < len(a); i++ {
		if b[i] < a[i] {
			bDescendant = false
			break
		}
		if b[i] > a[i] {
			bGreaterAtLeastOnce = true
		}
	}
	if bDescendant && bGreaterAtLeastOnce {
		return ancestor
	}

	// If neither is a descendant of the other, they are concurrent
	return concurrent
}

// cloneVectorClock creates a copy of a vector clock
func cloneVectorClock(vc []int) []int {
	clone := make([]int, len(vc))
	copy(clone, vc)
	return clone
}