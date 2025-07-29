class StreamAggregator {
  constructor() {
    // Data structure: Map of deviceId -> Map of metric -> Array of events { timestamp, value }
    this.data = new Map();
  }

  ingest(deviceId, timestamp, metric, value) {
    if (!this.data.has(deviceId)) {
      this.data.set(deviceId, new Map());
    }
    const metricsMap = this.data.get(deviceId);
    if (!metricsMap.has(metric)) {
      metricsMap.set(metric, []);
    }
    metricsMap.get(metric).push({ timestamp, value });
  }

  query(deviceId, metric, aggregationType, timeWindow) {
    const events = [];

    // Determine which devices to include based on wildcard or specific deviceId.
    const devices = deviceId === '*' ? Array.from(this.data.keys()) : [deviceId];

    for (const dev of devices) {
      if (this.data.has(dev)) {
        const metricsMap = this.data.get(dev);
        // Determine which metrics to include
        if (metric === '*') {
          for (const [, eventsArray] of metricsMap.entries()) {
            eventsArray.forEach(event => {
              if (event.timestamp >= timeWindow.start && event.timestamp <= timeWindow.end) {
                events.push(event);
              }
            });
          }
        } else {
          if (metricsMap.has(metric)) {
            metricsMap.get(metric).forEach(event => {
              if (event.timestamp >= timeWindow.start && event.timestamp <= timeWindow.end) {
                events.push(event);
              }
            });
          }
        }
      }
    }

    if (events.length === 0) {
      return 0;
    }

    switch (aggregationType) {
      case 'count':
        return events.length;
      case 'sum': {
        const result = events.reduce((acc, curr) => acc + curr.value, 0);
        return result;
      }
      case 'avg': {
        const total = events.reduce((acc, curr) => acc + curr.value, 0);
        return total / events.length;
      }
      case 'min': {
        const minValue = events.reduce((acc, curr) => Math.min(acc, curr.value), Infinity);
        return minValue;
      }
      case 'max': {
        const maxValue = events.reduce((acc, curr) => Math.max(acc, curr.value), -Infinity);
        return maxValue;
      }
      default:
        throw new Error(`Unsupported aggregation type: ${aggregationType}`);
    }
  }
}

module.exports = { StreamAggregator };