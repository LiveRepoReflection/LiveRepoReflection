package dist_tx_orchestrator

import "context"

type Service interface {
	Prepare(ctx context.Context, txID string) error
	Commit(ctx context.Context, txID string) error
	Rollback(ctx context.Context, txID string) error
}