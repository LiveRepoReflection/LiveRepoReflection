const { findOptimalPath } = require('../path_planning');

describe('findOptimalPath', () => {
  test('should return correct path for basic graph with no traffic signals', () => {
    const graph = {
      1: [{ destination: 2, length: 1000, speed_limit: 50, traffic_signals: [] }],
      2: [{ destination: 3, length: 500, speed_limit: 30, traffic_signals: [] }],
      3: []
    };
    const congestionLevels = { '1,2': 5, '2,3': 2 };
    const riskFactor = 1.0;
    const weightTime = 0.5;
    const weightRisk = 0.5;
    const currentTime = 0;

    const result = findOptimalPath(1, 3, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);
    expect(result).toEqual([1, 2, 3]);
  });

  test('should return null when no path exists', () => {
    const graph = {
      1: [{ destination: 2, length: 1000, speed_limit: 50, traffic_signals: [] }],
      2: [],
      3: []
    };
    const congestionLevels = { '1,2': 3 };
    const riskFactor = 1.0;
    const weightTime = 0.5;
    const weightRisk = 0.5;
    const currentTime = 0;

    const result = findOptimalPath(1, 3, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);
    expect(result).toBeNull();
  });

  test('should handle traffic signals waiting times correctly', () => {
    const graph = {
      1: [{
        destination: 2,
        length: 1000,
        speed_limit: 50,
        traffic_signals: [{
          position: 500,
          cycle: ["red", "green"],
          durations: [30, 30],
          offset: 0
        }]
      }],
      2: [{
        destination: 3,
        length: 800,
        speed_limit: 40,
        traffic_signals: [{
          position: 400,
          cycle: ["green", "red"],
          durations: [20, 40],
          offset: 10
        }]
      }],
      3: []
    };
    const congestionLevels = { '1,2': 4, '2,3': 3 };
    const riskFactor = 1.0;
    const weightTime = 0.7;
    const weightRisk = 0.3;
    const currentTime = 5;

    const result = findOptimalPath(1, 3, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);
    expect(result).toEqual([1, 2, 3]);
  });

  test('should choose path with optimal cost in a complex graph', () => {
    const graph = {
      1: [
        { destination: 2, length: 500, speed_limit: 60, traffic_signals: [] },
        { destination: 3, length: 1000, speed_limit: 60, traffic_signals: [] }
      ],
      2: [
        { destination: 4, length: 700, speed_limit: 50, traffic_signals: [] }
      ],
      3: [
        { destination: 4, length: 300, speed_limit: 40, traffic_signals: [] }
      ],
      4: []
    };
    const congestionLevels = {
      '1,2': 2,
      '1,3': 8,
      '2,4': 2,
      '3,4': 1
    };
    const riskFactor = 1.0;
    const weightTime = 0.6;
    const weightRisk = 0.4;
    const currentTime = 0;

    const result = findOptimalPath(1, 4, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);
    expect(result).toEqual([1, 2, 4]);
  });

  test('should handle invalid input parameters gracefully', () => {
    const graph = {
      1: [{ destination: 2, length: -1000, speed_limit: 50, traffic_signals: [] }],
      2: []
    };
    const congestionLevels = { '1,2': 3 };
    const riskFactor = 1.0;
    const weightTime = 0.5;
    const weightRisk = 0.5;
    const currentTime = 0;

    const result = findOptimalPath(1, 2, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime);
    expect(result).toBeNull();
  });
});