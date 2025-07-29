// Package tenant_limiter provides functionality for rate limiting requests on a per-tenant basis.
package tenant_limiter

// Allow checks if a request from the given tenant is allowed based on its rate limit.
// It returns true if the request is allowed, and false otherwise.
// If the request is allowed, the rate limiter should atomically increment the request count for that tenant.
//
// tenantID: A string identifying the tenant making the request.
// rateLimit: The maximum number of requests allowed per window for the tenant.
// window: The time window in seconds for the rate limit (e.g., 60 for 60 seconds).
//
// Implement this function to be thread-safe and goroutine-safe.
func Allow(tenantID string, rateLimit int, window int) bool {
	// Stub implementation to allow tests to compile
	// This will be replaced with the actual implementation
	return false
}