package distlock

import "errors"

var (
	// ErrTimeout occurs when lock acquisition times out
	ErrTimeout = errors.New("lock acquisition timeout")
	
	// ErrInvalidResource occurs when an invalid resource ID is provided
	ErrInvalidResource = errors.New("invalid resource ID")
	
	// ErrSystemFailure occurs when there's an internal system error
	ErrSystemFailure = errors.New("system failure")
	
	// ErrInvalidOperation occurs when an invalid operation is attempted
	ErrInvalidOperation = errors.New("invalid operation")
)