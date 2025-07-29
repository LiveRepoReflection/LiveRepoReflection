package weighted_limiter

import "errors"

var (
	ErrInvalidTierConfig    = errors.New("invalid tier configuration")
	ErrInvalidWeight        = errors.New("invalid request weight")
	ErrInvalidClientID      = errors.New("invalid client ID")
	ErrRateLimitExceeded    = errors.New("rate limit exceeded")
	ErrInternalServerError  = errors.New("internal server error")
)