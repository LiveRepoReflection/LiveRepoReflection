import threading

class DistLog:
    def __init__(self):
        self.log = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def append(self, data: str) -> int:
        with self.condition:
            self.log.append(data)
            index = len(self.log)
            self.condition.notify_all()
            return index

    def read(self, index: int) -> str:
        if index < 1:
            raise ValueError("Index must be at least 1.")
        with self.condition:
            while len(self.log) < index:
                self.condition.wait()
            return self.log[index - 1]

    def get_highest_index(self) -> int:
        with self.lock:
            return len(self.log)