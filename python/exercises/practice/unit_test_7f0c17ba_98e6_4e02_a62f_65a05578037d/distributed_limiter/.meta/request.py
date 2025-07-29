import time

class Request:
    def __init__(self, data=None):
        self.data = data
        self.timestamp = time.time()
    
    def __repr__(self):
        return f"Request(data={self.data}, timestamp={self.timestamp})"