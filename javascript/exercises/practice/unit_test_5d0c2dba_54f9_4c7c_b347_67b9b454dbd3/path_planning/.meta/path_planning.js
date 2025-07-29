/**
 * Finds the optimal path from start to destination in a graph.
 *
 * @param {number} start The starting intersection ID.
 * @param {number} destination The destination intersection ID.
 * @param {object} graph A graph represented as an adjacency list where keys are intersection IDs
 *                       and values are arrays of objects representing outgoing edges.
 *                       Each edge object has the following properties:
 *                       { destination: number, length: number, speed_limit: number, traffic_signals: [] }
 * @param {object} congestionLevels An object where keys are tuples of (source, destination) intersection IDs
 *                                  representing road segments and values are congestion levels (integers between 0 and 10).
 * @param {number} riskFactor A constant factor to multiply the risk score (positive number).
 * @param {number} weightTime The weight for travel time in the cost function (positive number).
 * @param {number} weightRisk The weight for risk in the cost function (positive number).
 * @param {number} currentTime The current time in seconds from start of simulation (non-negative integer). Used to calculate traffic light state.
 *
 * @returns {Array<number> | null} An array of intersection IDs representing the optimal path from start to destination,
 *                                 or null if no path exists.
 */
function findOptimalPath(start, destination, graph, congestionLevels, riskFactor, weightTime, weightRisk, currentTime) {
  if (typeof start !== 'number' || typeof destination !== 'number' || currentTime < 0) {
    return null;
  }

  // Validate graph and parameters on edges.
  for (let node in graph) {
    let edges = graph[node];
    if (!Array.isArray(edges)) continue;
    for (let edge of edges) {
      if (edge.length < 0 || edge.speed_limit < 0) {
        return null;
      }
      if (!Array.isArray(edge.traffic_signals)) {
        return null;
      }
      for (let signal of edge.traffic_signals) {
        if (typeof signal.position !== 'number' || signal.position < 0 || signal.position >= edge.length) {
          return null;
        }
        if (!Array.isArray(signal.cycle) || !Array.isArray(signal.durations) || signal.cycle.length !== signal.durations.length) {
          return null;
        }
        for (let d of signal.durations) {
          if (d <= 0) return null;
        }
        if (signal.offset < 0) return null;
      }
    }
  }

  // Priority Queue Implementation (Min Heap)
  class MinHeap {
    constructor() {
      this.heap = [];
    }

    push(item) {
      this.heap.push(item);
      this.bubbleUp(this.heap.length - 1);
    }

    pop() {
      if (this.heap.length === 0) return null;
      const top = this.heap[0];
      const end = this.heap.pop();
      if (this.heap.length > 0) {
        this.heap[0] = end;
        this.bubbleDown(0);
      }
      return top;
    }

    bubbleUp(index) {
      const item = this.heap[index];
      while (index > 0) {
        const parentIdx = Math.floor((index - 1) / 2);
        if (this.heap[parentIdx].totalCost <= item.totalCost) break;
        this.heap[index] = this.heap[parentIdx];
        index = parentIdx;
      }
      this.heap[index] = item;
    }

    bubbleDown(index) {
      const length = this.heap.length;
      const item = this.heap[index];
      while (true) {
        let leftIndex = 2 * index + 1;
        let rightIndex = 2 * index + 2;
        let swapIndex = null;
        if (leftIndex < length) {
          if (this.heap[leftIndex].totalCost < item.totalCost) {
            swapIndex = leftIndex;
          }
        }
        if (rightIndex < length) {
          if (
            (swapIndex === null && this.heap[rightIndex].totalCost < item.totalCost) ||
            (swapIndex !== null && this.heap[rightIndex].totalCost < this.heap[leftIndex].totalCost)
          ) {
            swapIndex = rightIndex;
          }
        }
        if (swapIndex === null) break;
        this.heap[index] = this.heap[swapIndex];
        index = swapIndex;
      }
      this.heap[index] = item;
    }

    isEmpty() {
      return this.heap.length === 0;
    }
  }

  // Helper function: simulate travel along a segment including traffic signals delays.
  // Returns an object: { travelTime: number, arrivalTime: number }
  function simulateSegment(departureTime, segment) {
    const speedLimit = segment.speed_limit;
    // if speed limit is less than 1 km/h, treat as 0 km/h -> cannot traverse.
    if (speedLimit < 1) return { travelTime: Infinity, arrivalTime: Infinity };
    let t = departureTime;
    let prevPosition = 0;
    // Sort signals by position.
    const signals = segment.traffic_signals.slice().sort((a, b) => a.position - b.position);
    for (let signal of signals) {
      const distance = signal.position - prevPosition;
      const travelToSignal = (distance * 3.6) / speedLimit; // seconds
      t += travelToSignal;
      // Compute waiting time at this signal.
      const wait = getSignalWaitTime(t, signal);
      t += wait;
      prevPosition = signal.position;
    }
    // Travel the remainder of the segment.
    const remainingDistance = segment.length - prevPosition;
    const travelRemaining = (remainingDistance * 3.6) / speedLimit;
    t += travelRemaining;
    return { travelTime: t - departureTime, arrivalTime: t };
  }

  // Helper function: Calculate waiting time for a signal given the arrival time.
  function getSignalWaitTime(arrival, signal) {
    let effectiveArrival = arrival;
    // If arrival is before the signal's cycle starts, wait until offset.
    if (effectiveArrival < signal.offset) {
      effectiveArrival = signal.offset;
    }
    const cycleTotal = signal.durations.reduce((acc, d) => acc + d, 0);
    const elapsedInCycle = (effectiveArrival - signal.offset) % cycleTotal;
    // Precompute cumulative durations.
    let cumulative = [];
    let sum = 0;
    for (let d of signal.durations) {
      sum += d;
      cumulative.push(sum);
    }
    // Helper: returns state at a given time offset within the cycle.
    function getState(timeInCycle) {
      for (let i = 0; i < cumulative.length; i++) {
        if (timeInCycle < cumulative[i]) {
          return signal.cycle[i];
        }
      }
      return signal.cycle[signal.cycle.length - 1]; // fallback, should not reach here.
    }
    // If the current state is green then no waiting is needed.
    if (getState(elapsedInCycle) === 'green') {
      return 0;
    }

    // Search for the minimal waiting time until a green phase is encountered.
    for (let dt = 0; dt <= cycleTotal; dt++) {
      const candidate = (elapsedInCycle + dt) % cycleTotal;
      if (getState(candidate) === 'green') {
        return dt;
      }
    }
    return 0; // default fallback.
  }

  // Main Dijkstra-like search with simulation of signal waiting times.
  // Each entry in the priority queue is an object: { node, totalCost, currentTime, path }
  const heap = new MinHeap();
  // Map to store the best encountered cost for (node, currentTime), we store best cost per node.
  const bestCost = {};
  heap.push({ node: start, totalCost: 0, currentTime: currentTime, path: [start] });
  bestCost[start] = 0;

  while (!heap.isEmpty()) {
    const current = heap.pop();
    const { node, totalCost, currentTime: currTime, path } = current;

    if (node === destination) {
      return path;
    }

    if (!graph[node]) continue;
    for (let edge of graph[node]) {
      const key = `${node},${edge.destination}`;
      const congestion = (congestionLevels.hasOwnProperty(key)) ? congestionLevels[key] : 0;
      // Calculate risk value for this segment.
      const segmentRisk = riskFactor * (2 + congestion);
      // Simulate the travel along the current segment.
      const simulation = simulateSegment(currTime, edge);
      const travelTime = simulation.travelTime;
      if (travelTime === Infinity) continue; // Skip segments that cannot be traversed.
      const segmentCost = weightTime * travelTime + weightRisk * segmentRisk;
      const newTotalCost = totalCost + segmentCost;
      const newTime = simulation.arrivalTime;
      // If we have found a cheaper route to the neighbor, use it.
      if (bestCost[edge.destination] === undefined || newTotalCost < bestCost[edge.destination]) {
        bestCost[edge.destination] = newTotalCost;
        heap.push({
          node: edge.destination,
          totalCost: newTotalCost,
          currentTime: newTime,
          path: [...path, edge.destination]
        });
      }
    }
  }

  return null;
}

module.exports = { findOptimalPath };