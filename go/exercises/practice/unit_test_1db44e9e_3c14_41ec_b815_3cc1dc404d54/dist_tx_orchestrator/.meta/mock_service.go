package dist_tx_orchestrator

import (
	"context"
	"errors"
	"time"
)

type MockService struct {
	Name           string
	ShouldFail     bool
	ShouldTimeout  bool
	CompensateFail bool
}

func (m *MockService) Prepare(ctx context.Context, txID string) error {
	if m.ShouldTimeout {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(2 * time.Second):
			return nil
		}
	}
	if m.ShouldFail {
		return errors.New("prepare failed")
	}
	return nil
}

func (m *MockService) Commit(ctx context.Context, txID string) error {
	if m.ShouldFail {
		return errors.New("commit failed")
	}
	return nil
}

func (m *MockService) Rollback(ctx context.Context, txID string) error {
	if m.CompensateFail {
		return errors.New("compensate failed")
	}
	return nil
}