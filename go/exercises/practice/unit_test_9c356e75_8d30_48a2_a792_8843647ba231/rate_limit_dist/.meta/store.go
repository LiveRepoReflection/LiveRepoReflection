package rate_limit_dist

import (
	"context"
	"time"
)

type Store interface {
	Increment(ctx context.Context, key string, window time.Duration) (int, error)
	GetCount(ctx context.Context, key string) (int, error)
	SetLimit(ctx context.Context, key string, limit int, window time.Duration) error
	GetLimit(ctx context.Context, key string) (int, time.Duration, error)
	Reset(ctx context.Context, key string) error
}