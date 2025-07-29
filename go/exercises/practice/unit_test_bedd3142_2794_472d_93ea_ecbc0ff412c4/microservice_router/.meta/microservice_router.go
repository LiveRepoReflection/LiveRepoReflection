package microservice_router

import (
	"errors"
	"sync"
	"time"
)

// ServiceRegistry is the interface for service discovery.
type ServiceRegistry interface {
	GetServiceEndpoints(serviceID string) []string
}

// sendRequest is a function type for sending requests to a service endpoint.
// In production, this function should be implemented to perform actual network communication.
type sendRequestFunc func(endpoint string, payload []byte) ([]byte, error)

// Router handles routing of requests to microservice endpoints.
type Router struct {
	registry    ServiceRegistry
	timeout     time.Duration
	mu          sync.Mutex
	counters    map[string]int
	sendRequest sendRequestFunc
}

// NewRouter creates a new Router instance.
func NewRouter(reg ServiceRegistry, timeout time.Duration) *Router {
	return &Router{
		registry:    reg,
		timeout:     timeout,
		counters:    make(map[string]int),
		sendRequest: defaultSendRequest,
	}
}

// defaultSendRequest is a placeholder function that returns an error.
// It should be replaced by an actual implementation in production.
func defaultSendRequest(endpoint string, payload []byte) ([]byte, error) {
	return nil, errors.New("sendRequest not implemented")
}

// RouteRequest routes the payload to the destination service.
// It uses round-robin load balancing and retries up to 3 times on failure.
func (r *Router) RouteRequest(destinationServiceID string, requestPayload []byte) ([]byte, error) {
	const maxRetries = 3

	// Discover available endpoints.
	endpoints := r.registry.GetServiceEndpoints(destinationServiceID)
	if len(endpoints) == 0 {
		return nil, errors.New("service unavailable: no endpoints found")
	}

	var lastErr error
	var attempt int

	// Attempt up to maxRetries times.
	for attempt < maxRetries {
		// Get the next endpoint using round-robin.
		endpoint := r.getNextEndpoint(destinationServiceID, endpoints)

		// Create a channel to receive the response.
		respChan := make(chan []byte, 1)
		errChan := make(chan error, 1)

		// Execute sendRequest in a separate goroutine.
		go func(ep string) {
			resp, err := r.sendRequest(ep, requestPayload)
			if err != nil {
				errChan <- err
			} else {
				respChan <- resp
			}
		}(endpoint)

		select {
		case resp := <-respChan:
			return resp, nil
		case err := <-errChan:
			lastErr = err
		case <-time.After(r.timeout):
			lastErr = errors.New("request timeout")
		}

		attempt++
	}
	return nil, lastErr
}

// getNextEndpoint selects the next endpoint using round-robin.
func (r *Router) getNextEndpoint(serviceID string, endpoints []string) string {
	r.mu.Lock()
	defer r.mu.Unlock()
	index := r.counters[serviceID]
	endpoint := endpoints[index%len(endpoints)]
	r.counters[serviceID] = index + 1
	return endpoint
}