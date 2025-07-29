const { optimalMeetingPoint } = require('../meeting_point');

describe('Optimal Meeting Point', () => {
  test('Single node graph', () => {
    const n = 1;
    const roads = [];
    const meetingParticipants = [0];
    const result = optimalMeetingPoint(n, roads, meetingParticipants);
    expect(result).toBe(0);
  });

  test('Example provided in description', () => {
    const n = 5;
    const roads = [
      [0, 1, 5],
      [0, 2, 2],
      [1, 2, 3],
      [1, 3, 1],
      [2, 3, 4],
      [3, 4, 6]
    ];
    const meetingParticipants = [0, 4];
    const result = optimalMeetingPoint(n, roads, meetingParticipants);
    expect(result).toBe(3);
  });

  test('Disconnected graph with isolated node', () => {
    const n = 4;
    const roads = [
      [0, 1, 10],
      [1, 2, 10]
    ];
    // Node 3 is isolated. Meeting participants are 0 and 2.
    // Only nodes 0, 1, 2 are reachable for both, node 1 gives min maximum cost.
    const meetingParticipants = [0, 2];
    const result = optimalMeetingPoint(n, roads, meetingParticipants);
    expect(result).toBe(1);
  });

  test('Multiple optimal meeting point candidates', () => {
    const n = 6;
    const roads = [
      [0, 1, 2],
      [1, 2, 2],
      [2, 3, 2],
      [3, 4, 2],
      [4, 5, 2],
      [0, 2, 3],
      [3, 5, 3]
    ];
    // Meeting participants at nodes 0 and 5.
    // Candidate 2 and 3 both yield a maximum cost of 6, so the smallest index (2) should be returned.
    const meetingParticipants = [0, 5];
    const result = optimalMeetingPoint(n, roads, meetingParticipants);
    expect(result).toBe(2);
  });

  test('Graph with cycle and alternate paths', () => {
    const n = 4;
    const roads = [
      [0, 1, 1],
      [1, 2, 1],
      [2, 3, 1],
      [3, 0, 1],
      [0, 2, 10]
    ];
    // Meeting participants at nodes 0 and 2.
    // For candidate 1: 0->1:1, 2->1:1, max=1;
    // For candidate 3: 0->3:1, 2->3:1, max=1.
    // Expect candidate 1 because it's the smallest index.
    const meetingParticipants = [0, 2];
    const result = optimalMeetingPoint(n, roads, meetingParticipants);
    expect(result).toBe(1);
  });
});