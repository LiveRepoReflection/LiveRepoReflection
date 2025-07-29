package saga_tx

import (
	"fmt"
	"time"
)

type TransactionStep struct {
	ServiceID    string
	Operation    string
	Data         string
	Compensation func(data string) error
}

var CallService = func(serviceID string, operation string, data string) error {
	// Default implementation: in production this calls the actual microservice.
	return nil
}

func OrchestrateTransaction(steps []TransactionStep) error {
	const maxAttempts = 3
	const baseDelay = 50 * time.Millisecond

	executedSteps := make([]TransactionStep, 0, len(steps))

	for idx, step := range steps {
		var err error
		// Execute the service call with retry mechanism.
		for attempt := 1; attempt <= maxAttempts; attempt++ {
			err = CallService(step.ServiceID, step.Operation, step.Data)
			if err == nil {
				break
			}
			delay := baseDelay * time.Duration(1<<(attempt-1))
			time.Sleep(delay)
		}
		if err != nil {
			// Failure detected, trigger asynchronous compensations in reverse order.
			for i := len(executedSteps) - 1; i >= 0; i-- {
				go func(compStep TransactionStep) {
					for compAttempt := 1; compAttempt <= maxAttempts; compAttempt++ {
						compErr := compStep.Compensation(compStep.Data)
						if compErr == nil {
							break
						}
						delay := baseDelay * time.Duration(1<<(compAttempt-1))
						time.Sleep(delay)
					}
				}(executedSteps[i])
			}
			return fmt.Errorf("transaction failed at step %d: %w", idx, err)
		}
		executedSteps = append(executedSteps, step)
	}
	return nil
}