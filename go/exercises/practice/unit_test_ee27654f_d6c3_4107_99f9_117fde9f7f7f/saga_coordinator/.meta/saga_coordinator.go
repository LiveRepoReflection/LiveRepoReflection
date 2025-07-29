package saga_coordinator

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

type SagaStep struct {
	Service      string
	Transaction  string
	Compensation string
}

type SagaConfig struct {
	SagaName string
	Steps    []SagaStep
	Timeout  time.Duration
}

type SagaResult struct {
	SagaName string
	Status   string            // "Success", "Compensated", "Failed"
	Details  map[string]string // key: step identifier, value: status ("Executed", "Compensated", "Failed", "Timeout", "Skipped", "HandlerNotFound")
}

// txKey is used to identify a transaction handler by service and transaction name.
type txKey struct {
	service     string
	transaction string
}

// cpKey is used to identify a compensation handler by service and compensation name.
type cpKey struct {
	service      string
	compensation string
}

var (
	handlerMu sync.RWMutex
	txHandlers = make(map[txKey]func() error)
	cpHandlers = make(map[cpKey]func() error)
)

// RegisterTransactionHandler registers a handler for the given service and transaction.
func RegisterTransactionHandler(service, transaction string, handler func() error) {
	handlerMu.Lock()
	defer handlerMu.Unlock()
	txHandlers[txKey{service, transaction}] = handler
}

// RegisterCompensationHandler registers a handler for the given service and compensation.
func RegisterCompensationHandler(service, compensation string, handler func() error) {
	handlerMu.Lock()
	defer handlerMu.Unlock()
	cpHandlers[cpKey{service, compensation}] = handler
}

// ResetHandlers clears all registered transaction and compensation handlers.
func ResetHandlers() {
	handlerMu.Lock()
	defer handlerMu.Unlock()
	txHandlers = make(map[txKey]func() error)
	cpHandlers = make(map[cpKey]func() error)
}

// ExecuteSaga executes the given saga as defined in the configuration.
// If any transaction step fails or times out, compensation is performed in reverse order on the executed steps.
// Returns a SagaResult and an error if the saga did not complete successfully.
func ExecuteSaga(config *SagaConfig) (*SagaResult, error) {
	result := &SagaResult{
		SagaName: config.SagaName,
		Details:  make(map[string]string),
	}
	var executedSteps []SagaStep

	for _, step := range config.Steps {
		// Skip steps with empty transaction names.
		if step.Transaction == "" {
			key := fmt.Sprintf("%s:%s", step.Service, "empty_transaction")
			result.Details[key] = "Skipped"
			continue
		}

		handlerMu.RLock()
		txHandler, ok := txHandlers[txKey{step.Service, step.Transaction}]
		handlerMu.RUnlock()
		if !ok {
			key := fmt.Sprintf("%s:%s", step.Service, step.Transaction)
			result.Details[key] = "HandlerNotFound"
			result.Status = "Failed"
			return result, errors.New("transaction handler not found for " + step.Service + ":" + step.Transaction)
		}

		txErrChan := make(chan error, 1)
		go func(handler func() error) {
			err := handler()
			txErrChan <- err
		}(txHandler)

		select {
		case err := <-txErrChan:
			if err != nil {
				key := fmt.Sprintf("%s:%s", step.Service, step.Transaction)
				result.Details[key] = "Failed"
				// Initiate compensation for all previously successful steps.
				compensate(executedSteps, result)
				result.Status = "Compensated"
				return result, err
			}
			key := fmt.Sprintf("%s:%s", step.Service, step.Transaction)
			result.Details[key] = "Executed"
			executedSteps = append(executedSteps, step)
		case <-time.After(config.Timeout):
			key := fmt.Sprintf("%s:%s", step.Service, step.Transaction)
			result.Details[key] = "Timeout"
			// Timeout triggers compensation for the already executed steps.
			compensate(executedSteps, result)
			result.Status = "Compensated"
			return result, errors.New("transaction timeout for " + step.Service + ":" + step.Transaction)
		}
	}
	result.Status = "Success"
	return result, nil
}

// compensate performs compensation for each executed step in reverse order.
func compensate(steps []SagaStep, result *SagaResult) {
	for i := len(steps) - 1; i >= 0; i-- {
		step := steps[i]
		if step.Compensation == "" {
			key := fmt.Sprintf("%s:%s", step.Service, "empty_compensation")
			result.Details[key] = "Skipped"
			continue
		}
		handlerMu.RLock()
		cpHandler, ok := cpHandlers[cpKey{step.Service, step.Compensation}]
		handlerMu.RUnlock()
		key := fmt.Sprintf("%s:%s", step.Service, step.Compensation)
		if !ok {
			result.Details[key] = "HandlerNotFound"
			continue
		}
		err := cpHandler()
		if err != nil {
			result.Details[key] = "Failed"
		} else {
			result.Details[key] = "Compensated"
		}
	}
}