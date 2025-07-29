package load_balancer

import (
	"fmt"
	"io/ioutil"
	"net"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

// The tests assume the existence of the following types and functions
// in the load_balancer package:
//
// type Config struct {
//     ListenAddr          string
//     Strategy            string
//     HealthCheckInterval time.Duration
//     HealthCheckTimeout  time.Duration
//     Backends            []Backend
// }
//
// type Backend struct {
//     ID             string
//     URL            string
//     Weight         int
//     HealthEndpoint string
// }
//
// func NewLoadBalancer(config Config) *LoadBalancer
//
// type LoadBalancer struct { ... }
// Methods of LoadBalancer:
//   func (lb *LoadBalancer) Start() error
//   func (lb *LoadBalancer) Stop() error
//   func (lb *LoadBalancer) AddBackend(b Backend) error
//   func (lb *LoadBalancer) RemoveBackend(id string) error
//   func (lb *LoadBalancer) ListenAddr() string
//
// The tests below use these assumed interfaces to verify the functionality
// of the load balancer.

// dummyBackend returns a new httptest server that always replies with the given response.
func dummyBackend(response string) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, response)
	}))
}

// dummyFlakyBackend simulates a backend that always returns a failure status code when healthy is false.
func dummyFlakyBackend(healthy bool) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if healthy {
			fmt.Fprint(w, "healthy")
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprint(w, "unhealthy")
		}
	}))
}

// getAvailableLocalAddr returns an available TCP address for listening.
func getAvailableLocalAddr() string {
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}
	defer l.Close()
	return l.Addr().String()
}

func TestWeightedDistribution(t *testing.T) {
	// Create two dummy backend servers with responses "A" and "B".
	serverA := dummyBackend("A")
	defer serverA.Close()
	serverB := dummyBackend("B")
	defer serverB.Close()

	// Setup load balancer configuration with weights 2 for A and 1 for B.
	config := Config{
		ListenAddr:          getAvailableLocalAddr(),
		Strategy:            "weighted",
		HealthCheckInterval: 500 * time.Millisecond,
		HealthCheckTimeout:  200 * time.Millisecond,
		Backends: []Backend{
			{ID: "A", URL: serverA.URL, Weight: 2, HealthEndpoint: serverA.URL},
			{ID: "B", URL: serverB.URL, Weight: 1, HealthEndpoint: serverB.URL},
		},
	}

	lb := NewLoadBalancer(config)
	go lb.Start()
	// Wait for the load balancer to initialize.
	time.Sleep(300 * time.Millisecond)
	defer lb.Stop()

	client := http.Client{Timeout: 1 * time.Second}
	var countA, countB int
	totalRequests := 30

	for i := 0; i < totalRequests; i++ {
		resp, err := client.Get("http://" + lb.ListenAddr())
		if err != nil {
			t.Fatalf("Request failed: %v", err)
		}
		body, err := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			t.Fatalf("Failed reading response: %v", err)
		}

		switch string(body) {
		case "A":
			countA++
		case "B":
			countB++
		default:
			t.Fatalf("Unexpected response: %s", string(body))
		}
		time.Sleep(50 * time.Millisecond)
	}

	// Expect roughly a 2:1 ratio between "A" and "B".
	if float64(countA)/float64(countB) < 1.5 {
		t.Errorf("Weighted distribution improper: countA=%d, countB=%d", countA, countB)
	}
}

func TestDynamicServerPool(t *testing.T) {
	// Start with one backend server.
	serverA := dummyBackend("A")
	defer serverA.Close()

	config := Config{
		ListenAddr:          getAvailableLocalAddr(),
		Strategy:            "weighted",
		HealthCheckInterval: 500 * time.Millisecond,
		HealthCheckTimeout:  200 * time.Millisecond,
		Backends: []Backend{
			{ID: "A", URL: serverA.URL, Weight: 1, HealthEndpoint: serverA.URL},
		},
	}

	lb := NewLoadBalancer(config)
	go lb.Start()
	time.Sleep(300 * time.Millisecond)
	defer lb.Stop()

	client := http.Client{Timeout: 1 * time.Second}

	// Validate initial behavior with one backend.
	for i := 0; i < 5; i++ {
		resp, err := client.Get("http://" + lb.ListenAddr())
		if err != nil {
			t.Fatalf("Initial request failed: %v", err)
		}
		body, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if string(body) != "A" {
			t.Errorf("Expected response A, got %s", string(body))
		}
		time.Sleep(50 * time.Millisecond)
	}

	// Dynamically add a new backend B.
	serverB := dummyBackend("B")
	defer serverB.Close()
	err := lb.AddBackend(Backend{ID: "B", URL: serverB.URL, Weight: 1, HealthEndpoint: serverB.URL})
	if err != nil {
		t.Fatalf("Failed to add backend B: %v", err)
	}
	time.Sleep(300 * time.Millisecond)

	var countA, countB int
	for i := 0; i < 20; i++ {
		resp, err := client.Get("http://" + lb.ListenAddr())
		if err != nil {
			t.Fatalf("Request after adding backend failed: %v", err)
		}
		body, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		switch string(body) {
		case "A":
			countA++
		case "B":
			countB++
		}
		time.Sleep(50 * time.Millisecond)
	}
	if countA == 0 || countB == 0 {
		t.Errorf("Dynamic server pool did not distribute correctly: countA=%d, countB=%d", countA, countB)
	}
}

func TestHealthCheck(t *testing.T) {
	// Create one healthy and one unhealthy backend.
	healthyServer := dummyBackend("Healthy")
	defer healthyServer.Close()
	unhealthyServer := dummyFlakyBackend(false)
	defer unhealthyServer.Close()

	config := Config{
		ListenAddr:          getAvailableLocalAddr(),
		Strategy:            "weighted",
		HealthCheckInterval: 300 * time.Millisecond,
		HealthCheckTimeout:  200 * time.Millisecond,
		Backends: []Backend{
			{ID: "healthy", URL: healthyServer.URL, Weight: 1, HealthEndpoint: healthyServer.URL},
			{ID: "unhealthy", URL: unhealthyServer.URL, Weight: 1, HealthEndpoint: unhealthyServer.URL},
		},
	}

	lb := NewLoadBalancer(config)
	go lb.Start()
	time.Sleep(500 * time.Millisecond)
	defer lb.Stop()

	client := http.Client{Timeout: 1 * time.Second}
	// Verify that only the healthy backend serves requests.
	for i := 0; i < 10; i++ {
		resp, err := client.Get("http://" + lb.ListenAddr())
		if err != nil {
			t.Fatalf("Request failed: %v", err)
		}
		body, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if string(body) != "Healthy" {
			t.Errorf("Expected Healthy response, got: %s", string(body))
		}
		time.Sleep(100 * time.Millisecond)
	}
}

func TestConcurrentRequests(t *testing.T) {
	// Setup two backend servers.
	serverA := dummyBackend("A")
	defer serverA.Close()
	serverB := dummyBackend("B")
	defer serverB.Close()

	config := Config{
		ListenAddr:          getAvailableLocalAddr(),
		Strategy:            "weighted",
		HealthCheckInterval: 300 * time.Millisecond,
		HealthCheckTimeout:  200 * time.Millisecond,
		Backends: []Backend{
			{ID: "A", URL: serverA.URL, Weight: 1, HealthEndpoint: serverA.URL},
			{ID: "B", URL: serverB.URL, Weight: 1, HealthEndpoint: serverB.URL},
		},
	}

	lb := NewLoadBalancer(config)
	go lb.Start()
	time.Sleep(300 * time.Millisecond)
	defer lb.Stop()

	var wg sync.WaitGroup
	client := http.Client{Timeout: 1 * time.Second}
	requestCount := 50
	responses := make(chan string, requestCount)

	for i := 0; i < requestCount; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			resp, err := client.Get("http://" + lb.ListenAddr())
			if err != nil {
				responses <- "error"
				return
			}
			body, _ := ioutil.ReadAll(resp.Body)
			resp.Body.Close()
			responses <- string(body)
		}()
	}
	wg.Wait()
	close(responses)

	counts := make(map[string]int)
	for res := range responses {
		counts[res]++
	}
	if counts["A"] == 0 || counts["B"] == 0 {
		t.Errorf("Concurrent requests not balanced: %v", counts)
	}
}

func TestGracefulShutdown(t *testing.T) {
	// Create one backend server.
	serverA := dummyBackend("A")
	defer serverA.Close()

	config := Config{
		ListenAddr:          getAvailableLocalAddr(),
		Strategy:            "weighted",
		HealthCheckInterval: 300 * time.Millisecond,
		HealthCheckTimeout:  200 * time.Millisecond,
		Backends: []Backend{
			{ID: "A", URL: serverA.URL, Weight: 1, HealthEndpoint: serverA.URL},
		},
	}

	lb := NewLoadBalancer(config)
	go lb.Start()
	time.Sleep(300 * time.Millisecond)

	client := http.Client{Timeout: 1 * time.Second}

	// Initiate graceful shutdown.
	if err := lb.Stop(); err != nil {
		t.Fatalf("Graceful shutdown failed: %v", err)
	}

	// After shutdown, new requests should not be accepted.
	_, err := client.Get("http://" + lb.ListenAddr())
	if err == nil {
		t.Errorf("Expected error after shutdown, but request succeeded")
	}
}