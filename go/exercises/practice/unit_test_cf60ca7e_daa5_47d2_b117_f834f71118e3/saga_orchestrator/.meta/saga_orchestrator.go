package saga_orchestrator

import (
	"errors"
	"sync"
	"time"
)

type SagaStep struct {
	Commit   func() error
	Rollback func() error
	Timeout  time.Duration
}

type SagaOrchestrator struct {
	mu sync.Mutex
}

func NewSagaOrchestrator() *SagaOrchestrator {
	return &SagaOrchestrator{}
}

func (o *SagaOrchestrator) Execute(steps []SagaStep) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	var completedSteps []int
	var lastErr error

	for i, step := range steps {
		errChan := make(chan error, 1)
		go func(step SagaStep) {
			errChan <- step.Commit()
		}(step)

		select {
		case err := <-errChan:
			if err != nil {
				lastErr = err
				if rollbackErr := o.rollback(steps, completedSteps); rollbackErr != nil {
					return errors.Join(err, rollbackErr)
				}
				return err
			}
			completedSteps = append(completedSteps, i)
		case <-time.After(step.Timeout):
			lastErr = errors.New("operation timed out")
			if rollbackErr := o.rollback(steps, completedSteps); rollbackErr != nil {
				return errors.Join(lastErr, rollbackErr)
			}
			return lastErr
		}
	}

	return nil
}

func (o *SagaOrchestrator) rollback(steps []SagaStep, completedSteps []int) error {
	var lastErr error

	for i := len(completedSteps) - 1; i >= 0; i-- {
		stepIndex := completedSteps[i]
		step := steps[stepIndex]

		for {
			errChan := make(chan error, 1)
			go func(step SagaStep) {
				errChan <- step.Rollback()
			}(step)

			select {
			case err := <-errChan:
				if err == nil {
					break
				}
				lastErr = errors.Join(lastErr, err)
				time.Sleep(time.Second * time.Duration(i+1)) // Exponential backoff
				continue
			case <-time.After(step.Timeout):
				lastErr = errors.Join(lastErr, errors.New("rollback timed out"))
				time.Sleep(time.Second * time.Duration(i+1)) // Exponential backoff
				continue
			}
			break
		}
	}

	return lastErr
}