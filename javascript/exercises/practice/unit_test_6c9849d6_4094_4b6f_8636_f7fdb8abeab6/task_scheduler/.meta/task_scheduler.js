function scheduleTasks(tasks) {
  const n = tasks.length;
  if (n === 0) return 0;

  // Build a mapping from task id to its index in the tasks array.
  const idToIndex = {};
  for (let i = 0; i < n; i++) {
    const id = tasks[i].id;
    idToIndex[id] = i;
  }

  // Build dependency graph: for each task, create an edge from a dependency to the task.
  const graph = Array.from({ length: n }, () => []);
  for (let i = 0; i < n; i++) {
    for (const dep of tasks[i].dependencies) {
      if (dep in idToIndex) {
        const depIndex = idToIndex[dep];
        graph[depIndex].push(i);
      }
    }
  }

  // Check for cycles using DFS.
  const visited = new Array(n).fill(0); // 0: unvisited, 1: visiting, 2: visited
  function hasCycle(node) {
    if (visited[node] === 1) return true;
    if (visited[node] === 2) return false;
    visited[node] = 1;
    for (const neighbor of graph[node]) {
      if (hasCycle(neighbor)) return true;
    }
    visited[node] = 2;
    return false;
  }
  for (let i = 0; i < n; i++) {
    if (visited[i] === 0 && hasCycle(i)) return -1;
  }

  // DP approach using bitmasking with merging of Pareto-optimal states.
  // dp[mask] will store objects { time, lateness } representing the cumulative time and total lateness
  // achieved for the set of tasks indicated by mask.
  const totalStates = 1 << n;
  const dp = new Array(totalStates);
  for (let i = 0; i < totalStates; i++) {
    dp[i] = [];
  }
  dp[0].push({ time: 0, lateness: 0 });

  // Helper: Check if task index j is available given current mask.
  function isAvailable(j, mask) {
    for (const dep of tasks[j].dependencies) {
      const depIndex = idToIndex[dep];
      if ((mask & (1 << depIndex)) === 0) return false;
    }
    return true;
  }

  // Helper: Merge a new state into dp[newMask] maintaining Pareto optimality.
  function mergeState(newMask, newState) {
    for (const state of dp[newMask]) {
      if (state.time <= newState.time && state.lateness <= newState.lateness) {
        return;
      }
    }
    dp[newMask] = dp[newMask].filter(
      (state) => !(newState.time <= state.time && newState.lateness <= state.lateness)
    );
    dp[newMask].push(newState);
  }

  // Iterate over all possible masks.
  for (let mask = 0; mask < totalStates; mask++) {
    if (dp[mask].length === 0) continue;
    for (let j = 0; j < n; j++) {
      if ((mask & (1 << j)) !== 0) continue;
      if (!isAvailable(j, mask)) continue;
      for (const state of dp[mask]) {
        const task = tasks[j];
        const newTime = state.time + task.duration;
        const taskLateness = Math.max(0, newTime - task.deadline);
        const newLateness = state.lateness + taskLateness;
        const newMask = mask | (1 << j);
        mergeState(newMask, { time: newTime, lateness: newLateness });
      }
    }
  }

  // The final state is when all tasks have been scheduled.
  const finalMask = totalStates - 1;
  let result = Infinity;
  for (const state of dp[finalMask]) {
    result = Math.min(result, state.lateness);
  }
  return result;
}

module.exports = { scheduleTasks };