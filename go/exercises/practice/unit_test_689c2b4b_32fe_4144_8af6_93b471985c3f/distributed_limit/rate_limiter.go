package distributed_limit

import "time"

// RateLimiter interface defines the methods that any rate limiter implementation must provide
type RateLimiter interface {
	// Allow checks if a request with the given identifier should be allowed
	// and returns a time.Duration indicating how long to wait before trying again if not allowed
	Allow(identifier string) (bool, time.Duration)

	// ConfigureLimit sets a custom limit and window for a specific identifier
	ConfigureLimit(identifier string, limit int, window time.Duration)

	// GetLimit retrieves the current limit and window for a specific identifier
	GetLimit(identifier string) (int, time.Duration)
}