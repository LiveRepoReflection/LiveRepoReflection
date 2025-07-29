package loadbalance

import (
	"fmt"
	"sync"
	"testing"
)

func TestLoadBalancerBasicOperations(t *testing.T) {
	lb := NewLoadBalancer()

	// Test adding servers
	lb.AddServer(1, 100)
	lb.AddServer(2, 200)
	lb.AddServer(3, 300)

	// Test basic request distribution
	requests := make(map[int]int)
	for i := 0; i < 600; i++ {
		server := lb.Request()
		requests[server]++
	}

	// Verify distribution roughly matches capacity ratios
	if requests[1] < 80 || requests[1] > 120 {
		t.Errorf("Server 1 got %d requests, expected around 100", requests[1])
	}
	if requests[2] < 160 || requests[2] > 240 {
		t.Errorf("Server 2 got %d requests, expected around 200", requests[2])
	}
	if requests[3] < 240 || requests[3] > 360 {
		t.Errorf("Server 3 got %d requests, expected around 300", requests[3])
	}
}

func TestLoadBalancerServerRemoval(t *testing.T) {
	lb := NewLoadBalancer()

	lb.AddServer(1, 100)
	lb.AddServer(2, 200)

	// Remove server and verify requests are redistributed
	lb.RemoveServer(2)

	for i := 0; i < 10; i++ {
		server := lb.Request()
		if server != 1 {
			t.Errorf("Request returned server %d, expected 1", server)
		}
	}
}

func TestLoadBalancerCapacityUpdate(t *testing.T) {
	lb := NewLoadBalancer()

	lb.AddServer(1, 100)
	lb.AddServer(2, 100)

	// Update capacity and verify distribution changes
	lb.UpdateCapacity(1, 300)

	requests := make(map[int]int)
	for i := 0; i < 400; i++ {
		server := lb.Request()
		requests[server]++
	}

	ratio := float64(requests[1]) / float64(requests[2])
	if ratio < 2.5 || ratio > 3.5 {
		t.Errorf("Distribution ratio %f not close to expected 3.0", ratio)
	}
}

func TestLoadBalancerAvailability(t *testing.T) {
	lb := NewLoadBalancer()

	lb.AddServer(1, 100)
	lb.AddServer(2, 100)

	// Mark server unavailable and verify requests go to available server
	lb.MarkServerUnavailable(2)

	for i := 0; i < 10; i++ {
		server := lb.Request()
		if server != 1 {
			t.Errorf("Request returned server %d, expected 1", server)
		}
	}

	// Mark server available again and verify distribution resumes
	lb.MarkServerAvailable(2)

	seen2 := false
	for i := 0; i < 20; i++ {
		if lb.Request() == 2 {
			seen2 = true
			break
		}
	}

	if !seen2 {
		t.Error("Server 2 never received requests after becoming available")
	}
}

func TestLoadBalancerConcurrency(t *testing.T) {
	lb := NewLoadBalancer()
	lb.AddServer(1, 100)
	lb.AddServer(2, 100)
	lb.AddServer(3, 100)

	var wg sync.WaitGroup
	requestCount := 1000
	workerCount := 10

	results := make(chan int, requestCount*workerCount)

	// Launch multiple goroutines to simulate concurrent requests
	for i := 0; i < workerCount; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < requestCount; j++ {
				server := lb.Request()
				results <- server
			}
		}()
	}

	// Launch goroutines to simulate concurrent server updates
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			lb.UpdateCapacity(1, 100+i)
			lb.UpdateCapacity(2, 200+i)
			lb.UpdateCapacity(3, 300+i)
		}
	}()

	wg.Wait()
	close(results)

	// Verify all requests were handled
	totalRequests := 0
	for range results {
		totalRequests++
	}

	if totalRequests != requestCount*workerCount {
		t.Errorf("Expected %d total requests, got %d", requestCount*workerCount, totalRequests)
	}
}

func TestLoadBalancerEdgeCases(t *testing.T) {
	lb := NewLoadBalancer()

	// Test empty load balancer
	func() {
		defer func() {
			if r := recover(); r == nil {
				t.Error("Expected panic with no servers, but it didn't")
			}
		}()
		lb.Request()
	}()

	// Test adding server with invalid capacity
	func() {
		defer func() {
			if r := recover(); r == nil {
				t.Error("Expected panic with invalid capacity, but it didn't")
			}
		}()
		lb.AddServer(1, 0)
	}()

	// Test removing non-existent server
	lb.RemoveServer(999) // Should not panic

	// Test updating non-existent server
	lb.UpdateCapacity(999, 100) // Should not panic

	// Test marking non-existent server availability
	lb.MarkServerAvailable(999)   // Should not panic
	lb.MarkServerUnavailable(999) // Should not panic
}

func TestLoadBalancerStress(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping stress test in short mode")
	}

	lb := NewLoadBalancer()
	serverCount := 100
	requestCount := 10000

	// Add many servers
	for i := 1; i <= serverCount; i++ {
		lb.AddServer(i, i*100)
	}

	// Make many requests
	results := make(map[int]int)
	var mu sync.Mutex

	var wg sync.WaitGroup
	for i := 0; i < requestCount; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			server := lb.Request()
			mu.Lock()
			results[server]++
			mu.Unlock()
		}()
	}

	wg.Wait()

	// Verify all servers received some requests
	for i := 1; i <= serverCount; i++ {
		if results[i] == 0 {
			t.Errorf("Server %d received no requests", i)
		}
	}
}

func BenchmarkLoadBalancerRequest(b *testing.B) {
	lb := NewLoadBalancer()
	lb.AddServer(1, 100)
	lb.AddServer(2, 200)
	lb.AddServer(3, 300)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		lb.Request()
	}
}

func BenchmarkLoadBalancerConcurrentRequests(b *testing.B) {
	lb := NewLoadBalancer()
	lb.AddServer(1, 100)
	lb.AddServer(2, 200)
	lb.AddServer(3, 300)

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			lb.Request()
		}
	})
}

func ExampleLoadBalancer() {
	lb := NewLoadBalancer()
	lb.AddServer(1, 100)
	lb.AddServer(2, 200)
	lb.AddServer(3, 300)

	// Make some requests
	for i := 0; i < 5; i++ {
		server := lb.Request()
		fmt.Printf("Request assigned to server: %d\n", server)
	}
}
