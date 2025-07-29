package transaction_saga

import (
	"context"
	"errors"
	"time"
)

var (
	ErrOrderCreationFailed         = errors.New("order creation failed")
	ErrPaymentFailed               = errors.New("payment processing failed")
	ErrInventoryReservationFailed  = errors.New("inventory reservation failed")
	ErrOrderCancellationFailed     = errors.New("order cancellation failed")
	ErrPaymentRefundFailed         = errors.New("payment refund failed")
	ErrInventoryReleaseFailed      = errors.New("inventory release failed")

	SimulatePaymentFailure    = false
	SimulateInventoryFailure  = false
)

func CreateOrder(ctx context.Context, orderID string) error {
	select {
	case <-time.After(100 * time.Millisecond):
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func CancelOrder(ctx context.Context, orderID string) error {
	select {
	case <-time.After(100 * time.Millisecond):
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func ProcessPayment(ctx context.Context, orderID string, amount float64) error {
	select {
	case <-time.After(100 * time.Millisecond):
		if SimulatePaymentFailure {
			return ErrPaymentFailed
		}
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func RefundPayment(ctx context.Context, orderID string, amount float64) error {
	select {
	case <-time.After(100 * time.Millisecond):
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func ReserveInventory(ctx context.Context, orderID string, items []string) error {
	select {
	case <-time.After(100 * time.Millisecond):
		if SimulateInventoryFailure {
			return ErrInventoryReservationFailed
		}
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func ReleaseInventory(ctx context.Context, orderID string, items []string) error {
	select {
	case <-time.After(100 * time.Millisecond):
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}