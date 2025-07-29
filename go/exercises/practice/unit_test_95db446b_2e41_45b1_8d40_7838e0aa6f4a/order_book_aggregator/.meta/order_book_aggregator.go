package order_book_aggregator

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"sort"
	"sync"
	"time"
)

type ShardConfig struct {
	Endpoint string
	Weight   float64
}

type Config struct {
	Shards    []ShardConfig
	Depth     int
	Staleness time.Duration
}

type OrderLevel struct {
	Price    float64
	Quantity float64
}

type OrderBook struct {
	Bids []OrderLevel
	Asks []OrderLevel
}

type Aggregator struct {
	config       Config
	book         OrderBook
	metricsMutex sync.Mutex
	Updates      int
	TotalLatency time.Duration
}

type shardResponse struct {
	Orders []orderEntry `json:"orders"`
}

type orderEntry struct {
	Price     float64 `json:"price"`
	Quantity  float64 `json:"quantity"`
	Timestamp string  `json:"timestamp"`
	Side      string  `json:"side"`
}

type shardResult struct {
	orders  []orderEntry
	weight  float64
	latency time.Duration
	err     error
}

func NewAggregator(config Config) *Aggregator {
	return &Aggregator{
		config: config,
	}
}

func (a *Aggregator) RunOnce() error {
	var wg sync.WaitGroup
	ch := make(chan shardResult, len(a.config.Shards))
	for _, shard := range a.config.Shards {
		wg.Add(1)
		go func(s ShardConfig) {
			defer wg.Done()
			start := time.Now()
			resp, err := http.Get(s.Endpoint)
			latency := time.Since(start)
			if err != nil {
				ch <- shardResult{err: err, weight: s.Weight, latency: latency}
				return
			}
			body, err := ioutil.ReadAll(resp.Body)
			resp.Body.Close()
			if err != nil {
				ch <- shardResult{err: err, weight: s.Weight, latency: latency}
				return
			}
			if resp.StatusCode != http.StatusOK {
				ch <- shardResult{err: errors.New("non-200 response"), weight: s.Weight, latency: latency}
				return
			}
			var sr shardResponse
			err = json.Unmarshal(body, &sr)
			if err != nil {
				ch <- shardResult{err: err, weight: s.Weight, latency: latency}
				return
			}
			ch <- shardResult{orders: sr.Orders, weight: s.Weight, latency: latency, err: nil}
		}(shard)
	}
	wg.Wait()
	close(ch)

	now := time.Now().UTC()
	bidMap := make(map[float64]float64)
	askMap := make(map[float64]float64)
	var anySuccess bool

	for res := range ch {
		if res.err != nil {
			continue
		}
		anySuccess = true
		for _, order := range res.orders {
			ts, err := time.Parse(time.RFC3339, order.Timestamp)
			if err != nil {
				continue
			}
			if now.Sub(ts) > a.config.Staleness {
				continue
			}
			weightedQty := order.Quantity * res.weight
			if order.Side == "bid" {
				bidMap[order.Price] += weightedQty
			} else if order.Side == "ask" {
				askMap[order.Price] += weightedQty
			}
		}
		a.metricsMutex.Lock()
		a.TotalLatency += res.latency
		a.metricsMutex.Unlock()
	}
	if !anySuccess {
		return errors.New("all shard requests failed")
	}

	var bids []OrderLevel
	for price, qty := range bidMap {
		bids = append(bids, OrderLevel{Price: price, Quantity: qty})
	}
	var asks []OrderLevel
	for price, qty := range askMap {
		asks = append(asks, OrderLevel{Price: price, Quantity: qty})
	}

	sort.Slice(bids, func(i, j int) bool {
		return bids[i].Price > bids[j].Price
	})
	sort.Slice(asks, func(i, j int) bool {
		return asks[i].Price < asks[j].Price
	})

	if len(bids) > a.config.Depth {
		bids = bids[:a.config.Depth]
	}
	if len(asks) > a.config.Depth {
		asks = asks[:a.config.Depth]
	}

	a.book = OrderBook{
		Bids: bids,
		Asks: asks,
	}
	a.metricsMutex.Lock()
	a.Updates++
	a.metricsMutex.Unlock()

	return nil
}

func (a *Aggregator) GetAggregatedBook() OrderBook {
	return a.book
}

func (a *Aggregator) GetMetrics() (updates int, avgLatency time.Duration) {
	a.metricsMutex.Lock()
	defer a.metricsMutex.Unlock()
	if a.Updates == 0 {
		return 0, 0
	}
	return a.Updates, a.TotalLatency / time.Duration(a.Updates)
}