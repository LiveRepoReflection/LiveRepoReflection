package consistent_replication

import (
	"errors"
	"strconv"
	"sync"
)

type Version struct {
	id      string
	value   string
	parents []string
	// children holds the ids of versions that derive from this version.
	children []string
}

type keyStore struct {
	// versions maps version id to Version.
	versions map[string]*Version
}

type Store struct {
	mu             sync.RWMutex
	keys           map[string]*keyStore
	versionCounter int64
}

func NewStore() *Store {
	return &Store{
		keys:           make(map[string]*keyStore),
		versionCounter: 0,
	}
}

// Write creates a new version for the specified key. 
// It returns the new version's id or an error if any parent ids are invalid or cyclic dependencies are introduced.
func (s *Store) Write(key string, value string, parents []string) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// If key does not exist, it must be a new key with no parents.
	ks, exists := s.keys[key]
	if !exists {
		if len(parents) > 0 {
			return "", errors.New("cannot specify parents for a non-existent key")
		}
		ks = &keyStore{
			versions: make(map[string]*Version),
		}
		s.keys[key] = ks
	}

	// Validate that all parents exist.
	for _, pid := range parents {
		if _, ok := ks.versions[pid]; !ok {
			return "", errors.New("invalid parent version id: " + pid)
		}
	}

	// Generate a unique version id.
	s.versionCounter++
	newVersionID := strconv.FormatInt(s.versionCounter, 10)

	// Create the new version.
	newVersion := &Version{
		id:      newVersionID,
		value:   value,
		parents: parents,
		// children is initially empty.
		children: []string{},
	}

	// Add newVersion as a child to each parent.
	for _, pid := range parents {
		parentVersion := ks.versions[pid]
		parentVersion.children = append(parentVersion.children, newVersionID)
	}

	// Insert the new version into the key's versions.
	ks.versions[newVersionID] = newVersion

	return newVersionID, nil
}

// Read returns the value and version id of a "latest" version (leaf in the DAG) for the specified key.
// It returns an error if the key is not found or if no latest version exists.
func (s *Store) Read(key string) (string, string, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	ks, exists := s.keys[key]
	if !exists {
		return "", "", errors.New("key not found")
	}
	// A leaf version is one that has no children.
	for _, ver := range ks.versions {
		if len(ver.children) == 0 {
			// Ensure causal consistency: if a version has parents, then all its parents are in the versions map.
			// In this implementation, a version is only added after its parents have been verified and updated,
			// so we can safely return the leaf.
			return ver.value, ver.id, nil
		}
	}
	return "", "", errors.New("no latest version found")
}