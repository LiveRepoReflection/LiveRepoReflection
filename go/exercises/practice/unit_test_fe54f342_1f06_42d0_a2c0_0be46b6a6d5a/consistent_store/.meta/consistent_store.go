package consistentstore

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"math"
	"sort"
	"sync"
)

const (
	virtualNodesPerServer = 1024
	replicationFactor    = 3
)

type Server struct {
	id       string
	data     map[string][]byte
	mutex    sync.RWMutex
	virtuals []uint64
}

type Store struct {
	servers     map[string]*Server
	virtualMap  map[uint64]string // maps virtual node position to server ID
	ring        []uint64         // sorted list of virtual node positions
	mutex       sync.RWMutex
}

func NewStore() *Store {
	return &Store{
		servers:    make(map[string]*Server),
		virtualMap: make(map[uint64]string),
		ring:      make([]uint64, 0),
	}
}

func (s *Store) AddServer(serverID string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if _, exists := s.servers[serverID]; exists {
		return errors.New("server already exists")
	}

	server := &Server{
		id:       serverID,
		data:     make(map[string][]byte),
		virtuals: make([]uint64, 0, virtualNodesPerServer),
	}

	// Create virtual nodes
	for i := 0; i < virtualNodesPerServer; i++ {
		hash := s.hashKey([]byte(serverID + string(rune(i))))
		server.virtuals = append(server.virtuals, hash)
		s.virtualMap[hash] = serverID
	}

	s.servers[serverID] = server
	s.updateRing()
	s.rebalanceData()

	return nil
}

func (s *Store) RemoveServer(serverID string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	server, exists := s.servers[serverID]
	if !exists {
		return errors.New("server does not exist")
	}

	// Remove virtual nodes
	for _, hash := range server.virtuals {
		delete(s.virtualMap, hash)
	}

	// Redistribute data
	for key, value := range server.data {
		targetServer := s.getServerForKey([]byte(key))
		if targetServer != nil && targetServer.id != serverID {
			targetServer.mutex.Lock()
			targetServer.data[key] = value
			targetServer.mutex.Unlock()
		}
	}

	delete(s.servers, serverID)
	s.updateRing()

	return nil
}

func (s *Store) Put(key, value []byte) error {
	if key == nil || value == nil {
		return errors.New("key and value cannot be nil")
	}

	s.mutex.RLock()
	if len(s.servers) == 0 {
		s.mutex.RUnlock()
		return errors.New("no servers available")
	}

	// Find primary and replica servers
	servers := s.getReplicaServers(key)
	s.mutex.RUnlock()

	// Store on all replica servers
	for _, server := range servers {
		server.mutex.Lock()
		server.data[string(key)] = value
		server.mutex.Unlock()
	}

	return nil
}

func (s *Store) Get(key []byte) ([]byte, error) {
	if key == nil {
		return nil, errors.New("key cannot be nil")
	}

	s.mutex.RLock()
	if len(s.servers) == 0 {
		s.mutex.RUnlock()
		return nil, errors.New("no servers available")
	}

	servers := s.getReplicaServers(key)
	s.mutex.RUnlock()

	// Try to get from any replica
	for _, server := range servers {
		server.mutex.RLock()
		if value, exists := server.data[string(key)]; exists {
			server.mutex.RUnlock()
			return value, nil
		}
		server.mutex.RUnlock()
	}

	return nil, errors.New("key not found")
}

func (s *Store) Remove(key []byte) error {
	if key == nil {
		return errors.New("key cannot be nil")
	}

	s.mutex.RLock()
	if len(s.servers) == 0 {
		s.mutex.RUnlock()
		return errors.New("no servers available")
	}

	servers := s.getReplicaServers(key)
	s.mutex.RUnlock()

	// Remove from all replicas
	for _, server := range servers {
		server.mutex.Lock()
		delete(server.data, string(key))
		server.mutex.Unlock()
	}

	return nil
}

func (s *Store) hashKey(key []byte) uint64 {
	hash := sha256.Sum256(key)
	return binary.BigEndian.Uint64(hash[:8])
}

func (s *Store) updateRing() {
	s.ring = make([]uint64, 0, len(s.virtualMap))
	for hash := range s.virtualMap {
		s.ring = append(s.ring, hash)
	}
	sort.Slice(s.ring, func(i, j int) bool {
		return s.ring[i] < s.ring[j]
	})
}

func (s *Store) getServerForKey(key []byte) *Server {
	if len(s.ring) == 0 {
		return nil
	}

	hash := s.hashKey(key)
	idx := sort.Search(len(s.ring), func(i int) bool {
		return s.ring[i] >= hash
	})

	if idx == len(s.ring) {
		idx = 0
	}

	serverID := s.virtualMap[s.ring[idx]]
	return s.servers[serverID]
}

func (s *Store) getReplicaServers(key []byte) []*Server {
	if len(s.ring) == 0 {
		return nil
	}

	hash := s.hashKey(key)
	replicas := make([]*Server, 0, replicationFactor)
	seen := make(map[string]bool)

	idx := sort.Search(len(s.ring), func(i int) bool {
		return s.ring[i] >= hash
	})

	if idx == len(s.ring) {
		idx = 0
	}

	// Find unique servers for replication
	for len(replicas) < replicationFactor && len(replicas) < len(s.servers) {
		serverID := s.virtualMap[s.ring[idx]]
		if !seen[serverID] {
			seen[serverID] = true
			replicas = append(replicas, s.servers[serverID])
		}
		idx = (idx + 1) % len(s.ring)
	}

	return replicas
}

func (s *Store) rebalanceData() {
	// Collect all data
	allData := make(map[string][]byte)
	for _, server := range s.servers {
		server.mutex.RLock()
		for k, v := range server.data {
			allData[k] = v
		}
		server.mutex.RUnlock()
	}

	// Clear all servers
	for _, server := range s.servers {
		server.mutex.Lock()
		server.data = make(map[string][]byte)
		server.mutex.Unlock()
	}

	// Redistribute data
	for key, value := range allData {
		servers := s.getReplicaServers([]byte(key))
		for _, server := range servers {
			server.mutex.Lock()
			server.data[key] = value
			server.mutex.Unlock()
		}
	}
}

func (s *Store) GetLoadDistribution() map[string]float64 {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	distribution := make(map[string]float64)
	totalKeys := 0

	for serverID, server := range s.servers {
		server.mutex.RLock()
		keyCount := len(server.data)
		server.mutex.RUnlock()
		distribution[serverID] = float64(keyCount)
		totalKeys += keyCount
	}

	if totalKeys > 0 {
		for serverID := range distribution {
			distribution[serverID] = (distribution[serverID] / float64(totalKeys)) * 100
		}
	}

	return distribution
}

func (s *Store) GetServerCount() int {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	return len(s.servers)
}

func (s *Store) GetStandardDeviation() float64 {
	distribution := s.GetLoadDistribution()
	if len(distribution) == 0 {
		return 0
	}

	mean := 100.0 / float64(len(distribution))
	variance := 0.0

	for _, load := range distribution {
		diff := load - mean
		variance += (diff * diff)
	}

	variance /= float64(len(distribution))
	return math.Sqrt(variance)
}