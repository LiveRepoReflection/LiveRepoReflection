package disttxmanager

import "errors"

var (
	ErrInvalidTransaction = errors.New("invalid transaction")
	ErrInvalidStore      = errors.New("invalid store")
	ErrInvalidKey        = errors.New("invalid key")
	ErrInvalidValue      = errors.New("invalid value")
)