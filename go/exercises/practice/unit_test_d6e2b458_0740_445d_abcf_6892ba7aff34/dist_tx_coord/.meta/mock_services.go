package dist_tx_coord

import (
	"errors"
	"time"
)

type InventoryService struct {
	prepareDelay time.Duration
	commitDelay  time.Duration
}

func NewInventoryService(prepareDelay, commitDelay time.Duration) *InventoryService {
	return &InventoryService{
		prepareDelay: prepareDelay,
		commitDelay:  commitDelay,
	}
}

func (i *InventoryService) Prepare() error {
	time.Sleep(i.prepareDelay)
	return nil
}

func (i *InventoryService) CommitRollback(commit bool) error {
	time.Sleep(i.commitDelay)
	return nil
}

func (i *InventoryService) GetName() string {
	return "InventoryService"
}

type PaymentService struct {
	prepareDelay time.Duration
	commitDelay  time.Duration
	failPrepare  bool
	failCommit   bool
}

func NewPaymentService(prepareDelay, commitDelay time.Duration, failPrepare, failCommit bool) *PaymentService {
	return &PaymentService{
		prepareDelay: prepareDelay,
		commitDelay:  commitDelay,
		failPrepare:  failPrepare,
		failCommit:   failCommit,
	}
}

func (p *PaymentService) Prepare() error {
	time.Sleep(p.prepareDelay)
	if p.failPrepare {
		return errors.New("payment service: insufficient funds")
	}
	return nil
}

func (p *PaymentService) CommitRollback(commit bool) error {
	time.Sleep(p.commitDelay)
	if commit && p.failCommit {
		return errors.New("payment service: commit failed")
	}
	return nil
}

func (p *PaymentService) GetName() string {
	return "PaymentService"
}

type ShippingService struct {
	prepareDelay time.Duration
	commitDelay  time.Duration
}

func NewShippingService(prepareDelay, commitDelay time.Duration) *ShippingService {
	return &ShippingService{
		prepareDelay: prepareDelay,
		commitDelay:  commitDelay,
	}
}

func (s *ShippingService) Prepare() error {
	time.Sleep(s.prepareDelay)
	return nil
}

func (s *ShippingService) CommitRollback(commit bool) error {
	time.Sleep(s.commitDelay)
	return nil
}

func (s *ShippingService) GetName() string {
	return "ShippingService"
}