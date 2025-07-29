package distributedtx

import "errors"

var (
    ErrServiceUnavailable = errors.New("service unavailable")
    ErrInvalidState      = errors.New("invalid transaction state")
    ErrTransactionFailed = errors.New("transaction failed")
)