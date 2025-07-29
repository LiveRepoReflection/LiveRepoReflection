import unittest
from unittest.mock import Mock, patch
from task_orchestration import orchestrate_tasks

class TestTaskOrchestration(unittest.TestCase):
    def test_basic_dependencies(self):
        task_graph = {
            1: [],
            2: [1],
            3: [1],
            4: [2, 3],
            5: [4]
        }
        
        task_functions = {
            1: Mock(return_value=10),
            2: Mock(side_effect=lambda deps: deps[1] * 2),
            3: Mock(side_effect=lambda deps: deps[1] + 5),
            4: Mock(side_effect=lambda deps: deps[2] + deps[3]),
            5: Mock(side_effect=lambda deps: deps[4] * 3)
        }
        
        results = orchestrate_tasks(task_graph, task_functions, max_workers=2)
        self.assertEqual(results, {1: 10, 2: 20, 3: 15, 4: 35, 5: 105})

    def test_failed_task_propagation(self):
        task_graph = {
            1: [],
            2: [1],
            3: [1],
            4: [2, 3]
        }
        
        task_functions = {
            1: Mock(return_value=10),
            2: Mock(side_effect=Exception("Task failed")),
            3: Mock(side_effect=lambda deps: deps[1] + 5),
            4: Mock(side_effect=lambda deps: deps[2] + deps[3])
        }
        
        results = orchestrate_tasks(task_graph, task_functions, max_workers=2)
        self.assertEqual(results, {1: 10, 2: None, 3: 15, 4: None})

    def test_empty_graph(self):
        results = orchestrate_tasks({}, {}, max_workers=2)
        self.assertEqual(results, {})

    def test_parallel_execution(self):
        task_graph = {
            1: [],
            2: [],
            3: [],
            4: [1, 2, 3]
        }
        
        task_functions = {
            1: Mock(return_value=1),
            2: Mock(return_value=2),
            3: Mock(return_value=3),
            4: Mock(side_effect=lambda deps: sum(deps.values()))
        }
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_executor.return_value.__enter__.return_value.submit.side_effect = lambda fn, *args: fn(*args)
            results = orchestrate_tasks(task_graph, task_functions, max_workers=3)
            
        self.assertEqual(results, {1: 1, 2: 2, 3: 3, 4: 6})
        self.assertEqual(task_functions[4].call_count, 1)

    def test_complex_dag(self):
        task_graph = {
            1: [],
            2: [1],
            3: [1],
            4: [2],
            5: [3],
            6: [4, 5],
            7: [6],
            8: [6],
            9: [7, 8]
        }
        
        task_functions = {
            i: Mock(return_value=i) for i in range(1, 10)
        }
        
        results = orchestrate_tasks(task_graph, task_functions, max_workers=4)
        expected = {i: i for i in range(1, 10)}
        self.assertEqual(results, expected)

    def test_task_with_no_dependencies(self):
        task_graph = {
            1: [],
            2: [],
            3: []
        }
        
        task_functions = {
            1: Mock(return_value=10),
            2: Mock(return_value=20),
            3: Mock(return_value=30)
        }
        
        results = orchestrate_tasks(task_graph, task_functions, max_workers=3)
        self.assertEqual(results, {1: 10, 2: 20, 3: 30})

if __name__ == '__main__':
    unittest.main()