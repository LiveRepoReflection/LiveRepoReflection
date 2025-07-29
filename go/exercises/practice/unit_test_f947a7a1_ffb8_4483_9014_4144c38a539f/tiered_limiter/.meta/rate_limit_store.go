package tiered_limiter

import "time"

type RateLimitStore interface {
	GetRateLimit(tier string) (int, time.Duration, error)
}