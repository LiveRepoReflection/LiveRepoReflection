const eventsStore = new Map();

function scheduleEvent(event) {
  // In a real decentralized system, additional consistency logic and data replication would be implemented here.
  eventsStore.set(event.id, event);
}

function cancelEvent(eventId) {
  // In a real scenario, cancellation would be propagated across nodes.
  eventsStore.delete(eventId);
}

function retrieveEvents(participantId, startTime, endTime) {
  const result = [];
  eventsStore.forEach(event => {
    if (
      event.participants.includes(participantId) &&
      event.timestamp >= startTime &&
      event.timestamp <= endTime
    ) {
      result.push(event);
    }
  });
  result.sort((a, b) => a.timestamp - b.timestamp);
  return result;
}

function triggerEvents() {
  const now = Date.now();
  const eventsToTrigger = [];
  eventsStore.forEach(event => {
    if (event.timestamp <= now) {
      eventsToTrigger.push(event);
    }
  });

  for (const event of eventsToTrigger) {
    try {
      // Attempt to notify all participants
      for (const participant of event.participants) {
        global.notifyUser(participant, event.payload);
      }
      // If all notifications are successful, remove the event from the store.
      eventsStore.delete(event.id);
    } catch (error) {
      // If any notification fails, do not remove the event, ensuring it can be retried.
      throw error;
    }
  }
}

// Helper function for testing purposes to reset the internal event store.
function _resetStore() {
  eventsStore.clear();
}

module.exports = {
  scheduleEvent,
  cancelEvent,
  retrieveEvents,
  triggerEvents,
  _resetStore
};