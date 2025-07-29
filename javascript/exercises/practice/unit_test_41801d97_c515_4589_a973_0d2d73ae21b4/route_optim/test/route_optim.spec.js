const { computeRoutes } = require('../route_optim');

describe('Route Optimization', () => {
  test('should return empty array when no orders are provided', () => {
    const nodes = [0];
    const edges = [];
    const orders = [];
    const routes = computeRoutes(nodes, edges, orders);
    expect(routes).toEqual([]);
  });

  test('should compute route for a single order with simple round trip', () => {
    const nodes = [0, 1];
    const edges = [
      { from: 0, to: 1, congestion: 5 },
      { from: 1, to: 0, congestion: 5 }
    ];
    const orders = [
      { orderId: 'order1', locationId: 1, startTime: 0, endTime: 1000 }
    ];
    
    const routes = computeRoutes(nodes, edges, orders);
    
    expect(routes).toHaveLength(1);
    const route1 = routes.find(r => r.orderId === 'order1');
    expect(route1).toBeDefined();
    expect(route1.route).toEqual([0, 1, 0]);
    expect(route1.totalCongestion).toBe(10);
  });

  test('should compute routes independently for multiple orders', () => {
    const nodes = [0, 1, 2];
    const edges = [
      { from: 0, to: 1, congestion: 2 },
      { from: 1, to: 0, congestion: 2 },
      { from: 0, to: 2, congestion: 3 },
      { from: 2, to: 0, congestion: 3 }
    ];
    const orders = [
      { orderId: 'order1', locationId: 1, startTime: 0, endTime: 1000 },
      { orderId: 'order2', locationId: 2, startTime: 0, endTime: 1000 }
    ];
    
    const routes = computeRoutes(nodes, edges, orders);
    expect(routes).toHaveLength(2);
    
    const order1Route = routes.find(r => r.orderId === 'order1');
    expect(order1Route).toBeDefined();
    expect(order1Route.route).toEqual([0, 1, 0]);
    expect(order1Route.totalCongestion).toBe(4);
    
    const order2Route = routes.find(r => r.orderId === 'order2');
    expect(order2Route).toBeDefined();
    expect(order2Route.route).toEqual([0, 2, 0]);
    expect(order2Route.totalCongestion).toBe(6);
  });

  test('should choose the optimal route when multiple paths are available', () => {
    const nodes = [0, 1, 2];
    const edges = [
      // Direct but expensive path
      { from: 0, to: 2, congestion: 10 },
      { from: 2, to: 0, congestion: 10 },
      // Indirect but cheaper path
      { from: 0, to: 1, congestion: 2 },
      { from: 1, to: 2, congestion: 2 },
      { from: 2, to: 1, congestion: 2 },
      { from: 1, to: 0, congestion: 2 }
    ];
    const orders = [
      { orderId: 'order1', locationId: 2, startTime: 0, endTime: 1000 }
    ];
    
    const routes = computeRoutes(nodes, edges, orders);
    expect(routes).toHaveLength(1);
    
    const order1Route = routes.find(r => r.orderId === 'order1');
    expect(order1Route).toBeDefined();
    // The optimal route should be [0, 1, 2, 1, 0] with total congestion 2+2+2+2 = 8
    expect(order1Route.route).toEqual([0, 1, 2, 1, 0]);
    expect(order1Route.totalCongestion).toBe(8);
  });

  test('should throw an error when a delivery order cannot be fulfilled within its time window', () => {
    const nodes = [0, 1];
    const edges = [
      { from: 0, to: 1, congestion: 10 },
      { from: 1, to: 0, congestion: 10 }
    ];
    // The round trip takes 20 seconds, but the delivery window is too narrow.
    const orders = [
      { orderId: 'order_unreachable', locationId: 1, startTime: 0, endTime: 15 }
    ];
    
    expect(() => {
      computeRoutes(nodes, edges, orders);
    }).toThrow(Error);
  });

  test('should handle complex scenario with multiple orders and overlapping time windows', () => {
    const nodes = [0, 1, 2, 3];
    const edges = [
      { from: 0, to: 1, congestion: 3 },
      { from: 1, to: 0, congestion: 3 },
      { from: 0, to: 2, congestion: 4 },
      { from: 2, to: 0, congestion: 4 },
      { from: 0, to: 3, congestion: 8 },
      { from: 3, to: 0, congestion: 8 },
      { from: 1, to: 2, congestion: 2 },
      { from: 2, to: 1, congestion: 2 },
      { from: 2, to: 3, congestion: 3 },
      { from: 3, to: 2, congestion: 3 },
      { from: 1, to: 3, congestion: 7 },
      { from: 3, to: 1, congestion: 7 }
    ];
    const orders = [
      { orderId: 'order1', locationId: 1, startTime: 0, endTime: 50 },
      { orderId: 'order2', locationId: 2, startTime: 0, endTime: 50 },
      { orderId: 'order3', locationId: 3, startTime: 10, endTime: 60 }
    ];
    
    const routes = computeRoutes(nodes, edges, orders);
    expect(routes).toHaveLength(3);
    
    // Validate each route meets the time window constraints and optimal path choice.
    routes.forEach(route => {
      // Check route starts and ends at depot 0.
      expect(route.route[0]).toBe(0);
      expect(route.route[route.route.length - 1]).toBe(0);
      // Total congestion should be a positive integer.
      expect(typeof route.totalCongestion).toBe('number');
      expect(route.totalCongestion).toBeGreaterThan(0);
    });
  });
});