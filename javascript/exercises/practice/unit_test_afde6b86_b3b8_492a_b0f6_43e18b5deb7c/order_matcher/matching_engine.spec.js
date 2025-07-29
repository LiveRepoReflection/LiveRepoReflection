const MatchingEngine = require('./matching_engine');

describe('MatchingEngine', () => {
  let engine;

  beforeEach(() => {
    engine = new MatchingEngine();
  });

  test('should add an order if no match is available', () => {
    const order = {
      id: 'order1',
      type: 'buy',
      price: 100,
      quantity: 10,
      timestamp: 1000,
      trader: 'trader1'
    };
    engine.addOrder(order);
    const book = engine.getOrderBook();
    expect(book.bids.length).toBe(1);
    expect(book.asks.length).toBe(0);
    expect(book.bids[0]).toEqual(order);
  });

  test('should execute a trade when matching orders meet price conditions', () => {
    // Add a buy order and then a matching sell order.
    const buyOrder = {
      id: 'buy1',
      type: 'buy',
      price: 100,
      quantity: 10,
      timestamp: 1000,
      trader: 'buyer1'
    };
    engine.addOrder(buyOrder);

    const sellOrder = {
      id: 'sell1',
      type: 'sell',
      price: 90,
      quantity: 10,
      timestamp: 1010,
      trader: 'seller1'
    };
    engine.addOrder(sellOrder);

    const book = engine.getOrderBook();
    // Both orders should be fully matched, so the order book is empty.
    expect(book.bids.length).toBe(0);
    expect(book.asks.length).toBe(0);
  });

  test('should partially fill an order if quantities differ', () => {
    // Buy order quantity is 15 and sell order quantity is 10.
    const buyOrder = {
      id: 'buy2',
      type: 'buy',
      price: 100,
      quantity: 15,
      timestamp: 2000,
      trader: 'buyer2'
    };
    engine.addOrder(buyOrder);

    const sellOrder = {
      id: 'sell2',
      type: 'sell',
      price: 95,
      quantity: 10,
      timestamp: 2010,
      trader: 'seller2'
    };
    engine.addOrder(sellOrder);

    const book = engine.getOrderBook();
    // The sell order should be fully executed and the buy order remains with quantity 5.
    expect(book.bids.length).toBe(1);
    expect(book.bids[0].id).toBe('buy2');
    expect(book.bids[0].quantity).toBe(5);
    expect(book.asks.length).toBe(0);
  });

  test('should place an order on the opposite side if no match due to price gap', () => {
    // Buy order price is lower than sell order price; no trade should occur.
    const buyOrder = {
      id: 'buy3',
      type: 'buy',
      price: 80,
      quantity: 10,
      timestamp: 3000,
      trader: 'buyer3'
    };
    engine.addOrder(buyOrder);

    const sellOrder = {
      id: 'sell3',
      type: 'sell',
      price: 90,
      quantity: 10,
      timestamp: 3010,
      trader: 'seller3'
    };
    engine.addOrder(sellOrder);

    const book = engine.getOrderBook();
    expect(book.bids.length).toBe(1);
    expect(book.asks.length).toBe(1);
    expect(book.bids[0]).toEqual(buyOrder);
    expect(book.asks[0]).toEqual(sellOrder);
  });

  test('should cancel an existing order', () => {
    const order = {
      id: 'order4',
      type: 'buy',
      price: 110,
      quantity: 20,
      timestamp: 4000,
      trader: 'trader4'
    };
    engine.addOrder(order);
    const cancelled = engine.cancelOrder('order4');
    expect(cancelled).toBe(true);
    const book = engine.getOrderBook();
    // Ensure that the canceled order has been removed.
    expect(book.bids.length).toBe(0);
    expect(book.asks.length).toBe(0);
  });
  
  test('should return false when trying to cancel a non-existent order', () => {
    const cancelled = engine.cancelOrder('nonexistent');
    expect(cancelled).toBe(false);
  });
  
  test('should maintain proper ordering of bids (descending by price then timestamp)', () => {
    const orderA = {
      id: 'orderA',
      type: 'buy',
      price: 105,
      quantity: 10,
      timestamp: 5000,
      trader: 'traderA'
    };
    const orderB = {
      id: 'orderB',
      type: 'buy',
      price: 110,
      quantity: 15,
      timestamp: 5001,
      trader: 'traderB'
    };
    const orderC = {
      id: 'orderC',
      type: 'buy',
      price: 110,
      quantity: 5,
      timestamp: 5000,
      trader: 'traderC'
    };
    engine.addOrder(orderA);
    engine.addOrder(orderB);
    engine.addOrder(orderC);
    
    const book = engine.getOrderBook();
    expect(book.bids.length).toBe(3);
    // Verify that orders with higher prices come first and orders with equal price are sorted by timestamp.
    expect(book.bids[0]).toEqual(orderC);
    expect(book.bids[1]).toEqual(orderB);
    expect(book.bids[2]).toEqual(orderA);
  });
  
  test('should maintain proper ordering of asks (ascending by price then timestamp)', () => {
    const orderX = {
      id: 'orderX',
      type: 'sell',
      price: 95,
      quantity: 8,
      timestamp: 6000,
      trader: 'traderX'
    };
    const orderY = {
      id: 'orderY',
      type: 'sell',
      price: 90,
      quantity: 12,
      timestamp: 6001,
      trader: 'traderY'
    };
    const orderZ = {
      id: 'orderZ',
      type: 'sell',
      price: 90,
      quantity: 7,
      timestamp: 6000,
      trader: 'traderZ'
    };
    engine.addOrder(orderX);
    engine.addOrder(orderY);
    engine.addOrder(orderZ);
    
    const book = engine.getOrderBook();
    expect(book.asks.length).toBe(3);
    // Verify that orders with lower prices come first and orders with equal price are sorted by timestamp.
    expect(book.asks[0]).toEqual(orderZ);
    expect(book.asks[1]).toEqual(orderY);
    expect(book.asks[2]).toEqual(orderX);
  });
  
  test('should throw error when adding orders with invalid quantity or price', () => {
    const invalidOrder1 = {
      id: 'invalid1',
      type: 'buy',
      price: -100,
      quantity: 10,
      timestamp: 7000,
      trader: 'traderInvalid'
    };
    const invalidOrder2 = {
      id: 'invalid2',
      type: 'sell',
      price: 100,
      quantity: 0,
      timestamp: 7001,
      trader: 'traderInvalid'
    };
    expect(() => engine.addOrder(invalidOrder1)).toThrow();
    expect(() => engine.addOrder(invalidOrder2)).toThrow();
  });
  
  test('should process multiple orders concurrently', async () => {
    // Simulate concurrent addition of orders.
    const orders = [];
    for (let i = 1; i <= 100; i++) {
      orders.push({
        id: `order_concurrent_${i}`,
        type: i % 2 === 0 ? 'buy' : 'sell',
        price: 100 + (i % 10),
        quantity: 5 + (i % 3),
        timestamp: 8000 + i,
        trader: `trader_${i}`
      });
    }
  
    await Promise.all(orders.map(order => {
      return new Promise(resolve => {
        engine.addOrder(order);
        resolve();
      });
    }));
  
    const book = engine.getOrderBook();
    // Check that all orders in the book have valid positive price and quantity.
    book.bids.forEach(order => {
      expect(order.price).toBeGreaterThan(0);
      expect(order.quantity).toBeGreaterThan(0);
    });
    book.asks.forEach(order => {
      expect(order.price).toBeGreaterThan(0);
      expect(order.quantity).toBeGreaterThan(0);
    });
  });
});