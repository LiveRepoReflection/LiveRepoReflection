const { calculateFastestRoute } = require('./route_planner');

describe('calculateFastestRoute', () => {
  test('Basic route: should calculate correct total travel time for a simple route', () => {
    const edges = [
      [0, 1, 10],
      [0, 2, 15],
      [1, 2, 5],
      [2, 3, 20],
      [1, 3, 12]
    ];
    const trafficData = [
      [0, 1, 1.5],
      [1, 2, 2.0],
      [2, 3, 1.2]
    ];
    const deliveryPoints = [0, 1, 2, 3];
    // Expected: (10*1.5) + (5*2.0) + (20*1.2) = 15 + 10 + 24 = 49
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBe(49);
  });

  test('Unreachable route: should return -1 when a route between delivery points is impossible', () => {
    const edges = [
      [0, 1, 10],
      [2, 3, 20]
    ];
    const trafficData = [
      [0, 1, 1.0],
      [2, 3, 1.0]
    ];
    const deliveryPoints = [0, 1, 2];
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBe(-1);
  });

  test('Multiple paths: should choose the fastest path from multiple available routes', () => {
    const edges = [
      [0, 1, 10],
      [0, 2, 5],
      [1, 2, 2],
      [1, 3, 10],
      [2, 3, 10]
    ];
    const trafficData = [
      [0, 1, 1.0],
      [0, 2, 1.2],
      [1, 2, 1.0],
      [1, 3, 1.0],
      [2, 3, 1.5]
    ];
    // Two possible paths from 0 to 3:
    // 0->1->3: 10*1.0 + 10*1.0 = 20
    // 0->2->3: 5*1.2 + 10*1.5 = 6 + 15 = 21
    const deliveryPoints = [0, 3];
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBe(20);
  });

  test('Floating point precision: should correctly calculate travel time with non-integer traffic factors', () => {
    const edges = [
      [0, 1, 3]
    ];
    const trafficData = [
      [0, 1, 1.3333333333]
    ];
    const deliveryPoints = [0, 1];
    // Expected travel time: 3 * 1.3333333333 = 4.0 (approximately)
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBeCloseTo(4.0, 5);
  });

  test('Route with cycle: should avoid infinite loops and calculate correct travel time', () => {
    const edges = [
      [0, 1, 5],
      [1, 2, 5],
      [2, 0, 5],
      [2, 3, 10],
      [1, 3, 20]
    ];
    const trafficData = [
      [0, 1, 2],
      [1, 2, 2],
      [2, 0, 2],
      [2, 3, 1],
      [1, 3, 1.5]
    ];
    // Possible paths:
    // 0->1->3: 5*2 + 20*1.5 = 10 + 30 = 40
    // 0->1->2->3: 5*2 + 5*2 + 10*1 = 10 + 10 + 10 = 30
    const deliveryPoints = [0, 3];
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBe(30);
  });

  test('Complex multi-stop: should correctly calculate route for multiple delivery points', () => {
    const edges = [
      [0, 1, 5],
      [1, 2, 10],
      [2, 3, 5],
      [3, 4, 10],
      [0, 4, 50],
      [1, 3, 15]
    ];
    const trafficData = [
      [0, 1, 1],
      [1, 2, 1.5],
      [2, 3, 1],
      [3, 4, 1],
      [0, 4, 1],
      [1, 3, 2]
    ];
    // The route is split into two segments:
    // Segment 1: from 0 to 2 = 0->1->2: 5*1 + 10*1.5 = 5 + 15 = 20
    // Segment 2: from 2 to 4 = 2->3->4: 5*1 + 10*1 = 5 + 10 = 15
    // Total expected = 20 + 15 = 35
    const deliveryPoints = [0, 2, 4];
    const result = calculateFastestRoute(edges, trafficData, deliveryPoints);
    expect(result).toBe(35);
  });
});