package distributed_saga

// This test file contains test cases for the distributed transaction orchestration system

type TransactionTestCase struct {
	description string
	orderID     string
	userID      string
	products    []Product
	expected    TransactionResult
	expectedLog []string
	failures    []SimulatedFailure
	config      OrchestratorConfig
}

// Product represents a product to be ordered
type Product struct {
	ID       string
	Quantity int
	Price    float64
}

// TransactionResult represents the expected result of a transaction
type TransactionResult struct {
	Status           TransactionStatus
	OrderStatus      string
	PaymentStatus    string
	InventoryStatus  string
	NotificationSent bool
}

// TransactionStatus represents the possible statuses of a transaction
type TransactionStatus string

const (
	TransactionSuccess TransactionStatus = "SUCCESS"
	TransactionFailure TransactionStatus = "FAILURE"
	TransactionTimeout TransactionStatus = "TIMEOUT"
)

// SimulatedFailure represents a simulated failure in the system
type SimulatedFailure struct {
	Service   string
	Operation string
	ErrorMsg  string
	Count     int // Number of consecutive failures before succeeding
}

// OrchestratorConfig contains configuration for the orchestrator
type OrchestratorConfig struct {
	RetryCount      int
	RetryDelayMs    int
	TimeoutMs       int
	ConcurrencyMode string
}

var testCases = []TransactionTestCase{
	{
		description: "Successful transaction",
		orderID:     "order-123",
		userID:      "user-456",
		products: []Product{
			{ID: "product-1", Quantity: 2, Price: 10.0},
			{ID: "product-2", Quantity: 1, Price: 20.0},
		},
		expected: TransactionResult{
			Status:           TransactionSuccess,
			OrderStatus:      "CONFIRMED",
			PaymentStatus:    "AUTHORIZED",
			InventoryStatus:  "RESERVED",
			NotificationSent: true,
		},
		expectedLog: []string{
			"Order created",
			"Payment authorized",
			"Inventory reserved",
			"Order confirmed",
			"Notification sent",
		},
		failures: []SimulatedFailure{},
		config: OrchestratorConfig{
			RetryCount:      3,
			RetryDelayMs:    100,
			TimeoutMs:       5000,
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
	{
		description: "Payment failure with rollback",
		orderID:     "order-124",
		userID:      "user-456",
		products: []Product{
			{ID: "product-1", Quantity: 2, Price: 10.0},
		},
		expected: TransactionResult{
			Status:           TransactionFailure,
			OrderStatus:      "CANCELLED",
			PaymentStatus:    "FAILED",
			InventoryStatus:  "INITIAL",
			NotificationSent: false,
		},
		expectedLog: []string{
			"Order created",
			"Payment failed",
			"Order cancelled",
		},
		failures: []SimulatedFailure{
			{
				Service:   "payment",
				Operation: "authorize",
				ErrorMsg:  "Insufficient funds",
				Count:     3,
			},
		},
		config: OrchestratorConfig{
			RetryCount:      3,
			RetryDelayMs:    100,
			TimeoutMs:       5000,
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
	{
		description: "Inventory failure with rollback",
		orderID:     "order-125",
		userID:      "user-457",
		products: []Product{
			{ID: "product-3", Quantity: 100, Price: 5.0}, // Intentionally large quantity to cause inventory failure
		},
		expected: TransactionResult{
			Status:           TransactionFailure,
			OrderStatus:      "CANCELLED",
			PaymentStatus:    "CANCELLED", // Payment was authorized but then cancelled
			InventoryStatus:  "FAILED",
			NotificationSent: false,
		},
		expectedLog: []string{
			"Order created",
			"Payment authorized",
			"Inventory failed",
			"Payment cancelled",
			"Order cancelled",
		},
		failures: []SimulatedFailure{
			{
				Service:   "inventory",
				Operation: "reserve",
				ErrorMsg:  "Insufficient inventory",
				Count:     3,
			},
		},
		config: OrchestratorConfig{
			RetryCount:      3,
			RetryDelayMs:    100,
			TimeoutMs:       5000,
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
	{
		description: "Notification failure but transaction succeeds",
		orderID:     "order-126",
		userID:      "user-458",
		products: []Product{
			{ID: "product-1", Quantity: 1, Price: 10.0},
		},
		expected: TransactionResult{
			Status:           TransactionSuccess,
			OrderStatus:      "CONFIRMED",
			PaymentStatus:    "AUTHORIZED",
			InventoryStatus:  "RESERVED",
			NotificationSent: false,
		},
		expectedLog: []string{
			"Order created",
			"Payment authorized",
			"Inventory reserved",
			"Order confirmed",
			"Notification failed",
		},
		failures: []SimulatedFailure{
			{
				Service:   "notification",
				Operation: "send",
				ErrorMsg:  "Email service down",
				Count:     5, // More than retry count to ensure it always fails
			},
		},
		config: OrchestratorConfig{
			RetryCount:      3,
			RetryDelayMs:    100,
			TimeoutMs:       5000,
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
	{
		description: "Transient payment failure with successful retry",
		orderID:     "order-127",
		userID:      "user-459",
		products: []Product{
			{ID: "product-1", Quantity: 1, Price: 10.0},
		},
		expected: TransactionResult{
			Status:           TransactionSuccess,
			OrderStatus:      "CONFIRMED",
			PaymentStatus:    "AUTHORIZED",
			InventoryStatus:  "RESERVED",
			NotificationSent: true,
		},
		expectedLog: []string{
			"Order created",
			"Payment failed",
			"Payment retry",
			"Payment authorized", // Should succeed on retry
			"Inventory reserved",
			"Order confirmed",
			"Notification sent",
		},
		failures: []SimulatedFailure{
			{
				Service:   "payment",
				Operation: "authorize",
				ErrorMsg:  "Network error",
				Count:     1, // Fails once, then succeeds
			},
		},
		config: OrchestratorConfig{
			RetryCount:      3,
			RetryDelayMs:    100,
			TimeoutMs:       5000,
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
	{
		description: "Transaction timeout",
		orderID:     "order-128",
		userID:      "user-460",
		products: []Product{
			{ID: "product-1", Quantity: 1, Price: 10.0},
		},
		expected: TransactionResult{
			Status:           TransactionTimeout,
			OrderStatus:      "CANCELLED",
			PaymentStatus:    "UNKNOWN",
			InventoryStatus:  "INITIAL",
			NotificationSent: false,
		},
		expectedLog: []string{
			"Order created",
			"Payment timed out",
			"Order cancelled",
		},
		failures: []SimulatedFailure{},
		config: OrchestratorConfig{
			RetryCount:      1,
			RetryDelayMs:    100,
			TimeoutMs:       200, // Very low timeout to trigger timeout failure
			ConcurrencyMode: "SEQUENTIAL",
		},
	},
}