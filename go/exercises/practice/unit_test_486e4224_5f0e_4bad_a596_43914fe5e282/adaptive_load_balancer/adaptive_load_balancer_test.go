package adaptive_load_balancer

import (
	"strconv"
	"sync"
	"testing"
	"time"
)

func TestAddServerAndDistribution(t *testing.T) {
	// Create a new load balancer instance.
	lb := NewLoadBalancer()

	// Add servers with different capacities.
	lb.AddServer(0, 100)
	lb.AddServer(1, 200)
	lb.AddServer(2, 150)

	// Retrieve the distribution.
	dist := lb.GetDistribution()

	// Check that all servers exist in the distribution.
	if len(dist) != 3 {
		t.Fatalf("Expected distribution for 3 servers, got %d", len(dist))
	}
	// Each server should have at least one virtual node.
	for id, vnodes := range dist {
		if len(vnodes) < 1 {
			t.Fatalf("Server %d should have at least one virtual node", id)
		}
	}
}

func TestGetServerMapping(t *testing.T) {
	lb := NewLoadBalancer()

	// Add two servers.
	lb.AddServer(0, 100)
	lb.AddServer(1, 200)

	// Get server for a given request.
	reqIDs := []string{"req1", "req2", "req3", "req4", "req5"}
	for _, req := range reqIDs {
		serverID := lb.GetServer(req)
		if serverID != 0 && serverID != 1 {
			t.Fatalf("GetServer returned invalid server id %d for request %s", serverID, req)
		}
	}
}

func TestUpdateCapacity(t *testing.T) {
	lb := NewLoadBalancer()

	// Add servers.
	lb.AddServer(0, 100)
	lb.AddServer(1, 200)

	// Get initial distribution counts.
	initialDist := lb.GetDistribution()
	count0Initial := len(initialDist[0])
	count1Initial := len(initialDist[1])

	// Update capacity of server 0 to a higher value.
	lb.UpdateCapacity(0, 300)

	// Wait a small time if the update is asynchronous.
	time.Sleep(50 * time.Millisecond)

	updatedDist := lb.GetDistribution()
	count0Updated := len(updatedDist[0])
	count1Updated := len(updatedDist[1])

	// Check that server 0 now has more virtual nodes than before.
	if count0Updated <= count0Initial {
		t.Fatalf("Expected increased virtual nodes for server 0 after capacity update, was %d, now %d", count0Initial, count0Updated)
	}

	// Ensure that server 1's count remains unchanged.
	if count1Updated != count1Initial {
		t.Fatalf("Server 1's virtual node count changed unexpectedly from %d to %d", count1Initial, count1Updated)
	}
}

func TestRemoveServer(t *testing.T) {
	lb := NewLoadBalancer()

	// Add three servers.
	lb.AddServer(0, 100)
	lb.AddServer(1, 200)
	lb.AddServer(2, 150)

	// Remove one server.
	lb.RemoveServer(1)

	// Get distribution.
	dist := lb.GetDistribution()
	if _, exists := dist[1]; exists {
		t.Fatalf("Server 1 should have been removed from distribution")
	}
	// Ensure the remaining servers are still present.
	if len(dist) != 2 {
		t.Fatalf("Expected 2 servers in distribution after removal, got %d", len(dist))
	}

	// Test that GetServer never returns server 1.
	for i := 0; i < 100; i++ {
		reqID := "test_req_" + strconv.Itoa(i)
		sID := lb.GetServer(reqID)
		if sID == 1 {
			t.Fatalf("GetServer returned removed server id 1 for request %s", reqID)
		}
	}
}

func TestConcurrentAccess(t *testing.T) {
	lb := NewLoadBalancer()

	// Add initial servers.
	for i := 0; i < 5; i++ {
		lb.AddServer(i, 100+(i*50))
	}

	var wg sync.WaitGroup

	// Run concurrent GetServer calls.
	numConcurrent := 50
	numReqPerGoRoutine := 100

	wg.Add(numConcurrent)
	for i := 0; i < numConcurrent; i++ {
		go func(index int) {
			defer wg.Done()
			for j := 0; j < numReqPerGoRoutine; j++ {
				reqID := "request_" + strconv.Itoa(index) + "_" + strconv.Itoa(j)
				_ = lb.GetServer(reqID)
			}
		}(i)
	}

	// Run concurrent capacity updates and removals.
	wg.Add(2)
	go func() {
		defer wg.Done()
		// Update capacities concurrently.
		for i := 0; i < 50; i++ {
			for serverID := 0; serverID < 5; serverID++ {
				newCap := 100 + (i % 10 * 20)
				lb.UpdateCapacity(serverID, newCap)
			}
			time.Sleep(5 * time.Millisecond)
		}
	}()
	go func() {
		defer wg.Done()
		// Add and remove a server concurrently.
		for i := 100; i < 110; i++ {
			lb.AddServer(i, 150)
			time.Sleep(2 * time.Millisecond)
		}
		for i := 100; i < 110; i++ {
			lb.RemoveServer(i)
			time.Sleep(2 * time.Millisecond)
		}
	}()

	wg.Wait()

	// After all operations, call GetDistribution and GetServer to check consistency.
	dist := lb.GetDistribution()
	if len(dist) < 5 {
		t.Fatalf("Expected at least 5 servers in distribution, got %d", len(dist))
	}
	for i := 0; i < 100; i++ {
		reqID := "final_req_" + strconv.Itoa(i)
		sID := lb.GetServer(reqID)
		if _, exists := dist[sID]; !exists {
			t.Fatalf("GetServer returned server id %d not present in distribution", sID)
		}
	}
}