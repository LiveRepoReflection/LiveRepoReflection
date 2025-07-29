package dtc_coordinator

import (
	"errors"
	"sync"
	"testing"
	"time"
)

func TestCoordinateTransaction_AllSuccessful(t *testing.T) {
	var mu sync.Mutex
	var prepared []string
	var committed []string
	var rolledBack []string

	ops := []ServiceOperation{
		{
			ServiceID: "service1",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service1")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				mu.Lock()
				committed = append(committed, "service1")
				mu.Unlock()
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service1")
				mu.Unlock()
				return nil
			},
		},
		{
			ServiceID: "service2",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service2")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				mu.Lock()
				committed = append(committed, "service2")
				mu.Unlock()
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service2")
				mu.Unlock()
				return nil
			},
		},
	}

	err := CoordinateTransaction("tx1", ops, 3*time.Second)
	if err != nil {
		t.Errorf("expected nil error, got: %v", err)
	}
	if len(committed) != 2 {
		t.Errorf("expected 2 services to commit, got: %v", committed)
	}
	if len(rolledBack) != 0 {
		t.Errorf("expected no rollback, got: %v", rolledBack)
	}
}

func TestCoordinateTransaction_PrepareFailure(t *testing.T) {
	var mu sync.Mutex
	var prepared []string
	var rolledBack []string

	ops := []ServiceOperation{
		{
			ServiceID: "service1",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service1")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service1")
				mu.Unlock()
				return nil
			},
		},
		{
			ServiceID: "service2",
			PrepareFunc: func(tid string) error {
				return errors.New("prepare error")
			},
			CommitFunc: func(tid string) error {
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service2")
				mu.Unlock()
				return nil
			},
		},
	}

	err := CoordinateTransaction("tx2", ops, 3*time.Second)
	if err == nil {
		t.Errorf("expected error due to prepare failure, got nil")
	}
	// Only service1 should have been prepared successfully and thus require rollback.
	mu.Lock()
	defer mu.Unlock()
	if len(rolledBack) != 1 || rolledBack[0] != "service1" {
		t.Errorf("expected rollback called only for service1, got: %v", rolledBack)
	}
}

func TestCoordinateTransaction_PrepareTimeout(t *testing.T) {
	var mu sync.Mutex
	var prepared []string
	var rolledBack []string

	ops := []ServiceOperation{
		{
			ServiceID: "service1",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service1")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service1")
				mu.Unlock()
				return nil
			},
		},
		{
			ServiceID: "service2",
			PrepareFunc: func(tid string) error {
				// Sleep longer than the timeout
				time.Sleep(500 * time.Millisecond)
				mu.Lock()
				prepared = append(prepared, "service2")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service2")
				mu.Unlock()
				return nil
			},
		},
	}

	err := CoordinateTransaction("tx3", ops, 100*time.Millisecond)
	if err == nil {
		t.Errorf("expected error due to timeout, got nil")
	}
	mu.Lock()
	if len(rolledBack) == 0 {
		t.Errorf("expected rollback for services that prepared, got: %v", rolledBack)
	}
	mu.Unlock()
}

func TestCoordinateTransaction_CommitFailure(t *testing.T) {
	var mu sync.Mutex
	var prepared []string
	var committed []string
	var rolledBack []string

	ops := []ServiceOperation{
		{
			ServiceID: "service1",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service1")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				mu.Lock()
				committed = append(committed, "service1")
				mu.Unlock()
				return nil
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service1")
				mu.Unlock()
				return nil
			},
		},
		{
			ServiceID: "service2",
			PrepareFunc: func(tid string) error {
				mu.Lock()
				prepared = append(prepared, "service2")
				mu.Unlock()
				return nil
			},
			CommitFunc: func(tid string) error {
				return errors.New("commit failure")
			},
			RollbackFunc: func(tid string) error {
				mu.Lock()
				rolledBack = append(rolledBack, "service2")
				mu.Unlock()
				return nil
			},
		},
	}

	err := CoordinateTransaction("tx4", ops, 3*time.Second)
	if err == nil {
		t.Errorf("expected error due to commit failure, got nil")
	}
	mu.Lock()
	if len(committed) != 1 || committed[0] != "service1" {
		t.Errorf("expected commit success only for service1, got: %v", committed)
	}
	// In commit failure scenario, rollback is not triggered because prepare phase succeeded.
	if len(rolledBack) != 0 {
		t.Errorf("expected no rollback during commit phase, got: %v", rolledBack)
	}
	mu.Unlock()
}