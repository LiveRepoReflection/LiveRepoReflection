const { ScalableAnalyticsPlatform } = require('./stream_analytics');

describe('ScalableAnalyticsPlatform', () => {
  const baseTime = 1609459200000; // January 1, 2021 00:00:00.000 UTC
  let platform;

  beforeEach(() => {
    platform = new ScalableAnalyticsPlatform();
  });

  describe('Stream and Window Management', () => {
    test('should create a new stream successfully', () => {
      platform.createStream('stream1');
      // Before any events are ingested, querying a configured window should return empty aggregates.
      platform.addTimeWindow('stream1', 60000);
      const stats = platform.query('stream1', 60000);
      expect(stats).toEqual({ sum: 0, average: 0, min: Infinity, max: -Infinity });
    });

    test('should add a time window to an existing stream', () => {
      platform.createStream('stream1');
      platform.addTimeWindow('stream1', 60000);
      const stats = platform.query('stream1', 60000);
      expect(stats).toEqual({ sum: 0, average: 0, min: Infinity, max: -Infinity });
    });

    test('should throw an error when adding a time window to a non-existent stream', () => {
      expect(() => {
        platform.addTimeWindow('nonexistent', 60000);
      }).toThrow();
    });
  });

  describe('Event Ingestion and Aggregation', () => {
    beforeEach(() => {
      platform.createStream('stream1');
      platform.addTimeWindow('stream1', 60000); // 1 minute window
      platform.addTimeWindow('stream1', 300000); // 5 minute window
    });

    test('should ingest events and compute aggregates for 1-minute window', () => {
      platform.ingestEvent('stream1', { timestamp: baseTime, value: 10 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 1000, value: 20 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 2000, value: 5 });
      const stats = platform.query('stream1', 60000);
      expect(stats.sum).toBe(35);
      expect(stats.average).toBeCloseTo(35 / 3);
      expect(stats.min).toBe(5);
      expect(stats.max).toBe(20);
    });

    test('should compute aggregates correctly for a 5-minute window', () => {
      platform.ingestEvent('stream1', { timestamp: baseTime, value: 10 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 59000, value: 20 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 60000, value: 5 });
      const statsWindow1 = platform.query('stream1', 60000);
      const statsWindow5 = platform.query('stream1', 300000);
      // Depending on the window definition, events on the boundary should be included.
      expect(statsWindow1.sum).toBe(35);
      expect(statsWindow1.average).toBeCloseTo(35 / 3);
      expect(statsWindow1.min).toBe(5);
      expect(statsWindow1.max).toBe(20);
      expect(statsWindow5.sum).toBe(35);
      expect(statsWindow5.average).toBeCloseTo(35 / 3);
      expect(statsWindow5.min).toBe(5);
      expect(statsWindow5.max).toBe(20);
    });

    test('should remove events outside of the defined time window', () => {
      platform.ingestEvent('stream1', { timestamp: baseTime, value: 15 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 30000, value: 25 });
      // Ingest an event that advances the current time beyond the 1-minute window from the initial event.
      platform.ingestEvent('stream1', { timestamp: baseTime + 61000, value: 10 });
      const stats = platform.query('stream1', 60000);
      // The first event (timestamp baseTime) should have been purged as it is now outside the latest 60000 milliseconds window.
      expect(stats.sum).toBe(25 + 10);
      expect(stats.average).toBeCloseTo((25 + 10) / 2);
      expect(stats.min).toBe(Math.min(25, 10));
      expect(stats.max).toBe(Math.max(25, 10));
    });

    test('should handle events with negative values', () => {
      platform.ingestEvent('stream1', { timestamp: baseTime, value: -10 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 500, value: 20 });
      platform.ingestEvent('stream1', { timestamp: baseTime + 1000, value: -5 });
      const stats = platform.query('stream1', 60000);
      expect(stats.sum).toBe(-10 + 20 - 5);
      expect(stats.average).toBeCloseTo((-10 + 20 - 5) / 3);
      expect(stats.min).toBe(-10);
      expect(stats.max).toBe(20);
    });
  });

  describe('Error Handling', () => {
    test('should throw an error when ingesting an event for a non-existent stream', () => {
      expect(() => {
        platform.ingestEvent('nonexistent', { timestamp: baseTime, value: 10 });
      }).toThrow();
    });
    
    test('should throw an error when querying a non-configured time window', () => {
      platform.createStream('stream2');
      platform.addTimeWindow('stream2', 60000);
      expect(() => {
        platform.query('stream2', 300000);
      }).toThrow();
    });

    test('should throw an error when ingesting an event with invalid data types', () => {
      platform.createStream('stream3');
      platform.addTimeWindow('stream3', 60000);
      expect(() => {
        platform.ingestEvent('stream3', { timestamp: "invalid", value: 10 });
      }).toThrow();
      expect(() => {
        platform.ingestEvent('stream3', { timestamp: baseTime, value: "not a number" });
      }).toThrow();
    });
  });

  describe('Concurrent Ingestion and Querying', () => {
    beforeEach(() => {
      platform.createStream('stream4');
      platform.addTimeWindow('stream4', 60000);
    });

    test('should handle concurrent event ingestion', async () => {
      const ingestionPromises = [];
      for (let i = 0; i < 100; i++) {
        ingestionPromises.push(new Promise((resolve) => {
          setTimeout(() => {
            platform.ingestEvent('stream4', { timestamp: baseTime + i * 500, value: i });
            resolve();
          }, Math.random() * 10);
        }));
      }
      await Promise.all(ingestionPromises);
      const stats = platform.query('stream4', 60000);
      const latestTimestamp = baseTime + 99 * 500;
      const windowStart = latestTimestamp - 60000;
      let expectedSum = 0, count = 0, expectedMin = Infinity, expectedMax = -Infinity;
      for (let i = 0; i < 100; i++) {
        const ts = baseTime + i * 500;
        if (ts >= windowStart) {
          expectedSum += i;
          expectedMin = Math.min(expectedMin, i);
          expectedMax = Math.max(expectedMax, i);
          count++;
        }
      }
      const expectedAverage = count === 0 ? 0 : expectedSum / count;
      expect(stats.sum).toBe(expectedSum);
      expect(stats.average).toBeCloseTo(expectedAverage);
      expect(stats.min).toBe(expectedMin);
      expect(stats.max).toBe(expectedMax);
    });
  });
});