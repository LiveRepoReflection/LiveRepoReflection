package service_orchestrator

import (
	"context"
	"errors"
	"sync"
	"time"
)

var ExecuteServiceFunc func(serviceName string, input map[string]interface{}) (map[string]interface{}, error)

const maxRetries = 3
const retryDelay = 10 * time.Millisecond

// ExecuteWorkflow executes a workflow defined by an ordered list of services and their dependencies.
// It returns a map where each key is a service name and the value is the output returned by that service.
// If any service fails (after the allowed number of retries) or if any dependency is unsatisfied,
// the entire workflow is considered failed and an error is returned.
func ExecuteWorkflow(workflowID string, services []string, dependencies []map[string][]string) (map[string]interface{}, error) {
	if len(services) != len(dependencies) {
		return nil, errors.New("services and dependencies length mismatch")
	}

	// Return an empty map if there are no services.
	if len(services) == 0 {
		return map[string]interface{}{}, nil
	}

	// Create a context to support cancellation in case of any error.
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create a mapping from service names to their index for dependency look-up.
	serviceIndex := make(map[string]int)
	for i, s := range services {
		serviceIndex[s] = i
	}

	// Create a slice of channels to signal completion of each service.
	doneCh := make([]chan struct{}, len(services))
	for i := range doneCh {
		doneCh[i] = make(chan struct{})
	}

	// Use a mutex to protect concurrent writes to the results map.
	var mu sync.Mutex
	results := make(map[string]interface{})

	var wg sync.WaitGroup
	var execErr error
	var errOnce sync.Once

	// setError records an error only once and cancels the context.
	setError := func(err error) {
		errOnce.Do(func() {
			execErr = err
			cancel()
		})
	}

	// Launch a goroutine for each service in the workflow.
	for i, serviceName := range services {
		wg.Add(1)
		// Capture variables for proper closure use.
		i := i
		serviceName := serviceName

		go func() {
			defer wg.Done()

			// Wait for all dependencies of this service to complete.
			for depService, keys := range dependencies[i] {
				// Validate the dependency exists and is scheduled before the current service.
				depIndex, ok := serviceIndex[depService]
				if !ok || depIndex >= i {
					setError(errors.New("invalid dependency: " + depService))
					return
				}
				// Wait for the dependency service to signal completion.
				select {
				case <-doneCh[depIndex]:
				case <-ctx.Done():
					return
				}
				// Check that the dependency output contains all required keys.
				mu.Lock()
				depOutputRaw, found := results[depService]
				mu.Unlock()
				if !found {
					setError(errors.New("missing output from dependency: " + depService))
					return
				}
				depOutput, ok := depOutputRaw.(map[string]interface{})
				if !ok {
					setError(errors.New("invalid output format from dependency: " + depService))
					return
				}
				for _, key := range keys {
					if _, exists := depOutput[key]; !exists {
						setError(errors.New("dependency " + depService + " missing key: " + key))
						return
					}
				}
			}

			// Construct the input map for the current service from its dependencies.
			input := make(map[string]interface{})
			for depService, keys := range dependencies[i] {
				mu.Lock()
				depOutputRaw := results[depService]
				mu.Unlock()
				depOutput := depOutputRaw.(map[string]interface{})
				for _, key := range keys {
					input[key] = depOutput[key]
				}
			}

			// Attempt to execute the service with retry logic.
			var output map[string]interface{}
			var err error
			for attempt := 1; attempt <= maxRetries; attempt++ {
				select {
				case <-ctx.Done():
					return
				default:
				}
				output, err = ExecuteServiceFunc(serviceName, input)
				if err == nil {
					break
				}
				time.Sleep(retryDelay)
			}
			if err != nil {
				setError(errors.New("service " + serviceName + " failed after retries: " + err.Error()))
				return
			}

			// Save the successful output.
			mu.Lock()
			results[serviceName] = output
			mu.Unlock()

			// Signal that this service has finished execution.
			close(doneCh[i])
		}()
	}

	// Wait for all services to complete.
	wg.Wait()

	if execErr != nil {
		return nil, execErr
	}
	return results, nil
}