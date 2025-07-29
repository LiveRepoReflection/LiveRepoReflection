package adaptive_balancer

import (
	"strconv"
	"sync"
	"testing"
	"time"
)

func TestRouteRequest_NoServers(t *testing.T) {
	var lb LoadBalancer
	// Without any servers registered, RouteRequest should return an empty string.
	if res := lb.RouteRequest(); res != "" {
		t.Errorf("expected empty string when no servers registered, got: %s", res)
	}
}

func TestRouteRequest_NoMetrics(t *testing.T) {
	var lb LoadBalancer
	lb.RegisterServer("server1", 100)
	lb.RegisterServer("server2", 100)

	// With no metrics provided, assume registration order decides (server1).
	if res := lb.RouteRequest(); res != "server1" {
		t.Errorf("expected 'server1' in absence of metrics, got: %s", res)
	}
}

func TestRoutingWithMetrics(t *testing.T) {
	var lb LoadBalancer
	lb.RegisterServer("server1", 100)
	lb.RegisterServer("server2", 100)
	lb.RegisterServer("server3", 100)

	// Provide metrics: server1 load=50, latency=30; server2 load=70, latency=20; server3 load=50, latency=10.
	lb.ReceiveMetrics(map[string]int{
		"server1": 50,
		"server2": 70,
		"server3": 50,
	}, map[string]int{
		"server1": 30,
		"server2": 20,
		"server3": 10,
	})

	// Among server1 and server3 (both load 50), server3 should be preferred due to lower latency.
	if res := lb.RouteRequest(); res != "server3" {
		t.Errorf("expected 'server3' to be selected, got: %s", res)
	}

	// Overload server3 and test that server1 is then selected.
	lb.ReceiveMetrics(map[string]int{
		"server1": 50,
		"server2": 70,
		"server3": 92,
	}, map[string]int{
		"server1": 30,
		"server2": 20,
		"server3": 10,
	})
	if res := lb.RouteRequest(); res != "server1" {
		t.Errorf("expected 'server1' after overloading server3, got: %s", res)
	}
}

func TestOverloadedServers(t *testing.T) {
	var lb LoadBalancer
	lb.RegisterServer("server1", 100)
	lb.RegisterServer("server2", 100)

	// Provide metrics where both servers are overloaded.
	lb.ReceiveMetrics(map[string]int{
		"server1": 95,
		"server2": 98,
	}, map[string]int{
		"server1": 10,
		"server2": 15,
	})

	// Neither server should be available.
	if res := lb.RouteRequest(); res != "" {
		t.Errorf("expected empty string when all servers are overloaded, got: %s", res)
	}
}

func TestServerRemoval(t *testing.T) {
	var lb LoadBalancer
	lb.RegisterServer("server1", 100)
	lb.RegisterServer("server2", 100)

	lb.ReceiveMetrics(map[string]int{
		"server1": 50,
		"server2": 50,
	}, map[string]int{
		"server1": 10,
		"server2": 5,
	})

	// server2 should be selected because it has lower latency.
	if res := lb.RouteRequest(); res != "server2" {
		t.Errorf("expected 'server2' to be selected, got: %s", res)
	}

	lb.RemoveServer("server2")
	// Now only server1 remains.
	if res := lb.RouteRequest(); res != "server1" {
		t.Errorf("expected 'server1' after removing server2, got: %s", res)
	}
}

func TestConcurrentAccess(t *testing.T) {
	var lb LoadBalancer
	var wg sync.WaitGroup
	numServers := 100

	// Register servers.
	for i := 0; i < numServers; i++ {
		serverID := "server" + strconv.Itoa(i)
		lb.RegisterServer(serverID, 100)
	}

	wg.Add(3)

	// Goroutine to update metrics concurrently.
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			metrics := make(map[string]int)
			latencies := make(map[string]int)
			for j := 0; j < numServers; j++ {
				serverID := "server" + strconv.Itoa(j)
				// Even-indexed servers get lower load and latency.
				if j%2 == 0 {
					metrics[serverID] = 50
					latencies[serverID] = 20
				} else {
					metrics[serverID] = 70
					latencies[serverID] = 30
				}
			}
			lb.ReceiveMetrics(metrics, latencies)
			time.Sleep(1 * time.Millisecond)
		}
	}()

	// Goroutine to route requests concurrently.
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			_ = lb.RouteRequest()
			time.Sleep(1 * time.Millisecond)
		}
	}()

	// Goroutine to add and remove servers concurrently.
	go func() {
		defer wg.Done()
		for i := numServers; i < numServers+50; i++ {
			serverID := "server" + strconv.Itoa(i)
			lb.RegisterServer(serverID, 100)
			time.Sleep(500 * time.Microsecond)
			lb.RemoveServer(serverID)
		}
	}()

	wg.Wait()
}