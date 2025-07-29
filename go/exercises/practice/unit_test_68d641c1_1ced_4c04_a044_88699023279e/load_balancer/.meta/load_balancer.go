package load_balancer

import (
	"errors"
	"io"
	"net"
	"net/http"
	"sync"
	"time"
)

// Config defines the configuration for the load balancer.
type Config struct {
	ListenAddr          string
	Strategy            string // "weighted" or "consistent"
	HealthCheckInterval time.Duration
	HealthCheckTimeout  time.Duration
	Backends            []Backend
}

// Backend represents a backend server.
type Backend struct {
	ID             string
	URL            string
	Weight         int
	HealthEndpoint string
}

// LoadBalancer represents the load balancer.
type LoadBalancer struct {
	config       Config
	server       *http.Server
	backends     map[string]*backendStatus
	mu           sync.RWMutex
	healthTicker *time.Ticker
	shutdownCh   chan struct{}
	wg           sync.WaitGroup
}

// backendStatus wraps a Backend and tracks its state for load balancing.
type backendStatus struct {
	backend         Backend
	healthy         bool
	currentWeight   int
	effectiveWeight int
}

// NewLoadBalancer creates a new LoadBalancer instance with the given configuration.
func NewLoadBalancer(config Config) *LoadBalancer {
	lb := &LoadBalancer{
		config:     config,
		backends:   make(map[string]*backendStatus),
		shutdownCh: make(chan struct{}),
	}
	// Initialize backends from config.
	for _, b := range config.Backends {
		lb.backends[b.ID] = &backendStatus{
			backend:         b,
			healthy:         true, // assume healthy initially
			effectiveWeight: b.Weight,
			currentWeight:   0,
		}
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/", lb.handleRequest)
	lb.server = &http.Server{
		Addr:    config.ListenAddr,
		Handler: mux,
	}
	return lb
}

// Start initializes the health checking loop and starts the HTTP server.
func (lb *LoadBalancer) Start() error {
	// Start health checker.
	lb.healthTicker = time.NewTicker(lb.config.HealthCheckInterval)
	lb.wg.Add(1)
	go lb.healthCheckLoop()

	// Start the HTTP server.
	ln, err := net.Listen("tcp", lb.config.ListenAddr)
	if err != nil {
		return err
	}
	go func() {
		lb.server.Serve(ln)
	}()
	return nil
}

// Stop gracefully stops the load balancer.
func (lb *LoadBalancer) Stop() error {
	// Signal shutdown to health checker.
	close(lb.shutdownCh)
	if lb.healthTicker != nil {
		lb.healthTicker.Stop()
	}
	lb.wg.Wait()
	// Close the HTTP server.
	err := lb.server.Close()
	return err
}

// AddBackend adds a new backend server to the pool.
func (lb *LoadBalancer) AddBackend(b Backend) error {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	if _, exists := lb.backends[b.ID]; exists {
		return errors.New("backend already exists")
	}
	lb.backends[b.ID] = &backendStatus{
		backend:         b,
		healthy:         true,
		effectiveWeight: b.Weight,
		currentWeight:   0,
	}
	return nil
}

// RemoveBackend removes a backend server from the pool.
func (lb *LoadBalancer) RemoveBackend(id string) error {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	if _, exists := lb.backends[id]; !exists {
		return errors.New("backend not found")
	}
	delete(lb.backends, id)
	return nil
}

// ListenAddr returns the address where the load balancer is listening.
func (lb *LoadBalancer) ListenAddr() string {
	return lb.server.Addr
}

// healthCheckLoop periodically checks the health of each backend.
func (lb *LoadBalancer) healthCheckLoop() {
	defer lb.wg.Done()
	client := &http.Client{
		Timeout: lb.config.HealthCheckTimeout,
	}
	for {
		select {
		case <-lb.shutdownCh:
			return
		case <-lb.healthTicker.C:
			lb.mu.Lock()
			for _, b := range lb.backends {
				resp, err := client.Get(b.backend.HealthEndpoint)
				if err != nil || resp.StatusCode != http.StatusOK {
					b.healthy = false
				} else {
					b.healthy = true
				}
				if resp != nil {
					io.Copy(io.Discard, resp.Body)
					resp.Body.Close()
				}
			}
			lb.mu.Unlock()
		}
	}
}

// chooseBackend selects a backend using the smooth weighted round robin algorithm.
func (lb *LoadBalancer) chooseBackend() (*backendStatus, error) {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	totalWeight := 0
	var best *backendStatus
	for _, b := range lb.backends {
		if !b.healthy {
			continue
		}
		b.currentWeight += b.effectiveWeight
		totalWeight += b.effectiveWeight
		if best == nil || b.currentWeight > best.currentWeight {
			best = b
		}
	}
	if best == nil {
		return nil, errors.New("no healthy backends available")
	}
	best.currentWeight -= totalWeight
	return best, nil
}

// handleRequest forwards incoming requests to the selected backend.
func (lb *LoadBalancer) handleRequest(w http.ResponseWriter, r *http.Request) {
	b, err := lb.chooseBackend()
	if err != nil {
		http.Error(w, "No healthy backends available", http.StatusServiceUnavailable)
		return
	}
	resp, err := http.Get(b.backend.URL)
	if err != nil {
		http.Error(w, "Error contacting backend", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()
	// Copy response headers.
	for key, values := range resp.Header {
		for _, value := range values {
			w.Header().Add(key, value)
		}
	}
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}