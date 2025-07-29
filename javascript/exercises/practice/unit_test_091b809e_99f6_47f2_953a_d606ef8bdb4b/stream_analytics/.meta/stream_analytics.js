class ScalableAnalyticsPlatform {
  constructor() {
    this.streams = new Map();
  }

  createStream(streamId) {
    if (this.streams.has(streamId)) {
      throw new Error('Stream already exists');
    }
    this.streams.set(streamId, { events: [], windows: new Set() });
  }

  addTimeWindow(streamId, duration) {
    if (!this.streams.has(streamId)) {
      throw new Error('Stream does not exist');
    }
    if (typeof duration !== 'number' || duration <= 0) {
      throw new Error('Invalid window duration');
    }
    const stream = this.streams.get(streamId);
    stream.windows.add(duration);
  }

  ingestEvent(streamId, event) {
    if (!this.streams.has(streamId)) {
      throw new Error('Stream does not exist');
    }
    if (!event || typeof event.timestamp !== 'number' || typeof event.value !== 'number') {
      throw new Error('Invalid event data');
    }
    const stream = this.streams.get(streamId);
    // Append the new event (assumed to be in chronological order for a given stream)
    stream.events.push(event);
    // Purge events that are not needed for any active window.
    if (stream.windows.size > 0) {
      const maxDuration = Math.max(...stream.windows);
      const currentTime = event.timestamp;
      const threshold = currentTime - maxDuration;
      while (stream.events.length > 0 && stream.events[0].timestamp < threshold) {
        stream.events.shift();
      }
    }
  }

  query(streamId, duration) {
    if (!this.streams.has(streamId)) {
      throw new Error('Stream does not exist');
    }
    const stream = this.streams.get(streamId);
    if (!stream.windows.has(duration)) {
      throw new Error('Time window not configured for the stream');
    }
    if (stream.events.length === 0) {
      return { sum: 0, average: 0, min: Infinity, max: -Infinity };
    }
    // Use the timestamp of the latest event as the current time.
    const currentTime = stream.events[stream.events.length - 1].timestamp;
    const threshold = currentTime - duration;
    let sum = 0;
    let count = 0;
    let min = Infinity;
    let max = -Infinity;
    for (const evt of stream.events) {
      if (evt.timestamp >= threshold) {
        sum += evt.value;
        count++;
        if (evt.value < min) {
          min = evt.value;
        }
        if (evt.value > max) {
          max = evt.value;
        }
      }
    }
    const average = count ? sum / count : 0;
    return { sum, average, min, max };
  }
}

module.exports = { ScalableAnalyticsPlatform };