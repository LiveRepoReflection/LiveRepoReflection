package hash_balancer

import (
	"hash/fnv"
	"sort"
	"strconv"
	"sync"
)

type ConsistentHashLoadBalancer struct {
	replicas int
	ring     []uint64
	hashMap  map[uint64]string
	servers  map[string]bool
	dist     map[string]int
	sync.Mutex
}

func NewConsistentHashLoadBalancer(replicas int) *ConsistentHashLoadBalancer {
	return &ConsistentHashLoadBalancer{
		replicas: replicas,
		ring:     make([]uint64, 0),
		hashMap:  make(map[uint64]string),
		servers:  make(map[string]bool),
		dist:     make(map[string]int),
	}
}

func hashKey(key string) uint64 {
	h := fnv.New64a()
	h.Write([]byte(key))
	return h.Sum64()
}

func (lb *ConsistentHashLoadBalancer) AddServer(serverID string) {
	lb.Lock()
	defer lb.Unlock()
	if lb.servers[serverID] {
		return
	}
	lb.servers[serverID] = true
	for i := 0; i < lb.replicas; i++ {
		vnodeKey := serverID + "#" + strconv.Itoa(i)
		h := hashKey(vnodeKey)
		lb.ring = append(lb.ring, h)
		lb.hashMap[h] = serverID
	}
	sort.Slice(lb.ring, func(i, j int) bool {
		return lb.ring[i] < lb.ring[j]
	})
}

func (lb *ConsistentHashLoadBalancer) RemoveServer(serverID string) {
	lb.Lock()
	defer lb.Unlock()
	if !lb.servers[serverID] {
		return
	}
	delete(lb.servers, serverID)
	newRing := make([]uint64, 0, len(lb.ring))
	for _, h := range lb.ring {
		if lb.hashMap[h] == serverID {
			delete(lb.hashMap, h)
		} else {
			newRing = append(newRing, h)
		}
	}
	lb.ring = newRing
	sort.Slice(lb.ring, func(i, j int) bool {
		return lb.ring[i] < lb.ring[j]
	})
}

func (lb *ConsistentHashLoadBalancer) GetServerForKey(key string) string {
	lb.Lock()
	defer lb.Unlock()
	if len(lb.ring) == 0 {
		return ""
	}
	h := hashKey(key)
	idx := sort.Search(len(lb.ring), func(i int) bool {
		return lb.ring[i] >= h
	})
	if idx == len(lb.ring) {
		idx = 0
	}
	server := lb.hashMap[lb.ring[idx]]
	lb.dist[server]++
	return server
}

func (lb *ConsistentHashLoadBalancer) GetKeyDistribution() map[string]int {
	lb.Lock()
	defer lb.Unlock()
	copyDist := make(map[string]int)
	for k, v := range lb.dist {
		copyDist[k] = v
	}
	return copyDist
}