package adaptive_lb

import (
	"testing"
	"time"
)

type mockServer struct {
	id       string
	capacity int
	latency  map[string]time.Duration
	load     float64
	healthy  bool
}

func (m *mockServer) ServeRequest(request Request) Response {
	return Response{ServerID: m.id, ProcessingTime: 10 * time.Millisecond}
}

func TestRegisterServer(t *testing.T) {
	lb := NewLoadBalancer()
	serverID := "server1"
	capacity := 100
	latency := map[string]time.Duration{"us-east": 50 * time.Millisecond}

	lb.RegisterServer(serverID, capacity, latency)

	if len(lb.servers) != 1 {
		t.Errorf("Expected 1 server, got %d", len(lb.servers))
	}

	if lb.servers[serverID] == nil {
		t.Errorf("Server %s not registered", serverID)
	}
}

func TestUpdateServerLoad(t *testing.T) {
	lb := NewLoadBalancer()
	serverID := "server1"
	lb.RegisterServer(serverID, 100, map[string]time.Duration{"us-east": 50 * time.Millisecond})

	lb.UpdateServerLoad(serverID, 0.75)

	if lb.servers[serverID].load != 0.75 {
		t.Errorf("Expected load 0.75, got %f", lb.servers[serverID].load)
	}
}

func TestHandleRequest(t *testing.T) {
	lb := NewLoadBalancer()
	lb.RegisterServer("server1", 100, map[string]time.Duration{"us-east": 50 * time.Millisecond})
	lb.RegisterServer("server2", 100, map[string]time.Duration{"us-east": 30 * time.Millisecond})
	lb.UpdateServerLoad("server1", 0.2)
	lb.UpdateServerLoad("server2", 0.8)

	request := Request{ID: "req1"}
	response := lb.HandleRequest(request, "us-east")

	if response.ServerID != "server1" {
		t.Errorf("Expected request to be routed to server1, got %s", response.ServerID)
	}
}

func TestUnhealthyServer(t *testing.T) {
	lb := NewLoadBalancer()
	lb.RegisterServer("server1", 100, map[string]time.Duration{"us-east": 50 * time.Millisecond})
	lb.RegisterServer("server2", 100, map[string]time.Duration{"us-east": 30 * time.Millisecond})
	lb.servers["server1"].healthy = false

	request := Request{ID: "req1"}
	response := lb.HandleRequest(request, "us-east")

	if response.ServerID != "server2" {
		t.Errorf("Expected request to be routed to server2, got %s", response.ServerID)
	}
}

func TestConcurrentRequests(t *testing.T) {
	lb := NewLoadBalancer()
	lb.RegisterServer("server1", 100, map[string]time.Duration{"us-east": 50 * time.Millisecond})
	lb.RegisterServer("server2", 100, map[string]time.Duration{"us-east": 30 * time.Millisecond})

	requests := 100
	results := make(chan Response, requests)

	for i := 0; i < requests; i++ {
		go func(i int) {
			request := Request{ID: string(rune(i))}
			results <- lb.HandleRequest(request, "us-east")
		}(i)
	}

	serverCounts := make(map[string]int)
	for i := 0; i < requests; i++ {
		res := <-results
		serverCounts[res.ServerID]++
	}

	if serverCounts["server1"] == 0 || serverCounts["server2"] == 0 {
		t.Errorf("Requests not distributed between servers: %v", serverCounts)
	}
}