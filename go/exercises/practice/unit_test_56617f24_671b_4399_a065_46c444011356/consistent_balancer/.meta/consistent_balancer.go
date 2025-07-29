package consistent_balancer

import (
	"crypto/sha256"
	"encoding/binary"
	"sort"
	"strconv"
	"sync"
)

type Balancer struct {
	replicaCount int
	ring         []uint64            // Sorted slice of virtual node hashes
	hashMap      map[uint64]string   // Mapping from virtual node hash to server ID
	servers      map[string]bool     // Registered servers with online status
	serverNodes  map[string][]uint64 // Mapping from server ID to its virtual node hashes
	mutex        sync.RWMutex
}

func NewBalancer(replicaCount int) *Balancer {
	return &Balancer{
		replicaCount: replicaCount,
		ring:         make([]uint64, 0),
		hashMap:      make(map[uint64]string),
		servers:      make(map[string]bool),
		serverNodes:  make(map[string][]uint64),
	}
}

func (b *Balancer) generateHash(key string) uint64 {
	hash := sha256.Sum256([]byte(key))
	return binary.LittleEndian.Uint64(hash[:8])
}

func (b *Balancer) RegisterServer(serverID string) {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	if _, exists := b.servers[serverID]; exists {
		return
	}
	b.servers[serverID] = true

	var vnodeHashes []uint64
	for i := 0; i < b.replicaCount; i++ {
		vnodeKey := serverID + ":" + strconv.Itoa(i)
		vnodeHash := b.generateHash(vnodeKey)
		b.ring = append(b.ring, vnodeHash)
		b.hashMap[vnodeHash] = serverID
		vnodeHashes = append(vnodeHashes, vnodeHash)
	}
	b.serverNodes[serverID] = vnodeHashes
	sort.Slice(b.ring, func(i, j int) bool {
		return b.ring[i] < b.ring[j]
	})
}

func (b *Balancer) UnregisterServer(serverID string) {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	if _, exists := b.servers[serverID]; !exists {
		return
	}
	delete(b.servers, serverID)

	vnodeHashes, exists := b.serverNodes[serverID]
	if exists {
		for _, hashVal := range vnodeHashes {
			delete(b.hashMap, hashVal)
			index := sort.Search(len(b.ring), func(i int) bool {
				return b.ring[i] >= hashVal
			})
			if index < len(b.ring) && b.ring[index] == hashVal {
				b.ring = append(b.ring[:index], b.ring[index+1:]...)
			}
		}
		delete(b.serverNodes, serverID)
	}
}

func (b *Balancer) GetServerStatus(serverID string) string {
	b.mutex.RLock()
	defer b.mutex.RUnlock()

	if _, exists := b.servers[serverID]; exists {
		return "online"
	}
	return "offline"
}

func (b *Balancer) GetServerForKey(key string) string {
	b.mutex.RLock()
	defer b.mutex.RUnlock()

	if len(b.ring) == 0 {
		return ""
	}
	keyHash := b.generateHash(key)
	index := sort.Search(len(b.ring), func(i int) bool {
		return b.ring[i] >= keyHash
	})
	if index == len(b.ring) {
		index = 0
	}
	return b.hashMap[b.ring[index]]
}