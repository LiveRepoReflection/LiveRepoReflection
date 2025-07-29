from collections import defaultdict, deque
import threading

class TransactionSystem:
    def __init__(self):
        self.lock = threading.Lock()
        self.graph = defaultdict(set)  # adjacency list for dependencies
        self.reverse_graph = defaultdict(set)  # reverse adjacency list
        self.status = {}  # 'pending', 'ready', 'failed', 'blocked'
        self.in_degree = defaultdict(int)
        self.ready_queue = deque()
        
    def add_transaction(self, transaction_id, dependencies):
        with self.lock:
            if transaction_id in self.status:
                return  # already exists
            
            self.status[transaction_id] = 'pending'
            self.in_degree[transaction_id] = len(dependencies)
            
            for dep in dependencies:
                self.graph[dep].add(transaction_id)
                self.reverse_graph[transaction_id].add(dep)
                
            if not dependencies:
                self._mark_ready(transaction_id)
                
            self._detect_cycles(transaction_id)
    
    def _detect_cycles(self, start_id):
        visited = set()
        stack = set()
        
        def dfs(node):
            if node in stack:
                return True
            if node in visited:
                return False
                
            visited.add(node)
            stack.add(node)
            
            for neighbor in self.graph.get(node, set()):
                if dfs(neighbor):
                    return True
                    
            stack.remove(node)
            return False
            
        if dfs(start_id):
            raise Exception("Circular dependency detected")
    
    def _mark_ready(self, transaction_id):
        self.status[transaction_id] = 'ready'
        self.ready_queue.append(transaction_id)
    
    def mark_transaction_failed(self, transaction_id):
        with self.lock:
            if transaction_id not in self.status:
                return
                
            self.status[transaction_id] = 'failed'
            self._block_dependents(transaction_id)
    
    def _block_dependents(self, transaction_id):
        queue = deque([transaction_id])
        
        while queue:
            current = queue.popleft()
            
            for dependent in self.graph.get(current, set()):
                if self.status[dependent] not in ('failed', 'blocked'):
                    self.status[dependent] = 'blocked'
                    queue.append(dependent)
    
    def get_ready_transactions(self):
        with self.lock:
            ready = []
            while self.ready_queue:
                transaction_id = self.ready_queue.popleft()
                if self.status[transaction_id] == 'ready':
                    ready.append(transaction_id)
            return ready
    
    def get_blocked_transactions(self):
        with self.lock:
            return [tid for tid, stat in self.status.items() if stat == 'blocked']
    
    def _update_dependencies(self, completed_id):
        for dependent in self.graph.get(completed_id, set()):
            with self.lock:
                if self.status[dependent] == 'pending':
                    self.in_degree[dependent] -= 1
                    if self.in_degree[dependent] == 0:
                        self._mark_ready(dependent)