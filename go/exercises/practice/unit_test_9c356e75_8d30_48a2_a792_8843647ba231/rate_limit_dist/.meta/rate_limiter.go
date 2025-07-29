package rate_limit_dist

import (
	"context"
	"errors"
	"time"
)

type RateLimitResult struct {
	Allowed    bool
	RetryAfter time.Duration
}

type RateLimiter struct {
	store Store
}

func NewRateLimiter(store Store) *RateLimiter {
	return &RateLimiter{
		store: store,
	}
}

func (rl *RateLimiter) Allow(ctx context.Context, clientID, endpoint string) (*RateLimitResult, error) {
	key := clientID + ":" + endpoint

	limit, window, err := rl.store.GetLimit(ctx, key)
	if err != nil {
		return nil, err
	}

	if limit == 0 {
		return &RateLimitResult{Allowed: true}, nil
	}

	count, err := rl.store.Increment(ctx, key, window)
	if err != nil {
		return nil, err
	}

	if count > limit {
		_, window, err := rl.store.GetLimit(ctx, key)
		if err != nil {
			return nil, err
		}
		return &RateLimitResult{
			Allowed:    false,
			RetryAfter: window,
		}, nil
	}

	return &RateLimitResult{Allowed: true}, nil
}

func (rl *RateLimiter) SetLimit(ctx context.Context, clientID, endpoint string, limit int, window time.Duration) error {
	if limit < 0 {
		return errors.New("limit must be non-negative")
	}
	if window <= 0 {
		return errors.New("window must be positive")
	}

	key := clientID + ":" + endpoint
	return rl.store.SetLimit(ctx, key, limit, window)
}

func (rl *RateLimiter) GetLimit(ctx context.Context, clientID, endpoint string) (int, time.Duration, error) {
	key := clientID + ":" + endpoint
	return rl.store.GetLimit(ctx, key)
}

func (rl *RateLimiter) Reset(ctx context.Context, clientID, endpoint string) error {
	key := clientID + ":" + endpoint
	return rl.store.Reset(ctx, key)
}