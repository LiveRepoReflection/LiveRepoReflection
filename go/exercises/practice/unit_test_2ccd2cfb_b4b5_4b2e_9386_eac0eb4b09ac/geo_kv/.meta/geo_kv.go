package geo_kv

import (
	"errors"
	"sync"
	"time"
)

type KeyValueStore interface {
	Get(key string) (string, bool, error)
	Put(key, value string) error
}

type kvStore struct {
	config        Config
	data          map[string]string
	mu            sync.RWMutex
	replicaNodes  map[string][]string
	quorum        int
	healthChecker *healthCheck
}

type healthCheck struct {
	nodeStatus map[string]bool
	lastCheck  map[string]time.Time
	mu         sync.RWMutex
}

func NewKeyValueStore(config Config) (KeyValueStore, error) {
	if err := validateConfig(config); err != nil {
		return nil, err
	}

	store := &kvStore{
		config: config,
		data:   make(map[string]string),
		healthChecker: &healthCheck{
			nodeStatus: make(map[string]bool),
			lastCheck:  make(map[string]time.Time),
		},
	}

	store.initializeReplicaNodes()
	store.quorum = (config.ReplicationFactor / 2) + 1

	go store.healthChecker.monitorNodes()

	return store, nil
}

func (k *kvStore) Get(key string) (string, bool, error) {
	k.mu.RLock()
	defer k.mu.RUnlock()

	value, exists := k.data[key]
	return value, exists, nil
}

func (k *kvStore) Put(key, value string) error {
	if len(key) > 1024*1024 || len(value) > 1024*1024 {
		return errors.New("key or value exceeds 1MB limit")
	}

	k.mu.Lock()
	defer k.mu.Unlock()

	k.data[key] = value

	// In a real implementation, we would replicate to other nodes here
	// For this simplified version, we just store locally
	return nil
}

func (k *kvStore) initializeReplicaNodes() {
	k.replicaNodes = make(map[string][]string)
	for _, dc := range k.config.DataCenters {
		for _, node := range dc.Nodes {
			k.replicaNodes[node] = make([]string, 0)
			k.healthChecker.nodeStatus[node] = true
			k.healthChecker.lastCheck[node] = time.Now()
		}
	}
}

func (h *healthCheck) monitorNodes() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		h.mu.Lock()
		for node := range h.nodeStatus {
			// In a real implementation, we would actually ping the node
			// For this simplified version, we just mark all nodes as healthy
			h.nodeStatus[node] = true
			h.lastCheck[node] = time.Now()
		}
		h.mu.Unlock()
	}
}

func validateConfig(config Config) error {
	if len(config.DataCenters) == 0 {
		return errors.New("at least one data center must be specified")
	}

	totalNodes := 0
	for _, dc := range config.DataCenters {
		if len(dc.Nodes) == 0 {
			return errors.New("data center must have at least one node")
		}
		totalNodes += len(dc.Nodes)
	}

	if config.ReplicationFactor < 1 || config.ReplicationFactor > totalNodes {
		return errors.New("replication factor must be between 1 and total number of nodes")
	}

	switch config.ConsistencyLevel {
	case ConsistencyLevelQuorum, ConsistencyLevelStrong, ConsistencyLevelEventual:
		// valid
	default:
		return errors.New("invalid consistency level")
	}

	return nil
}