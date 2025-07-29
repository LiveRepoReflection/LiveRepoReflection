const { OrderBookAggregator } = require('../order_book');

describe('OrderBookAggregator', () => {
  let aggregator;
  
  beforeEach(() => {
    aggregator = new OrderBookAggregator();
  });

  test('initializes with an empty order book across symbols', () => {
    expect(aggregator.getSymbols()).toEqual([]);
  });

  test('processes a single order update and updates the order book correctly', () => {
    const update = {
      timestamp: 1000,
      symbol: "BTC/USD",
      side: "buy",
      price: 25000,
      quantity: 1.5,
      exchange: "ExchangeA"
    };

    aggregator.update(update);

    const bestBid = aggregator.getBestBid("BTC/USD");
    expect(bestBid).toEqual({ price: 25000, quantity: 1.5 });

    const bestAsk = aggregator.getBestAsk("BTC/USD");
    expect(bestAsk).toBeNull();
  });

  test('aggregates orders from multiple exchanges at the same price level', () => {
    const updateA = {
      timestamp: 1000,
      symbol: "BTC/USD",
      side: "sell",
      price: 25500,
      quantity: 2.0,
      exchange: "ExchangeA"
    };
    const updateB = {
      timestamp: 2000,
      symbol: "BTC/USD",
      side: "sell",
      price: 25500,
      quantity: 1.5,
      exchange: "ExchangeB"
    };

    aggregator.update(updateA);
    aggregator.update(updateB);

    const bestAsk = aggregator.getBestAsk("BTC/USD");
    expect(bestAsk).toEqual({ price: 25500, quantity: 3.5 });
  });

  test('ignores out-of-order updates based on the timestamp', () => {
    const updateNew = {
      timestamp: 3000,
      symbol: "BTC/USD",
      side: "buy",
      price: 24900,
      quantity: 2.0,
      exchange: "ExchangeA"
    };
    const updateOld = {
      timestamp: 2000,
      symbol: "BTC/USD",
      side: "buy",
      price: 24900,
      quantity: 1.0,
      exchange: "ExchangeA"
    };

    aggregator.update(updateNew);
    aggregator.update(updateOld);

    const bestBid = aggregator.getBestBid("BTC/USD");
    expect(bestBid).toEqual({ price: 24900, quantity: 2.0 });
  });

  test('removes price level when an update with zero quantity is received', () => {
    const addUpdate = {
      timestamp: 1000,
      symbol: "ETH/USD",
      side: "sell",
      price: 1800,
      quantity: 5.0,
      exchange: "ExchangeC"
    };

    aggregator.update(addUpdate);
    let bestAsk = aggregator.getBestAsk("ETH/USD");
    expect(bestAsk).toEqual({ price: 1800, quantity: 5.0 });

    const removeUpdate = {
      timestamp: 2000,
      symbol: "ETH/USD",
      side: "sell",
      price: 1800,
      quantity: 0,
      exchange: "ExchangeC"
    };

    aggregator.update(removeUpdate);
    bestAsk = aggregator.getBestAsk("ETH/USD");
    expect(bestAsk).toBeNull();
  });

  test('calculates depth correctly when a specific depth is queried', () => {
    const updates = [
      { timestamp: 1000, symbol: "BTC/USD", side: "buy", price: 25000, quantity: 1.0, exchange: "ExchangeA" },
      { timestamp: 1100, symbol: "BTC/USD", side: "buy", price: 24950, quantity: 2.0, exchange: "ExchangeB" },
      { timestamp: 1200, symbol: "BTC/USD", side: "buy", price: 24900, quantity: 3.0, exchange: "ExchangeC" },
      { timestamp: 1300, symbol: "BTC/USD", side: "buy", price: 24850, quantity: 4.0, exchange: "ExchangeA" }
    ];

    updates.forEach(update => aggregator.update(update));

    const depthResult = aggregator.getDepth("BTC/USD", 3);
    // Expected buy side: top three price levels 25000 (1.0), 24950 (2.0), 24900 (3.0)
    expect(depthResult.buy).toBeCloseTo(6.0, 5);
    // No sell orders added.
    expect(depthResult.sell).toBe(0);
  });

  test('calculates weighted average price (WAP) correctly for both buy and sell sides', () => {
    // Setup buy side orders.
    const buyUpdates = [
      { timestamp: 1000, symbol: "BTC/USD", side: "buy", price: 25000, quantity: 1.0, exchange: "ExchangeA" },
      { timestamp: 1100, symbol: "BTC/USD", side: "buy", price: 24950, quantity: 2.0, exchange: "ExchangeB" },
      { timestamp: 1200, symbol: "BTC/USD", side: "buy", price: 24900, quantity: 3.0, exchange: "ExchangeC" }
    ];
    buyUpdates.forEach(update => aggregator.update(update));

    // For a WAP request on buy side for quantity 3.0:
    // Use 1.0 at 25000 and 2.0 at 24950 => WAP = (25000*1 + 24950*2) / 3
    const wapBuy = aggregator.calculateWAP("BTC/USD", "buy", 3.0);
    expect(wapBuy).toBeCloseTo((25000 * 1 + 24950 * 2) / 3, 5);

    // Setup sell side orders.
    const sellUpdates = [
      { timestamp: 2000, symbol: "BTC/USD", side: "sell", price: 25500, quantity: 1.5, exchange: "ExchangeA" },
      { timestamp: 2100, symbol: "BTC/USD", side: "sell", price: 25550, quantity: 2.5, exchange: "ExchangeB" }
    ];
    sellUpdates.forEach(update => aggregator.update(update));

    // For a WAP request on sell side for quantity 3.0:
    // Use 1.5 at 25500 and 1.5 at 25550 => WAP = (25500*1.5 + 25550*1.5) / 3
    const wapSell = aggregator.calculateWAP("BTC/USD", "sell", 3.0);
    expect(wapSell).toBeCloseTo((25500 * 1.5 + 25550 * 1.5) / 3, 5);
  });

  test('returns null for WAP when the requested quantity is not available', () => {
    const update = {
      timestamp: 1000,
      symbol: "ETH/USD",
      side: "buy",
      price: 1800,
      quantity: 1.0,
      exchange: "ExchangeC"
    };

    aggregator.update(update);
    const wapBuy = aggregator.calculateWAP("ETH/USD", "buy", 2.0);
    expect(wapBuy).toBeNull();
  });

  test('handles multiple symbols independently', () => {
    const updates = [
      { timestamp: 1000, symbol: "BTC/USD", side: "buy", price: 25000, quantity: 1.0, exchange: "ExchangeA" },
      { timestamp: 1000, symbol: "ETH/USD", side: "sell", price: 1800, quantity: 2.0, exchange: "ExchangeB" }
    ];

    updates.forEach(update => aggregator.update(update));

    const bestBidBTC = aggregator.getBestBid("BTC/USD");
    expect(bestBidBTC).toEqual({ price: 25000, quantity: 1.0 });

    const bestAskETH = aggregator.getBestAsk("ETH/USD");
    expect(bestAskETH).toEqual({ price: 1800, quantity: 2.0 });
  });
});