const { describe, test, expect } = require('@jest/globals');
const { MedianTracker } = require('./median_tracker');

describe('MedianTracker', () => {
  test('should return null if no data points added', () => {
    const tracker = new MedianTracker();
    expect(tracker.getMedian()).toBe(null);
  });

  test('should return the same value for a single data point', () => {
    const tracker = new MedianTracker();
    tracker.addDataPoint(10);
    expect(tracker.getMedian()).toBe(10);
  });

  test('should compute the correct median for an odd number of data points', () => {
    const tracker = new MedianTracker();
    tracker.addDataPoint(5);
    tracker.addDataPoint(1);
    tracker.addDataPoint(9);
    // Sorted: [1, 5, 9] => median is 5
    expect(tracker.getMedian()).toBe(5);
  });

  test('should compute the correct median for an even number of data points', () => {
    const tracker = new MedianTracker();
    tracker.addDataPoint(2);
    tracker.addDataPoint(8);
    tracker.addDataPoint(3);
    tracker.addDataPoint(5);
    // Sorted: [2, 3, 5, 8] => median is (3+5)/2 = 4
    expect(tracker.getMedian()).toBe(4);
  });

  test('should update the median dynamically as new data points are added', () => {
    const tracker = new MedianTracker();
    const values = [3, 1, 4, 1, 5, 9, 2, 6];
    const sortedValues = [];
    for (let i = 0; i < values.length; i++) {
      tracker.addDataPoint(values[i]);
      sortedValues.push(values[i]);
      sortedValues.sort((a, b) => a - b);
      let median;
      const n = sortedValues.length;
      if (n % 2 === 1) {
        median = sortedValues[Math.floor(n / 2)];
      } else {
        median = (sortedValues[n / 2 - 1] + sortedValues[n / 2]) / 2;
      }
      expect(tracker.getMedian()).toBe(median);
    }
  });

  test('should handle negative and floating point values', () => {
    const tracker = new MedianTracker();
    const values = [-1.5, 3.2, 0, -2.8, 5.6];
    const sortedValues = [...values].sort((a, b) => a - b);
    let expectedMedian;
    const n = sortedValues.length;
    if (n % 2 === 1) {
      expectedMedian = sortedValues[Math.floor(n / 2)];
    } else {
      expectedMedian = (sortedValues[n / 2 - 1] + sortedValues[n / 2]) / 2;
    }
    values.forEach(val => tracker.addDataPoint(val));
    expect(tracker.getMedian()).toBe(expectedMedian);
  });
});