package sliding_window_rate_limiter

import "time"

// Config represents the configuration for the rate limiter
type Config struct {
	RequestLimit    int
	WindowSize      time.Duration
	DataStoreAddr   string
	CleanupInterval time.Duration
}

// DefaultConfig returns a default configuration
func DefaultConfig() *Config {
	return &Config{
		RequestLimit:    100,
		WindowSize:      time.Minute,
		DataStoreAddr:   "localhost:6379",
		CleanupInterval: time.Minute,
	}
}