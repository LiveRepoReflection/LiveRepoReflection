package adaptive_load_balancer

import (
	"crypto/md5"
	"encoding/binary"
	"sort"
	"strconv"
	"sync"
)

type virtualNode struct {
	hash     uint32
	serverID int
}

type LoadBalancer struct {
	mu           sync.RWMutex
	ring         []virtualNode
	serverVNodes map[int][]uint32
	capacityMap  map[int]int
}

func NewLoadBalancer() *LoadBalancer {
	return &LoadBalancer{
		ring:         make([]virtualNode, 0),
		serverVNodes: make(map[int][]uint32),
		capacityMap:  make(map[int]int),
	}
}

func hashString(s string) uint32 {
	h := md5.Sum([]byte(s))
	return binary.LittleEndian.Uint32(h[:4])
}

func computeVirtualNodes(serverID int, capacity int) []virtualNode {
	num := capacity / 10
	if num < 1 {
		num = 1
	}
	nodes := make([]virtualNode, num)
	for i := 0; i < num; i++ {
		s := strconv.Itoa(serverID) + "-" + strconv.Itoa(i)
		nodes[i] = virtualNode{
			hash:     hashString(s),
			serverID: serverID,
		}
	}
	return nodes
}

func (lb *LoadBalancer) rebuildRing() {
	newRing := make([]virtualNode, 0)
	for serverID, vnodes := range lb.serverVNodes {
		for _, h := range vnodes {
			newRing = append(newRing, virtualNode{hash: h, serverID: serverID})
		}
	}
	sort.Slice(newRing, func(i, j int) bool {
		return newRing[i].hash < newRing[j].hash
	})
	lb.ring = newRing
}

func (lb *LoadBalancer) AddServer(serverID int, capacity int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if _, exists := lb.serverVNodes[serverID]; exists {
		return
	}
	lb.capacityMap[serverID] = capacity
	nodes := computeVirtualNodes(serverID, capacity)
	vnodeHashes := make([]uint32, len(nodes))
	for i, n := range nodes {
		vnodeHashes[i] = n.hash
	}
	lb.serverVNodes[serverID] = vnodeHashes
	lb.rebuildRing()
}

func (lb *LoadBalancer) RemoveServer(serverID int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	delete(lb.serverVNodes, serverID)
	delete(lb.capacityMap, serverID)
	lb.rebuildRing()
}

func (lb *LoadBalancer) UpdateCapacity(serverID int, newCapacity int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if _, exists := lb.serverVNodes[serverID]; !exists {
		return
	}
	lb.capacityMap[serverID] = newCapacity
	nodes := computeVirtualNodes(serverID, newCapacity)
	vnodeHashes := make([]uint32, len(nodes))
	for i, n := range nodes {
		vnodeHashes[i] = n.hash
	}
	lb.serverVNodes[serverID] = vnodeHashes
	lb.rebuildRing()
}

func (lb *LoadBalancer) GetServer(requestID string) int {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	if len(lb.ring) == 0 {
		return -1
	}
	h := hashString(requestID)
	idx := sort.Search(len(lb.ring), func(i int) bool {
		return lb.ring[i].hash >= h
	})
	if idx == len(lb.ring) {
		idx = 0
	}
	return lb.ring[idx].serverID
}

func (lb *LoadBalancer) GetDistribution() map[int][]uint32 {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	dist := make(map[int][]uint32)
	for serverID, vnodes := range lb.serverVNodes {
		nodesCopy := make([]uint32, len(vnodes))
		copy(nodesCopy, vnodes)
		dist[serverID] = nodesCopy
	}
	return dist
}