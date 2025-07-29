import unittest
import time

from parallel_pipeline import run_pipeline

def step_a(data_id):
    return data_id * 2

def step_b(data_id):
    return data_id + 1

def step_c(data_id):
    return data_id ** 2

def step_sleep(data_id):
    time.sleep(0.1)
    return data_id - 1

def step_error(data_id):
    raise ValueError("Error in step processing")

class TestParallelPipeline(unittest.TestCase):
    def test_basic_pipeline(self):
        data_objects = [1, 2, 3]
        processing_steps = {
            "A": step_a,
            "B": step_b,
            "C": step_c
        }
        dependencies = {
            "A": [],
            "B": ["A"],
            "C": ["B"]
        }
        expected = {}
        for data_id in data_objects:
            expected[data_id] = {
                "A": step_a(data_id),
                "B": step_b(data_id),
                "C": step_c(data_id)
            }
        result = run_pipeline(data_objects, processing_steps, dependencies)
        self.assertEqual(result, expected)

    def test_dependency_order(self):
        execution_order = {}

        def step_recorder(name):
            def wrapper(data_id):
                execution_order.setdefault(data_id, [])
                execution_order[data_id].append(name)
                return f"{name}_{data_id}"
            return wrapper

        data_objects = [10, 20]
        processing_steps = {
            "X": step_recorder("X"),
            "Y": step_recorder("Y"),
            "Z": step_recorder("Z")
        }
        dependencies = {
            "X": [],
            "Y": ["X"],
            "Z": ["Y"]
        }
        _ = run_pipeline(data_objects, processing_steps, dependencies)
        for data_id in data_objects:
            self.assertEqual(execution_order[data_id], ["X", "Y", "Z"])

    def test_error_handling(self):
        def safe_step(data_id):
            return data_id * 3

        data_objects = [4, 5]
        processing_steps = {
            "A": step_a,
            "Error": step_error,
            "Safe": safe_step
        }
        dependencies = {
            "A": [],
            "Error": ["A"],
            "Safe": ["A"]
        }
        result = run_pipeline(data_objects, processing_steps, dependencies)
        for data_id in data_objects:
            self.assertEqual(result[data_id].get("A"), step_a(data_id))
            self.assertEqual(result[data_id].get("Safe"), safe_step(data_id))
            self.assertIn("Error", result[data_id])
            self.assertIsInstance(result[data_id]["Error"], str)
            self.assertEqual(result[data_id]["Error"], "Error in step processing")

    def test_parallelism_efficiency(self):
        data_objects = list(range(1, 11))
        processing_steps = {
            "Sleep": step_sleep,
            "A": step_a
        }
        dependencies = {
            "Sleep": [],
            "A": ["Sleep"]
        }
        start_time = time.time()
        result = run_pipeline(data_objects, processing_steps, dependencies)
        end_time = time.time()
        elapsed = end_time - start_time
        # Each step_sleep takes 0.1 sec. If processed sequentially for 10 items, it would take at least 1 sec.
        # We expect the parallel implementation to be significantly faster.
        self.assertTrue(elapsed < 1.0, "Pipeline did not execute in parallel as expected")
        for data_id in data_objects:
            self.assertEqual(result[data_id]["Sleep"], step_sleep(data_id))
            self.assertEqual(result[data_id]["A"], step_a(data_id))

    def test_no_dependencies(self):
        data_objects = [7, 8, 9]
        processing_steps = {
            "A": step_a,
            "B": step_b,
            "C": step_c
        }
        dependencies = {
            "A": [],
            "B": [],
            "C": []
        }
        expected = {}
        for data_id in data_objects:
            expected[data_id] = {
                "A": step_a(data_id),
                "B": step_b(data_id),
                "C": step_c(data_id)
            }
        result = run_pipeline(data_objects, processing_steps, dependencies)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()