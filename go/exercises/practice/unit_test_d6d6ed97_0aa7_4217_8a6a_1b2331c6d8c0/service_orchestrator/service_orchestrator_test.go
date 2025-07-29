package service_orchestrator

import (
	"errors"
	"reflect"
	"strconv"
	"sync"
	"testing"
	"time"
)

// Assume that the production code defines the following:
// var ExecuteServiceFunc func(serviceName string, input map[string]interface{}) (map[string]interface{}, error)
// func ExecuteWorkflow(workflowID string, services []string, dependencies []map[string][]string) (map[string]interface{}, error)
// The unit tests below override ExecuteServiceFunc to simulate service behavior.

// TestEmptyWorkflow verifies that an empty workflow returns an empty result without calling any services.
func TestEmptyWorkflow(t *testing.T) {
	ExecuteServiceFunc = func(name string, input map[string]interface{}) (map[string]interface{}, error) {
		return nil, errors.New("ExecuteServiceFunc should not be called for empty workflow")
	}

	services := []string{}
	dependencies := []map[string][]string{}

	result, err := ExecuteWorkflow("empty_workflow", services, dependencies)
	if err != nil {
		t.Fatalf("Expected no error for empty workflow, got: %v", err)
	}
	if len(result) != 0 {
		t.Fatalf("Expected empty result map, got: %v", result)
	}
}

// TestSuccessfulWorkflow verifies a workflow where all services execute successfully.
// It checks that dependencies are correctly passed and outputs aggregated.
func TestSuccessfulWorkflow(t *testing.T) {
	ExecuteServiceFunc = func(name string, input map[string]interface{}) (map[string]interface{}, error) {
		switch name {
		case "serviceA":
			return map[string]interface{}{"resultA": "A", "resultA2": "A2"}, nil
		case "serviceB":
			if input["resultA"] != "A" {
				return nil, errors.New("Missing dependency: resultA")
			}
			return map[string]interface{}{"resultB": "B"}, nil
		case "serviceC":
			if input["resultA2"] != "A2" || input["resultB"] != "B" {
				return nil, errors.New("Missing dependency for serviceC")
			}
			return map[string]interface{}{"resultC": "C"}, nil
		default:
			return nil, errors.New("Unknown service: " + name)
		}
	}

	services := []string{"serviceA", "serviceB", "serviceC"}
	dependencies := []map[string][]string{
		{},
		{"serviceA": {"resultA"}},
		{"serviceA": {"resultA2"}, "serviceB": {"resultB"}},
	}

	result, err := ExecuteWorkflow("workflow_success", services, dependencies)
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}
	expected := map[string]interface{}{
		"serviceA": map[string]interface{}{"resultA": "A", "resultA2": "A2"},
		"serviceB": map[string]interface{}{"resultB": "B"},
		"serviceC": map[string]interface{}{"resultC": "C"},
	}
	if !reflect.DeepEqual(result, expected) {
		t.Fatalf("Expected result %v, got %v", expected, result)
	}
}

// TestFailedServiceWorkflow verifies that if any service fails, the entire workflow returns an error.
func TestFailedServiceWorkflow(t *testing.T) {
	ExecuteServiceFunc = func(name string, input map[string]interface{}) (map[string]interface{}, error) {
		switch name {
		case "serviceA":
			return map[string]interface{}{"resultA": "A"}, nil
		case "serviceB":
			return nil, errors.New("Simulated failure in serviceB")
		default:
			return nil, errors.New("Unknown service: " + name)
		}
	}

	services := []string{"serviceA", "serviceB"}
	dependencies := []map[string][]string{
		{},
		{"serviceA": {"resultA"}},
	}

	result, err := ExecuteWorkflow("workflow_failure", services, dependencies)
	if err == nil {
		t.Fatalf("Expected error due to service failure, but received result: %v", result)
	}
}

// TestRetryServiceWorkflow simulates transient failures for a service that eventually succeeds after retries.
func TestRetryServiceWorkflow(t *testing.T) {
	var mu sync.Mutex
	attempts := make(map[string]int)

	ExecuteServiceFunc = func(name string, input map[string]interface{}) (map[string]interface{}, error) {
		mu.Lock()
		attempts[name]++
		currentAttempt := attempts[name]
		mu.Unlock()

		if name == "serviceB" {
			// Fail the first two attempts, succeed on the third attempt.
			if currentAttempt < 3 {
				return nil, errors.New("Transient error in serviceB, attempt " + strconv.Itoa(currentAttempt))
			}
			if input["resultA"] != "A" {
				return nil, errors.New("Missing dependency: resultA")
			}
			return map[string]interface{}{"resultB": "B"}, nil
		} else if name == "serviceA" {
			return map[string]interface{}{"resultA": "A"}, nil
		}
		return nil, errors.New("Unknown service: " + name)
	}

	services := []string{"serviceA", "serviceB"}
	dependencies := []map[string][]string{
		{},
		{"serviceA": {"resultA"}},
	}

	result, err := ExecuteWorkflow("workflow_retry", services, dependencies)
	if err != nil {
		t.Fatalf("Expected workflow to succeed after retries, got error: %v", err)
	}
	expected := map[string]interface{}{
		"serviceA": map[string]interface{}{"resultA": "A"},
		"serviceB": map[string]interface{}{"resultB": "B"},
	}
	if !reflect.DeepEqual(result, expected) {
		t.Fatalf("Expected result %v, got %v", expected, result)
	}
}

// TestConcurrentWorkflows verifies that multiple workflows can be executed concurrently without interference.
func TestConcurrentWorkflows(t *testing.T) {
	ExecuteServiceFunc = func(name string, input map[string]interface{}) (map[string]interface{}, error) {
		// Introduce a small delay to simulate real work.
		time.Sleep(10 * time.Millisecond)
		switch name {
		case "serviceA":
			return map[string]interface{}{"resultA": "A"}, nil
		case "serviceB":
			if input["resultA"] != "A" {
				return nil, errors.New("Missing dependency: resultA")
			}
			return map[string]interface{}{"resultB": "B"}, nil
		default:
			return nil, errors.New("Unknown service: " + name)
		}
	}

	services := []string{"serviceA", "serviceB"}
	dependencies := []map[string][]string{
		{},
		{"serviceA": {"resultA"}},
	}
	const numWorkflows = 10
	var wg sync.WaitGroup
	wg.Add(numWorkflows)
	errCh := make(chan error, numWorkflows)
	resultCh := make(chan map[string]interface{}, numWorkflows)

	for i := 0; i < numWorkflows; i++ {
		go func(id int) {
			defer wg.Done()
			workflowID := "concurrent_" + strconv.Itoa(id)
			result, err := ExecuteWorkflow(workflowID, services, dependencies)
			if err != nil {
				errCh <- err
				return
			}
			resultCh <- result
		}(i)
	}
	wg.Wait()
	close(errCh)
	close(resultCh)

	if len(errCh) > 0 {
		for err := range errCh {
			t.Errorf("Workflow error: %v", err)
		}
		t.Fatalf("Expected all concurrent workflows to succeed")
	}

	count := 0
	expected := map[string]interface{}{
		"serviceA": map[string]interface{}{"resultA": "A"},
		"serviceB": map[string]interface{}{"resultB": "B"},
	}
	for res := range resultCh {
		if !reflect.DeepEqual(res, expected) {
			t.Errorf("Expected result %v, got %v", expected, res)
		}
		count++
	}
	if count != numWorkflows {
		t.Fatalf("Expected %d workflows to complete, but got %d", numWorkflows, count)
	}
}