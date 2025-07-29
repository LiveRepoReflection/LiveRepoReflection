package ordermatcher

type Order struct {
	OrderID   string
	OrderType string // "BUY" or "SELL"
	Price     int    // Price per token
	Quantity  int    // Number of tokens
	Timestamp int64  // Unix timestamp of order placement (nanoseconds)
	UserID    string // Unique identifier for the user who placed the order
}

type Trade struct {
	BuyOrderID  string
	SellOrderID string
	Price       int
	Quantity    int
}