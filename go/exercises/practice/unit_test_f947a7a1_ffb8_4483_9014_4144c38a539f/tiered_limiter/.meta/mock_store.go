package tiered_limiter

import (
	"errors"
	"time"
)

type MockRateLimitStore struct {
	Limits map[string]struct {
		Limit    int
		Duration time.Duration
	}
}

func (m *MockRateLimitStore) GetRateLimit(tier string) (int, time.Duration, error) {
	if limit, exists := m.Limits[tier]; exists {
		return limit.Limit, limit.Duration, nil
	}
	return 0, 0, errors.New("tier not found")
}