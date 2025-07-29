package adaptive_lb

import (
	"sync"
	"time"
)

type Request struct {
	ID string
}

type Response struct {
	ServerID       string
	ProcessingTime time.Duration
}

type Server struct {
	id        string
	capacity  int
	latency   map[string]time.Duration
	load      float64
	healthy   bool
	mu        sync.Mutex
	activeConns int
}

type LoadBalancer struct {
	servers map[string]*Server
	mu      sync.RWMutex
}

func NewLoadBalancer() *LoadBalancer {
	return &LoadBalancer{
		servers: make(map[string]*Server),
	}
}

func (lb *LoadBalancer) RegisterServer(serverID string, capacity int, latency map[string]time.Duration) {
	lb.mu.Lock()
	defer lb.mu.Unlock()

	lb.servers[serverID] = &Server{
		id:       serverID,
		capacity: capacity,
		latency:  latency,
		healthy:  true,
	}
}

func (lb *LoadBalancer) UpdateServerLoad(serverID string, load float64) {
	lb.mu.RLock()
	server, exists := lb.servers[serverID]
	lb.mu.RUnlock()

	if !exists {
		return
	}

	server.mu.Lock()
	defer server.mu.Unlock()
	server.load = load
}

func (lb *LoadBalancer) HandleRequest(request Request, clientRegion string) Response {
	lb.mu.RLock()
	defer lb.mu.RUnlock()

	var bestServer *Server
	var bestScore float64 = -1

	for _, server := range lb.servers {
		if !server.healthy {
			continue
		}

		server.mu.Lock()
		latency := server.latency[clientRegion]
		score := lb.calculateScore(server.load, latency, server.activeConns, server.capacity)
		server.mu.Unlock()

		if score > bestScore {
			bestScore = score
			bestServer = server
		}
	}

	if bestServer == nil {
		return Response{ServerID: "", ProcessingTime: 0}
	}

	bestServer.mu.Lock()
	bestServer.activeConns++
	bestServer.mu.Unlock()

	defer func() {
		bestServer.mu.Lock()
		bestServer.activeConns--
		bestServer.mu.Unlock()
	}()

	return bestServer.ServeRequest(request)
}

func (lb *LoadBalancer) calculateScore(load float64, latency time.Duration, activeConns, capacity int) float64 {
	if capacity == 0 {
		return 0
	}

	// Weighted score considering load (30%), latency (50%), and connection utilization (20%)
	loadFactor := 1.0 - load
	latencyFactor := 1.0 / float64(latency.Milliseconds())
	connUtilization := 1.0 - float64(activeConns)/float64(capacity)

	return 0.3*loadFactor + 0.5*latencyFactor + 0.2*connUtilization
}

func (s *Server) ServeRequest(request Request) Response {
	// Simulate processing time based on current load
	processingTime := time.Duration(float64(10) * (1.0 + s.load)) * time.Millisecond
	time.Sleep(processingTime)
	return Response{
		ServerID:       s.id,
		ProcessingTime: processingTime,
	}
}