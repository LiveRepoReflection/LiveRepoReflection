package loadbalance

import (
	"container/heap"
	"sync"
)

// LoadBalancer represents the main load balancer structure
type LoadBalancer struct {
	mu            sync.RWMutex
	servers       map[int]*Server
	activeServers *ServerHeap
	totalCapacity int
	roundRobin    int
}

// Server represents a single server in the load balancer
type Server struct {
	id          int
	capacity    int
	available   bool
	loadCount   int
	lastUpdated int
}

// ServerHeap is a min-heap of servers ordered by their current load relative to capacity
type ServerHeap []*Server

// NewLoadBalancer creates a new load balancer instance
func NewLoadBalancer() *LoadBalancer {
	return &LoadBalancer{
		servers:       make(map[int]*Server),
		activeServers: &ServerHeap{},
		totalCapacity: 0,
		roundRobin:    0,
	}
}

// Heap interface implementation
func (h ServerHeap) Len() int           { return len(h) }
func (h ServerHeap) Less(i, j int) bool { return float64(h[i].loadCount)/float64(h[i].capacity) < float64(h[j].loadCount)/float64(h[j].capacity) }
func (h ServerHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *ServerHeap) Push(x interface{}) {
	*h = append(*h, x.(*Server))
}

func (h *ServerHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// AddServer adds a new server to the load balancer
func (lb *LoadBalancer) AddServer(serverID int, capacity int) {
	if capacity <= 0 {
		panic("Server capacity must be positive")
	}

	lb.mu.Lock()
	defer lb.mu.Unlock()

	if _, exists := lb.servers[serverID]; exists {
		return
	}

	server := &Server{
		id:        serverID,
		capacity:  capacity,
		available: true,
		loadCount: 0,
	}

	lb.servers[serverID] = server
	heap.Push(lb.activeServers, server)
	lb.totalCapacity += capacity
}

// RemoveServer removes a server from the load balancer
func (lb *LoadBalancer) RemoveServer(serverID int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if server, exists := lb.servers[serverID]; exists {
		// Remove from active servers if it's there
		for i := 0; i < lb.activeServers.Len(); i++ {
			if (*lb.activeServers)[i].id == serverID {
				heap.Remove(lb.activeServers, i)
				break
			}
		}
		lb.totalCapacity -= server.capacity
		delete(lb.servers, serverID)
	}
}

// UpdateCapacity updates the capacity of a server
func (lb *LoadBalancer) UpdateCapacity(serverID int, newCapacity int) {
	if newCapacity <= 0 {
		return
	}

	lb.mu.Lock()
	defer lb.mu.Unlock()

	if server, exists := lb.servers[serverID]; exists {
		lb.totalCapacity = lb.totalCapacity - server.capacity + newCapacity
		server.capacity = newCapacity
		// Reheapify if server is active
		if server.available {
			heap.Init(lb.activeServers)
		}
	}
}

// MarkServerAvailable marks a server as available
func (lb *LoadBalancer) MarkServerAvailable(serverID int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if server, exists := lb.servers[serverID]; exists && !server.available {
		server.available = true
		heap.Push(lb.activeServers, server)
	}
}

// MarkServerUnavailable marks a server as unavailable
func (lb *LoadBalancer) MarkServerUnavailable(serverID int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if server, exists := lb.servers[serverID]; exists && server.available {
		server.available = false
		// Remove from active servers
		for i := 0; i < lb.activeServers.Len(); i++ {
			if (*lb.activeServers)[i].id == serverID {
				heap.Remove(lb.activeServers, i)
				break
			}
		}
	}
}

// Request handles an incoming request and returns the selected server ID
func (lb *LoadBalancer) Request() int {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	if lb.activeServers.Len() == 0 {
		panic("No available servers")
	}

	// Get the least loaded server
	server := (*lb.activeServers)[0]
	
	// Update server load
	server.loadCount++
	heap.Fix(lb.activeServers, 0)

	return server.id
}

// Helper function to get the current load distribution (for testing)
func (lb *LoadBalancer) getLoadDistribution() map[int]float64 {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	distribution := make(map[int]float64)
	for id, server := range lb.servers {
		if server.available {
			distribution[id] = float64(server.loadCount) / float64(server.capacity)
		}
	}
	return distribution
}