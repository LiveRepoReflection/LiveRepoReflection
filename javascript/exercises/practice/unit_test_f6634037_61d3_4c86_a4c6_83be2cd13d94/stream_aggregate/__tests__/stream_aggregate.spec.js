const { StreamAggregator } = require('../stream_aggregate');

describe('StreamAggregator Unit Tests', () => {
  let aggregator;
  beforeEach(() => {
    aggregator = new StreamAggregator();
  });

  test('query returns 0 for no events', () => {
    const timeWindow = { start: 1609459200, end: 1609459200 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(0);
    expect(aggregator.query('device1', 'temperature', 'sum', timeWindow)).toBe(0);
    expect(aggregator.query('device1', 'temperature', 'avg', timeWindow)).toBe(0);
    expect(aggregator.query('device1', 'temperature', 'min', timeWindow)).toBe(0);
    expect(aggregator.query('device1', 'temperature', 'max', timeWindow)).toBe(0);
  });

  test('single event aggregation for sum, count, avg, min, and max', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 20);
    const timeWindow = { start: 1609459200, end: 1609459200 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(1);
    expect(aggregator.query('device1', 'temperature', 'sum', timeWindow)).toBe(20);
    expect(aggregator.query('device1', 'temperature', 'avg', timeWindow)).toBe(20);
    expect(aggregator.query('device1', 'temperature', 'min', timeWindow)).toBe(20);
    expect(aggregator.query('device1', 'temperature', 'max', timeWindow)).toBe(20);
  });

  test('multiple events aggregation with same metric and device', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 10);
    aggregator.ingest('device1', 1609459260, 'temperature', 30);
    aggregator.ingest('device1', 1609459320, 'temperature', 20);
    const timeWindow = { start: 1609459200, end: 1609459320 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(3);
    expect(aggregator.query('device1', 'temperature', 'sum', timeWindow)).toBe(60);
    expect(aggregator.query('device1', 'temperature', 'avg', timeWindow)).toBe(20);
    expect(aggregator.query('device1', 'temperature', 'min', timeWindow)).toBe(10);
    expect(aggregator.query('device1', 'temperature', 'max', timeWindow)).toBe(30);
  });

  test('time window boundaries and filtering by device', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 50);
    aggregator.ingest('device2', 1609459260, 'temperature', 30);
    aggregator.ingest('device1', 1609459320, 'temperature', 20);
    const timeWindow = { start: 1609459200, end: 1609459260 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(1);
    expect(aggregator.query('device2', 'temperature', 'sum', timeWindow)).toBe(30);
    expect(aggregator.query('*', 'temperature', 'count', timeWindow)).toBe(2);
  });

  test('wildcard query for devices and metrics', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 25);
    aggregator.ingest('device1', 1609459260, 'pressure', 1010);
    aggregator.ingest('device2', 1609459320, 'temperature', 35);
    aggregator.ingest('device2', 1609459380, 'pressure', 1020);
    const timeWindow = { start: 1609459200, end: 1609459380 };

    // Aggregating all temperature readings
    expect(aggregator.query('*', 'temperature', 'sum', timeWindow)).toBe(60);

    // Aggregating all pressure readings (average)
    expect(aggregator.query('*', 'pressure', 'avg', timeWindow)).toBe((1010 + 1020) / 2);

    // Aggregating all events for device1
    expect(aggregator.query('device1', '*', 'count', timeWindow)).toBe(2);

    // Aggregating all events for all devices and metrics
    expect(aggregator.query('*', '*', 'count', timeWindow)).toBe(4);
  });

  test('aggregation with unsupported aggregationType should throw an error', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 25);
    const timeWindow = { start: 1609459200, end: 1609459200 };
    expect(() => {
      aggregator.query('device1', 'temperature', 'median', timeWindow);
    }).toThrow(Error);
  });

  test('edge case: empty time window with start equal to end', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 15);
    aggregator.ingest('device1', 1609459210, 'temperature', 25);
    const timeWindow = { start: 1609459200, end: 1609459200 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(1);
    expect(aggregator.query('device1', 'temperature', 'sum', timeWindow)).toBe(15);
  });

  test('aggregation should only include events within the time window', () => {
    aggregator.ingest('device1', 1609459000, 'temperature', 10);
    aggregator.ingest('device1', 1609459200, 'temperature', 20);
    aggregator.ingest('device1', 1609459400, 'temperature', 30);
    const timeWindow = { start: 1609459200, end: 1609459200 };
    expect(aggregator.query('device1', 'temperature', 'count', timeWindow)).toBe(1);
  });

  test('multiple metrics for the same device', () => {
    aggregator.ingest('device1', 1609459200, 'temperature', 22);
    aggregator.ingest('device1', 1609459260, 'pressure', 1005);
    aggregator.ingest('device1', 1609459320, 'temperature', 28);
    aggregator.ingest('device1', 1609459380, 'pressure', 1015);
    const timeWindow = { start: 1609459200, end: 1609459380 };

    expect(aggregator.query('device1', 'temperature', 'avg', timeWindow)).toBe(25);
    expect(aggregator.query('device1', 'pressure', 'min', timeWindow)).toBe(1005);
    expect(aggregator.query('device1', 'pressure', 'max', timeWindow)).toBe(1015);
  });
});