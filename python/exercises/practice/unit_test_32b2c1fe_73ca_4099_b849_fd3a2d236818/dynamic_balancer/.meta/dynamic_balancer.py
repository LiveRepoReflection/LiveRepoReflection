import time
from collections import deque, defaultdict

class DynamicBalancer:
    def __init__(self):
        # Pending queues for each priority in order: High > Medium > Low
        self.priority_order = ["High", "Medium", "Low"]
        self.pending_queues = {priority: deque() for priority in self.priority_order}
        # Dictionary to keep track of processing requests: request_id -> request info
        self.processing_requests = {}
        # Average response time trackers: priority -> {"total": float, "count": int}
        self.response_times = {priority: {"total": 0.0, "count": 0} for priority in self.priority_order}
        # Active worker nodes
        self.active_workers = 1
        # Last time a significant activity occurred (submit, finish, fail)
        self.last_activity_time = time.time()
        # Scaling parameters
        self.scale_up_multiplier = 2   # if pending requests > active_workers * multiplier, scale up
        self.scale_down_period = 0.15  # seconds of idle time to trigger scale down

    def submit_request(self, request_id, priority, processing_time, timeout):
        current_time = time.time()
        request = {
            "request_id": request_id,
            "priority": priority,
            "processing_time": processing_time,
            "timeout": timeout / 1000.0,  # convert milliseconds to seconds
            "submission_time": current_time,
            "start_time": None
        }
        if priority not in self.pending_queues:
            # If an unknown priority is sent, treat it as Low priority.
            priority = "Low"
        self.pending_queues[priority].append(request)
        self.last_activity_time = current_time
        self._check_scale_up()

    def worker_node_available(self):
        current_time = time.time()
        # Before dispatching, check pending queues for timed out requests and requeue them if necessary.
        for priority in self.priority_order:
            queue = self.pending_queues[priority]
            # Check each request in the queue, if timed out, requeue it by moving it to the end.
            for _ in range(len(queue)):
                request = queue.popleft()
                wait_time = current_time - request["submission_time"]
                if wait_time > request["timeout"]:
                    # Timed out; requeue by updating submission time to now.
                    request["submission_time"] = current_time
                    queue.append(request)
                else:
                    # Not timed out, push back and break; this maintains the order.
                    queue.appendleft(request)
                    break

        # Now, dispatch the highest priority available request.
        for priority in self.priority_order:
            if self.pending_queues[priority]:
                request = self.pending_queues[priority].popleft()
                request["start_time"] = current_time
                self.processing_requests[request["request_id"]] = request
                self.last_activity_time = current_time
                return request["request_id"]
        return None

    def worker_node_finished(self, request_id):
        current_time = time.time()
        if request_id in self.processing_requests:
            request = self.processing_requests.pop(request_id)
            if request["start_time"] is not None:
                response_time = (current_time - request["start_time"]) * 1000  # convert to milliseconds
                priority = request["priority"]
                self.response_times[priority]["total"] += response_time
                self.response_times[priority]["count"] += 1
        self.last_activity_time = current_time
        self._check_scale_down()

    def worker_node_failed(self, request_id):
        current_time = time.time()
        if request_id in self.processing_requests:
            request = self.processing_requests.pop(request_id)
            # Requeue the request to its corresponding pending queue.
            request["submission_time"] = current_time  # update submission time upon requeue
            request["start_time"] = None
            self.pending_queues[request["priority"]].append(request)
        self.last_activity_time = current_time
        self._check_scale_down()

    def get_system_state(self):
        current_time = time.time()
        # Before reporting state, update scaling based on idle time.
        self._check_scale_down()
        pending_counts = {priority: len(self.pending_queues[priority]) for priority in self.priority_order}
        average_response = {}
        for priority in self.priority_order:
            stats = self.response_times[priority]
            if stats["count"] > 0:
                average_response[priority] = stats["total"] / stats["count"]
            else:
                average_response[priority] = 0
        return {
            "active_workers": self.active_workers,
            "pending_requests": pending_counts,
            "average_response_time": average_response
        }

    def _check_scale_up(self):
        # Calculates total pending requests.
        total_pending = sum(len(q) for q in self.pending_queues.values())
        # If pending requests greatly exceed capacity, add a worker.
        if total_pending > self.active_workers * self.scale_up_multiplier:
            self.active_workers += 1
            self.last_activity_time = time.time()

    def _check_scale_down(self):
        current_time = time.time()
        # If the system has been idle for a while (no significant activity), scale down.
        if (current_time - self.last_activity_time) > self.scale_down_period and self.active_workers > 1:
            # Scale down by one worker.
            self.active_workers -= 1
            self.last_activity_time = current_time