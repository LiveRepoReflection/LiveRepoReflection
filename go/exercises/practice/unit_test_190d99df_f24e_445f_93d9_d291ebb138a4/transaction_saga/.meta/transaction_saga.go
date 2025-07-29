package transaction_saga

import (
	"context"
	"errors"
	"log"
	"sync"
	"time"
)

type Action struct {
	Name        string
	Forward     func(ctx context.Context) error
	Compensation func(ctx context.Context) error
	Timeout     time.Duration
}

type TransactionOrchestrator struct {
	mu sync.Mutex
}

func NewTransactionOrchestrator() *TransactionOrchestrator {
	return &TransactionOrchestrator{}
}

func (o *TransactionOrchestrator) Execute(ctx context.Context, actions []Action) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	var completedActions []Action
	var finalErr error

	for _, action := range actions {
		actionCtx, cancel := context.WithTimeout(ctx, action.Timeout)
		defer cancel()

		log.Printf("Executing action: %s", action.Name)
		err := action.Forward(actionCtx)
		if err != nil {
			log.Printf("Action %s failed: %v", action.Name, err)
			finalErr = err
			break
		}
		log.Printf("Action %s completed successfully", action.Name)
		completedActions = append(completedActions, action)
	}

	if finalErr != nil {
		log.Printf("Transaction failed, executing compensations")
		compensationErrs := o.executeCompensations(ctx, completedActions)
		if len(compensationErrs) > 0 {
			finalErr = errors.Join(append([]error{finalErr}, compensationErrs...)...)
		}
	}

	return finalErr
}

func (o *TransactionOrchestrator) executeCompensations(ctx context.Context, actions []Action) []error {
	var errs []error

	for i := len(actions) - 1; i >= 0; i-- {
		action := actions[i]
		actionCtx, cancel := context.WithTimeout(ctx, action.Timeout)
		defer cancel()

		log.Printf("Executing compensation for action: %s", action.Name)
		err := action.Compensation(actionCtx)
		if err != nil {
			log.Printf("Compensation for action %s failed: %v", action.Name, err)
			errs = append(errs, err)
		} else {
			log.Printf("Compensation for action %s completed successfully", action.Name)
		}
	}

	return errs
}