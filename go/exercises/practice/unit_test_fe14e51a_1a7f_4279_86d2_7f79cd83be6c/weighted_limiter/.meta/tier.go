package weighted_limiter

// BucketTierConfig represents the configuration for creating a new bucket tier
type BucketTierConfig struct {
	Capacity   int `json:"capacity"`
	RefillRate int `json:"refill_rate"`
}

func validateTierConfig(config BucketTierConfig) error {
	if config.Capacity <= 0 {
		return ErrInvalidTierConfig
	}
	if config.RefillRate <= 0 {
		return ErrInvalidTierConfig
	}
	return nil
}