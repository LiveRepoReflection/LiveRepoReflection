package consistentstore

import "errors"

var (
	ErrServerNotFound     = errors.New("server not found")
	ErrServerExists       = errors.New("server already exists")
	ErrKeyNotFound        = errors.New("key not found")
	ErrNoServersAvailable = errors.New("no servers available")
	ErrInvalidKey         = errors.New("invalid key")
	ErrInvalidValue       = errors.New("invalid value")
	ErrServerOverloaded   = errors.New("server is overloaded")
	ErrTimeout           = errors.New("operation timed out")
)