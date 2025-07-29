package dist_tx_orchestrator

import (
	"context"
	"errors"
	"sync"
	"time"
)

var (
	ErrPrepareFailed    = errors.New("prepare phase failed")
	ErrCommitFailed     = errors.New("commit phase failed")
	ErrRollbackFailed   = errors.New("rollback phase failed")
	ErrTransactionAborted = errors.New("transaction aborted")
)

type Orchestrator struct {
	services []Service
	timeout  time.Duration
}

func NewOrchestrator(services []Service) *Orchestrator {
	return &Orchestrator{
		services: services,
		timeout:  5 * time.Second,
	}
}

func (o *Orchestrator) ExecuteTransaction(ctx context.Context, txID string) error {
	if len(o.services) == 0 {
		return nil
	}

	ctx, cancel := context.WithTimeout(ctx, o.timeout)
	defer cancel()

	var wg sync.WaitGroup
	errChan := make(chan error, len(o.services))
	prepared := make([]Service, 0, len(o.services))

	// Prepare phase
	for _, svc := range o.services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			if err := s.Prepare(ctx, txID); err != nil {
				errChan <- err
			}
		}(svc)
	}

	go func() {
		wg.Wait()
		close(errChan)
	}()

	for err := range errChan {
		if err != nil {
			o.rollbackServices(ctx, txID, prepared)
			return errors.Join(ErrPrepareFailed, err)
		}
	}

	// All services prepared successfully
	for _, svc := range o.services {
		prepared = append(prepared, svc)
	}

	// Commit phase
	var commitErr error
	for _, svc := range prepared {
		if err := svc.Commit(ctx, txID); err != nil {
			commitErr = errors.Join(commitErr, err)
		}
	}

	if commitErr != nil {
		return errors.Join(ErrCommitFailed, commitErr)
	}

	return nil
}

func (o *Orchestrator) rollbackServices(ctx context.Context, txID string, services []Service) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(services))

	for _, svc := range services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			if err := s.Rollback(ctx, txID); err != nil {
				errChan <- err
			}
		}(svc)
	}

	go func() {
		wg.Wait()
		close(errChan)
	}()

	var rollbackErr error
	for err := range errChan {
		rollbackErr = errors.Join(rollbackErr, err)
	}

	if rollbackErr != nil {
		return errors.Join(ErrRollbackFailed, rollbackErr)
	}

	return nil
}